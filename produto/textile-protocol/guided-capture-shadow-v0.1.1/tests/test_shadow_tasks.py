import csv
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from db import connect, init_db
from task_service import compare_shadow_decision, ingest_baseline, list_tasks, resolve_task

SAMPLE_FIELDS = [
    "sample_id","image_count","has_macro","has_backlight","focus_ok",
    "warp_weft_visible","loop_structure_visible","knit_direction",
    "web_structure_visible","braided_visible","stitch_bonded_visible",
    "composite_layers_visible","diagonal_ribs_visible","long_floats_visible",
    "regular_over_under_visible","transparency_observation","document_available",
    "document_structure_family","document_construction","notes"
]
PRED_FIELDS = [
    "sample_id","structure_family","construction_primary","visual_transparency",
    "capture_quality","decision","reason_codes","structure_assertion_kind",
    "structure_evidence_status","construction_assertion_kind",
    "construction_evidence_status","transparency_assertion_kind",
    "transparency_evidence_status","fired_rule_ids","ruleset_version",
    "benchmark_version_id","review_required","conflict_codes",
    "structure_candidates","construction_candidates"
]

class ShadowTaskTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "test.db"
        init_db(self.db)
        self.samples = Path(self.temp.name) / "samples.csv"
        self.pred = Path(self.temp.name) / "pred.csv"
        with self.samples.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=SAMPLE_FIELDS)
            w.writeheader()
            w.writerow({
                "sample_id":"sample:synthetic:001","image_count":"1","has_macro":"no",
                "has_backlight":"no","focus_ok":"unknown","warp_weft_visible":"unknown",
                "loop_structure_visible":"unknown","knit_direction":"indeterminate",
                "web_structure_visible":"unknown","braided_visible":"unknown",
                "stitch_bonded_visible":"unknown","composite_layers_visible":"unknown",
                "diagonal_ribs_visible":"unknown","long_floats_visible":"unknown",
                "regular_over_under_visible":"unknown","transparency_observation":"indeterminate",
                "document_available":"no","document_structure_family":"",
                "document_construction":"","notes":"synthetic"
            })
        with self.pred.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=PRED_FIELDS)
            w.writeheader()
            w.writerow({
                "sample_id":"sample:synthetic:001","structure_family":"indeterminate",
                "construction_primary":"not_applicable","visual_transparency":"indeterminate",
                "capture_quality":"insufficient","decision":"request_new_evidence",
                "reason_codes":"capture_insufficient","structure_assertion_kind":"inferred",
                "structure_evidence_status":"absent","construction_assertion_kind":"inferred",
                "construction_evidence_status":"absent","transparency_assertion_kind":"inferred",
                "transparency_evidence_status":"absent","fired_rule_ids":"RF-CQ-001",
                "ruleset_version":"0.1.1",
                "benchmark_version_id":"benchmark-version:benchmark-1:v1.0.0",
                "review_required":"no","conflict_codes":"",
                "structure_candidates":"","construction_candidates":""
            })

    def tearDown(self):
        self.temp.cleanup()

    def test_generation_is_idempotent_and_shadow(self):
        first = ingest_baseline(self.db, self.samples, self.pred)
        second = ingest_baseline(self.db, self.samples, self.pred)
        self.assertGreater(first["new_tasks"], 0)
        self.assertEqual(second["new_tasks"], 0)
        for task in list_tasks(self.db):
            self.assertEqual(task["mode"], "shadow")
            self.assertFalse(task["affects_official_decision"])

    def test_unknown_proposal_field_is_rejected(self):
        ingest_baseline(self.db, self.samples, self.pred)
        task = list_tasks(self.db)[0]
        with self.assertRaises(ValueError):
            compare_shadow_decision(
                self.db, task["task_id"], {"invented_field":"anything"}
            )

    def test_invalid_class_value_is_rejected(self):
        ingest_baseline(self.db, self.samples, self.pred)
        task = list_tasks(self.db)[0]
        with self.assertRaises(ValueError):
            compare_shadow_decision(
                self.db, task["task_id"], {"structure_family":"denim"}
            )

    def test_would_change_only_compares_official_fields(self):
        ingest_baseline(self.db, self.samples, self.pred)
        task = list_tasks(self.db)[0]
        result = compare_shadow_decision(
            self.db, task["task_id"],
            {
                "structure_family":"woven_fabric",
                "construction_primary":"plain_weave",
                "decision":"classify"
            }
        )
        self.assertTrue(result["would_change"])
        self.assertEqual(
            set(result["changed_fields"]),
            {"structure_family","construction_primary","decision"}
        )
        self.assertNotIn("reason_codes", result["compared_fields"])

    def test_resolution_does_not_mutate_snapshot(self):
        ingest_baseline(self.db, self.samples, self.pred)
        task = list_tasks(self.db)[0]
        with connect(self.db) as conn:
            before = tuple(conn.execute(
                "SELECT decision_hash,decision_json FROM official_decision_snapshots"
            ).fetchone())
        resolve_task(
            self.db, task["task_id"], "corrected", "reviewer:1", "synthetic",
            proposed_decision={
                "structure_family":"woven_fabric",
                "construction_primary":"plain_weave",
                "decision":"classify"
            }
        )
        with connect(self.db) as conn:
            after = tuple(conn.execute(
                "SELECT decision_hash,decision_json FROM official_decision_snapshots"
            ).fetchone())
        self.assertEqual(before, after)

    def test_snapshot_and_events_are_immutable(self):
        ingest_baseline(self.db, self.samples, self.pred)
        with self.assertRaises(sqlite3.DatabaseError):
            with connect(self.db) as conn:
                conn.execute("UPDATE official_decision_snapshots SET decision_json='{}'")
        with self.assertRaises(sqlite3.DatabaseError):
            with connect(self.db) as conn:
                conn.execute("DELETE FROM task_events")
