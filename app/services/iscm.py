"""
ISCM — experimental_legacy; compatibilidade apenas, não é score oficial.

Três camadas:
  Camada 1: score interno 0–100 por dimensão (gestão/comparação)
  Camada 2: indicadores auditáveis (kg CO₂e, L/kg água, % cert, etc.)
  Camada 3: referências a padrões externos (GHG Protocol, ISO 14067, Higg,
             ZDHC, GOTS, Textile Exchange, ABVTEX, PEF/PEFCR)

Ponderação mássica:
  Cada material contribui proporcionalmente ao seu peso_kg na peça.
  Se peso_kg não estiver preenchido, cai para pesos iguais entre materiais
  e registra alerta. Com quantidade_m + gramatura + largura, peso_kg é
  calculado automaticamente ao vincular o material.

Fonte por dimensão:
  "primario"  — dado real registrado no banco
  "estimado"  — proxy a partir de campos relacionados
  "ausente"   — sem informação suficiente; pontuação mínima conservadora
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import EtapaProducao, FichaTecnica, Peca, PecaMaterial


# ── Tabelas de referência ────────────────────────────────────────────────────

_CERT_MATERIAL = {
    "GOTS": 100, "OCS": 85, "IBD": 85, "ECOCERT": 82, "SisOrg": 75,
    "Participativa": 70, "USDA_Organic": 80, "EU_Organic": 85,
    "GRS": 82, "RCS": 76, "Cradle_to_Cradle": 95, "BLUESIGN": 88,
}

_CERT_QUIMICO = {"OEKO-TEX": 85, "ZDHC": 92, "BLUESIGN": 88}

_CERT_SOCIAL = {"SA8000": 100, "ABVTEX": 90, "WRAP": 80, "BSCI": 70}

_TINGIMENTO_SCORE = {
    "sem_tingimento": 100,
    "vegetal": 82,
    "natural": 70,
    "convencional": 28,
}

_FIBRA_CARBON: list[tuple[list[str], int]] = [
    (["cânhamo", "canhamo", "hemp", "linho", "linen"], 90),
    (["reciclado", "reciclada", "recycled"],            84),
    (["orgânico", "organico", "organic"],               80),
    (["tencel", "lyocell"],                             74),
    (["modal"],                                         68),
    (["algodão", "algodao", "cotton"],                  52),
    (["viscose", "rayon"],                              46),
    (["poliéster", "poliester", "polyester"],           36),
    (["nylon", "poliamida", "polyamide"],               30),
    (["elastano", "spandex", "lycra"],                  25),
]

_AGUA_LIMIARES = [(100, 100), (300, 82), (500, 60), (800, 40), (float("inf"), 20)]

_ETAPAS = {"fiacao", "tecelagem", "tingimento", "corte", "costura", "acabamento", "lavanderia"}


# ── Tipos de resultado ───────────────────────────────────────────────────────

@dataclass
class DimensaoISCM:
    pontos: float
    peso: float
    fonte: str              # primario | estimado | ausente
    metodologia: str
    referencias: list[str] = field(default_factory=list)
    indicador_auditavel: Optional[str] = None


@dataclass
class ISCMResult:
    peca_codigo: str
    score_total: float
    nivel: str
    dimensoes: dict[str, DimensaoISCM]
    cobertura_dados_pct: float
    alertas: list[str]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _nivel(score: float) -> str:
    if score >= 85: return "referencia"
    if score >= 70: return "avancado"
    if score >= 55: return "intermediario"
    if score >= 35: return "basico"
    return "insuficiente"


def _fibra_carbon_score(fibra: str) -> int:
    fl = fibra.lower()
    for keywords, score in _FIBRA_CARBON:
        if any(k in fl for k in keywords):
            return score
    return 40


def _agua_score(litros_kg: float) -> float:
    for limiar, pts in _AGUA_LIMIARES:
        if litros_kg <= limiar:
            return float(pts)
    return 20.0


def _clamp(v: float) -> float:
    return round(max(0.0, min(100.0, v)), 1)


def _cert_score(certs, lookup: dict) -> Optional[float]:
    scores = [lookup[c.tipo] for c in certs if c.tipo in lookup]
    return float(max(scores)) if scores else None


def _fibra_score_from_json(composicao_fibras_json: str) -> float:
    """Score de carbono ponderado pelas frações de fibras."""
    try:
        fibras = json.loads(composicao_fibras_json)
    except (json.JSONDecodeError, TypeError):
        return 40.0
    if not fibras:
        return 40.0
    total = sum(f.get("pct") or 50 for f in fibras)
    weighted = sum(_fibra_carbon_score(f.get("fibra", "")) * (f.get("pct") or 50) for f in fibras)
    return weighted / total if total else 40.0


# ── Ponderação mássica ───────────────────────────────────────────────────────

def _fracoes(materiais: list[PecaMaterial]) -> tuple[dict[int, float], bool]:
    """
    Retorna (dict id→fração, usa_peso).
    Se todos os materiais têm peso_kg, usa ponderação mássica real.
    Caso contrário, distribui igual entre materiais.
    """
    pesos = {m.id: m.peso_kg for m in materiais if m.peso_kg and m.peso_kg > 0}
    if len(pesos) == len(materiais) and materiais:
        total = sum(pesos.values())
        return ({m.id: pesos[m.id] / total for m in materiais}, True)
    # fallback: peso igual
    n = len(materiais)
    return ({m.id: 1.0 / n for m in materiais} if n else {}, False)


# ── Calculadora principal ────────────────────────────────────────────────────

def calcular_iscm(peca: Peca, db: Session) -> ISCMResult:
    ficha: Optional[FichaTecnica] = peca.ficha_tecnica
    materiais: list[PecaMaterial] = peca.materiais or []
    etapas = db.query(EtapaProducao).filter(EtapaProducao.peca_id == peca.id).all()
    alertas: list[str] = []

    fracoes, usa_peso = _fracoes(materiais)
    if materiais and not usa_peso:
        alertas.append(
            "Ponderação mássica indisponível: preencha peso_kg (ou quantidade_m + "
            "gramatura + largura) nos materiais vinculados para scores mais precisos."
        )

    total_peso_peca = sum(m.peso_kg for m in materiais if m.peso_kg) if usa_peso else None

    # Agrega certificações de todos os fornecedores ponderadas
    certs_material_por_m: dict[int, list] = {}  # material_id → certs de ambiente
    certs_quimico_por_m: dict[int, list] = {}
    certs_social_por_m: dict[int, list] = {}
    tingimentos_por_m: dict[int, str] = {}
    agua_por_m: dict[int, float] = {}
    composicao_por_m: dict[int, str] = {}  # material_id → composicao texto
    fornecedores_por_m: dict[int, object] = {}

    for m in materiais:
        prod = m.produto
        forn = prod.fornecedor
        fornecedores_por_m[m.id] = forn
        if prod.tingimento:
            tingimentos_por_m[m.id] = prod.tingimento
        if getattr(prod, "consumo_agua_litros_kg", None) is not None:
            agua_por_m[m.id] = prod.consumo_agua_litros_kg
        if prod.composicao:
            composicao_por_m[m.id] = prod.composicao

        certs_material_por_m[m.id] = [c for c in forn.certificacoes if c.tipo in _CERT_MATERIAL]
        certs_quimico_por_m[m.id]  = [c for c in forn.certificacoes if c.tipo in _CERT_QUIMICO]
        certs_social_por_m[m.id]   = [c for c in forn.certificacoes if c.tipo in _CERT_SOCIAL]

    # ── D1: Carbono (25%) ────────────────────────────────────────────────────
    if ficha and ficha.pegada_carbono_kgco2e is not None:
        co2 = ficha.pegada_carbono_kgco2e
        if co2 <= 2:     c_pts = 100.0
        elif co2 <= 5:   c_pts = 100 - (co2 - 2) * 8.33
        elif co2 <= 10:  c_pts = 75  - (co2 - 5) * 4.0
        elif co2 <= 20:  c_pts = 55  - (co2 - 10) * 2.0
        else:            c_pts = 20.0
        c_fonte = "primario"
        c_metodo = "Pegada de carbono medida — ISO 14067 / GHG Protocol Scope 3"
        c_refs   = ["ISO 14067", "GHG Protocol Scope 3 Cat.1"]
        c_ind    = f"{co2:.2f} kg CO₂e"
    elif materiais:
        # Score ponderado pelo peso de cada material
        scores_por_m: dict[int, float] = {}
        for m in materiais:
            mid = m.id
            # Usa composicao_fibras da ficha se for o material principal, senão composicao do produto
            if ficha and ficha.composicao_fibras and m.funcao == "principal":
                scores_por_m[mid] = _fibra_score_from_json(ficha.composicao_fibras)
            elif mid in composicao_por_m:
                scores_por_m[mid] = float(_fibra_carbon_score(composicao_por_m[mid]))
            else:
                scores_por_m[mid] = 38.0  # sintético genérico sem dados

        c_pts = sum(scores_por_m[m.id] * fracoes[m.id] for m in materiais)
        c_fonte = "estimado"
        c_metodo = (
            "Estimativa ponderada por composição de fibras"
            + (" (fração mássica)" if usa_peso else " (pesos iguais)")
            + " — benchmark GHG Protocol Scope 3"
        )
        c_refs = ["ISO 14067", "GHG Protocol Scope 3 Cat.1"]
        c_ind  = "estimado por fibra" + (f" | peça ~{total_peso_peca*1000:.0f}g" if total_peso_peca else "")
        alertas.append(
            "Carbono: estimado por fibra. "
            "Registre pegada_carbono_kgco2e na ficha técnica para nota primária."
        )
    else:
        c_pts = 0.0
        c_fonte = "ausente"
        c_metodo = "Sem materiais ou pegada de carbono"
        c_refs = ["ISO 14067"]
        c_ind  = None
        alertas.append("Carbono: vincule materiais ou registre pegada_carbono_kgco2e.")

    d_carbono = DimensaoISCM(
        pontos=_clamp(c_pts), peso=0.25, fonte=c_fonte,
        metodologia=c_metodo, referencias=c_refs, indicador_auditavel=c_ind,
    )

    # ── D2: Água (15%) ───────────────────────────────────────────────────────
    if agua_por_m:
        if usa_peso and total_peso_peca:
            # Litros totais consumidos na produção desta peça
            litros_total = sum(
                agua_por_m[m.id] * m.peso_kg
                for m in materiais
                if m.id in agua_por_m and m.peso_kg
            )
            litros_por_kg_peca = litros_total / total_peso_peca
            a_pts  = _agua_score(litros_por_kg_peca)
            a_fonte = "primario"
            a_metodo = "Consumo hídrico real ponderado por peso de cada material — Higg FEM"
            a_refs  = ["Higg FEM", "ZDHC"]
            a_ind   = f"{litros_total:.1f} L / peça  ({litros_por_kg_peca:.0f} L/kg médio)"
        else:
            # Média simples dos materiais com dado
            avg = sum(agua_por_m.values()) / len(agua_por_m)
            a_pts  = _agua_score(avg)
            a_fonte = "primario"
            a_metodo = "Consumo hídrico declarado — média simples (pesos iguais)"
            a_refs  = ["Higg FEM", "ZDHC"]
            a_ind   = f"{avg:.0f} L/kg médio (não ponderado)"
            alertas.append(
                "Água: preencha peso_kg nos materiais para calcular litros totais por peça."
            )
    elif tingimentos_por_m:
        # Proxy ponderado pelo tingimento de cada material
        score_pond = sum(
            _TINGIMENTO_SCORE.get(tingimentos_por_m[m.id], 28) * fracoes[m.id]
            for m in materiais if m.id in tingimentos_por_m
        )
        a_pts   = score_pond * 0.92
        a_fonte = "estimado"
        tings   = sorted(set(tingimentos_por_m.values()))
        a_metodo = (
            f"Proxy ponderado por tingimento ({', '.join(tings)})"
            + (" — fração mássica" if usa_peso else " — pesos iguais")
            + " — Higg FEM"
        )
        a_refs = ["Higg FEM", "ZDHC"]
        a_ind  = f"processos: {', '.join(tings)}"
        alertas.append(
            "Água: estimado via tingimento. "
            "Solicite consumo_agua_litros_kg ao fornecedor para dado primário."
        )
    else:
        a_pts   = 0.0
        a_fonte = "ausente"
        a_metodo = "Sem dados de tingimento ou consumo hídrico"
        a_refs  = ["Higg FEM"]
        a_ind   = None
        alertas.append("Água: preencha o campo tingimento dos produtos do fornecedor.")

    d_agua = DimensaoISCM(
        pontos=_clamp(a_pts), peso=0.15, fonte=a_fonte,
        metodologia=a_metodo, referencias=a_refs, indicador_auditavel=a_ind,
    )

    # ── D3: Químicos (15%) ───────────────────────────────────────────────────
    if any(certs_quimico_por_m.values()):
        # Score ponderado: materiais com cert recebem score da cert; sem cert recebem proxy tingimento
        q_pond = 0.0
        for m in materiais:
            sc = _cert_score(certs_quimico_por_m[m.id], _CERT_QUIMICO)
            if sc is None:
                ting = tingimentos_por_m.get(m.id, "convencional")
                sc = float(_TINGIMENTO_SCORE.get(ting, 28)) * 0.88
            q_pond += sc * fracoes[m.id]
        q_pts   = q_pond
        q_fonte = "primario"
        certs_nomes = sorted({c.tipo for cs in certs_quimico_por_m.values() for c in cs})
        q_metodo = f"Certificação química verificada: {', '.join(certs_nomes)} (ponderado por peso)"
        q_refs  = certs_nomes + ["ZDHC MRSL v3.1"]
        q_ind   = f"certs: {', '.join(certs_nomes)}"
    elif tingimentos_por_m:
        q_pond = sum(
            _TINGIMENTO_SCORE.get(tingimentos_por_m[m.id], 28) * 0.88 * fracoes[m.id]
            for m in materiais if m.id in tingimentos_por_m
        )
        q_pts   = q_pond
        q_fonte = "estimado"
        tings   = sorted(set(tingimentos_por_m.values()))
        q_metodo = (
            f"Proxy ponderado por tingimento ({', '.join(tings)}) — sem cert ZDHC/OEKO-TEX"
        )
        q_refs = ["ZDHC MRSL v3.1", "OEKO-TEX Standard 100"]
        q_ind  = f"processos: {', '.join(tings)}"
        alertas.append(
            "Químicos: sem certificação ZDHC ou OEKO-TEX. "
            "Solicite RSL/MRSL e certificação dos fornecedores."
        )
    else:
        q_pts   = 0.0
        q_fonte = "ausente"
        q_metodo = "Sem dados de processo químico ou certificação"
        q_refs  = ["ZDHC MRSL v3.1"]
        q_ind   = None
        alertas.append("Químicos: cadastre tingimento e certs ZDHC/OEKO-TEX dos fornecedores.")

    d_quimico = DimensaoISCM(
        pontos=_clamp(q_pts), peso=0.15, fonte=q_fonte,
        metodologia=q_metodo, referencias=q_refs, indicador_auditavel=q_ind,
    )

    # ── D4: Materiais (15%) ──────────────────────────────────────────────────
    if any(certs_material_por_m.values()):
        # Score ponderado: cada material contribui com seu melhor cert (ou heurística por fibra)
        m_pond = 0.0
        for m in materiais:
            sc = _cert_score(certs_material_por_m[m.id], _CERT_MATERIAL)
            if sc is None:
                comp = composicao_por_m.get(m.id, "").lower()
                if any(k in comp for k in ["orgânico", "organico", "organic"]):       sc = 62.0
                elif any(k in comp for k in ["reciclado", "reciclada", "recycled"]): sc = 65.0
                elif any(k in comp for k in ["cânhamo", "canhamo", "hemp", "tencel", "lyocell"]): sc = 60.0
                else: sc = 35.0
            m_pond += sc * fracoes[m.id]
        m_pts   = m_pond
        m_fonte = "primario"
        certs_nomes = sorted({c.tipo for cs in certs_material_por_m.values() for c in cs})
        m_metodo = f"Certificação de material verificada: {', '.join(certs_nomes)} (ponderado por peso)"
        m_refs  = certs_nomes + ["Textile Exchange"]
        m_ind   = f"certs: {', '.join(certs_nomes)}"
    elif ficha and ficha.conteudo_reciclado_pct and ficha.conteudo_reciclado_pct > 0:
        m_pts   = 55 + (ficha.conteudo_reciclado_pct / 100) * 25
        m_fonte = "estimado"
        m_metodo = f"Conteúdo reciclado declarado: {ficha.conteudo_reciclado_pct:.0f}% — GRS proxy"
        m_refs  = ["GRS — Global Recycled Standard", "Textile Exchange"]
        m_ind   = f"{ficha.conteudo_reciclado_pct:.0f}% reciclado"
        alertas.append("Materiais: conteúdo reciclado sem certificação GRS verificada.")
    elif materiais:
        m_pond = 0.0
        for m in materiais:
            comp = composicao_por_m.get(m.id, "").lower()
            if any(k in comp for k in ["orgânico", "organico", "organic"]):       sc = 62.0
            elif any(k in comp for k in ["reciclado", "reciclada", "recycled"]): sc = 65.0
            elif any(k in comp for k in ["cânhamo", "canhamo", "hemp", "tencel", "lyocell"]): sc = 60.0
            elif comp: sc = 35.0
            else: sc = 22.0
            m_pond += sc * fracoes[m.id]
        m_pts   = m_pond
        m_fonte = "estimado"
        m_metodo = (
            "Composição declarada sem certificação"
            + (" — ponderada por peso mássico" if usa_peso else " — pesos iguais")
        )
        m_refs  = ["GOTS", "Textile Exchange", "OCS"]
        m_ind   = "sem cert verificada"
        alertas.append(
            "Materiais: composição sem certificação. "
            "Solicite GOTS/OCS/GRS ao fornecedor para dado primário."
        )
    else:
        m_pts   = 0.0
        m_fonte = "ausente"
        m_metodo = "Sem materiais ou certificações vinculados"
        m_refs  = ["GOTS", "Textile Exchange"]
        m_ind   = None
        alertas.append("Materiais: vincule materiais ao catálogo de fornecedores.")

    d_materiais = DimensaoISCM(
        pontos=_clamp(m_pts), peso=0.15, fonte=m_fonte,
        metodologia=m_metodo, referencias=m_refs, indicador_auditavel=m_ind,
    )

    # ── D5: Resíduos / Circularidade (10%) ───────────────────────────────────
    r_parts: list[float] = []

    if ficha and ficha.conteudo_reciclado_pct is not None:
        r_parts.append(40 + (ficha.conteudo_reciclado_pct / 100) * 50)
    if ficha and ficha.instrucoes_fim_de_vida:
        r_parts.append(78.0)
    if ficha and ficha.instrucoes_reparo:
        r_parts.append(72.0)
    if ficha and ficha.durabilidade_ciclos_lavagem:
        r_parts.append(min(90, max(40, 40 + (ficha.durabilidade_ciclos_lavagem / 200) * 50)))

    if r_parts:
        r_pts   = sum(r_parts) / len(r_parts)
        r_fonte = "primario" if (ficha and ficha.conteudo_reciclado_pct is not None) else "estimado"
        r_metodo = "Conteúdo reciclado + circularidade (reparo, fim-de-vida, durabilidade)"
        r_refs  = ["ISO 14040/14044 LCA", "PEF/PEFCR Apparel & Footwear"]
        r_ind_p = []
        if ficha and ficha.conteudo_reciclado_pct is not None:
            r_ind_p.append(f"{ficha.conteudo_reciclado_pct:.0f}% reciclado")
        if ficha and ficha.durabilidade_ciclos_lavagem:
            r_ind_p.append(f"{ficha.durabilidade_ciclos_lavagem} ciclos lavagem")
        r_ind   = "; ".join(r_ind_p) or None
    else:
        r_pts   = 0.0
        r_fonte = "ausente"
        r_metodo = "Sem dados de circularidade ou durabilidade"
        r_refs  = ["ISO 14040/14044 LCA", "PEF/PEFCR Apparel & Footwear"]
        r_ind   = None
        alertas.append(
            "Resíduos: preencha conteudo_reciclado_pct, instrucoes_fim_de_vida "
            "e durabilidade_ciclos_lavagem na ficha técnica."
        )

    d_residuos = DimensaoISCM(
        pontos=_clamp(r_pts), peso=0.10, fonte=r_fonte,
        metodologia=r_metodo, referencias=r_refs, indicador_auditavel=r_ind,
    )

    # ── D6: Social / Trabalho (10%) ──────────────────────────────────────────
    certs_social_todos = [c for cs in certs_social_por_m.values() for c in cs]
    if certs_social_todos:
        # Ponderado: fornecedores com cert recebem score alto
        s_pond = 0.0
        for m in materiais:
            sc = _cert_score(certs_social_por_m[m.id], _CERT_SOCIAL)
            if sc is None:
                forn = fornecedores_por_m[m.id]
                cs = getattr(forn, "conformidade_social", "nao_verificado") or "nao_verificado"
                sc_map = {"nao_verificado": 25, "em_processo": 50,
                          "certificado_abvtex": 90, "certificado_sa8000": 100}
                sc = float(sc_map.get(cs, 25))
            s_pond += sc * fracoes[m.id]
        s_pts   = s_pond
        s_fonte = "primario"
        certs_nomes = sorted({c.tipo for c in certs_social_todos})
        s_metodo = f"Certificação social verificada: {', '.join(certs_nomes)} (ponderado por peso)"
        s_refs  = certs_nomes + ["ABVTEX"]
        s_ind   = f"certs: {', '.join(certs_nomes)}"
    elif materiais:
        s_pond = 0.0
        sc_map = {"nao_verificado": 25, "em_processo": 50,
                  "certificado_abvtex": 90, "certificado_sa8000": 100}
        for m in materiais:
            forn = fornecedores_por_m[m.id]
            cs   = getattr(forn, "conformidade_social", "nao_verificado") or "nao_verificado"
            sc   = float(sc_map.get(cs, 25))
            if forn.nota_confianca is not None:
                sc = max(sc, 20 + (forn.nota_confianca / 5) * 55)
            s_pond += sc * fracoes[m.id]
        s_pts   = s_pond
        s_fonte = "estimado"
        s_metodo = (
            "Proxy conformidade_social + nota_confianca dos fornecedores"
            + (" — ponderado por peso" if usa_peso else " — pesos iguais")
        )
        s_refs = ["ABVTEX", "Higg FSLM"]
        s_ind  = f"média ponderada {s_pts:.0f}/100"
        alertas.append(
            "Social: pontuação estimada. "
            "Incentive fornecedores a obter certificação ABVTEX ou SA8000."
        )
    else:
        s_pts   = 0.0
        s_fonte = "ausente"
        s_metodo = "Sem fornecedores ou dados de conformidade social"
        s_refs  = ["ABVTEX", "Higg FSLM"]
        s_ind   = None
        alertas.append("Social: preencha nota_confianca e conformidade_social dos fornecedores.")

    d_social = DimensaoISCM(
        pontos=_clamp(s_pts), peso=0.10, fonte=s_fonte,
        metodologia=s_metodo, referencias=s_refs, indicador_auditavel=s_ind,
    )

    # ── D7: Rastreabilidade (10%) ────────────────────────────────────────────
    etapas_reg = {e.etapa for e in etapas}
    n_etapas   = len(etapas_reg & _ETAPAS)
    cobertura_etapas = n_etapas / len(_ETAPAS)

    gln_count  = sum(1 for e in etapas if getattr(e, "instalacao_gln", None))
    gln_ratio  = gln_count / len(etapas) if etapas else 0.0

    all_certs  = [c for cs in certs_material_por_m.values() for c in cs]
    certs_verif = [c for c in all_certs if c.apresentado == "sim" and c.nivel_confianca == "alto"]
    cert_ratio = len(certs_verif) / len(all_certs) if all_certs else 0.0

    if materiais:
        # Bônus se peso_kg está preenchido (indica diligência de rastreamento)
        bonus_peso = 5.0 if usa_peso else 0.0
        t_pts  = (
            cobertura_etapas * 45
            + gln_ratio * 20
            + cert_ratio * 20
            + (10.0 if materiais else 0)
            + bonus_peso
        )
        t_fonte = "primario" if cobertura_etapas >= 0.5 else "estimado"
        t_metodo = (
            f"Etapas {n_etapas}/{len(_ETAPAS)} | "
            f"GLN {gln_count}/{len(etapas)} | "
            f"Certs verificadas {len(certs_verif)}/{len(all_certs)} | "
            f"Peso mássico {'sim' if usa_peso else 'não'}"
        )
        t_refs = ["GS1 Digital Link v1.1", "GOTS Chain of Custody", "Textile Exchange"]
        t_ind  = f"{n_etapas}/{len(_ETAPAS)} etapas rastreadas"
        if n_etapas < 4:
            alertas.append(
                f"Rastreabilidade: {n_etapas}/7 etapas documentadas. "
                "Adicione etapas em /pecas/{codigo}/etapas-producao."
            )
    else:
        t_pts  = 0.0
        t_fonte = "ausente"
        t_metodo = "Sem materiais nem etapas vinculadas"
        t_refs = ["GS1 Digital Link v1.1"]
        t_ind  = "0/7 etapas"
        alertas.append("Rastreabilidade: vincule materiais e registre etapas de produção.")

    d_rastreabilidade = DimensaoISCM(
        pontos=_clamp(t_pts), peso=0.10, fonte=t_fonte,
        metodologia=t_metodo, referencias=t_refs, indicador_auditavel=t_ind,
    )

    # ── Score final ──────────────────────────────────────────────────────────
    dimensoes: dict[str, DimensaoISCM] = {
        "carbono":         d_carbono,
        "agua":            d_agua,
        "quimicos":        d_quimico,
        "materiais":       d_materiais,
        "residuos":        d_residuos,
        "social":          d_social,
        "rastreabilidade": d_rastreabilidade,
    }

    score_total  = sum(d.pontos * d.peso for d in dimensoes.values())
    n_primario   = sum(1 for d in dimensoes.values() if d.fonte == "primario")
    cobertura    = (n_primario / len(dimensoes)) * 100

    return ISCMResult(
        peca_codigo=peca.codigo,
        score_total=round(score_total, 1),
        nivel=_nivel(score_total),
        dimensoes=dimensoes,
        cobertura_dados_pct=round(cobertura, 0),
        alertas=alertas,
    )
