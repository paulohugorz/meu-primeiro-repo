from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

class EvidenceKind(str, Enum):
    IMAGE="image"; VISUAL_MODEL="visual_model"; DOCUMENT="document"; LAB_TEST="lab_test"
    HUMAN_VERIFICATION="human_verification"; DETERMINISTIC_CALCULATION="deterministic_calculation"

class ClaimType(str, Enum):
    OBSERVATION="observation"; STRUCTURE="structure"; COMPOSITION="composition"
    ORIGIN="origin"; CERTIFICATION="certification"; ENVIRONMENTAL="environmental"; LABOUR="labour"

class ClaimMode(str, Enum): FACT="fact"; CANDIDATE="candidate"; OBSERVATION="observation"
class DecisionAction(str, Enum): SHADOW="shadow"; REQUEST_EVIDENCE="request_evidence"; ESCALATE_CONFLICT="escalate_conflict"; HUMAN_REVIEW="human_review"

class EvidenceRef(BaseModel):
    evidence_id: str; kind: EvidenceKind; verified: bool=False
    supports_claim_types: list[ClaimType]=Field(default_factory=list)

class Claim(BaseModel):
    claim_id: str; text: str; claim_type: ClaimType; mode: ClaimMode=ClaimMode.FACT
    value: Any|None=None; evidence_ids: list[str]=Field(default_factory=list)

class FabricDecision(BaseModel):
    model_config=ConfigDict(extra="forbid")
    decision_id: str; model_version: str; action: DecisionAction=DecisionAction.SHADOW
    claims: list[Claim]=Field(default_factory=list); free_text: str|None=None
    missing_evidence: list[str]=Field(default_factory=list); experimental: bool=True
    @model_validator(mode="after")
    def shadow_only(self):
        if not self.experimental: raise ValueError("Fabric Intelligence permanece experimental")
        return self

class GuardResult(BaseModel):
    safe_to_render: bool; allowed_claims: list[Claim]; rejected: list[dict[str, Any]]
    free_text_allowed: bool; reasons: list[str]

class EvidenceAssertion(BaseModel):
    assertion_id: str; field_name: str; value: Any; source_kind: EvidenceKind
    source_id: str; confidence: float=Field(ge=0, le=1); verified: bool=False

class ConflictReport(BaseModel):
    conflict_detected: bool; fields: list[str]; action: DecisionAction; assertion_ids: list[str]
