#!/usr/bin/env python3
from __future__ import annotations
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from db import init_db
from capture_service import (
    add_capture_bytes, export_evidence_records, finalize_session,
    reconcile_artifacts, start_session
)
from task_service import ingest_baseline, list_tasks, resolve_task, shadow_report, report_markdown

SHOTS = [
    "face_overview", "reverse_overview", "macro_structure",
    "drape_fold", "backlight_transparency", "scale_reference"
]

def image_path(ops_id: str, index: int, shot: str) -> Path:
    return ROOT / "data" / "synthetic_pilot" / "source_images" / f"{ops_id}_{index:02d}_{shot}.png"

def capture_complete(db, artifacts, ops_id, supersedes=None):
    session = start_session(
        db, ops_id, "operator:synthetic-pilot",
        supersedes_session_id=supersedes,
        supersession_reason="synthetic supersession test" if supersedes else None,
        metadata={"synthetic": True, "physical_sample_received": False}
    )
    for idx, shot in enumerate(SHOTS, 1):
        add_capture_bytes(
            db, artifacts, session["session_id"], shot,
            image_path(ops_id, idx, shot).read_bytes(),
            "image/png", image_path(ops_id, idx, shot).name,
            {
                "focus_ok": True, "lighting_ok": True,
                "sample_fills_frame": True, "no_label_leak": True
            },
            "operator:synthetic-pilot"
        )
    return finalize_session(db, session["session_id"])

def main():
    db = ROOT / "runtime" / "synthetic_pilot.db"
    artifacts = ROOT / "runtime" / "artifacts"
    if db.exists():
        db.unlink()
    for suffix in ("-wal", "-shm"):
        p = Path(str(db) + suffix)
        if p.exists():
            p.unlink()
    if artifacts.exists():
        for p in artifacts.iterdir():
            if p.name != ".gitkeep":
                shutil.rmtree(p) if p.is_dir() else p.unlink()
    init_db(db)

    sessions = []
    for i in range(1, 6):
        sessions.append(capture_complete(db, artifacts, f"OPS-SYN-{i:03d}"))

    replacement = capture_complete(
        db, artifacts, "OPS-SYN-005",
        supersedes=sessions[-1]["session_id"]
    )
    sessions.append(replacement)

    ingest = ingest_baseline(
        db,
        ROOT / "data" / "synthetic_pilot" / "samples.csv",
        ROOT / "data" / "synthetic_pilot" / "rule_predictions.csv"
    )
    tasks = list_tasks(db, "open")
    if tasks:
        resolve_task(
            db, tasks[0]["task_id"], "corrected", "reviewer:synthetic",
            "Synthetic pipeline validation only.",
            proposed_decision={
                "structure_family": "woven_fabric",
                "construction_primary": "plain_weave",
                "visual_transparency": "opaque",
                "capture_quality": "adequate",
                "decision": "classify"
            }
        )

    evidence_export = export_evidence_records(
        db, ROOT / "outputs" / "synthetic_pilot_evidence.jsonl"
    )
    reconciliation = reconcile_artifacts(db, artifacts)
    report = shadow_report(db)
    report.update({
        "synthetic_record_count": 5,
        "physical_samples_received": 0,
        "gold_sample_count": 0,
        "empirical_metrics_allowed": False,
        "ingest": ingest,
        "artifact_reconciliation": reconciliation,
        "evidence_export": evidence_export
    })
    (ROOT / "reports" / "synthetic_pilot_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "reports" / "synthetic_pilot_report.md").write_text(
        report_markdown(report) + "\n"
        "## Estado\n\n"
        "- fixtures sintéticas: 5\n"
        "- amostras físicas: 0\n"
        "- conjunto ouro: 0\n"
        "- métricas empíricas permitidas: não\n"
        f"- reconciliação de arquivos saudável: {reconciliation['healthy']}\n",
        encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
