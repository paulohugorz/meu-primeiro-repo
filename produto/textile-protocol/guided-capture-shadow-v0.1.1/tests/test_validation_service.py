import base64
import io
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from capture_service import add_capture_base64, finalize_session, load_protocol, start_session
from db import init_db
from recognition_service import start_recognition
from validation_service import create_validation, list_validations

def image_data():
    out = io.BytesIO(); Image.new("RGB", (800, 600), "white").save(out, "PNG")
    return base64.b64encode(out.getvalue()).decode()

class ProfessionalValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); root = Path(self.tmp.name)
        self.db = root / "test.db"; self.artifacts = root / "artifacts"; init_db(self.db)
        session = start_session(self.db, "OPS-SYN-001", "validator:1")
        for step in load_protocol()["steps"]:
            add_capture_base64(self.db, self.artifacts, session["session_id"], {
                "shot_type": step["shot_type"], "mime_type": "image/png", "file_name": "x.png", "data_base64": image_data(),
                "quality_confirmed_by_actor_id": "validator:1", "quality": {"focus_ok": True, "lighting_ok": True, "sample_fills_frame": True, "no_label_leak": True}
            })
        finalize_session(self.db, session["session_id"])
        self.run = start_recognition(self.db, session["session_id"])

    def tearDown(self): self.tmp.cleanup()

    def payload(self):
        return {
            "validator_actor_id": "validator:1", "validator_role": "tecnologa textil", "status": "validada",
            "commercial_name": "viscolinho", "confirmation_source": "ficha_tecnica", "structure": "tecido plano",
            "transparency": "opaco", "weight_gsm": 145, "elasticity": "baixa", "composition_status": "confirmada_percentuais",
            "composition": [{"fiber": "viscose", "percent": 55}, {"fiber": "linho", "percent": 45}],
            "hypothesis_assessments": [{"name": "Viscolinho", "position": 1, "estimated_percent": 40, "assessment": "correta"}, {"name": "Tricoline", "position": 2, "estimated_percent": 35, "assessment": "incorreta"}, {"name": "Popeline", "position": 3, "estimated_percent": 25, "assessment": "incorreta"}],
            "no_hypothesis_correct": False,
            "image_assessments": [{"shot_type": x["shot_type"], "quality": "adequada"} for x in load_protocol()["steps"]],
            "recapture_request": {"requested": False, "views": []}, "notes": "confirmado pela ficha"
        }

    def test_validation_preserves_inference_and_computes_top_metrics(self):
        saved = create_validation(self.db, self.run["recognition_run_id"], self.payload())
        self.assertTrue(saved["top1_correct"]); self.assertTrue(saved["top3_correct"])
        self.assertTrue(saved["gold_set_eligible"]); self.assertEqual(saved["frozen_inference"]["hypothesis"]["class"], "plain_weave")
        self.assertEqual(len(saved["audit_events"]), 1); self.assertEqual(len(list_validations(self.db, self.run["recognition_run_id"])), 1)

    def test_invalid_composition_is_rejected(self):
        payload = self.payload(); payload["composition"][1]["percent"] = 40
        with self.assertRaisesRegex(ValueError, "sum to 100"):
            create_validation(self.db, self.run["recognition_run_id"], payload)
