"""Contratos canônicos PI5 v2 — B1 experimental, sem calibração científica."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class DataOrigin(str, Enum):
    MEASURED = "measured"
    CALCULATED = "calculated"
    SUPPLIER_DECLARED = "supplier_declared"
    DOCUMENTED = "documented"
    ESTIMATED = "estimated"
    INFERRED = "inferred"
    PROXY = "proxy"
    CONFLICTING = "conflicting"
    ABSENT = "absent"
    NOT_APPLICABLE = "not_applicable"


class Confidentiality(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    PERSONAL = "personal"


class ResultStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    INDETERMINATE = "indeterminate"


class ImpactDimension(str, Enum):
    CLIMATE_ENERGY = "climate_energy"
    WATER_CHEMICALS = "water_chemicals"
    MATERIALS_ORIGIN_LAND_USE = "materials_origin_land_use"
    WASTE_CIRCULARITY_DURABILITY = "waste_circularity_durability"
    SUPPLY_CHAIN_WORK_JUST_TRANSITION = "supply_chain_work_just_transition"


class MethodologyDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    methodology_id: str
    version: str
    status: str = "experimental"
    dimensions: list[ImpactDimension]
    weights: dict[ImpactDimension, float] = Field(default_factory=dict)
    required_indicators: dict[ImpactDimension, list[str]]
    minimum_coverage: dict[ImpactDimension, float] = Field(default_factory=dict)


class MethodologyVersion(MethodologyDefinition):
    approved_by: str | None = None
    changelog: str
    rollback_criteria: list[str] = Field(default_factory=list)


class ImpactIndicatorDefinition(BaseModel):
    indicator_id: str
    dimension: ImpactDimension
    version: str
    unit: str
    required: bool = True
    calculation_rule: str


class FactorVersion(BaseModel):
    factor_version_id: str
    factor_id: str
    version: str
    value: float
    unit: str
    source: str
    valid_from: datetime
    valid_until: datetime | None = None


class ImpactObservationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observation_id: str
    indicator_id: str
    piece_id: str | None = None
    lot_id: str
    supplier_id: str
    facility_id: str
    production_stage: str
    period_start: datetime
    period_end: datetime
    value: float | None = None
    unit: str | None = None
    origin: DataOrigin
    method_id: str
    factor_version_id: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    uncertainty: dict[str, Any] | None = None
    not_applicable_justification: str | None = None
    not_applicable_rule_id: str | None = None

    @model_validator(mode="after")
    def validate_semantics(self):
        if self.origin == DataOrigin.NOT_APPLICABLE and not (
            self.not_applicable_justification and self.not_applicable_rule_id
        ):
            raise ValueError("not_applicable exige justificativa e regra metodológica")
        if self.origin in {DataOrigin.ABSENT, DataOrigin.CONFLICTING} and self.value is not None:
            raise ValueError("absent/conflicting não pode carregar valor conclusivo")
        if self.origin not in {DataOrigin.ABSENT, DataOrigin.CONFLICTING, DataOrigin.NOT_APPLICABLE}:
            if self.value is None or not self.unit:
                raise ValueError("observação calculável exige valor e unidade")
        return self


class EvidenceRecordIn(BaseModel):
    evidence_id: str
    kind: str
    issuer: str
    subject: str
    period_start: datetime | None = None
    period_end: datetime | None = None
    content_hash: str
    location: str
    rights: str
    verification_status: str
    expires_at: datetime | None = None
    confidentiality: Confidentiality
    public_url: str | None = None


class EvidenceAssertion(BaseModel):
    assertion_id: str
    evidence_id: str
    subject_id: str
    predicate: str
    value: Any
    status: str = "pending_review"


class Claim(BaseModel):
    claim_id: str
    subject_id: str
    statement: str
    evidence_assertion_ids: list[str] = Field(default_factory=list)
    public: bool = False


class ReviewTask(BaseModel):
    task_id: str
    subject_id: str
    submitted_by: str
    reviewer_id: str
    status: str = "pending"

    @model_validator(mode="after")
    def enforce_segregation(self):
        if self.submitted_by == self.reviewer_id:
            raise ValueError("reviewer deve ser independente de submitted_by")
        return self


class PublicationDecision(BaseModel):
    decision_id: str
    subject_id: str
    reviewer_id: str
    decision: str
    rationale: str
    decided_at: datetime


class ImpactV2EvaluationRequest(BaseModel):
    observations: list[ImpactObservationIn] = Field(default_factory=list)
    evidence_records: list[EvidenceRecordIn] = Field(default_factory=list)


class DimensionResult(BaseModel):
    dimension: ImpactDimension
    status: ResultStatus
    score: float | None = None
    coverage: float
    missing_indicators: list[str]
    origin_distribution: dict[str, float]
    limitations: list[str]


class ConfidenceResult(BaseModel):
    status: ResultStatus
    overall_class: str | None
    coverage: float
    authority: float
    verification: float
    recency: float
    coherence: float
    specificity: float
    uncertainty: float
    provenance: float
    measured_ratio: float
    estimated_or_inferred_ratio: float
    conflicts: int
    method_version: str


class ReadinessResult(BaseModel):
    profile_id: str = "phyllos-evidence-readiness"
    profile_version: str
    internal_status: ResultStatus
    public_status: ResultStatus
    internal_coverage: float
    public_coverage: float
    gaps: list[str]


class ImpactV2Result(BaseModel):
    api_version: str = "v2"
    status: ResultStatus
    methodology_id: str
    methodology_version: str
    experimental: bool = True
    piece_id: str | None
    lot_id: str
    dimensions: list[DimensionResult]
    global_score: float | None = None
    evidence_readiness: ReadinessResult
    evidence_confidence: ConfidenceResult
    publication_blockers: list[str]
