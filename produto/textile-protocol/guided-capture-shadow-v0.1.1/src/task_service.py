from __future__ import annotations
import csv
import hashlib
import json
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from db import ROOT, canonical_json, connect, transaction, utcnow

POLICY = json.loads(
    (ROOT / "config" / "shadow_mode_policy_v0.1.1.json").read_text(encoding="utf-8")
)
BENCHMARK = json.loads(
    (ROOT / "config" / "benchmark_1.json").read_text(encoding="utf-8")
)
OFFICIAL_FIELDS = (
    "structure_family", "construction_primary", "visual_transparency",
    "capture_quality", "decision"
)

def _id(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"

def _hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def _read_csv(path: str | Path) -> List[Dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def _source_decision_id(prediction: Dict[str, str]) -> str:
    return f"benchmark-decision:{prediction['sample_id']}:{prediction.get('ruleset_version','unknown')}"

def benchmark_projection(value: Dict[str, Any]) -> Dict[str, Any]:
    return {field: value.get(field) for field in OFFICIAL_FIELDS}

def validate_projection(proposal: Dict[str, Any], partial: bool = True) -> Dict[str, Any]:
    if not isinstance(proposal, dict) or not proposal:
        raise ValueError("proposed_decision must be a non-empty object")
    unknown = sorted(set(proposal) - set(OFFICIAL_FIELDS))
    if unknown:
        raise ValueError(f"unknown benchmark proposal fields: {unknown}")
    if not partial:
        missing = sorted(set(OFFICIAL_FIELDS) - set(proposal))
        if missing:
            raise ValueError(f"missing benchmark fields: {missing}")

    allowed = {
        "structure_family": set(BENCHMARK["dimensions"]["structure_family"]["values"]),
        "construction_primary": set(BENCHMARK["dimensions"]["construction_primary"]["values"]),
        "visual_transparency": set(BENCHMARK["dimensions"]["visual_transparency"]["values"]),
        "capture_quality": set(BENCHMARK["dimensions"]["capture_quality"]["values"]),
        "decision": set(BENCHMARK["allowed_decisions"]),
    }
    for field, value in proposal.items():
        if value not in allowed[field]:
            raise ValueError(f"invalid value for {field}: {value}")
    return dict(proposal)

def validate_full_projection(projection: Dict[str, Any]) -> None:
    validate_projection(projection, partial=False)
    family = projection["structure_family"]
    construction = projection["construction_primary"]
    if family == "woven_fabric" and construction == "not_applicable":
        raise ValueError("woven_fabric cannot have construction_primary=not_applicable")
    if family != "woven_fabric" and construction not in {"not_applicable", "indeterminate"}:
        raise ValueError("non-woven families cannot receive a woven construction class")

def snapshot_official_decision(db_path: str | Path, prediction: Dict[str, str]) -> Dict[str, Any]:
    projection = benchmark_projection(prediction)
    validate_full_projection(projection)
    decision = {
        **projection,
        "sample_id": prediction["sample_id"],
        "reason_codes": prediction.get("reason_codes", ""),
        "ruleset_version": prediction.get("ruleset_version"),
        "benchmark_version_id": prediction.get("benchmark_version_id"),
    }
    decision_hash = _hash(decision)
    projection_hash = _hash(projection)
    source_decision_id = _source_decision_id(prediction)
    snapshot_id = f"official-snapshot:{decision_hash[:24]}"
    with transaction(db_path) as conn:
        conn.execute(
            """INSERT OR IGNORE INTO official_decision_snapshots(
                snapshot_id,sample_id,source_decision_id,decision_hash,decision_json,
                benchmark_projection_hash,benchmark_projection_json,captured_at
            ) VALUES(?,?,?,?,?,?,?,?)""",
            (
                snapshot_id, prediction["sample_id"], source_decision_id,
                decision_hash, canonical_json(decision), projection_hash,
                canonical_json(projection), utcnow()
            )
        )
    return {
        "snapshot_id": snapshot_id,
        "sample_id": prediction["sample_id"],
        "source_decision_id": source_decision_id,
        "decision_hash": decision_hash,
        "projection_hash": projection_hash,
        "decision": decision,
        "projection": projection
    }

def _deterministic_control(sample_id: str, rate: float) -> bool:
    bucket = int(hashlib.sha256(sample_id.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
    return bucket < rate

def derive_task_specs(sample: Dict[str, str], prediction: Dict[str, str]) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    decision = prediction.get("decision")
    reason_codes = set(filter(None, prediction.get("reason_codes", "").split("|")))
    capture_quality = prediction.get("capture_quality")

    def add(task_type: str, reason: str, evidence: List[str]):
        specs.append({
            "task_type": task_type,
            "priority": POLICY["task_types"][task_type]["priority"],
            "trigger_reason": reason,
            "requested_evidence": evidence
        })

    if decision == "request_new_evidence":
        if sample.get("focus_ok") != "yes":
            add("recapture_focus", "capture_insufficient:focus", ["face_overview", "reverse_overview"])
        if sample.get("has_macro") != "yes":
            add("recapture_macro_structure", "capture_insufficient:macro_missing", ["macro_structure"])
        if sample.get("has_backlight") != "yes":
            add("recapture_backlight", "capture_insufficient:backlight_missing", ["backlight_transparency"])
        if int(sample.get("image_count") or 0) < 3:
            add("complete_capture_set", "capture_insufficient:image_count", [
                "face_overview", "reverse_overview", "macro_structure",
                "drape_fold", "backlight_transparency", "scale_reference"
            ])
    if "conflicting_structural_cues" in reason_codes:
        add("resolve_structural_conflict", "conflicting_structural_cues", [
            "macro_structure", "reverse_overview", "specialist_review"
        ])
    if "structure_family_indeterminate" in reason_codes:
        add("verify_structure_family", "structure_family_indeterminate", [
            "macro_structure", "reverse_overview", "specialist_review"
        ])
    if "woven_construction_indeterminate" in reason_codes:
        add("verify_construction_primary", "woven_construction_indeterminate", [
            "macro_structure", "specialist_review"
        ])
    if "transparency_indeterminate" in reason_codes:
        add("verify_visual_transparency", "transparency_indeterminate", [
            "backlight_transparency"
        ])
    if capture_quality == "limited":
        add("quality_audit_limited_capture", "capture_quality_limited", ["capture_set_review"])
    if decision == "classify" and capture_quality == "adequate" and _deterministic_control(
        prediction["sample_id"], POLICY["control_audit_rate"]
    ):
        add("control_audit", "shadow_control_sample", ["independent_specialist_review"])

    return list({spec["task_type"]: spec for spec in specs}.values())

def _create_task(
    db_path: str | Path,
    sample_id: str,
    prediction: Dict[str, str],
    snapshot: Dict[str, Any],
    spec: Dict[str, Any],
) -> Dict[str, Any]:
    key_payload = {
        "sample_id": sample_id,
        "source_decision_id": snapshot["source_decision_id"],
        "decision_hash": snapshot["decision_hash"],
        "task_type": spec["task_type"],
        "policy_version": POLICY["version"],
    }
    task_key = _hash(key_payload)
    task_id = f"verification-task:{task_key[:24]}"
    created_at = utcnow()
    with transaction(db_path) as conn:
        conn.execute(
            """INSERT OR IGNORE INTO verification_tasks(
                task_id,task_key,sample_id,source_decision_id,source_ruleset_version,
                source_benchmark_version_id,source_snapshot_id,task_type,status,
                priority,mode,trigger_reason,requested_evidence_json,created_at,
                affects_official_decision,user_notification_sent
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,0)""",
            (
                task_id, task_key, sample_id, snapshot["source_decision_id"],
                prediction.get("ruleset_version", "unknown"),
                prediction.get("benchmark_version_id", "unknown"),
                snapshot["snapshot_id"], spec["task_type"], "open",
                spec["priority"], "shadow", spec["trigger_reason"],
                canonical_json(spec["requested_evidence"]), created_at
            )
        )
        inserted = conn.execute("SELECT changes()").fetchone()[0] == 1
        if inserted:
            conn.execute(
                "INSERT INTO task_events(task_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
                (
                    task_id, "created",
                    canonical_json({
                        "mode": "shadow",
                        "trigger_reason": spec["trigger_reason"],
                        "requested_evidence": spec["requested_evidence"]
                    }),
                    created_at
                )
            )
    return get_task(db_path, task_id)

def ingest_baseline(
    db_path: str | Path,
    samples_csv: str | Path,
    predictions_csv: str | Path,
) -> Dict[str, Any]:
    sample_rows = _read_csv(samples_csv)
    prediction_rows = _read_csv(predictions_csv)
    if len({r["sample_id"] for r in sample_rows}) != len(sample_rows):
        raise ValueError("duplicate sample_id in samples CSV")
    if len({r["sample_id"] for r in prediction_rows}) != len(prediction_rows):
        raise ValueError("duplicate sample_id in predictions CSV")
    samples = {r["sample_id"]: r for r in sample_rows}
    created_before = count_tasks(db_path)
    specs_total = 0
    for prediction in prediction_rows:
        sample = samples.get(prediction["sample_id"], {})
        snapshot = snapshot_official_decision(db_path, prediction)
        specs = derive_task_specs(sample, prediction)
        specs_total += len(specs)
        for spec in specs:
            _create_task(db_path, prediction["sample_id"], prediction, snapshot, spec)
    created_after = count_tasks(db_path)
    return {
        "processed_predictions": len(prediction_rows),
        "derived_task_specs": specs_total,
        "new_tasks": created_after - created_before,
        "total_tasks": created_after,
        "mode": "shadow"
    }

def count_tasks(db_path: str | Path) -> int:
    with connect(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM verification_tasks").fetchone()[0]

def get_task(db_path: str | Path, task_id: str) -> Dict[str, Any]:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM verification_tasks WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            raise KeyError("verification task not found")
        events = conn.execute(
            "SELECT event_id,event_type,payload_json,created_at FROM task_events WHERE task_id=? ORDER BY event_id",
            (task_id,)
        ).fetchall()
    result = dict(row)
    result["requested_evidence"] = json.loads(result.pop("requested_evidence_json"))
    result["resolution"] = json.loads(result["resolution_json"]) if result["resolution_json"] else None
    result.pop("resolution_json")
    result["affects_official_decision"] = bool(result["affects_official_decision"])
    result["user_notification_sent"] = bool(result["user_notification_sent"])
    result["events"] = [
        {
            "event_id": e["event_id"], "event_type": e["event_type"],
            "payload": json.loads(e["payload_json"]), "created_at": e["created_at"]
        } for e in events
    ]
    return result

def list_tasks(db_path: str | Path, status: str | None = None) -> List[Dict[str, Any]]:
    with connect(db_path) as conn:
        if status:
            rows = conn.execute(
                "SELECT task_id FROM verification_tasks WHERE status=? ORDER BY priority,created_at",
                (status,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT task_id FROM verification_tasks ORDER BY status,priority,created_at"
            ).fetchall()
    return [get_task(db_path, r["task_id"]) for r in rows]

def resolve_task(
    db_path: str | Path,
    task_id: str,
    outcome: str,
    performed_by_actor_id: str,
    notes: str,
    evidence_ids: List[str] | None = None,
    proposed_decision: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    allowed = {"confirmed", "corrected", "inconclusive", "evidence_unavailable", "cancelled"}
    if outcome not in allowed:
        raise ValueError("invalid outcome")
    if not performed_by_actor_id.strip():
        raise ValueError("performed_by_actor_id is required")
    current = get_task(db_path, task_id)
    if current["status"] in {"resolved", "cancelled"}:
        raise ValueError("task is already closed")
    if proposed_decision is not None:
        validate_projection(proposed_decision, partial=True)
    resolution = {
        "outcome": outcome,
        "performed_by_actor_id": performed_by_actor_id,
        "notes": notes,
        "evidence_ids": evidence_ids or [],
        "proposed_decision": proposed_decision
    }
    status = "cancelled" if outcome == "cancelled" else "resolved"
    now = utcnow()
    with transaction(db_path) as conn:
        conn.execute(
            """UPDATE verification_tasks
               SET status=?,resolution_json=?,resolved_at=?
               WHERE task_id=?""",
            (status, canonical_json(resolution), now, task_id)
        )
        conn.execute(
            "INSERT INTO task_events(task_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
            (task_id, "resolved", canonical_json(resolution), now)
        )
    if proposed_decision is not None:
        compare_shadow_decision(db_path, task_id, proposed_decision)
    return get_task(db_path, task_id)

def compare_shadow_decision(
    db_path: str | Path,
    task_id: str,
    proposed_decision: Dict[str, Any],
) -> Dict[str, Any]:
    proposal = validate_projection(proposed_decision, partial=True)
    with connect(db_path) as conn:
        row = conn.execute(
            """SELECT s.benchmark_projection_hash,s.benchmark_projection_json
               FROM verification_tasks t
               JOIN official_decision_snapshots s ON s.snapshot_id=t.source_snapshot_id
               WHERE t.task_id=?""",
            (task_id,)
        ).fetchone()
    if not row:
        raise KeyError("task or snapshot not found")
    official = json.loads(row["benchmark_projection_json"])
    normalized = dict(official)
    normalized.update(proposal)
    validate_full_projection(normalized)
    proposed_hash = _hash(normalized)
    would_change = proposed_hash != row["benchmark_projection_hash"]
    changed_fields = {
        field: {"official": official[field], "proposed": normalized[field]}
        for field in OFFICIAL_FIELDS if official[field] != normalized[field]
    }
    evaluation_id = _id("shadow-evaluation")
    payload = {
        "changed_fields": changed_fields,
        "compared_fields": list(OFFICIAL_FIELDS),
        "benchmark_version_id": BENCHMARK["id"],
        "promotion_performed": False,
        "mode": "shadow"
    }
    with transaction(db_path) as conn:
        conn.execute(
            """INSERT INTO shadow_evaluations(
                evaluation_id,task_id,compared_to_projection_hash,
                proposed_projection_json,proposed_projection_hash,would_change,
                comparison_json,created_at
            ) VALUES(?,?,?,?,?,?,?,?)""",
            (
                evaluation_id, task_id, row["benchmark_projection_hash"],
                canonical_json(normalized), proposed_hash, 1 if would_change else 0,
                canonical_json(payload), utcnow()
            )
        )
        conn.execute(
            "INSERT INTO task_events(task_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
            (
                task_id, "shadow_compared",
                canonical_json({"would_change": would_change, **payload}), utcnow()
            )
        )
    return {
        "evaluation_id": evaluation_id,
        "task_id": task_id,
        "would_change": would_change,
        "changed_fields": changed_fields,
        "compared_fields": list(OFFICIAL_FIELDS),
        "promotion_performed": False,
        "mode": "shadow"
    }

def shadow_report(db_path: str | Path) -> Dict[str, Any]:
    with connect(db_path) as conn:
        tasks = [dict(r) for r in conn.execute("SELECT * FROM verification_tasks").fetchall()]
        evals = [dict(r) for r in conn.execute("SELECT * FROM shadow_evaluations").fetchall()]
        snapshots = conn.execute("SELECT COUNT(*) FROM official_decision_snapshots").fetchone()[0]
        evidence = conn.execute("SELECT COUNT(*) FROM evidence_records").fetchone()[0]
        sessions = conn.execute("SELECT COUNT(*) FROM capture_sessions").fetchone()[0]
        superseded = conn.execute(
            "SELECT COUNT(*) FROM capture_sessions WHERE status='superseded'"
        ).fetchone()[0]
    return {
        "mode": "shadow",
        "policy_version": POLICY["version"],
        "tasks_total": len(tasks),
        "tasks_by_status": dict(Counter(t["status"] for t in tasks)),
        "tasks_by_type": dict(Counter(t["task_type"] for t in tasks)),
        "tasks_by_priority": dict(Counter(t["priority"] for t in tasks)),
        "official_snapshots": snapshots,
        "shadow_evaluations": len(evals),
        "would_change_count": sum(e["would_change"] for e in evals),
        "would_change_rate": (
            sum(e["would_change"] for e in evals) / len(evals) if evals else 0.0
        ),
        "capture_sessions": sessions,
        "superseded_sessions": superseded,
        "evidence_records": evidence,
        "official_mutations": 0,
        "user_notifications_sent": sum(t["user_notification_sent"] for t in tasks),
        "promotion_enabled": False
    }

def report_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# PHYLLOS — Engineering Guided Capture Shadow v0.1.1",
        "",
        f"- Modo: `{report['mode']}`",
        f"- Tarefas: {report['tasks_total']}",
        f"- Snapshots oficiais: {report['official_snapshots']}",
        f"- Sessões de captura: {report['capture_sessions']}",
        f"- Sessões supersedidas: {report['superseded_sessions']}",
        f"- Evidence de captura: {report['evidence_records']}",
        f"- Avaliações shadow: {report['shadow_evaluations']}",
        f"- Propostas que mudariam dimensões oficiais: {report['would_change_count']}",
        f"- Mutações oficiais: {report['official_mutations']}",
        f"- Notificações: {report['user_notifications_sent']}",
        f"- Promoção habilitada: {report['promotion_enabled']}",
        "",
        "Os registros incluídos são sintéticos. Nenhuma amostra física foi recebida.",
        ""
    ]
    return "\n".join(lines)
