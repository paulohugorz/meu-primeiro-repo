from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.security.pilot_access import PilotAccessMiddleware
from sqlalchemy.orm import Session
from app.core.database import initialize_schema_if_enabled, SessionLocal
from app.api.routes import public_dpp_url, router
from app.api.fornecedores import router as router_fornecedores
from app.api.modelagem import router as router_modelagem, router_banco as router_banco_modelagem
from app.api.catalogo import router as router_catalogo
from app.api.telemetry_dashboard import router as router_telemetry_dashboard
from app.api.iam import router as router_iam
from app.api.intake import router as router_intake
from app.api.impact_v2 import router as router_impact_v2
from app.api.telemetry_dashboard import require_dashboard_access
from fastapi import Depends
from app.validators.dpp_validators import EVIDENCE_LABELS
import os, json

initialize_schema_if_enabled()

app = FastAPI(
    title="PHYLLOS DPP",
    description="Infraestrutura de dados para publicar passaportes digitais de produtos de moda.",
    version="0.1.0",
)

app.add_middleware(PilotAccessMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
phyllos_site_dir = os.path.join(repo_root, "phyllos")

images_dir = os.path.join(os.path.dirname(__file__), "../data/images")
os.makedirs(images_dir, exist_ok=True)
app.mount("/static/images", StaticFiles(directory=images_dir), name="images")

app.include_router(router)
app.include_router(router_fornecedores)
app.include_router(router_modelagem)
app.include_router(router_banco_modelagem)
app.include_router(router_catalogo)
app.include_router(router_telemetry_dashboard)
app.include_router(router_iam)
app.include_router(router_intake)
app.include_router(router_impact_v2)


@app.get("/", response_class=HTMLResponse)
async def frontend(request: Request):
    dpp_studio_path = os.path.join(phyllos_site_dir, "dpp-studio.html")
    if os.path.exists(dpp_studio_path):
        with open(dpp_studio_path, "r", encoding="utf-8") as studio_file:
            studio_html = studio_file.read()
        instrumented_html = studio_html.replace(
            "</body>",
            '<a href="/iam" style="position:fixed;right:18px;bottom:18px;z-index:9999;background:#172019;color:white;padding:11px 15px;border-radius:999px;text-decoration:none;font:600 11px system-ui;box-shadow:0 5px 18px #0003">Pessoas e Workspaces</a>'
            '<script src="/telemetry.js" defer></script></body>',
            1,
        )
        return HTMLResponse(instrumented_html)
    return templates.TemplateResponse(request, "index.html")


@app.get("/atelier", response_class=HTMLResponse)
async def atelier(request: Request):
    """Ateliê SPA — gestão de peças, modelagens e DPP."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/iam", response_class=HTMLResponse)
async def iam_console(request: Request, _user: str = Depends(require_dashboard_access)):
    """Console administrativo persistente de Pessoas, Workspaces e Memberships."""
    return templates.TemplateResponse(request, "iam_workspaces.html")


def _dpp_context(peca, request):
    """Monta o contexto compartilhado entre /p/{uuid} e /etiqueta."""
    from app.models.models import EtapaProducao
    ficha    = peca.ficha_tecnica
    materiais = peca.materiais

    def json_or_empty(raw, fallback):
        if not raw:
            return fallback
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return fallback

    composicao = json_or_empty(ficha.composicao_fibras, []) if ficha else []
    certs      = json_or_empty(ficha.certificacoes, []) if ficha else []
    evidence_statuses = json_or_empty(ficha.evidencia_statuses, {}) if ficha else {}

    fornecedores_info = []
    seen = set()
    for m in materiais:
        f = m.produto.fornecedor
        if f.id not in seen:
            seen.add(f.id)
            fornecedores_info.append({
                "nome": f.nome, "cidade": f.cidade,
                "estado": f.estado, "nota": f.nota_confianca,
            })

    instrucoes_reparo   = ficha.instrucoes_reparo       if ficha else None
    instrucoes_fim_vida = ficha.instrucoes_fim_de_vida  if ficha else None
    total_cards = 3 + (1 if composicao else 0) + (1 if instrucoes_reparo or instrucoes_fim_vida else 0)

    return {
        "request": request,
        "peca_nome":         peca.nome,
        "peca_codigo":       peca.codigo,
        "peca_gtin":         peca.gtin,
        "peca_uuid":         peca.dpp_uuid,
        "peca_status":       peca.dpp_status,
        "dpp_version":       peca.dpp_version,
        "data_publicacao":   peca.data_publicacao,
        "composicao":        composicao,
        "certificacoes":     certs,
        "carbono_kgco2e":    ficha.pegada_carbono_kgco2e      if ficha else None,
        "agua_peca_litros":  ficha.agua_peca_litros            if ficha else None,
        "energia_peca_kwh":  ficha.energia_peca_kwh            if ficha else None,
        "impact_sources": {
            "agua": ficha.fonte_agua_litros_kg if ficha else None,
            "energia": ficha.fonte_energia_kwh_kg if ficha else None,
            "carbono": ficha.fonte_carbono_kgco2e_kg if ficha else None,
            "metodologia": ficha.metodologia_fatores_impacto if ficha else None,
        },
        "area_perdida_m2":   ficha.area_perdida_m2             if ficha else None,
        "peso_peca_kg":      ficha.peso_peca_kg                if ficha else None,
        "perda_corte_pct":   peca.perda_corte_pct,
        "lote_quantidade":   peca.lote_quantidade,
        "evidence_statuses": evidence_statuses,
        "evidence_labels":   EVIDENCE_LABELS,
        "durabilidade_ciclos": ficha.durabilidade_ciclos_lavagem if ficha else None,
        "instrucoes_reparo":  instrucoes_reparo,
        "instrucoes_fim_vida": instrucoes_fim_vida,
        "fornecedores":      fornecedores_info,
        "total_cards":       total_cards,
    }


@app.get("/p/{uuid}", response_class=HTMLResponse)
async def consumer_dpp(request: Request, uuid: str):
    from app.models.models import Peca
    db: Session = SessionLocal()
    try:
        peca = db.query(Peca).filter(
            Peca.dpp_uuid == uuid,
            Peca.dpp_status == "publicado",
        ).first()
        if not peca:
            return HTMLResponse(
                "<html><body style='font-family:sans-serif;padding:40px'>"
                "<h2>Passaporte não encontrado</h2>"
                "<p>O QR code pode estar desatualizado.</p></body></html>",
                status_code=404,
            )
        ctx = _dpp_context(peca, request)
    finally:
        db.close()
    return templates.TemplateResponse(request, "dpp_consumer.html", ctx)


@app.get("/pecas/{codigo}/etiqueta", response_class=HTMLResponse)
async def etiqueta_peca(request: Request, codigo: str):
    from app.models.models import Peca
    from app.api.routes import _gerar_qr_base64
    db: Session = SessionLocal()
    try:
        peca = db.query(Peca).filter(Peca.codigo == codigo).first()
        if not peca:
            return HTMLResponse("<h2>Peça não encontrada</h2>", status_code=404)
        if not peca.dpp_uuid:
            return HTMLResponse("<h2>Peça sem UUID — crie a peça novamente para gerar etiqueta</h2>", status_code=400)

        ctx = _dpp_context(peca, request)
        passport_url = public_dpp_url(peca.dpp_uuid)
        ctx["qr_b64"]       = _gerar_qr_base64(passport_url)
        ctx["passport_url"] = passport_url
    finally:
        db.close()
    return templates.TemplateResponse(request, "etiqueta.html", ctx)


if os.path.isdir(phyllos_site_dir):
    app.mount("/", StaticFiles(directory=phyllos_site_dir, html=True), name="phyllos_site")
