import json

from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from app.schemas.intake import IntakeImportResult, IntakeValidationResult
from app.services.intake_importer import parse_portfolio
from app.services.intake_validator import validate_intake


router = APIRouter(prefix="/intake", tags=["DPP Assistido — Intake"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def intake_page(request: Request):
    return templates.TemplateResponse(request, "intake.html")


@router.get("/capabilities")
def integration_capabilities():
    return {"version": "1.0", "modes": ["csv_upload", "xlsx_upload", "json_upload", "api_json"],
        "upload_endpoint": "/intake/upload", "api_endpoint": "/intake/validate",
        "formats": ["csv", "xlsx", "json"], "max_bytes": 10485760, "max_rows": 5000,
        "behavior": "preview_only", "persistence": False}


@router.get("/template.csv", response_class=PlainTextResponse)
def intake_template():
    return PlainTextResponse("product_id,product_name,sku,brand_name,gtin,fiber_composition,country_of_manufacture\n")


@router.post("/upload", response_model=IntakeImportResult)
async def upload_portfolio(file: UploadFile = File(...)):
    try:
        return parse_portfolio(file.filename or "portfolio", await file.read())
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/validate",
    response_model=IntakeValidationResult,
    responses={422: {"model": IntakeValidationResult}},
)
def validate_dpp_intake(payload: dict = Body(...)):
    """Valida completude sem persistir o conteúdo recebido."""
    result = validate_intake(payload)
    if not result.valid:
        return JSONResponse(status_code=422, content=result.model_dump(mode="json"))
    return result
