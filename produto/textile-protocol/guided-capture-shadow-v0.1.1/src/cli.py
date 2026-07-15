#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

from db import init_db
from id_service import list_mappings, resolve_mapping, set_mapping_state
from capture_service import (
    add_capture_bytes, export_baseline_capture_row, export_evidence_records,
    finalize_session, get_session, reconcile_artifacts, start_session
)
from task_service import (
    compare_shadow_decision, ingest_baseline, list_tasks, report_markdown,
    resolve_task, shadow_report
)

ROOT = Path(__file__).resolve().parents[1]

def print_json(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=str(ROOT / "runtime" / "phyllos_shadow.db"))
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init-db")

    s = sub.add_parser("resolve-id")
    s.add_argument("--sample-ref", required=True)

    s = sub.add_parser("list-id-mappings")
    s.add_argument("--record-kind")

    s = sub.add_parser("set-mapping-state")
    s.add_argument("--sample-ref", required=True)
    s.add_argument("--operations-status", required=True)
    s.add_argument("--physical-sample-received", action="store_true")
    s.add_argument("--capture-allowed", action="store_true")

    s = sub.add_parser("start-session")
    s.add_argument("--sample-ref", required=True)
    s.add_argument("--operator-id", required=True)
    s.add_argument("--device-id")
    s.add_argument("--supersedes-session-id")
    s.add_argument("--supersession-reason")

    s = sub.add_parser("add-file")
    s.add_argument("--session-id", required=True)
    s.add_argument("--shot-type", required=True)
    s.add_argument("--file", required=True)
    s.add_argument("--mime-type", required=True)
    s.add_argument("--quality-confirmed-by-actor-id", required=True)
    s.add_argument("--focus-ok", action="store_true")
    s.add_argument("--lighting-ok", action="store_true")
    s.add_argument("--sample-fills-frame", action="store_true")
    s.add_argument("--no-label-leak", action="store_true")
    s.add_argument("--artifacts-root", default=str(ROOT / "runtime" / "artifacts"))

    s = sub.add_parser("finalize-session")
    s.add_argument("--session-id", required=True)

    s = sub.add_parser("show-session")
    s.add_argument("--session-id", required=True)

    s = sub.add_parser("export-baseline")
    s.add_argument("--session-id", required=True)
    s.add_argument("--output", required=True)

    s = sub.add_parser("export-evidence")
    s.add_argument("--output", required=True)

    s = sub.add_parser("reconcile-artifacts")
    s.add_argument("--artifacts-root", default=str(ROOT / "runtime" / "artifacts"))
    s.add_argument("--delete-orphans", action="store_true")

    s = sub.add_parser("ingest-baseline")
    s.add_argument("--samples", required=True)
    s.add_argument("--predictions", required=True)

    s = sub.add_parser("list-tasks")
    s.add_argument("--status")

    s = sub.add_parser("resolve-task")
    s.add_argument("--task-id", required=True)
    s.add_argument("--outcome", required=True)
    s.add_argument("--actor-id", required=True)
    s.add_argument("--notes", default="")
    s.add_argument("--proposed-decision-json")

    s = sub.add_parser("compare-shadow")
    s.add_argument("--task-id", required=True)
    s.add_argument("--proposed-decision-json", required=True)

    s = sub.add_parser("shadow-report")
    s.add_argument("--json-output")
    s.add_argument("--markdown-output")

    s = sub.add_parser("serve")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8765)
    s.add_argument("--artifacts-root", default=str(ROOT / "runtime" / "artifacts"))

    args = p.parse_args()
    init_db(args.db)

    if args.command == "init-db":
        print_json({"status": "ok", "db": args.db})
    elif args.command == "resolve-id":
        print_json(resolve_mapping(args.db, args.sample_ref))
    elif args.command == "list-id-mappings":
        print_json(list_mappings(args.db, args.record_kind))
    elif args.command == "set-mapping-state":
        print_json(set_mapping_state(
            args.db, args.sample_ref, args.operations_status,
            args.physical_sample_received, args.capture_allowed
        ))
    elif args.command == "start-session":
        print_json(start_session(
            args.db, args.sample_ref, args.operator_id, args.device_id,
            supersedes_session_id=args.supersedes_session_id,
            supersession_reason=args.supersession_reason
        ))
    elif args.command == "add-file":
        path = Path(args.file)
        print_json(add_capture_bytes(
            args.db, args.artifacts_root, args.session_id, args.shot_type,
            path.read_bytes(), args.mime_type, path.name,
            {
                "focus_ok": args.focus_ok,
                "lighting_ok": args.lighting_ok,
                "sample_fills_frame": args.sample_fills_frame,
                "no_label_leak": args.no_label_leak,
            },
            args.quality_confirmed_by_actor_id
        ))
    elif args.command == "finalize-session":
        print_json(finalize_session(args.db, args.session_id))
    elif args.command == "show-session":
        print_json(get_session(args.db, args.session_id))
    elif args.command == "export-baseline":
        row = export_baseline_capture_row(args.db, args.session_id)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)
        print_json({"status": "ok", "output": str(output)})
    elif args.command == "export-evidence":
        print_json(export_evidence_records(args.db, args.output))
    elif args.command == "reconcile-artifacts":
        print_json(reconcile_artifacts(
            args.db, args.artifacts_root, args.delete_orphans
        ))
    elif args.command == "ingest-baseline":
        print_json(ingest_baseline(args.db, args.samples, args.predictions))
    elif args.command == "list-tasks":
        print_json(list_tasks(args.db, args.status))
    elif args.command == "resolve-task":
        proposed = json.loads(args.proposed_decision_json) if args.proposed_decision_json else None
        print_json(resolve_task(
            args.db, args.task_id, args.outcome, args.actor_id,
            args.notes, proposed_decision=proposed
        ))
    elif args.command == "compare-shadow":
        print_json(compare_shadow_decision(
            args.db, args.task_id, json.loads(args.proposed_decision_json)
        ))
    elif args.command == "shadow-report":
        report = shadow_report(args.db)
        if args.json_output:
            Path(args.json_output).write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        if args.markdown_output:
            Path(args.markdown_output).write_text(report_markdown(report), encoding="utf-8")
        print_json(report)
    elif args.command == "serve":
        from server import run
        run(args.db, args.artifacts_root, args.host, args.port)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
