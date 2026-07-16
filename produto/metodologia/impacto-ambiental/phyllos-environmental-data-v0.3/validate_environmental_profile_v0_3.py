#!/usr/bin/env python3
"""Validate a PHYLLOS environmental profile with JSON Schema and semantic rules."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ModuleNotFoundError as exc:  # pragma: no cover - exercised before installation
    raise SystemExit(
        "Dependência ausente: jsonschema. Execute: python -m pip install -r requirements.txt"
    ) from exc


def _duplicate_values(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def validate_semantic_references(profile: dict[str, Any]) -> list[dict[str, str]]:
    """Validate identity uniqueness and references between arrays in one profile."""
    errors: list[dict[str, str]] = []

    evidence_ids = [
        item.get("evidence_id")
        for item in profile.get("evidence", [])
        if isinstance(item, dict) and item.get("evidence_id")
    ]
    factor_ids = [
        item.get("factor_id")
        for item in profile.get("environmental_factors", [])
        if isinstance(item, dict) and item.get("factor_id")
    ]
    evidence_set = set(evidence_ids)
    factor_set = set(factor_ids)

    for duplicate in _duplicate_values(evidence_ids):
        errors.append({"code": "duplicate_evidence_id", "path": "evidence", "reference": duplicate})
    for duplicate in _duplicate_values(factor_ids):
        errors.append({
            "code": "duplicate_factor_id",
            "path": "environmental_factors",
            "reference": duplicate,
        })

    evidence_refs: list[tuple[str, str]] = []
    for index, component in enumerate(profile.get("composition", {}).get("components", [])):
        ref = component.get("evidence_id") if isinstance(component, dict) else None
        if ref:
            evidence_refs.append((f"composition.components[{index}].evidence_id", ref))

    for index, ref in enumerate(profile.get("physical_properties", {}).get("evidence_ids", [])):
        if ref:
            evidence_refs.append((f"physical_properties.evidence_ids[{index}]", ref))

    for stage_index, stage in enumerate(profile.get("supply_chain", [])):
        if not isinstance(stage, dict):
            continue
        for ref_index, ref in enumerate(stage.get("evidence_ids", [])):
            if ref:
                evidence_refs.append((f"supply_chain[{stage_index}].evidence_ids[{ref_index}]", ref))

    for path, ref in evidence_refs:
        if ref not in evidence_set:
            errors.append({"code": "dangling_evidence_reference", "path": path, "reference": ref})

    for calc_index, calculation in enumerate(profile.get("calculations", [])):
        if not isinstance(calculation, dict):
            continue
        refs = [ref for ref in calculation.get("factor_ids", []) if ref]
        for duplicate in _duplicate_values(refs):
            errors.append({
                "code": "duplicate_factor_reference",
                "path": f"calculations[{calc_index}].factor_ids",
                "reference": duplicate,
            })
        for factor_index, ref in enumerate(refs):
            if ref not in factor_set:
                errors.append({
                    "code": "dangling_factor_reference",
                    "path": f"calculations[{calc_index}].factor_ids[{factor_index}]",
                    "reference": ref,
                })

    return errors


def validate_profile(profile: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Return a structured validation report instead of raising on invalid data."""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_errors = []
    for error in sorted(validator.iter_errors(profile), key=lambda item: list(item.absolute_path)):
        schema_errors.append({
            "code": "json_schema_error",
            "path": ".".join(str(part) for part in error.absolute_path) or "$",
            "message": error.message,
        })

    semantic_errors = validate_semantic_references(profile)
    return {
        "valid": not schema_errors and not semantic_errors,
        "schema_errors": schema_errors,
        "semantic_errors": semantic_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).with_name("environmental-json-schema-v0.3.json"),
    )
    args = parser.parse_args()

    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    result = validate_profile(profile, schema)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
