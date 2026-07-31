import re
from .schemas import ClaimMode, ClaimType, DecisionAction, EvidenceKind, EvidenceRef, FabricDecision, GuardResult

DOCUMENTARY={EvidenceKind.DOCUMENT, EvidenceKind.LAB_TEST, EvidenceKind.HUMAN_VERIFICATION}
IMAGE_FORBIDDEN_FACTS={ClaimType.COMPOSITION, ClaimType.ORIGIN, ClaimType.CERTIFICATION, ClaimType.ENVIRONMENTAL, ClaimType.LABOUR}
UNSAFE_TEXT=re.compile(r"\b(certificad[oa]|comprovad[oa]|100%\s+\w+|sustent[aá]vel|zero impacto)\b", re.I)

def validate_decision(decision: FabricDecision, evidence: list[EvidenceRef]) -> GuardResult:
    by_id={item.evidence_id:item for item in evidence}; allowed=[]; rejected=[]; reasons=[]
    for claim in decision.claims:
        refs=[by_id[item] for item in claim.evidence_ids if item in by_id]
        verified={item.kind for item in refs if item.verified}
        claim_reasons=[]
        if not refs: claim_reasons.append("claim has no resolved evidence")
        if claim.mode == ClaimMode.FACT and claim.claim_type in IMAGE_FORBIDDEN_FACTS and not (verified & DOCUMENTARY):
            claim_reasons.append("image/model evidence cannot confirm this claim type")
        if decision.action == DecisionAction.REQUEST_EVIDENCE and claim.mode == ClaimMode.FACT:
            claim_reasons.append("evidence request cannot emit facts")
        if claim_reasons: rejected.append({"claim_id":claim.claim_id,"reasons":claim_reasons})
        else: allowed.append(claim)
    free_ok=not bool(decision.free_text and UNSAFE_TEXT.search(decision.free_text))
    if not free_ok: reasons.append("free text contains a strong or prohibited claim requiring policy review")
    return GuardResult(safe_to_render=not rejected and free_ok, allowed_claims=allowed,
                       rejected=rejected, free_text_allowed=free_ok, reasons=reasons)
