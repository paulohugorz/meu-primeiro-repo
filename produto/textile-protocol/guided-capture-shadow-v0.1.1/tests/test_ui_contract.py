import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class UIContractTests(unittest.TestCase):
    def test_quality_checkboxes_are_not_prechecked(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        for checkbox in ["focusOk", "lightingOk", "fillsFrame", "noLeak"]:
            fragment = f'id="{checkbox}" type="checkbox" checked'
            self.assertNotIn(fragment, js)

    def test_real_candidate_default_is_not_used(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('value="OPS-SYN-001"', html)
        self.assertNotIn('value="OPS-TX-001"', html)

    def test_dynamic_task_fields_are_escaped(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn("const escapeHtml", js)
        for field in ["task_type", "sample_id", "priority", "status", "mode"]:
            self.assertIn(f"escapeHtml(t.{field})", js)
