from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

from db import connect, transaction, utcnow

ID_COLUMNS = ("ops_id", "service_sample_id", "textile_sample_node_id")

def resolve_mapping(db_path: str | Path, sample_ref: str) -> Dict[str, Any]:
    if not isinstance(sample_ref, str) or not sample_ref.strip():
        raise ValueError("sample_ref is required")
    with connect(db_path) as conn:
        row = conn.execute(
            """SELECT * FROM sample_id_mappings
               WHERE ops_id=? OR service_sample_id=? OR textile_sample_node_id=?""",
            (sample_ref, sample_ref, sample_ref)
        ).fetchone()
    if not row:
        raise KeyError(f"sample identifier is not mapped: {sample_ref}")
    result = dict(row)
    result["physical_sample_received"] = bool(result["physical_sample_received"])
    result["capture_allowed"] = bool(result["capture_allowed"])
    return result

def list_mappings(db_path: str | Path, record_kind: str | None = None):
    with connect(db_path) as conn:
        if record_kind:
            rows = conn.execute(
                "SELECT * FROM sample_id_mappings WHERE record_kind=? ORDER BY ops_id",
                (record_kind,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM sample_id_mappings ORDER BY ops_id").fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["physical_sample_received"] = bool(item["physical_sample_received"])
        item["capture_allowed"] = bool(item["capture_allowed"])
        result.append(item)
    return result

def set_mapping_state(
    db_path: str | Path,
    sample_ref: str,
    operations_status: str,
    physical_sample_received: bool,
    capture_allowed: bool,
) -> Dict[str, Any]:
    mapping = resolve_mapping(db_path, sample_ref)
    if mapping["record_kind"] == "operations_candidate":
        if capture_allowed and not physical_sample_received:
            raise ValueError("real candidate capture cannot be enabled before physical receipt")
        if physical_sample_received and operations_status not in {
            "received_identified", "received_pending_document", "intake_review"
        }:
            raise ValueError("physical receipt requires a receipt-compatible operations_status")
    with transaction(db_path) as conn:
        conn.execute(
            """UPDATE sample_id_mappings
               SET operations_status=?,physical_sample_received=?,capture_allowed=?
               WHERE mapping_id=?""",
            (
                operations_status, 1 if physical_sample_received else 0,
                1 if capture_allowed else 0, mapping["mapping_id"]
            )
        )
    return resolve_mapping(db_path, sample_ref)
