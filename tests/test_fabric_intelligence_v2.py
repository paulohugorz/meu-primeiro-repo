import unittest
from app.fabric_intelligence.claim_guard import validate_decision
from app.fabric_intelligence.conflict_engine import detect_conflicts
from app.fabric_intelligence.schemas import (
    Claim, ClaimMode, ClaimType, EvidenceAssertion, EvidenceKind, EvidenceRef, FabricDecision,
)

class FabricIntelligenceV2Tests(unittest.TestCase):
    def test_image_cannot_confirm_composition(self):
        decision=FabricDecision(decision_id="d1",model_version="shadow-v1",claims=[Claim(
            claim_id="c1",text="100% algodão",claim_type=ClaimType.COMPOSITION,
            mode=ClaimMode.FACT,evidence_ids=["image:1"])])
        result=validate_decision(decision,[EvidenceRef(evidence_id="image:1",kind=EvidenceKind.IMAGE,verified=True)])
        self.assertFalse(result.safe_to_render)

    def test_verified_document_can_support_composition(self):
        decision=FabricDecision(decision_id="d2",model_version="shadow-v1",claims=[Claim(
            claim_id="c2",text="composição documentada",claim_type=ClaimType.COMPOSITION,
            mode=ClaimMode.FACT,evidence_ids=["doc:1"])])
        result=validate_decision(decision,[EvidenceRef(evidence_id="doc:1",kind=EvidenceKind.DOCUMENT,verified=True)])
        self.assertTrue(result.safe_to_render)

    def test_free_text_strong_claim_is_blocked(self):
        decision=FabricDecision(decision_id="d3",model_version="shadow-v1",free_text="Material sustentável e certificado")
        self.assertFalse(validate_decision(decision,[]).free_text_allowed)

    def test_conflict_escalates(self):
        items=[EvidenceAssertion(assertion_id="a1",field_name="composition",value="cotton",source_kind=EvidenceKind.IMAGE,source_id="i",confidence=.8),
               EvidenceAssertion(assertion_id="a2",field_name="composition",value="polyester",source_kind=EvidenceKind.DOCUMENT,source_id="d",confidence=1,verified=True)]
        result=detect_conflicts(items)
        self.assertTrue(result.conflict_detected)
        self.assertEqual(result.action,"escalate_conflict")
