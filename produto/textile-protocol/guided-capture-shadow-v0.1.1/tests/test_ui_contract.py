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
        self.assertIn("Marcar todos os critérios", js)
        self.assertIn('querySelectorAll("[data-quality]").forEach(box=>box.checked=true)', js)

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

    def test_expired_render_session_returns_to_setup_in_plain_language(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('includes("capture session not found")', js)
        self.assertIn("cleanup(false)", js)
        self.assertIn("A sessão expirou após a reinicialização do serviço", js)

    def test_visible_result_uses_natural_brazilian_portuguese(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('woven_fabric:"tecido plano', js)
        self.assertIn('plain_weave:"ligamento tela', js)
        self.assertIn('twill:"ligamento sarja', js)
        self.assertIn("não representam probabilidades calibradas", js)
        self.assertIn("Identificador da evidência", js)
        self.assertNotIn("<small>Score</small>", js)
        self.assertIn('"woven_fabric:plain_weave":"Tecido plano de ligamento tela"', js)
        self.assertIn('"woven_fabric:twill":"Tecido plano de sarja"', js)
        self.assertIn('<p class="kicker">Estimativa experimental</p>', js)
        self.assertIn('[["Viscolinho",40]', js)
        self.assertIn("Os percentuais ainda não representam probabilidades calibradas", js)
        self.assertIn("h=r.hypothesis,candidates=h?commercialCandidates(h):[]", js)
        self.assertIn("Não foi possível mostrar o resultado", js)
        self.assertIn("Validar resultado", js)
        self.assertIn("Nenhuma das sugestões estava correta", js)
        self.assertIn("gold_set_eligible", js)

    def test_result_displays_environmental_indicators_without_invented_values(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Mudança climática", js)
        self.assertIn("Consumo de água", js)
        self.assertIn("Demanda de energia", js)
        self.assertIn("Aguardando dados verificados", js)
        self.assertIn("environmentalPanel(r.environmental_indicators)", js)
        self.assertIn('/environmental.css', html)
