#!/usr/bin/env python3
"""Regression tests for PHYLLOS environmental profile schema and semantic validation."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from validate_environmental_profile_v0_3 import validate_profile

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "environmental-json-schema-v0.3.json").read_text(encoding="utf-8"))


def base_profile() -> dict:
    return {
        "schema_version": "0.3",
        "sample_id": "OPS-TX-061",
        "article_id": "article:cedro:061",
        "supplier_product_code": "CEDRO-RIPSTOP-SUPER",
        "batch_or_lot": None,
        "methodology_version": "phyllos-env-method-v0.1",
        "calculability_status": "material_estimate_only",
        "calculability_review_status": "pending_human_review",
        "composition": {
            "status": "extracted_pending_review",
            "components": [
                {
                    "fiber_type": "cotton",
                    "fiber_percentage": 30,
                    "source_status": "text_extraction",
                    "evidence_id": None,
                },
                {
                    "fiber_type": "polyester",
                    "fiber_percentage": 70,
                    "source_status": "text_extraction",
                    "evidence_id": None,
                },
            ],
            "sum_percentage": 100,
            "review_status": "not_reviewed",
        },
        "physical_properties": {"gsm": 210, "evidence_ids": []},
        "supply_chain": [],
        "environmental_factors": [],
        "calculations": [],
        "evidence": [],
        "data_quality": {
            "quality_level": "E",
            "completeness_score": 36.9,
            "uncertainty": None,
            "limitations": ["Extração pendente de revisão humana"],
            "review_status": "not_reviewed",
            "review_id": None,
        },
    }


def add_factor_and_calculation(profile: dict) -> None:
    profile["environmental_factors"] = [
        {
            "factor_id": "factor:climate:cotton:global:v1",
            "impact_category": "climate_change",
            "factor_value": 2.5,
            "factor_unit": "kgCO2e/kg",
            "functional_unit": "1_kg_textile",
            "geographic_scope": "global",
            "technology_scope": None,
            "temporal_scope": "2020-2025",
            "source": "Test fixture",
            "source_version": "v1",
            "quality_level": "C",
            "uncertainty": None,
        }
    ]
    profile["calculations"] = [
        {
            "calculation_id": "calc:OPS-TX-061:climate:v1",
            "impact_category": "climate_change",
            "functional_unit": "1_kg_textile",
            "system_boundary": "raw_material_only",
            "result": 2.5,
            "result_unit": "kgCO2e/kg",
            "uncertainty_range": None,
            "factor_ids": ["factor:climate:cotton:global:v1"],
            "calculated_at": "2026-07-16T12:00:00Z",
            "review_id": None,
            "calculation_status": "experimental",
        }
    ]


def add_evidence(
    profile: dict,
    *,
    evidence_id: str = "evidence:supplier:061:v1",
    source_type: str = "supplier_primary_verified",
    authenticity: str = "verified",
    relevance: str = "sufficient",
) -> None:
    profile["evidence"].append(
        {
            "evidence_id": evidence_id,
            "source_type": source_type,
            "artifact_hash": "a" * 64,
            "authenticity": authenticity,
            "relevance": relevance,
            "url": "https://example.org/document.pdf",
            "document_date": "2026-07-01",
        }
    )


def secondary_profile() -> dict:
    profile = base_profile()
    profile["calculability_status"] = "secondary_estimate"
    profile["calculability_review_status"] = "approved"
    add_factor_and_calculation(profile)
    return profile


def supplier_specific_profile() -> dict:
    profile = secondary_profile()
    profile["calculability_status"] = "supplier_specific_estimate"
    add_evidence(profile)
    return profile


def verified_profile() -> dict:
    profile = supplier_specific_profile()
    profile["calculability_status"] = "verified_environmental_profile"
    profile["data_quality"].update(
        quality_level="A",
        completeness_score=92,
        review_status="accepted",
        review_id="review:env:061:v1",
    )
    return profile


class EnvironmentalProfileTests(unittest.TestCase):
    def assertValid(self, profile: dict) -> None:  # noqa: N802
        result = validate_profile(profile, SCHEMA)
        self.assertTrue(result["valid"], result)

    def assertInvalid(self, profile: dict, code: str | None = None) -> dict:  # noqa: N802
        result = validate_profile(profile, SCHEMA)
        self.assertFalse(result["valid"], result)
        if code:
            codes = {item["code"] for item in result["semantic_errors"]}
            self.assertIn(code, codes, result)
        return result

    def test_schema_is_valid_draft_2020_12(self) -> None:
        Draft202012Validator.check_schema(SCHEMA)

    def test_provisional_material_profile_is_valid_but_has_no_calculation(self) -> None:
        profile = base_profile()
        self.assertEqual(profile["calculability_review_status"], "pending_human_review")
        self.assertEqual(profile["calculations"], [])
        self.assertValid(profile)

    def test_missing_factor_reference_is_rejected(self) -> None:
        profile = secondary_profile()
        profile["calculations"][0]["factor_ids"] = ["factor:missing"]
        self.assertInvalid(profile, "dangling_factor_reference")

    def test_duplicate_factor_definitions_are_rejected(self) -> None:
        profile = secondary_profile()
        profile["environmental_factors"].append(copy.deepcopy(profile["environmental_factors"][0]))
        self.assertInvalid(profile, "duplicate_factor_id")

    def test_duplicate_factor_references_are_rejected(self) -> None:
        profile = secondary_profile()
        factor_id = profile["environmental_factors"][0]["factor_id"]
        profile["calculations"][0]["factor_ids"] = [factor_id, factor_id]
        self.assertInvalid(profile, "duplicate_factor_reference")

    def test_duplicate_evidence_ids_are_rejected(self) -> None:
        profile = supplier_specific_profile()
        profile["evidence"].append(copy.deepcopy(profile["evidence"][0]))
        self.assertInvalid(profile, "duplicate_evidence_id")

    def test_supplier_specific_requires_evidence(self) -> None:
        profile = supplier_specific_profile()
        profile["evidence"] = []
        self.assertInvalid(profile)

    def test_supplier_specific_rejects_non_specific_evidence(self) -> None:
        profile = supplier_specific_profile()
        profile["evidence"][0]["source_type"] = "industry_average"
        self.assertInvalid(profile)

    def test_supplier_specific_accepts_allowed_primary_evidence(self) -> None:
        for source_type in (
            "supplier_primary_verified",
            "supplier_primary_unverified",
            "laboratory_test",
            "certification_document",
        ):
            with self.subTest(source_type=source_type):
                profile = secondary_profile()
                profile["calculability_status"] = "supplier_specific_estimate"
                add_evidence(profile, source_type=source_type)
                self.assertValid(profile)

    def test_verified_profile_requires_verified_authenticity(self) -> None:
        profile = verified_profile()
        profile["evidence"][0]["authenticity"] = "unverified"
        self.assertInvalid(profile)

    def test_verified_profile_requires_sufficient_relevance(self) -> None:
        profile = verified_profile()
        profile["evidence"][0]["relevance"] = "limited"
        self.assertInvalid(profile)

    def test_verified_profile_requires_high_quality_and_completed_review(self) -> None:
        cases = [
            ("quality_level", "C"),
            ("review_status", "not_reviewed"),
            ("review_id", None),
        ]
        for field, value in cases:
            with self.subTest(field=field):
                profile = verified_profile()
                profile["data_quality"][field] = value
                self.assertInvalid(profile)

    def test_verified_profile_valid_fixture(self) -> None:
        self.assertValid(verified_profile())

    def test_all_calculability_review_statuses_have_explicit_coverage(self) -> None:
        cases = {
            "not_applicable": lambda: {**base_profile(), "calculability_status": "not_calculable", "calculability_review_status": "not_applicable"},
            "pending_human_review": lambda: base_profile(),
            "reviewed": lambda: {**base_profile(), "calculability_review_status": "reviewed"},
            "approved": secondary_profile,
            "rejected": lambda: {**base_profile(), "calculability_review_status": "rejected"},
        }
        for status, factory in cases.items():
            with self.subTest(status=status):
                profile = factory()
                self.assertEqual(profile["calculability_review_status"], status)
                self.assertValid(profile)

    def test_calculated_statuses_require_approved_review(self) -> None:
        for status in ("not_applicable", "pending_human_review", "reviewed", "rejected"):
            with self.subTest(status=status):
                profile = secondary_profile()
                profile["calculability_review_status"] = status
                self.assertInvalid(profile)

    def test_calculations_are_blocked_for_non_approved_gate_states(self) -> None:
        for status in ("not_applicable", "pending_human_review", "rejected"):
            with self.subTest(status=status):
                profile = base_profile()
                profile["calculability_status"] = "not_calculable" if status == "not_applicable" else "material_estimate_only"
                profile["calculability_review_status"] = status
                add_factor_and_calculation(profile)
                self.assertInvalid(profile)


if __name__ == "__main__":
    unittest.main(verbosity=2)
