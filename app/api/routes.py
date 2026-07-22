from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from types import SimpleNamespace
import json
import hashlib
import os
import uuid
import io

import re

from app.core.database import get_db
from app.models.models import (
    Colecao, Peca, FichaTecnica, VisualReference,
    PecaVisualReference, EtapaProducao,
    PecaMaterial, ProdutoFornecedor,
    DppPublicationRecord, UsageEvent,
)
from app.schemas.schemas import (
    ColecaoCreate, ColecaoOut,
    PecaCreate, PecaUpdate, PecaOut,
    FichaTecnicaBase, FichaTecnicaCreate, FichaTecnicaOut,
    VisualReferenceCreate, VisualReferenceOut,
    PecaVisualReferenceCreate, PecaVisualReferenceOut,
    EtapaProducaoCreate, EtapaProducaoOut,
    PecaMaterialCreate, PecaMaterialOut,
    ISCMOut,
    UsageEventCreate,
)
from app.api.fornecedores import _produto_para_materia_prima
from app.services.dpp_calculator import (
    DppCalculationError,
    DppCalculationInput,
    calculate_dpp_indicators,
)
from app.validators.dpp_validators import validate_dpp_publication
from app.telemetry_contract import EVENT_PROPERTIES, validate_v3_properties

router = APIRouter()

DPP_BASE_URL = os.getenv("DPP_BASE_URL", "https://phyllos-evidence-os.onrender.com").rstrip("/")
DPP_PUBLICATION_GATE_VERSION = "dpp-publication-gate-v1"
USAGE_EVENT_SCHEMA_VERSION = "usage-event-v2"
USAGE_EVENT_V1_NAMES = {
    "page_view", "ui_click", "form_submit", "field_change",
    "api_error", "js_error", "flow_complete", "visibility_end",
}
USAGE_EVENT_V2_NAMES = {
    "workspace_viewed", "workflow_step_viewed",
    "piece_create_started", "piece_created", "piece_create_failed",
    "technical_sheet_saved", "technical_sheet_save_failed",
    "material_sheet_saved", "material_sheet_save_failed",
    "production_stage_add_started", "production_stage_added", "production_stage_add_failed",
    "publication_readiness_viewed", "dpp_publication_started",
    "dpp_publication_blocked", "dpp_published", "dpp_publication_recovered",
    "dpp_link_copied", "dpp_link_copy_failed",
    "qr_preview_opened", "qr_preview_closed", "qr_requested", "qr_served", "qr_request_failed",
    "label_viewed", "label_print_requested",
    "public_passport_viewed", "public_passport_section_viewed", "evidence_explanation_viewed",
    "public_passport_session_ended", "api_action_failed", "js_error",
}
USAGE_EVENT_NAMES_BY_SCHEMA = {
    "usage-event-v1": USAGE_EVENT_V1_NAMES,
    "usage-event-v2": USAGE_EVENT_V2_NAMES,
    "usage-event-v3": set(EVENT_PROPERTIES),
}


def public_dpp_url(dpp_uuid: str) -> str:
    return f"{DPP_BASE_URL}/p/{dpp_uuid}"


def _find_peca_by_public_identifier(db: Session, identifier: str):
    return db.query(Peca).filter(
        (Peca.gtin == identifier)
        | (Peca.dpp_uuid == identifier)
        | (Peca.codigo == identifier)
    ).first()


def _publication_snapshot(peca, ficha, evidence_statuses: dict[str, str]) -> str:
    payload = {
        "dpp_uuid": peca.dpp_uuid,
        "dpp_version": peca.dpp_version,
        "codigo": peca.codigo,
        "nome": peca.nome,
        "gtin": peca.gtin,
        "pais_fabricacao": peca.pais_fabricacao,
        "composicao_fibras": json.loads(ficha.composicao_fibras) if ficha.composicao_fibras else [],
        "certificacoes": json.loads(ficha.certificacoes) if ficha.certificacoes else [],
        "indicadores": {
            "peso_peca_kg": ficha.peso_peca_kg,
            "agua_peca_litros": ficha.agua_peca_litros,
            "energia_peca_kwh": ficha.energia_peca_kwh,
            "pegada_carbono_kgco2e": ficha.pegada_carbono_kgco2e,
        },
        "evidence_statuses": evidence_statuses,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _record_publication_attempt(
    db: Session,
    peca,
    validation,
    resultado: str,
    snapshot_json: str | None = None,
) -> DppPublicationRecord:
    record = DppPublicationRecord(
        peca_id=peca.id,
        dpp_uuid=peca.dpp_uuid,
        dpp_version=peca.dpp_version or "1.0",
        gate_version=DPP_PUBLICATION_GATE_VERSION,
        resultado=resultado,
        evidence_statuses=json.dumps(validation.evidence_statuses, ensure_ascii=False, sort_keys=True),
        errors=json.dumps(validation.errors, ensure_ascii=False),
        warnings=json.dumps(validation.warnings, ensure_ascii=False),
        snapshot_json=snapshot_json,
        snapshot_sha256=(
            hashlib.sha256(snapshot_json.encode("utf-8")).hexdigest()
            if snapshot_json is not None
            else None
        ),
    )
    db.add(record)
    return record


def _safe_event_metadata(metadata: dict, schema_version: str) -> dict:
    """Aceita apenas contexto técnico curto; conteúdo livre do usuário é descartado."""
    if schema_version == "usage-event-v3":
        raise RuntimeError("Eventos v3 devem usar o registro por evento")
    v1_allowed = {
        "target_type", "field_type", "form_id", "status_code", "duration_ms",
        "viewport_width", "viewport_height", "visibility_state", "flow", "step",
    }
    v2_allowed = {
        "surface", "flow", "step", "outcome", "error_code", "status_code",
        "duration_ms", "validation_issue_count", "section", "method",
    }
    allowed = v1_allowed if schema_version == "usage-event-v1" else v2_allowed
    unknown = set(metadata) - allowed
    if schema_version == "usage-event-v2" and unknown:
        raise HTTPException(status_code=422, detail="Propriedade de evento não permitida")

    enums = {
        "surface": {"studio", "atelier", "public_passport", "label", "api"},
        "outcome": {"success", "failure", "blocked", "cancelled", "empty"},
        "method": {"GET", "POST", "PATCH", "PUT", "DELETE"},
        "section": {"identity", "composition", "impact", "circularity", "supply_chain", "evidence"},
        "flow": {
            "workspace", "piece_creation", "technical_sheet", "material_sheet",
            "production_stage", "publication_readiness", "dpp_publication",
            "qr_preview", "qr_access", "label", "public_passport",
            "api_request", "interface",
        },
        "step": {
            "entry", "view", "request", "validation", "complete", "recover",
            "open", "close", "load", "print", "network", "runtime", "exit",
        },
        "error_code": {
            "validation_failed", "invalid_request", "access_denied", "not_found",
            "conflict", "unprocessable", "rate_limited", "server_error",
            "request_failed", "network_error", "image_load_failed", "runtime_error",
            "clipboard_error",
        },
    }
    safe = {}
    for key, value in metadata.items():
        if key not in allowed or not isinstance(value, (str, int, float, bool)):
            continue
        if key in enums and value not in enums[key]:
            raise HTTPException(status_code=422, detail=f"Valor inválido para {key}")
        if key in {"status_code", "duration_ms", "validation_issue_count"} and (
            isinstance(value, bool) or value < 0
        ):
            raise HTTPException(status_code=422, detail=f"Valor inválido para {key}")
        safe[key] = value[:80] if isinstance(value, str) else value
    return safe


def _safe_event_page(page: str, schema_version: str) -> str:
    if schema_version == "usage-event-v1":
        return page
    if page in {
        "/", "/atelier", "/pessoas", "/workspace", "/workspace/settings",
        "/workspace/members", "/invitation",
    }:
        return page
    if re.fullmatch(r"/p/[^/]+", page):
        return "/p/:id"
    if re.fullmatch(r"/pecas/[^/]+/etiqueta", page):
        return "/pecas/:id/etiqueta"
    raise HTTPException(status_code=422, detail="Página de evento não permitida")


def _safe_event_token(value: str | None, field_name: str, schema_version: str) -> str | None:
    if value is None or schema_version == "usage-event-v1":
        return value
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,79}", value):
        raise HTTPException(status_code=422, detail=f"{field_name} de evento inválido")
    return value


# ---------- Coleções ----------

@router.get("/colecoes", response_model=List[ColecaoOut], tags=["Coleções"])
def listar_colecoes(db: Session = Depends(get_db)):
    return db.query(Colecao).all()


@router.post("/colecoes", response_model=ColecaoOut, status_code=201, tags=["Coleções"])
def criar_colecao(data: ColecaoCreate, db: Session = Depends(get_db)):
    colecao = Colecao(**data.model_dump())
    db.add(colecao)
    db.commit()
    db.refresh(colecao)
    return colecao


@router.get("/colecoes/{colecao_id}", response_model=ColecaoOut, tags=["Coleções"])
def obter_colecao(colecao_id: int, db: Session = Depends(get_db)):
    colecao = db.query(Colecao).filter(Colecao.id == colecao_id).first()
    if not colecao:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    return colecao


# ---------- Peças ----------

@router.get("/pecas", response_model=List[PecaOut], tags=["Peças"])
def listar_pecas(db: Session = Depends(get_db)):
    return db.query(Peca).all()


@router.post("/pecas", response_model=PecaOut, status_code=201, tags=["Peças"])
def criar_peca(data: PecaCreate, db: Session = Depends(get_db)):
    if db.query(Peca).filter(Peca.codigo == data.codigo).first():
        raise HTTPException(status_code=400, detail="Código já existe")
    peca = Peca(**data.model_dump())
    if not peca.dpp_uuid:
        peca.dpp_uuid = str(uuid.uuid4())
    db.add(peca)
    db.commit()
    db.refresh(peca)
    return peca


@router.get("/pecas/{codigo}", response_model=PecaOut, tags=["Peças"])
def obter_peca(codigo: str, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    return peca


@router.patch("/pecas/{codigo}", response_model=PecaOut, tags=["Peças"])
def atualizar_peca(codigo: str, data: PecaUpdate, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(peca, field, value)
    db.commit()
    db.refresh(peca)
    return peca


# ---------- Fichas Técnicas ----------

@router.get("/fichas-tecnicas", response_model=List[FichaTecnicaOut], tags=["Fichas Técnicas"])
def listar_fichas(db: Session = Depends(get_db)):
    return db.query(FichaTecnica).all()


@router.post("/fichas-tecnicas", response_model=FichaTecnicaOut, status_code=201, tags=["Fichas Técnicas"])
def criar_ficha(data: FichaTecnicaCreate, db: Session = Depends(get_db)):
    if db.query(FichaTecnica).filter(FichaTecnica.peca_id == data.peca_id).first():
        raise HTTPException(status_code=400, detail="Ficha técnica já existe para esta peça")
    ficha = FichaTecnica(**data.model_dump())
    db.add(ficha)
    db.commit()
    db.refresh(ficha)
    return ficha


@router.get("/fichas-tecnicas/{peca_id}", response_model=FichaTecnicaOut, tags=["Fichas Técnicas"])
def obter_ficha(peca_id: int, db: Session = Depends(get_db)):
    ficha = db.query(FichaTecnica).filter(FichaTecnica.peca_id == peca_id).first()
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha técnica não encontrada")
    return ficha


@router.patch("/fichas-tecnicas/{peca_id}", response_model=FichaTecnicaOut, tags=["Fichas Técnicas"])
def atualizar_ficha(peca_id: int, data: FichaTecnicaBase, db: Session = Depends(get_db)):
    ficha = db.query(FichaTecnica).filter(FichaTecnica.peca_id == peca_id).first()
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha técnica não encontrada")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(ficha, field, value)
    db.commit()
    db.refresh(ficha)
    return ficha


# ---------- Referências Visuais ----------

@router.get("/referencias-visuais", response_model=List[VisualReferenceOut], tags=["Referências Visuais"])
def listar_referencias_visuais(
    contexto: str | None = None,
    categoria: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(VisualReference)
    if contexto:
        query = query.filter(VisualReference.contexto_uso.contains(contexto))
    if categoria:
        query = query.filter(VisualReference.categoria == categoria)
    if status:
        query = query.filter(VisualReference.status == status)
    return query.order_by(VisualReference.prioridade.desc(), VisualReference.titulo.asc()).all()


@router.post("/referencias-visuais", response_model=VisualReferenceOut, status_code=201, tags=["Referências Visuais"])
def criar_referencia_visual(data: VisualReferenceCreate, db: Session = Depends(get_db)):
    if db.query(VisualReference).filter(VisualReference.slug == data.slug).first():
        raise HTTPException(status_code=400, detail="Referência visual já existe")
    referencia = VisualReference(**data.model_dump())
    db.add(referencia)
    db.commit()
    db.refresh(referencia)
    return referencia


@router.get("/referencias-visuais/{slug}", response_model=VisualReferenceOut, tags=["Referências Visuais"])
def obter_referencia_visual(slug: str, db: Session = Depends(get_db)):
    referencia = db.query(VisualReference).filter(VisualReference.slug == slug).first()
    if not referencia:
        raise HTTPException(status_code=404, detail="Referência visual não encontrada")
    return referencia


@router.post("/pecas/{codigo}/referencias-visuais", response_model=PecaVisualReferenceOut, status_code=201, tags=["Referências Visuais"])
def vincular_referencia_visual(
    codigo: str,
    data: PecaVisualReferenceCreate,
    db: Session = Depends(get_db),
):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    if not db.query(VisualReference).filter(VisualReference.id == data.visual_reference_id).first():
        raise HTTPException(status_code=404, detail="Referência visual não encontrada")
    vinculo = PecaVisualReference(peca_id=peca.id, **data.model_dump())
    db.add(vinculo)
    db.commit()
    db.refresh(vinculo)
    return vinculo


@router.get("/pecas/{codigo}/referencias-visuais", response_model=List[VisualReferenceOut], tags=["Referências Visuais"])
def listar_referencias_da_peca(codigo: str, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    return (
        db.query(VisualReference)
        .join(PecaVisualReference)
        .filter(PecaVisualReference.peca_id == peca.id)
        .order_by(VisualReference.prioridade.desc(), VisualReference.titulo.asc())
        .all()
    )


# ---------- Etapas de Produção ----------

@router.post("/pecas/{codigo}/etapas-producao", response_model=EtapaProducaoOut, status_code=201, tags=["DPP"])
def adicionar_etapa(codigo: str, data: EtapaProducaoCreate, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    etapa = EtapaProducao(peca_id=peca.id, **data.model_dump(exclude={"peca_id"}))
    db.add(etapa)
    db.commit()
    db.refresh(etapa)
    return etapa


@router.get("/pecas/{codigo}/etapas-producao", response_model=List[EtapaProducaoOut], tags=["DPP"])
def listar_etapas(codigo: str, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    return db.query(EtapaProducao).filter(EtapaProducao.peca_id == peca.id).all()


# ---------- Materiais vinculados (catálogo → peça) ----------

@router.post("/pecas/{codigo}/materiais", response_model=PecaMaterialOut, status_code=201, tags=["Materiais"])
def vincular_material(codigo: str, data: PecaMaterialCreate, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")

    produto = db.query(ProdutoFornecedor).filter(ProdutoFornecedor.id == data.produto_fornecedor_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto do fornecedor não encontrado")

    # Impede duplicata da mesma função
    existe = db.query(PecaMaterial).filter(
        PecaMaterial.peca_id == peca.id,
        PecaMaterial.produto_fornecedor_id == produto.id,
        PecaMaterial.funcao == (data.funcao or "principal"),
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este material já está vinculado à peça com essa função")

    # Auto-calcula peso_kg se não informado mas quantidade_m + gramatura + largura disponíveis
    peso_kg = data.peso_kg
    if peso_kg is None and data.quantidade_m and produto.gramatura_gm2 and produto.largura_m:
        peso_kg = round(data.quantidade_m * produto.largura_m * produto.gramatura_gm2 / 1000, 4)

    vinculo = PecaMaterial(
        peca_id=peca.id,
        produto_fornecedor_id=produto.id,
        funcao=data.funcao or "principal",
        quantidade_m=data.quantidade_m,
        peso_kg=peso_kg,
        observacoes=data.observacoes,
    )
    db.add(vinculo)
    db.flush()

    # Auto-popula FichaTecnica com dados do produto
    _consolidar_ficha(peca, db)

    # Cria EtapaProducao se ainda não existe para esse fornecedor/etapa
    etapa_tipo = _etapa_para_tipo(produto.tipo)
    if etapa_tipo:
        ja_existe = db.query(EtapaProducao).filter(
            EtapaProducao.peca_id == peca.id,
            EtapaProducao.etapa == etapa_tipo,
            EtapaProducao.instalacao_nome == produto.fornecedor.nome,
        ).first()
        if not ja_existe:
            db.add(EtapaProducao(
                peca_id=peca.id,
                etapa=etapa_tipo,
                pais="Brasil",
                instalacao_nome=produto.fornecedor.nome,
            ))

    db.commit()
    db.refresh(vinculo)

    return {
        "id": vinculo.id,
        "peca_id": vinculo.peca_id,
        "produto_fornecedor_id": vinculo.produto_fornecedor_id,
        "funcao": vinculo.funcao,
        "quantidade_m": vinculo.quantidade_m,
        "peso_kg": vinculo.peso_kg,
        "observacoes": vinculo.observacoes,
        "criado_em": vinculo.criado_em,
        "produto": _produto_para_materia_prima(produto),
    }


@router.get("/pecas/{codigo}/materiais", response_model=List[PecaMaterialOut], tags=["Materiais"])
def listar_materiais_peca(codigo: str, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")

    vinculos = db.query(PecaMaterial).filter(PecaMaterial.peca_id == peca.id).all()
    return [
        {
            "id": v.id,
            "peca_id": v.peca_id,
            "produto_fornecedor_id": v.produto_fornecedor_id,
            "funcao": v.funcao,
            "quantidade_m": v.quantidade_m,
            "peso_kg": v.peso_kg,
            "observacoes": v.observacoes,
            "criado_em": v.criado_em,
            "produto": _produto_para_materia_prima(v.produto),
        }
        for v in vinculos
    ]


@router.delete("/pecas/{codigo}/materiais/{material_id}", status_code=204, tags=["Materiais"])
def remover_material_peca(codigo: str, material_id: int, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")

    vinculo = db.query(PecaMaterial).filter(
        PecaMaterial.id == material_id,
        PecaMaterial.peca_id == peca.id,
    ).first()
    if not vinculo:
        raise HTTPException(status_code=404, detail="Vínculo de material não encontrado")

    db.delete(vinculo)
    db.flush()
    _consolidar_ficha(peca, db)
    db.commit()


# ---------- helpers de integração ----------

def _etapa_para_tipo(tipo: str | None) -> str | None:
    return {
        "pluma": "fiacao",
        "fio": "fiacao",
        "malha": "tecelagem",
        "tecido_plano": "tecelagem",
        "lona": "tecelagem",
    }.get(tipo or "")


def _parse_composicao(composicao: str) -> list:
    """Converte string de composição em lista de fibras para FichaTecnica."""
    if not composicao:
        return []
    # "100% Algodão Orgânico" / "95% CO, 5% Elastano"
    matches = re.findall(r"(\d+)%\s*([^,%\n]+)", composicao)
    if matches:
        return [{"fibra": m[1].strip().lower(), "pct": int(m[0])} for m in matches]
    # "Algodão/Cânhamo" ou "Cânhamo/Algodão"
    partes = [p.strip() for p in re.split(r"[/,]", composicao) if p.strip()]
    if len(partes) > 1:
        return [{"fibra": p.lower(), "pct": None} for p in partes]
    return [{"fibra": composicao.strip().lower(), "pct": 100}]


def _consolidar_ficha(peca: Peca, db: Session):
    """Recalcula FichaTecnica a partir de todos os materiais vinculados à peça."""
    vinculos = db.query(PecaMaterial).filter(PecaMaterial.peca_id == peca.id).all()

    if not vinculos:
        # Sem materiais — limpa campos derivados
        ficha = db.query(FichaTecnica).filter(FichaTecnica.peca_id == peca.id).first()
        if ficha:
            ficha.materiais = None
            ficha.composicao_fibras = None
            ficha.certificacoes = None
        return

    # Monta descrição de materiais
    descricoes = []
    for v in vinculos:
        p = v.produto
        cidade = p.fornecedor.cidade or p.fornecedor.estado or ""
        descricoes.append(
            f"{p.nome} [{v.funcao}] — {p.fornecedor.nome} ({cidade})"
        )

    # Monta composição de fibras (só do material principal)
    fibras = []
    principal = next((v for v in vinculos if v.funcao == "principal"), vinculos[0])
    if principal.produto.composicao:
        fibras = _parse_composicao(principal.produto.composicao)

    # Coleta certificações únicas de todos os fornecedores vinculados
    certs_vistas = set()
    certs = []
    for v in vinculos:
        for c in v.produto.fornecedor.certificacoes:
            chave = (c.tipo, c.numero_licenca or "")
            if chave not in certs_vistas:
                certs_vistas.add(chave)
                certs.append({
                    "nome": c.tipo,
                    "numero": c.numero_licenca or "",
                    "validade": c.validade or "",
                    "escopo": c.escopo or "",
                    "nivel_confianca": c.nivel_confianca or "",
                    "fornecedor": v.produto.fornecedor.nome,
                })

    ficha = db.query(FichaTecnica).filter(FichaTecnica.peca_id == peca.id).first()
    campos = {
        "peca_id": peca.id,
        "materiais": "\n".join(descricoes),
        "composicao_fibras": json.dumps(fibras, ensure_ascii=False) if fibras else None,
        "certificacoes": json.dumps(certs, ensure_ascii=False) if certs else None,
    }

    if ficha:
        for k, v in campos.items():
            if k != "peca_id":
                setattr(ficha, k, v)
    else:
        db.add(FichaTecnica(**campos))


# ---------- Digital Product Passport ----------

@router.post("/pecas/{codigo}/dpp/publicar", response_model=PecaOut, tags=["DPP"])
def publicar_dpp(codigo: str, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    ficha = peca.ficha_tecnica
    if not ficha:
        raise HTTPException(status_code=422, detail={"errors": ["Ficha tecnica obrigatoria para publicar DPP"]})

    validation_ficha = SimpleNamespace(**{
        column.name: getattr(ficha, column.name)
        for column in FichaTecnica.__table__.columns
    })
    validation_peca = SimpleNamespace(**{
        column.name: getattr(peca, column.name)
        for column in Peca.__table__.columns
    })
    validation_peca.tem_pais_fabricacao = db.query(EtapaProducao).filter(
        EtapaProducao.peca_id == peca.id,
        EtapaProducao.pais.isnot(None),
    ).first() is not None

    calculated_fields = {}
    tier2_inputs = (
        peca.area_peca_m2,
        peca.perda_corte_pct,
        ficha.gramatura_g_m2,
        ficha.agua_litros_kg,
        ficha.energia_kwh_kg,
        ficha.carbono_kgco2e_kg,
    )
    if all(value is not None for value in tier2_inputs):
        try:
            result = calculate_dpp_indicators(DppCalculationInput(
                area_peca_m2=peca.area_peca_m2,
                perda_corte_pct=peca.perda_corte_pct,
                gramatura_g_m2=ficha.gramatura_g_m2,
                agua_litros_kg=ficha.agua_litros_kg,
                energia_kwh_kg=ficha.energia_kwh_kg,
                carbono_kgco2e_kg=ficha.carbono_kgco2e_kg,
            ))
        except DppCalculationError as exc:
            raise HTTPException(status_code=422, detail={"errors": [str(exc)]}) from exc

        calculated_fields = {
            "area_total_requerida_m2": result.area_total_requerida_m2,
            "area_perdida_m2": result.area_perdida_m2,
            "peso_peca_kg": result.peso_peca_kg,
            "agua_peca_litros": result.agua_peca_litros,
            "energia_peca_kwh": result.energia_peca_kwh,
            "pegada_carbono_kgco2e": result.carbono_peca_kgco2e,
        }

    for field, value in calculated_fields.items():
        setattr(validation_ficha, field, value)

    validation = validate_dpp_publication(validation_peca, validation_ficha)
    if not validation.can_publish:
        _record_publication_attempt(db, peca, validation, "bloqueado")
        db.commit()
        raise HTTPException(
            status_code=422,
            detail={
                "errors": validation.errors,
                "warnings": validation.warnings,
                "evidence_statuses": validation.evidence_statuses,
            },
        )

    for field, value in calculated_fields.items():
        setattr(ficha, field, value)

    now = datetime.now(timezone.utc)
    if not peca.dpp_uuid:
        peca.dpp_uuid = str(uuid.uuid4())
    peca.dpp_status = "publicado"
    peca.dpp_version = peca.dpp_version or "1.0"
    peca.data_publicacao = peca.data_publicacao or now
    peca.data_atualizacao = now
    ficha.evidencia_statuses = json.dumps(validation.evidence_statuses, ensure_ascii=False)
    snapshot_json = _publication_snapshot(peca, ficha, validation.evidence_statuses)
    _record_publication_attempt(db, peca, validation, "aprovado", snapshot_json)

    db.commit()
    db.refresh(peca)
    return peca


@router.get("/pecas/{codigo}/dpp/publicacoes", tags=["DPP"])
def listar_publicacoes_dpp(codigo: str, db: Session = Depends(get_db)):
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    records = (
        db.query(DppPublicationRecord)
        .filter(DppPublicationRecord.peca_id == peca.id)
        .order_by(DppPublicationRecord.id.asc())
        .all()
    )
    return [
        {
            "id": record.id,
            "dpp_uuid": record.dpp_uuid,
            "dpp_version": record.dpp_version,
            "gate_version": record.gate_version,
            "resultado": record.resultado,
            "evidence_statuses": json.loads(record.evidence_statuses),
            "errors": json.loads(record.errors),
            "warnings": json.loads(record.warnings),
            "snapshot": json.loads(record.snapshot_json) if record.snapshot_json else None,
            "snapshot_sha256": record.snapshot_sha256,
            "criado_em": record.criado_em,
        }
        for record in records
    ]


@router.post("/events/usage", status_code=202, tags=["Telemetria"])
def registrar_evento_uso(data: UsageEventCreate, db: Session = Depends(get_db)):
    allowed_names = USAGE_EVENT_NAMES_BY_SCHEMA.get(data.schema_version)
    if allowed_names is None:
        raise HTTPException(status_code=422, detail="Versão do schema de evento não suportada")
    if data.event_name not in allowed_names:
        raise HTTPException(status_code=422, detail="Nome de evento não permitido")
    if not (1 <= len(data.event_id) <= 64 and 1 <= len(data.session_id) <= 64):
        raise HTTPException(status_code=422, detail="Identificador de evento ou sessão inválido")
    if not data.page.startswith("/") or len(data.page) > 200:
        raise HTTPException(status_code=422, detail="Página inválida")
    if data.schema_version == "usage-event-v3":
        if data.source not in {"web", "backend", "worker"}:
            raise HTTPException(status_code=422, detail="Fonte de evento inválida")
        if data.environment not in {"development", "test", "staging", "production"}:
            raise HTTPException(status_code=422, detail="Ambiente de evento inválido")
        for field_name, value in {
            "anonymous_id": data.anonymous_id,
            "user_id_hash": data.user_id_hash,
            "workspace_id_hash": data.workspace_id_hash,
            "request_id": data.request_id,
        }.items():
            if value is not None and not re.fullmatch(r"[A-Za-z0-9_-]{8,128}", value):
                raise HTTPException(status_code=422, detail=f"{field_name} inválido")

    existing = db.query(UsageEvent).filter(UsageEvent.event_id == data.event_id).first()
    if existing:
        return {"accepted": True, "duplicate": True}

    safe_metadata = (
        validate_v3_properties(data.event_name, data.metadata)
        if data.schema_version == "usage-event-v3"
        else _safe_event_metadata(data.metadata, data.schema_version)
    )
    db.add(UsageEvent(
        event_id=data.event_id,
        schema_version=data.schema_version,
        session_id=data.session_id,
        event_name=data.event_name,
        page=_safe_event_page(data.page, data.schema_version),
        component=_safe_event_token(data.component, "Componente", data.schema_version),
        action=_safe_event_token(data.action, "Ação", data.schema_version),
        metadata_json=json.dumps(safe_metadata, ensure_ascii=False, sort_keys=True),
        occurred_at=data.occurred_at,
        event_version=data.event_version,
        anonymous_id=data.anonymous_id,
        user_id_hash=data.user_id_hash,
        workspace_id_hash=data.workspace_id_hash,
        source=data.source,
        environment=data.environment,
        application_version=data.application_version,
        request_id=data.request_id,
    ))
    db.commit()
    return {"accepted": True, "duplicate": False}


@router.get("/dpp/{identifier}", tags=["DPP"])
def obter_dpp(identifier: str, db: Session = Depends(get_db)):
    peca = _find_peca_by_public_identifier(db, identifier)
    if not peca or peca.dpp_status != "publicado":
        raise HTTPException(status_code=404, detail="DPP não encontrado ou não publicado")
    ficha = peca.ficha_tecnica
    etapas = db.query(EtapaProducao).filter(EtapaProducao.peca_id == peca.id).all()
    return {
        "@context": ["https://schema.org/", "https://gs1.org/voc/"],
        "@type": "Product",
        "gtin": peca.gtin,
        "identifier": peca.dpp_uuid,
        "name": peca.nome,
        "description": ficha.descricao_tecnica if ficha else None,
        "material": json.loads(ficha.composicao_fibras) if ficha and ficha.composicao_fibras else [],
        "recycledContent": ficha.conteudo_reciclado_pct if ficha else None,
        "weight": {"value": ficha.peso_peca_kg, "unitCode": "KGM"} if ficha and ficha.peso_peca_kg is not None else None,
        "carbonFootprint": {"value": ficha.pegada_carbono_kgco2e, "unitCode": "KGM"} if ficha and ficha.pegada_carbono_kgco2e is not None else None,
        "waterFootprint": {"value": ficha.agua_peca_litros, "unitCode": "LTR"} if ficha and ficha.agua_peca_litros is not None else None,
        "energyUse": {"value": ficha.energia_peca_kwh, "unitCode": "KWH"} if ficha and ficha.energia_peca_kwh is not None else None,
        "impactFactorSources": {
            "water": ficha.fonte_agua_litros_kg,
            "energy": ficha.fonte_energia_kwh_kg,
            "carbon": ficha.fonte_carbono_kgco2e_kg,
            "methodology": ficha.metodologia_fatores_impacto,
            "limitation": (
                "Fatores estimados com base genérica (Ecoinvent/IPCC). "
                "Valores reais dependem de dados primários do fornecedor e ACV oficial."
                if ficha.metodologia_fatores_impacto and "estimativa genérica" in ficha.metodologia_fatores_impacto
                else "Indicadores estimados não substituem ACV oficial ou auditoria ambiental."
            ),
        } if ficha else {},
        "cutWaste": {
            "areaLostM2": ficha.area_perdida_m2,
            "lossPercent": peca.perda_corte_pct,
        } if ficha and ficha.area_perdida_m2 is not None else None,
        "certifications": json.loads(ficha.certificacoes) if ficha and ficha.certificacoes else [],
        "evidence": json.loads(ficha.evidencia_statuses) if ficha and ficha.evidencia_statuses else {},
        "repairInstructions": ficha.instrucoes_reparo if ficha else None,
        "endOfLifeInstructions": ficha.instrucoes_fim_de_vida if ficha else None,
        "durability": {"washCycles": ficha.durabilidade_ciclos_lavagem} if ficha and ficha.durabilidade_ciclos_lavagem else None,
        "productionChain": [
            {"stage": e.etapa, "country": e.pais, "facility": e.instalacao_nome, "gln": e.instalacao_gln}
            for e in etapas
        ],
    }


@router.get("/dpp/{identifier}/qr", tags=["DPP"])
def obter_qr_dpp(identifier: str, db: Session = Depends(get_db)):
    try:
        import qrcode
    except ImportError:
        raise HTTPException(status_code=501, detail="qrcode não instalado")
    peca = _find_peca_by_public_identifier(db, identifier)
    if not peca or peca.dpp_status != "publicado":
        raise HTTPException(status_code=404, detail="DPP não encontrado ou não publicado")
    url = public_dpp_url(peca.dpp_uuid)
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


def _gerar_qr_base64(url: str) -> str:
    """Gera QR code como PNG base64 inline."""
    try:
        import qrcode
        import base64
        img = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2,
        )
        img.add_data(url)
        img.make(fit=True)
        pil = img.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        pil.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        return ""


@router.get("/pecas/{codigo}/qr", tags=["DPP"])
def qr_peca(codigo: str, db: Session = Depends(get_db)):
    """QR code PNG para qualquer peça com dpp_uuid, independente de estar publicada."""
    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")
    if not peca.dpp_uuid:
        raise HTTPException(status_code=400, detail="Peça sem UUID — recrie a peça para gerar o QR")
    url = public_dpp_url(peca.dpp_uuid)
    b64 = _gerar_qr_base64(url)
    if not b64:
        raise HTTPException(status_code=501, detail="qrcode não instalado")
    import base64
    png = base64.b64decode(b64.split(",")[1])
    return StreamingResponse(io.BytesIO(png), media_type="image/png")


# ---------- ISCM — Índice de Sustentabilidade da Cadeia de Moda ----------

@router.get("/pecas/{codigo}/iscm", response_model=ISCMOut, tags=["ISCM"])
def calcular_iscm_peca(codigo: str, db: Session = Depends(get_db)):
    """
    Calcula o ISCM (Índice de Sustentabilidade da Cadeia de Moda) para a peça.

    Score 0–100 por 7 dimensões ponderadas:
      carbono (25%), água (15%), químicos (15%), materiais (15%),
      resíduos/circularidade (10%), social (10%), rastreabilidade (10%)

    Níveis: insuficiente <35 | basico 35–55 | intermediario 55–70 |
            avancado 70–85 | referencia ≥85

    Metodologias de referência: ISO 14067, GHG Protocol Scope 3,
    Higg FEM, ZDHC MRSL, GOTS, Textile Exchange, ABVTEX, PEF/PEFCR.
    """
    from app.services.iscm import calcular_iscm

    peca = db.query(Peca).filter(Peca.codigo == codigo).first()
    if not peca:
        raise HTTPException(status_code=404, detail="Peça não encontrada")

    result = calcular_iscm(peca, db)
    return {
        "peca_codigo": result.peca_codigo,
        "score_total": result.score_total,
        "nivel": result.nivel,
        "dimensoes": {
            k: {
                "pontos": v.pontos,
                "peso": v.peso,
                "fonte": v.fonte,
                "metodologia": v.metodologia,
                "referencias": v.referencias,
                "indicador_auditavel": v.indicador_auditavel,
            }
            for k, v in result.dimensoes.items()
        },
        "cobertura_dados_pct": result.cobertura_dados_pct,
        "alertas": result.alertas,
    }


# ---------- Health ----------

@router.get("/api/status", tags=["Status"])
def root():
    commit_sha = os.getenv("RAILWAY_GIT_COMMIT_SHA") or os.getenv("GIT_COMMIT_SHA")
    return {
        "status": "ok",
        "sistema": "PHYLLOS DPP",
        "commit": commit_sha,
    }
