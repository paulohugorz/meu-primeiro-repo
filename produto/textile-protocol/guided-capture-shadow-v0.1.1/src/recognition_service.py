from __future__ import annotations

import csv
import json
import uuid
from pathlib import Path
from typing import Any, Dict

from capture_service import get_session
from db import ROOT, connect, transaction, utcnow

PREDICTIONS_PATH = ROOT / "data" / "synthetic_pilot" / "rule_predictions.csv"
SCHEMA_VERSION = "recognition-result:shadow:v0.1.2"


def _environmental_indicators() -> Dict[str, Any]:
    """Publish the impact contract without fabricating environmental values."""
    return {
        "status": "not_calculated",
        "methodology_version": "0.3.0-draft",
        "formula_version": "impact-mixture-v1.1",
        "functional_unit": "1 kg of finished fabric",
        "reason": "missing_verified_composition_mass_and_approved_factors",
        "items": [
            {"indicator": "climate_change", "value": None, "unit": "kg_co2e"},
            {"indicator": "water_consumption", "value": None, "unit": "litre"},
            {"indicator": "energy_demand", "value": None, "unit": "MJ"},
        ],
    }


def _prediction_for(service_sample_id: str) -> Dict[str, str]:
    with PREDICTIONS_PATH.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["sample_id"] == service_sample_id:
                return row
    raise KeyError("synthetic prediction fixture not found")


def _build_result(session: Dict[str, Any], prediction: Dict[str, str]) -> Dict[str, Any]:
    decision = prediction["decision"]
    abstained = decision in {"abstain", "request_new_evidence"}
    warnings = [x for x in prediction["reason_codes"].split("|") if x]
    evidence_ids = [
        item["evidence"]["evidence_id"]
        for item in session["items"] if item.get("evidence")
    ]
    family = prediction["structure_family"]
    construction = prediction["construction_primary"]
    alternatives = [x for x in prediction["construction_candidates"].split("|") if x]
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "shadow",
        "status": "completed",
        "result_kind": "frozen_synthetic_fixture_replay",
        "hypothesis": None if abstained else {
            "family": family,
            "class": construction,
            "subclass": None,
            "score": None,
            "characteristics": {
                "visual_transparency": prediction["visual_transparency"],
                "capture_quality": prediction["capture_quality"]
            }
        },
        "alternatives": [
            {"class": value, "score": None}
            for value in alternatives if value != construction
        ],
        "abstained": abstained,
        "abstention_reason": warnings if abstained else [],
        "review_required": True,
        "warnings": warnings,
        "evidence_ids": evidence_ids,
        "method_version": "human-rule-first:0.1.1:frozen-synthetic",
        "benchmark_version_id": prediction["benchmark_version_id"],
        "coverage": {
            "required_views": 6,
            "accepted_views": len(session["completion"]["accepted_shot_types"]),
            "complete": session["completion"]["complete"]
        },
        "environmental_indicators": _environmental_indicators(),
        "official_mutation_applied": False,
        "publication_decision_created": False,
        "notice": (
            "Reprodução da baseline congelada para validar a integração da interface. "
            "Não é reconhecimento visual novo nem métrica empírica."
        )
    }


def start_recognition(db_path: str | Path, session_id: str) -> Dict[str, Any]:
    session = get_session(db_path, session_id)
    if session["status"] != "complete" or not session["ready_for_baseline"]:
        raise ValueError("capture session must be complete before recognition")
    if not session["ops_id"].startswith("OPS-SYN-"):
        raise ValueError("recognition is restricted to synthetic fixtures")
    run_id = f"recognition-run:{uuid.uuid4().hex}"
    started_at = utcnow()
    prediction = _prediction_for(session["service_sample_id"])
    result = _build_result(session, prediction)
    completed_at = utcnow()
    with transaction(db_path) as conn:
        conn.execute(
            """INSERT INTO recognition_runs(
                recognition_run_id,capture_session_id,mode,status,stage,started_at,
                completed_at,result_json,schema_version
            ) VALUES(?,?,?,?,?,?,?,?,?)""",
            (run_id, session_id, "shadow", "completed", "completed", started_at,
             completed_at, json.dumps(result, ensure_ascii=False), SCHEMA_VERSION)
        )
    return get_recognition(db_path, run_id)


def get_recognition(db_path: str | Path, run_id: str) -> Dict[str, Any]:
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM recognition_runs WHERE recognition_run_id=?", (run_id,)
        ).fetchone()
    if not row:
        raise KeyError("recognition run not found")
    value = dict(row)
    value["official_mutation_applied"] = bool(value["official_mutation_applied"])
    value["publication_decision_created"] = bool(value["publication_decision_created"])
    value.pop("result_json")
    return value


def get_recognition_result(db_path: str | Path, run_id: str) -> Dict[str, Any]:
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT status,result_json FROM recognition_runs WHERE recognition_run_id=?",
            (run_id,)
        ).fetchone()
    if not row:
        raise KeyError("recognition run not found")
    if row["status"] != "completed" or not row["result_json"]:
        raise ValueError("recognition result is not available")
    return json.loads(row["result_json"])
