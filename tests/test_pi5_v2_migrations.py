import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class MigrationContractTests(unittest.TestCase):
    def test_up_and_down_are_additive_and_reversible(self):
        up=(ROOT/"migrations/20260731_001_pi5_v2_up.sql").read_text()
        down=(ROOT/"migrations/20260731_001_pi5_v2_down.sql").read_text()
        self.assertNotIn("DROP TABLE",up.upper())
        self.assertNotIn("ALTER TABLE",up.upper())
        for table in ("impact_observations_v2","evidence_records_v2","review_tasks_v2","claims_v2"):
            self.assertIn(table,up); self.assertIn(table,down)
