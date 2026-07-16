import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class UIContractTests(unittest.TestCase):
    def test_quality_checkboxes_are_not_prechecked(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn('type="checkbox" checked', js)
        for gate in ["correct_view", "sample_visible", "focus_ok", "lighting_ok",
                     "no_obstruction", "not_edited"]:
            self.assertIn(f'["{gate}"', js)

    def test_real_candidate_default_is_not_used(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('value="OPS-SYN-001"', html)
        self.assertNotIn('value="OPS-TX-001"', html)

    def test_dynamic_task_fields_are_escaped(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function esc", js)

    def test_shadow_warning_is_permanent_and_promotion_is_absent(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("AMBIENTE SHADOW", html)
        for forbidden in [">Aprovar<", ">Publicar<", ">Promover<"]:
            self.assertNotIn(forbidden, html)

    def test_explicit_workflow_and_synthetic_allowlist_exist(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn("allowedStates", js)
        self.assertIn("/^OPS-SYN-00[1-5]$/", js)
        self.assertIn("URL.revokeObjectURL", js)

    def test_review_unlock_uses_confirmed_cards_and_refreshes_session(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('document.querySelectorAll(".capture-card.complete").length', js)
        self.assertIn('$("reviewButton").onclick=async()=>', js)
        self.assertIn("await refreshSession();renderReview()", js)

    def test_visible_result_uses_natural_brazilian_portuguese(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('woven_fabric:"tecido plano', js)
        self.assertIn('plain_weave:"ligamento tela', js)
        self.assertIn('twill:"ligamento sarja', js)
        self.assertIn("não confirmação de composição", js)
        self.assertIn("Identificador da evidência", js)
        self.assertNotIn("<small>Score</small>", js)
        self.assertIn('"woven_fabric:plain_weave":"Tecido plano de ligamento tela"', js)
        self.assertIn('"woven_fabric:twill":"Tecido plano de sarja"', js)
        self.assertIn('<p class="kicker">Possível tecido</p>', js)
        self.assertIn('[["Viscolinho",40]', js)
        self.assertIn("Percentuais experimentais e não calibrados", js)
