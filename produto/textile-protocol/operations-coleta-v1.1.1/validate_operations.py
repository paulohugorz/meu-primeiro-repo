#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

MAX_SUPPLIER_SHARE = 0.35

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def validate_intake(instance_path: Path, schema_path: Path) -> list[str]:
    instance = load_json(instance_path)
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        loc = ".".join(str(x) for x in err.path) or "<root>"
        errors.append(f"{loc}: {err.message}")

    # Semantic cross-reference checks for accepted records.
    decision = instance.get("dataset_intake_decision", {})
    if decision.get("outcome") == "accept":
        evidence_ids = {e.get("id") for e in instance.get("evidence", [])}
        assertion_ids = {a.get("id") for a in instance.get("assertions", [])}
        actor_ids = {a.get("id") for a in instance.get("actors", [])}

        for assertion in instance.get("assertions", []):
            missing = [
                eid for eid in assertion.get("supported_by_evidence_ids", [])
                if eid not in evidence_ids
            ]
            if missing:
                errors.append(
                    f"assertion {assertion.get('id')}: unknown evidence IDs {missing}"
                )

        reviewed_assertions = {
            r.get("assertion_id") for r in instance.get("reviews", [])
            if r.get("outcome") in {"accepted", "corrected"}
        }
        if not (assertion_ids & reviewed_assertions):
            errors.append(
                "accepted intake requires at least one accepted/corrected review "
                "for an existing assertion"
            )

        decider = decision.get("decided_by_actor_id")
        if decider not in actor_ids:
            errors.append(
                "dataset_intake_decision.decided_by_actor_id must reference an Actor"
            )
    return errors

def validate_registry(registry_path: Path) -> list[str]:
    records = load_json(registry_path)
    errors = []
    accepted = [
        r for r in records
        if r.get("intake_status") == "Aceita"
        or r.get("graph", {}).get("proposed_family_mapping", {}).get("mapping_status") == "accepted_gold"
    ]
    if not accepted:
        return errors

    counts = Counter(r.get("supplier") or "<missing>" for r in accepted)
    total = len(accepted)
    for supplier, count in counts.items():
        share = count / total
        if share > MAX_SUPPLIER_SHARE:
            errors.append(
                f"supplier concentration violation: {supplier} has "
                f"{count}/{total} accepted samples ({share:.1%}), "
                f"above {MAX_SUPPLIER_SHARE:.0%}"
            )
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("schemas/sample-intake-v1.1.1.schema.json"),
    )
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()

    errors = []
    if args.intake:
        errors.extend(validate_intake(args.intake, args.schema))
    if args.registry:
        errors.extend(validate_registry(args.registry))

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    return 0

if __name__ == "__main__":
    sys.exit(main())
