import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from capture_service import add_capture_bytes, finalize_session, load_protocol, start_session
from db import init_db
from recognition_service import get_recognition_result, start_recognition


class RecognitionServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.db = root / "test.db"
        self.artifacts = root / "artifacts"
        init_db(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def _complete(self, ops_id="OPS-SYN-001"):
        session = start_session(self.db, ops_id, "operator:test")
        image_path = ROOT / "data" / "synthetic_pilot" / "source_images" / f"{ops_id}_01_face_overview.png"
        data = image_path.read_bytes()
        for step in load_protocol()["steps"]:
            add_capture_bytes(
                self.db, self.artifacts, session["session_id"], step["shot_type"],
                data, "image/png", "fixture.png",
                {"focus_ok": True, "lighting_ok": True,
                 "sample_fills_frame": True, "no_label_leak": True},
                "operator:test"
            )
        return finalize_session(self.db, session["session_id"])

    def test_completed_session_returns_shadow_result_without_mutation(self):
        session = self._complete()
        run = start_recognition(self.db, session["session_id"])
        result = get_recognition_result(self.db, run["recognition_run_id"])
        self.assertEqual(result["mode"], "shadow")
        self.assertEqual(result["hypothesis"]["family"], "woven_fabric")
        self.assertTrue(result["review_required"])
        self.assertFalse(result["official_mutation_applied"])
        self.assertFalse(result["publication_decision_created"])
        self.assertEqual(len(result["evidence_ids"]), 6)

    def test_incomplete_session_is_refused(self):
        session = start_session(self.db, "OPS-SYN-001", "operator:test")
        with self.assertRaisesRegex(ValueError, "must be complete"):
            start_recognition(self.db, session["session_id"])

    def test_abstention_fixture_is_preserved(self):
        session = self._complete("OPS-SYN-005")
        run = start_recognition(self.db, session["session_id"])
        result = get_recognition_result(self.db, run["recognition_run_id"])
        self.assertTrue(result["abstained"])
        self.assertIsNone(result["hypothesis"])
