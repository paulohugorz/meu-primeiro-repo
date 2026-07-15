import io
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from db import connect, init_db
from capture_service import (
    add_capture_bytes, export_baseline_capture_row, finalize_session, get_session,
    reconcile_artifacts, remove_capture_item, start_session, validate_image_bytes
)

SHOTS = [
    "face_overview", "reverse_overview", "macro_structure",
    "drape_fold", "backlight_transparency", "scale_reference"
]

def image_bytes(fmt="PNG", size=(1024, 768)):
    out = io.BytesIO()
    Image.new("RGB", size, "white").save(out, format=fmt)
    return out.getvalue()

class CaptureServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "test.db"
        self.artifacts = Path(self.temp.name) / "artifacts"
        init_db(self.db)
        self.session = start_session(self.db, "OPS-SYN-001", "operator:test")

    def tearDown(self):
        self.temp.cleanup()

    def add(self, shot_type, accepted=True, data=None, mime="image/png"):
        return add_capture_bytes(
            self.db, self.artifacts, self.session["session_id"], shot_type,
            data or image_bytes(), mime, f"{shot_type}.png",
            {
                "focus_ok": accepted, "lighting_ok": accepted,
                "sample_fills_frame": accepted, "no_label_leak": accepted
            },
            "operator:test"
        )

    def test_real_candidate_is_blocked_until_physical_receipt(self):
        with self.assertRaises(ValueError):
            start_session(self.db, "OPS-TX-001", "operator:test")

    def test_global_field_gate_blocks_real_candidate_after_receipt(self):
        from id_service import set_mapping_state
        set_mapping_state(
            self.db, "OPS-TX-001", "received_identified", True, True
        )
        with self.assertRaisesRegex(ValueError, "field test is globally disabled"):
            start_session(self.db, "OPS-TX-001", "operator:test")

    def test_all_three_ids_resolve_to_same_mapping(self):
        from id_service import resolve_mapping
        a = resolve_mapping(self.db, "OPS-TX-001")
        b = resolve_mapping(self.db, "sample:ops-tx-001")
        c = resolve_mapping(self.db, "textile-sample:ops-tx-001")
        self.assertEqual(a["mapping_id"], b["mapping_id"])
        self.assertEqual(b["mapping_id"], c["mapping_id"])

    def test_quality_confirmation_actor_is_required(self):
        with self.assertRaises(ValueError):
            add_capture_bytes(
                self.db, self.artifacts, self.session["session_id"],
                "face_overview", image_bytes(), "image/png", "x.png",
                {
                    "focus_ok": True, "lighting_ok": True,
                    "sample_fills_frame": True, "no_label_leak": True
                }, ""
            )

    def test_mime_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add("face_overview", data=image_bytes("PNG"), mime="image/jpeg")

    def test_invalid_bytes_are_rejected(self):
        with self.assertRaises(ValueError):
            self.add("face_overview", data=b"not-an-image")

    def test_dimensions_below_minimum_are_rejected(self):
        with self.assertRaises(ValueError):
            self.add("face_overview", data=image_bytes(size=(400, 300)))

    def test_capture_creates_evidence_record(self):
        item = self.add("face_overview")
        self.assertTrue(item["evidence"]["evidence_id"].startswith("evidence:capture:"))
        self.assertEqual(item["evidence"]["artifact_hash_sha256"], item["sha256"])
        self.assertEqual(item["evidence"]["source_authenticity"], "unreviewed")

    def test_capture_can_be_removed_before_session_confirmation(self):
        item = self.add("face_overview")
        artifact = Path(item["artifact_path"])
        self.assertTrue(artifact.exists())
        removed = remove_capture_item(
            self.db, self.session["session_id"], item["item_id"]
        )
        self.assertTrue(removed["removed"])
        self.assertFalse(artifact.exists())
        refreshed = get_session(self.db, self.session["session_id"])
        self.assertEqual(refreshed["items"], [])

    def test_incomplete_session_goes_to_quality_review(self):
        self.add("face_overview")
        result = finalize_session(self.db, self.session["session_id"])
        self.assertEqual(result["status"], "quality_review")
        self.assertFalse(result["ready_for_baseline"])

    def test_complete_session_exports_baseline_row(self):
        for shot in SHOTS:
            self.add(shot)
        result = finalize_session(self.db, self.session["session_id"])
        self.assertEqual(result["status"], "complete")
        row = export_baseline_capture_row(self.db, self.session["session_id"])
        self.assertEqual(row["sample_id"], "sample:synthetic:001")
        self.assertIn("textile-sample:synthetic:001", row["notes"])

    def test_concurrent_uploads_receive_unique_sequences(self):
        def upload(idx):
            return add_capture_bytes(
                self.db, self.artifacts, self.session["session_id"],
                "face_overview", image_bytes(), "image/png", f"{idx}.png",
                {
                    "focus_ok": True, "lighting_ok": True,
                    "sample_fills_frame": True, "no_label_leak": True
                }, f"operator:{idx}"
            )
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(upload, range(4)))
        sequences = [r["sequence_no"] for r in results]
        self.assertEqual(len(sequences), len(set(sequences)))

    def test_reconcile_detects_and_deletes_orphan(self):
        orphan = self.artifacts / "orphan.png"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_bytes(image_bytes())
        report = reconcile_artifacts(self.db, self.artifacts)
        self.assertIn(str(orphan.resolve()), report["orphan_files"])
        deleted = reconcile_artifacts(self.db, self.artifacts, delete_orphans=True)
        self.assertFalse(orphan.exists())
        self.assertIn(str(orphan.resolve()), deleted["deleted_files"])

    def test_complete_session_can_be_superseded_only_after_replacement_complete(self):
        for shot in SHOTS:
            self.add(shot)
        old = finalize_session(self.db, self.session["session_id"])
        replacement = start_session(
            self.db, "textile-sample:synthetic:001", "operator:replacement",
            supersedes_session_id=old["session_id"],
            supersession_reason="controlled recapture"
        )
        with connect(self.db) as conn:
            before = conn.execute(
                "SELECT status FROM capture_sessions WHERE session_id=?",
                (old["session_id"],)
            ).fetchone()[0]
        self.assertEqual(before, "complete")
        for shot in SHOTS:
            add_capture_bytes(
                self.db, self.artifacts, replacement["session_id"], shot,
                image_bytes(), "image/png", f"{shot}.png",
                {
                    "focus_ok": True, "lighting_ok": True,
                    "sample_fills_frame": True, "no_label_leak": True
                }, "operator:replacement"
            )
        finalize_session(self.db, replacement["session_id"])
        with connect(self.db) as conn:
            after = conn.execute(
                "SELECT status,superseded_by_session_id FROM capture_sessions WHERE session_id=?",
                (old["session_id"],)
            ).fetchone()
            superseded_evidence = conn.execute(
                "SELECT COUNT(*) FROM evidence_records WHERE review_status='superseded_capture'"
            ).fetchone()[0]
        self.assertEqual(after["status"], "superseded")
        self.assertEqual(after["superseded_by_session_id"], replacement["session_id"])
        self.assertEqual(superseded_evidence, 6)
