import os, unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.impact_v2 import DataOrigin, ImpactObservationIn, ReviewTask
from app.services.impact_v2 import calculate_impact_v2
from app.services.iscm import calcular_iscm

def observation(indicator, origin=DataOrigin.MEASURED, value=1.0, evidence=True):
    now = datetime.now(timezone.utc)
    return ImpactObservationIn(
        observation_id=f"obs:{indicator}", indicator_id=indicator, piece_id="piece:1", lot_id="lot:1",
        supplier_id="supplier:1", facility_id="facility:1", production_stage="production",
        period_start=now, period_end=now, value=value, unit="kg", origin=origin,
        method_id="method:v2", evidence_ids=[f"ev:{indicator}"] if evidence else [],
    )

class ImpactV2Tests(unittest.TestCase):
    def test_empty_is_indeterminate_and_never_scores(self):
        result = calculate_impact_v2([])
        self.assertEqual(result.status, "indeterminate")
        self.assertIsNone(result.global_score)
        self.assertTrue(all(item.score is None for item in result.dimensions))

    def test_missing_required_indicator_is_not_neutral_or_positive(self):
        result = calculate_impact_v2([observation("ghg_emissions")])
        climate = result.dimensions[0]
        self.assertEqual(climate.status, "partial")
        self.assertIsNone(climate.score)
        self.assertIn("energy_use", climate.missing_indicators)

    def test_conflict_makes_dimension_indeterminate(self):
        item = observation("ghg_emissions")
        item.origin = DataOrigin.CONFLICTING
        item.value = None
        result = calculate_impact_v2([item])
        self.assertEqual(result.dimensions[0].status, "indeterminate")
        self.assertGreater(result.evidence_confidence.conflicts, 0)

    def test_not_applicable_needs_rule_and_does_not_complete_dimension(self):
        now=datetime.now(timezone.utc)
        na=ImpactObservationIn(observation_id="na",indicator_id="energy_use",piece_id="piece:1",lot_id="lot:1",
            supplier_id="supplier:1",facility_id="facility:1",production_stage="production",
            period_start=now,period_end=now,origin=DataOrigin.NOT_APPLICABLE,method_id="method:v2",
            not_applicable_justification="processo manual sem energia adquirida",not_applicable_rule_id="rule:energy-na:v1")
        result=calculate_impact_v2([observation("ghg_emissions"),na])
        self.assertEqual(result.dimensions[0].status,"partial")
        self.assertIsNone(result.dimensions[0].score)

    def test_feature_flag_is_deny_by_default(self):
        os.environ.pop("PI5_V2_ENABLED", None)
        with TestClient(app) as client:
            response = client.post("/api/v2/impact/evaluate", json={})
        self.assertEqual(response.status_code, 404)

    def test_feature_flag_enables_additive_endpoint(self):
        os.environ["PI5_V2_ENABLED"] = "true"
        try:
            with TestClient(app) as client:
                response = client.post("/api/v2/impact/evaluate", json={})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "indeterminate")
        finally:
            os.environ.pop("PI5_V2_ENABLED", None)

    def test_legacy_iscm_missing_data_has_no_positive_points(self):
        peca=SimpleNamespace(codigo="EMPTY",ficha_tecnica=None,materiais=[],id=1)
        db=MagicMock(); db.query.return_value.filter.return_value.all.return_value=[]
        result=calcular_iscm(peca,db)
        self.assertEqual(result.score_total,0)
        self.assertTrue(all(item.pontos == 0 for item in result.dimensoes.values()))

    def test_all_required_indicators_can_be_complete_without_global_score(self):
        indicators = ["ghg_emissions", "energy_use", "water_use", "chemical_process",
            "fiber_composition", "material_origin", "production_waste", "durability",
            "supplier_traceability", "work_conditions"]
        result = calculate_impact_v2([observation(item) for item in indicators])
        self.assertEqual(result.status, "complete")
        self.assertIsNone(result.global_score)

    def test_reviewer_cannot_review_own_submission(self):
        with self.assertRaises(ValueError):
            ReviewTask(task_id="r1", subject_id="lot:1", submitted_by="u1", reviewer_id="u1")
