import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.intake import DppIntakePayload
from app.services.intake_validator import FIELD_TO_POINT, validate_intake
from app.services.intake_importer import parse_portfolio


def complete_payload():
    payload = {}
    for field in DppIntakePayload.model_fields:
        payload[field] = "informado"
    payload.update(
        product_image_urls=["https://example.test/product.jpg"],
        fiber_composition=[{"fibra": "algodao", "pct": 100}],
        product_parts=[{"name": "corpo"}],
        material_weight_g=250,
        fabric_weight_g_m2=180,
        substances_of_concern=[{"status": "none_declared"}],
        recycled_content_pct=0,
        renewable_content_pct=100,
        material_origin=[{"country": "BR"}],
        manufacturing_sites=[{"country": "BR"}],
        supply_chain_steps=[{"step": "confeccao"}],
        supplier_identifiers=["supplier-1"],
        certifications=[{"status": "none_declared"}],
        carbon_footprint_kgco2e=1.2,
        water_use_liters=30,
        energy_use_kwh=2.5,
        environmental_source_versions=["source:v1"],
        evidence_references=[{
            "evidence_id": "ev-1", "field": "fiber_composition",
            "status": "documentado", "source": "supplier declaration",
            "source_version": "v1", "collected_at": "2026-07-31",
            "owner": "brand", "retention_until": "2036-07-31",
        }],
        applicable_market=["BR", "EU"],
    )
    return payload


class IntakeValidatorTests(unittest.TestCase):
    def test_profile_maps_exactly_49_fields(self):
        self.assertEqual(len(DppIntakePayload.model_fields), 49)
        self.assertEqual(len(FIELD_TO_POINT), 49)
        self.assertEqual(FIELD_TO_POINT["product_id"], "JRC-01")
        self.assertEqual(FIELD_TO_POINT["declaration_date"], "JRC-49")

    def test_missing_fields_have_specific_field_and_point(self):
        result = validate_intake({"product_id": "prod-1"})
        self.assertFalse(result.valid)
        issue = next(item for item in result.issues if item.field == "product_name")
        self.assertEqual(issue.jrc_point, "JRC-02")
        self.assertEqual(issue.code, "missing")
        self.assertNotIn("product_id", {item.field for item in result.issues})

    def test_invalid_composition_has_specific_message(self):
        payload = complete_payload()
        payload["fiber_composition"] = [{"fibra": "algodao", "pct": 80}]
        result = validate_intake(payload)
        issue = next(item for item in result.issues if item.code == "percentage_total")
        self.assertEqual(issue.jrc_point, "JRC-16")
        self.assertIn("80%", issue.message)

    def test_complete_payload_is_valid(self):
        result = validate_intake(complete_payload())
        self.assertTrue(result.valid, result.issues)
        self.assertEqual(result.received_points, 49)

    def test_endpoint_rejects_incomplete_payload_with_structured_issues(self):
        with TestClient(app) as client:
            response = client.post("/intake/validate", json={"product_id": "prod-1"})
        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertFalse(body["valid"])
        self.assertEqual(body["total_points"], 49)
        self.assertEqual(body["profile_status"], "provisional")
        self.assertTrue(any(item["jrc_point"] == "JRC-02" for item in body["issues"]))

    def test_endpoint_accepts_complete_payload(self):
        with TestClient(app) as client:
            response = client.post("/intake/validate", json=complete_payload())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["valid"])

    def test_csv_upload_maps_portuguese_columns_without_persisting(self):
        content = "id produto;nome produto;sku;marca;composição\np1;Camiseta;SKU1;Marca A;algodão:100\n".encode()
        result = parse_portfolio("portfolio.csv", content)
        self.assertEqual(result.total_rows, 1)
        self.assertEqual(result.mapped_columns["nome produto"], "product_name")
        self.assertFalse(result.persisted)

    def test_upload_endpoint_is_preview_only(self):
        with TestClient(app) as client:
            response = client.post("/intake/upload", files={"file": ("portfolio.csv", b"product_id,product_name\np1,Produto\n", "text/csv")})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertFalse(response.json()["persisted"])


if __name__ == "__main__":
    unittest.main()
