from __future__ import annotations
import base64
import hashlib
import io
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image, UnidentifiedImageError

from db import ROOT, connect, transaction, utcnow
from id_service import resolve_mapping

PROTOCOL_PATH = ROOT / "config" / "capture_protocol_v0.1.1.json"
OPERATIONS_STATE_PATH = ROOT / "config" / "operations_state_v1.1.1.json"
FORMAT_TO_MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
MIME_TO_EXTENSION = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

def load_protocol() -> Dict[str, Any]:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))

def load_operations_state() -> Dict[str, Any]:
    return json.loads(OPERATIONS_STATE_PATH.read_text(encoding="utf-8"))

def _id(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"

def _bool(value: Any) -> int:
    return 1 if bool(value) else 0

def _step_map() -> Dict[str, Dict[str, Any]]:
    return {s["shot_type"]: s for s in load_protocol()["steps"]}

def validate_image_bytes(data: bytes, claimed_mime_type: str) -> Dict[str, Any]:
    protocol = load_protocol()
    limits = protocol["image_validation"]
    if not data:
        raise ValueError("empty file")
    if len(data) > protocol["max_file_bytes"]:
        raise ValueError("file exceeds max_file_bytes")
    try:
        with Image.open(io.BytesIO(data)) as image:
            detected_format = image.format
            width, height = image.size
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            width, height = image.size
            detected_format = image.format
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("image signature or decoding is invalid") from exc

    actual_mime_type = FORMAT_TO_MIME.get(detected_format or "")
    if actual_mime_type not in protocol["allowed_mime_types"]:
        raise ValueError(f"unsupported detected image format: {detected_format}")
    if limits["claimed_mime_must_match_actual"] and claimed_mime_type != actual_mime_type:
        raise ValueError(
            f"claimed MIME {claimed_mime_type} does not match detected {actual_mime_type}"
        )
    if width < limits["min_width_px"] or height < limits["min_height_px"]:
        raise ValueError(
            f"image dimensions {width}x{height} are below minimum "
            f"{limits['min_width_px']}x{limits['min_height_px']}"
        )
    if width > limits["max_width_px"] or height > limits["max_height_px"]:
        raise ValueError("image dimensions exceed maximum")
    if width * height > limits["max_pixels"]:
        raise ValueError("image pixel count exceeds maximum")
    return {
        "actual_mime_type": actual_mime_type,
        "image_format": detected_format,
        "width_px": width,
        "height_px": height,
        "extension": MIME_TO_EXTENSION[actual_mime_type]
    }

def start_session(
    db_path: str | Path,
    sample_ref: str,
    operator_id: str,
    device_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
    supersedes_session_id: str | None = None,
    supersession_reason: str | None = None,
) -> Dict[str, Any]:
    if not operator_id or not operator_id.strip():
        raise ValueError("operator_id is required")
    mapping = resolve_mapping(db_path, sample_ref)
    operations_state = load_operations_state()
    if (
        mapping["record_kind"] == "operations_candidate"
        and not operations_state.get("field_test_enabled", False)
    ):
        raise ValueError("field test is globally disabled for operations candidates")
    if not mapping["capture_allowed"]:
        raise ValueError(
            f"capture is blocked for {mapping['ops_id']}: "
            f"operations_status={mapping['operations_status']}"
        )
    session_id = _id("capture-session")
    with transaction(db_path) as conn:
        if supersedes_session_id:
            previous = conn.execute(
                "SELECT * FROM capture_sessions WHERE session_id=?",
                (supersedes_session_id,)
            ).fetchone()
            if not previous:
                raise KeyError("superseded session not found")
            if previous["status"] != "complete":
                raise ValueError("only a complete session can be superseded")
            if previous["mapping_id"] != mapping["mapping_id"]:
                raise ValueError("superseded session belongs to a different sample")
            if previous["superseded_by_session_id"]:
                raise ValueError("session has already been superseded")
            if not supersession_reason or not supersession_reason.strip():
                raise ValueError("supersession_reason is required")
        conn.execute(
            """INSERT INTO capture_sessions(
                session_id,mapping_id,ops_id,service_sample_id,textile_sample_node_id,
                protocol_version,status,operator_id,device_id,created_at,
                supersedes_session_id,supersession_reason,metadata_json
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                session_id, mapping["mapping_id"], mapping["ops_id"],
                mapping["service_sample_id"], mapping["textile_sample_node_id"],
                "0.1.1", "draft", operator_id, device_id, utcnow(),
                supersedes_session_id, supersession_reason,
                json.dumps(metadata or {}, ensure_ascii=False)
            )
        )
    return get_session(db_path, session_id)

def add_capture_bytes(
    db_path: str | Path,
    artifacts_root: str | Path,
    session_id: str,
    shot_type: str,
    data: bytes,
    claimed_mime_type: str,
    file_name: str,
    quality: Dict[str, bool],
    quality_confirmed_by_actor_id: str,
) -> Dict[str, Any]:
    protocol = load_protocol()
    steps = _step_map()
    if shot_type not in steps:
        raise ValueError(f"unknown shot_type: {shot_type}")
    if claimed_mime_type not in protocol["allowed_mime_types"]:
        raise ValueError(f"unsupported claimed MIME: {claimed_mime_type}")
    if not quality_confirmed_by_actor_id or not quality_confirmed_by_actor_id.strip():
        raise ValueError("quality_confirmed_by_actor_id is required")

    required_quality = ["focus_ok", "lighting_ok", "sample_fills_frame", "no_label_leak"]
    missing = [k for k in required_quality if k not in quality]
    if missing:
        raise ValueError(f"missing quality fields: {missing}")
    if any(type(quality[k]) is not bool for k in required_quality):
        raise ValueError("quality fields must be booleans")

    image_info = validate_image_bytes(data, claimed_mime_type)
    gates = steps[shot_type]["quality_gates"]
    accepted = all(bool(quality[g]) for g in gates)
    rejection_reasons = [g for g in gates if not bool(quality[g])]
    digest = hashlib.sha256(data).hexdigest()
    item_id = _id("capture-item")
    evidence_id = f"evidence:capture:{item_id.split(':')[-1]}"
    artifacts_root = Path(artifacts_root)
    session_dir = artifacts_root / session_id.replace(":", "_")
    session_dir.mkdir(parents=True, exist_ok=True)

    temp_path = None
    final_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=session_dir, prefix=".upload-", suffix=".tmp", delete=False
        ) as temp:
            temp.write(data)
            temp.flush()
            os.fsync(temp.fileno())
            temp_path = Path(temp.name)

        with transaction(db_path) as conn:
            session = conn.execute(
                """SELECT s.*,m.record_kind
                   FROM capture_sessions s
                   JOIN sample_id_mappings m ON m.mapping_id=s.mapping_id
                   WHERE s.session_id=?""",
                (session_id,)
            ).fetchone()
            if not session:
                raise KeyError("capture session not found")
            if session["status"] in {"complete", "superseded", "cancelled"}:
                raise ValueError("capture session is closed")

            current_bytes = conn.execute(
                "SELECT COALESCE(SUM(bytes_size),0) FROM capture_items WHERE session_id=?",
                (session_id,)
            ).fetchone()[0]
            if current_bytes + len(data) > protocol["max_session_bytes"]:
                raise ValueError("session accumulated byte limit exceeded")

            sequence_no = conn.execute(
                "SELECT COALESCE(MAX(sequence_no),0)+1 FROM capture_items WHERE session_id=?",
                (session_id,)
            ).fetchone()[0]
            final_path = session_dir / (
                f"{sequence_no:03d}_{shot_type}_{item_id.split(':')[-1]}"
                f"{image_info['extension']}"
            )
            os.replace(temp_path, final_path)
            temp_path = None
            confirmed_at = utcnow()
            conn.execute(
                """INSERT INTO capture_items(
                    item_id,session_id,shot_type,sequence_no,artifact_path,sha256,
                    claimed_mime_type,actual_mime_type,image_format,width_px,height_px,
                    bytes_size,captured_at,focus_ok,lighting_ok,sample_fills_frame,
                    no_label_leak,quality_confirmed_by_actor_id,quality_confirmed_at,
                    accepted,rejection_reasons_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    item_id, session_id, shot_type, sequence_no, str(final_path), digest,
                    claimed_mime_type, image_info["actual_mime_type"],
                    image_info["image_format"], image_info["width_px"],
                    image_info["height_px"], len(data), confirmed_at,
                    _bool(quality["focus_ok"]), _bool(quality["lighting_ok"]),
                    _bool(quality["sample_fills_frame"]), _bool(quality["no_label_leak"]),
                    quality_confirmed_by_actor_id, confirmed_at, _bool(accepted),
                    json.dumps(rejection_reasons, ensure_ascii=False)
                )
            )
            conn.execute(
                """INSERT INTO evidence_records(
                    evidence_id,mapping_id,ops_id,service_sample_id,textile_sample_node_id,
                    capture_session_id,capture_item_id,evidence_type,artifact_path,
                    artifact_hash_sha256,artifact_integrity,source_authenticity,
                    evidentiary_relevance,review_status,record_kind,
                    created_by_actor_id,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    evidence_id, session["mapping_id"], session["ops_id"],
                    session["service_sample_id"], session["textile_sample_node_id"],
                    session_id, item_id, "photograph", str(final_path), digest,
                    "sha256_recorded", "unreviewed", "unreviewed",
                    "captured_unreviewed_shadow", session["record_kind"],
                    quality_confirmed_by_actor_id, confirmed_at
                )
            )
            conn.execute(
                "UPDATE capture_sessions SET status='in_progress' WHERE session_id=?",
                (session_id,)
            )
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        if final_path and final_path.exists():
            final_path.unlink()
        raise

    return get_capture_item(db_path, item_id)

def add_capture_base64(
    db_path: str | Path,
    artifacts_root: str | Path,
    session_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    try:
        data = base64.b64decode(payload["data_base64"], validate=True)
    except Exception as exc:
        raise ValueError("invalid base64 payload") from exc
    return add_capture_bytes(
        db_path=db_path,
        artifacts_root=artifacts_root,
        session_id=session_id,
        shot_type=payload["shot_type"],
        data=data,
        claimed_mime_type=payload["mime_type"],
        file_name=payload.get("file_name", "capture.bin"),
        quality=payload["quality"],
        quality_confirmed_by_actor_id=payload["quality_confirmed_by_actor_id"],
    )

def get_capture_item(db_path: str | Path, item_id: str) -> Dict[str, Any]:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM capture_items WHERE item_id=?", (item_id,)).fetchone()
        evidence = conn.execute(
            "SELECT * FROM evidence_records WHERE capture_item_id=?", (item_id,)
        ).fetchone()
    if not row:
        raise KeyError("capture item not found")
    result = dict(row)
    result["accepted"] = bool(result["accepted"])
    result["quality"] = {
        "focus_ok": bool(result.pop("focus_ok")),
        "lighting_ok": bool(result.pop("lighting_ok")),
        "sample_fills_frame": bool(result.pop("sample_fills_frame")),
        "no_label_leak": bool(result.pop("no_label_leak")),
        "confirmed_by_actor_id": result.pop("quality_confirmed_by_actor_id"),
        "confirmed_at": result.pop("quality_confirmed_at")
    }
    result["rejection_reasons"] = json.loads(result.pop("rejection_reasons_json"))
    result["evidence"] = dict(evidence) if evidence else None
    return result

def remove_capture_item(
    db_path: str | Path, session_id: str, item_id: str
) -> Dict[str, Any]:
    artifact_path = None
    with transaction(db_path) as conn:
        session = conn.execute(
            "SELECT status FROM capture_sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        if not session:
            raise KeyError("capture session not found")
        if session["status"] in {"complete", "superseded", "cancelled"}:
            raise ValueError("confirmed capture session cannot be edited")
        item = conn.execute(
            "SELECT artifact_path FROM capture_items WHERE item_id=? AND session_id=?",
            (item_id, session_id)
        ).fetchone()
        if not item:
            raise KeyError("capture item not found")
        artifact_path = Path(item["artifact_path"])
        conn.execute("DELETE FROM evidence_records WHERE capture_item_id=?", (item_id,))
        conn.execute("DELETE FROM capture_items WHERE item_id=?", (item_id,))
    if artifact_path and artifact_path.exists():
        artifact_path.unlink()
    return {"removed": True, "capture_item_id": item_id, "session_id": session_id}

def completion_status(db_path: str | Path, session_id: str) -> Dict[str, Any]:
    protocol = load_protocol()
    required = [s["shot_type"] for s in protocol["steps"] if s["required"]]
    with connect(db_path) as conn:
        rows = conn.execute(
            """SELECT shot_type, COUNT(*) AS n
               FROM capture_items
               WHERE session_id=? AND accepted=1
               GROUP BY shot_type""",
            (session_id,)
        ).fetchall()
    accepted = {r["shot_type"]: r["n"] for r in rows}
    missing = [shot for shot in required if accepted.get(shot, 0) < 1]
    return {
        "required_shot_types": required,
        "accepted_shot_types": sorted(accepted),
        "missing_shot_types": missing,
        "complete": not missing
    }

def get_session(db_path: str | Path, session_id: str) -> Dict[str, Any]:
    with connect(db_path) as conn:
        session = conn.execute(
            "SELECT * FROM capture_sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        if not session:
            raise KeyError("capture session not found")
        items = conn.execute(
            "SELECT item_id FROM capture_items WHERE session_id=? ORDER BY sequence_no",
            (session_id,)
        ).fetchall()
    result = dict(session)
    result["ready_for_baseline"] = bool(result["ready_for_baseline"])
    result["metadata"] = json.loads(result.pop("metadata_json"))
    result["items"] = [get_capture_item(db_path, r["item_id"]) for r in items]
    result["completion"] = completion_status(db_path, session_id)
    return result

def _apply_supersession(conn, new_session) -> None:
    previous_id = new_session["supersedes_session_id"]
    if not previous_id:
        return
    previous = conn.execute(
        "SELECT * FROM capture_sessions WHERE session_id=?", (previous_id,)
    ).fetchone()
    if not previous or previous["status"] != "complete":
        raise ValueError("superseded session is no longer eligible")
    old_evidence = conn.execute(
        """SELECT e.evidence_id,i.shot_type
           FROM evidence_records e
           JOIN capture_items i ON i.item_id=e.capture_item_id
           WHERE e.capture_session_id=?""",
        (previous_id,)
    ).fetchall()
    new_evidence = conn.execute(
        """SELECT e.evidence_id,i.shot_type
           FROM evidence_records e
           JOIN capture_items i ON i.item_id=e.capture_item_id
           WHERE e.capture_session_id=?""",
        (new_session["session_id"],)
    ).fetchall()
    old_by_shot = {r["shot_type"]: r["evidence_id"] for r in old_evidence}
    new_by_shot = {r["shot_type"]: r["evidence_id"] for r in new_evidence}
    for shot_type, new_id in new_by_shot.items():
        old_id = old_by_shot.get(shot_type)
        if old_id:
            conn.execute(
                "UPDATE evidence_records SET supersedes_evidence_id=? WHERE evidence_id=?",
                (old_id, new_id)
            )
            conn.execute(
                """UPDATE evidence_records
                   SET review_status='superseded_capture',
                       superseded_by_evidence_id=?
                   WHERE evidence_id=?""",
                (new_id, old_id)
            )
    conn.execute(
        """UPDATE capture_sessions
           SET status='superseded',ready_for_baseline=0,superseded_by_session_id=?
           WHERE session_id=?""",
        (new_session["session_id"], previous_id)
    )

def finalize_session(db_path: str | Path, session_id: str) -> Dict[str, Any]:
    status = completion_status(db_path, session_id)
    with transaction(db_path) as conn:
        session = conn.execute(
            "SELECT * FROM capture_sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        if not session:
            raise KeyError("capture session not found")
        if session["status"] in {"complete", "superseded", "cancelled"}:
            raise ValueError("capture session is already closed")
        if status["complete"]:
            _apply_supersession(conn, session)
            conn.execute(
                """UPDATE capture_sessions
                   SET status='complete',ready_for_baseline=1,completed_at=?
                   WHERE session_id=?""",
                (utcnow(), session_id)
            )
        else:
            conn.execute(
                """UPDATE capture_sessions
                   SET status='quality_review',ready_for_baseline=0
                   WHERE session_id=?""",
                (session_id,)
            )
    return get_session(db_path, session_id)

def export_baseline_capture_row(db_path: str | Path, session_id: str) -> Dict[str, str]:
    session = get_session(db_path, session_id)
    if session["status"] != "complete" or not session["ready_for_baseline"]:
        raise ValueError("session is not the active complete baseline session")
    items = [x for x in session["items"] if x["accepted"]]
    focus_ok = all(x["quality"]["focus_ok"] for x in items)
    shot_types = {x["shot_type"] for x in items}
    return {
        "sample_id": session["service_sample_id"],
        "image_count": str(len(items)),
        "has_macro": "yes" if "macro_structure" in shot_types else "no",
        "has_backlight": "yes" if "backlight_transparency" in shot_types else "no",
        "focus_ok": "yes" if focus_ok else "no",
        "warp_weft_visible": "unknown",
        "loop_structure_visible": "unknown",
        "knit_direction": "indeterminate",
        "web_structure_visible": "unknown",
        "braided_visible": "unknown",
        "stitch_bonded_visible": "unknown",
        "composite_layers_visible": "unknown",
        "diagonal_ribs_visible": "unknown",
        "long_floats_visible": "unknown",
        "regular_over_under_visible": "unknown",
        "transparency_observation": "indeterminate",
        "document_available": "no",
        "document_structure_family": "",
        "document_construction": "",
        "notes": (
            f"capture_session={session_id}; ops_id={session['ops_id']}; "
            f"textile_sample_node_id={session['textile_sample_node_id']}; "
            "structural observations pending; synthetic fixtures excluded from empirical metrics"
        )
    }

def export_evidence_records(db_path: str | Path, output_path: str | Path) -> Dict[str, Any]:
    with connect(db_path) as conn:
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM evidence_records ORDER BY created_at,evidence_id"
        ).fetchall()]
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".jsonl":
        output.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8"
        )
    else:
        if rows:
            with output.open("w", encoding="utf-8", newline="") as f:
                writer = __import__("csv").DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        else:
            output.write_text("", encoding="utf-8")
    return {"output": str(output), "records": len(rows)}

def reconcile_artifacts(
    db_path: str | Path,
    artifacts_root: str | Path,
    delete_orphans: bool = False
) -> Dict[str, Any]:
    artifacts_root = Path(artifacts_root)
    artifacts_root.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT item_id,artifact_path FROM capture_items"
        ).fetchall()
    referenced = {Path(r["artifact_path"]).resolve(): r["item_id"] for r in rows}
    missing = [
        {"item_id": item_id, "artifact_path": str(path)}
        for path, item_id in referenced.items() if not path.exists()
    ]
    filesystem_files = {
        p.resolve() for p in artifacts_root.rglob("*")
        if p.is_file() and p.name != ".gitkeep" and not p.name.startswith(".upload-")
    }
    orphans = sorted(filesystem_files - set(referenced))
    deleted = []
    if delete_orphans:
        for path in orphans:
            path.unlink()
            deleted.append(str(path))
    stale_temps = sorted(
        p.resolve() for p in artifacts_root.rglob(".upload-*") if p.is_file()
    )
    if delete_orphans:
        for path in stale_temps:
            path.unlink()
            deleted.append(str(path))
    return {
        "referenced_files": len(referenced),
        "filesystem_files": len(filesystem_files),
        "missing_files": missing,
        "orphan_files": [str(p) for p in orphans],
        "stale_temp_files": [str(p) for p in stale_temps],
        "deleted_files": deleted,
        "healthy": not missing and not orphans and not stale_temps
    }
