from __future__ import annotations
import json
import uuid
from pathlib import Path
from typing import Any, Dict

from db import canonical_json, connect, transaction, utcnow
from recognition_service import get_recognition, get_recognition_result

ASSESSMENTS = {"correta", "parcialmente_correta", "incorreta", "indeterminada"}
STATUSES = {"em_validacao", "validada", "divergencia", "aguardando_segunda_revisao"}
SOURCES = {"etiqueta", "ficha_tecnica", "declaracao_fornecedor", "ensaio_laboratorial", "avaliacao_profissional", "outra"}

def _validate_composition(payload: Dict[str, Any]) -> list[dict]:
    status = payload.get("composition_status", "nao_confirmada")
    fibers = payload.get("composition", [])
    if status == "confirmada_percentuais":
        if not fibers or round(sum(float(x["percent"]) for x in fibers), 4) != 100:
            raise ValueError("composition percentages must sum to 100")
    return fibers

def create_validation(db_path: str | Path, run_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    run = get_recognition(db_path, run_id)
    result = get_recognition_result(db_path, run_id)
    if payload.get("status") not in STATUSES:
        raise ValueError("invalid validation status")
    if payload.get("confirmation_source") not in SOURCES:
        raise ValueError("invalid confirmation source")
    assessments = payload.get("hypothesis_assessments", [])
    if any(x.get("assessment") not in ASSESSMENTS for x in assessments):
        raise ValueError("invalid hypothesis assessment")
    fibers = _validate_composition(payload)
    top1 = bool(assessments and assessments[0].get("assessment") == "correta")
    top3 = any(x.get("assessment") == "correta" for x in assessments[:3])
    image_assessments = payload.get("image_assessments", [])
    reasons = []
    if payload.get("status") != "validada": reasons.append("avaliação profissional não concluída")
    if payload.get("composition_status") == "nao_confirmada": reasons.append("composição não confirmada")
    if not payload.get("commercial_name", "").strip(): reasons.append("identidade comercial ausente")
    if len(image_assessments) != 6 or any(x.get("quality") != "adequada" for x in image_assessments): reasons.append("protocolo de imagens insuficiente")
    if payload.get("status") in {"divergencia", "aguardando_segunda_revisao"}: reasons.append("divergência não resolvida")
    validation_id = f"professional-validation:{uuid.uuid4().hex}"
    now = utcnow()
    values = (
        validation_id, run_id, run["capture_session_id"], payload["validator_actor_id"], payload["validator_role"],
        payload["status"], payload.get("commercial_name", "").strip(), payload.get("structure"), payload.get("transparency"),
        payload.get("weight_gsm"), payload.get("elasticity"), payload["confirmation_source"], payload.get("composition_status", "nao_confirmada"),
        canonical_json(fibers), canonical_json(assessments), int(bool(payload.get("no_hypothesis_correct"))),
        canonical_json(image_assessments), canonical_json(payload.get("recapture_request", {})), payload.get("notes", ""),
        int(top1), int(top3), int(not reasons), "; ".join(reasons) or None, "professional-validation-form:0.1.0",
        payload.get("taxonomy_version", "textile-taxonomy:0.3"), now
    )
    with transaction(db_path) as conn:
        conn.execute("""INSERT INTO professional_validations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", values)
        conn.execute("""INSERT INTO validation_audit_events VALUES(?,?,?,?,?,?,?,?)""", (
            f"audit-event:{uuid.uuid4().hex}", validation_id, payload["validator_actor_id"], "validation_created", None,
            canonical_json({"payload": payload, "frozen_inference": result}), payload.get("justification", "validação profissional inicial"), now
        ))
    return get_validation(db_path, validation_id)

def get_validation(db_path: str | Path, validation_id: str) -> Dict[str, Any]:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM professional_validations WHERE validation_id=?", (validation_id,)).fetchone()
        events = conn.execute("SELECT * FROM validation_audit_events WHERE validation_id=? ORDER BY created_at", (validation_id,)).fetchall()
    if not row: raise KeyError("professional validation not found")
    value = dict(row)
    for key in ("composition_json", "hypothesis_assessments_json", "image_assessments_json", "recapture_request_json"):
        value[key.removesuffix("_json")] = json.loads(value.pop(key))
    for key in ("no_hypothesis_correct", "top1_correct", "top3_correct", "gold_set_eligible"):
        value[key] = bool(value[key])
    value["audit_events"] = [dict(x) for x in events]
    value["frozen_inference"] = get_recognition_result(db_path, value["recognition_run_id"])
    return value

def list_validations(db_path: str | Path, run_id: str) -> list[Dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute("SELECT validation_id FROM professional_validations WHERE recognition_run_id=? ORDER BY created_at", (run_id,)).fetchall()
    return [get_validation(db_path, x["validation_id"]) for x in rows]
