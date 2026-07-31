"""Cálculo seguro PI5 v2: ausência nunca recebe pontuação."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone, timedelta
from app.schemas.impact_v2 import (
    Confidentiality, ConfidenceResult, DataOrigin, DimensionResult,
    EvidenceRecordIn, ImpactDimension, ImpactObservationIn, ImpactV2Result,
    MethodologyDefinition, ReadinessResult, ResultStatus,
)

DEFAULT_METHOD = MethodologyDefinition(
    methodology_id="phyllos-impact-v2",
    version="2.0.0-experimental",
    dimensions=list(ImpactDimension),
    weights={dimension: 0.2 for dimension in ImpactDimension},
    required_indicators={
        ImpactDimension.CLIMATE_ENERGY: ["ghg_emissions", "energy_use"],
        ImpactDimension.WATER_CHEMICALS: ["water_use", "chemical_process"],
        ImpactDimension.MATERIALS_ORIGIN_LAND_USE: ["fiber_composition", "material_origin"],
        ImpactDimension.WASTE_CIRCULARITY_DURABILITY: ["production_waste", "durability"],
        ImpactDimension.SUPPLY_CHAIN_WORK_JUST_TRANSITION: ["supplier_traceability", "work_conditions"],
    },
    minimum_coverage={},
)

INDICATOR_DIMENSION = {
    indicator: dimension
    for dimension, indicators in DEFAULT_METHOD.required_indicators.items()
    for indicator in indicators
}
STRONG_ORIGINS = {DataOrigin.MEASURED, DataOrigin.DOCUMENTED, DataOrigin.CALCULATED}
WEAK_ORIGINS = {DataOrigin.ESTIMATED, DataOrigin.INFERRED, DataOrigin.PROXY}


def _ratio(n: int, d: int) -> float:
    return round(n / d, 4) if d else 0.0


def calculate_impact_v2(
    observations: list[ImpactObservationIn],
    evidence_records: list[EvidenceRecordIn] | None = None,
    method: MethodologyDefinition = DEFAULT_METHOD,
) -> ImpactV2Result:
    evidence_records = evidence_records or []
    now = datetime.now(timezone.utc)
    evidence_by_id = {item.evidence_id: item for item in evidence_records}
    valid_evidence_ids = {
        item.evidence_id for item in evidence_records
        if item.expires_at is None or item.expires_at >= now
    }
    verified_evidence_ids = {
        item.evidence_id for item in evidence_records
        if item.verification_status.lower() in {"verified", "approved", "valid"}
    } & valid_evidence_ids
    public_evidence_ids = {
        item.evidence_id for item in evidence_records
        if item.confidentiality == Confidentiality.PUBLIC and item.public_url
    } & valid_evidence_ids
    by_indicator = {item.indicator_id: item for item in observations}
    dimensions: list[DimensionResult] = []
    blockers: list[str] = []

    for dimension in method.dimensions:
        required = method.required_indicators.get(dimension, [])
        present = [by_indicator[item] for item in required if item in by_indicator]
        calculable = [item for item in present if item.origin not in {
            DataOrigin.ABSENT, DataOrigin.CONFLICTING, DataOrigin.NOT_APPLICABLE
        }]
        missing = [item for item in required if item not in by_indicator or by_indicator[item].origin == DataOrigin.ABSENT]
        not_applicable = [item.indicator_id for item in present if item.origin == DataOrigin.NOT_APPLICABLE]
        conflicts = [item.indicator_id for item in present if item.origin == DataOrigin.CONFLICTING]
        coverage = _ratio(len(calculable), len(required))
        if conflicts or not calculable:
            status = ResultStatus.INDETERMINATE
        elif missing or not_applicable or len(calculable) < len(required):
            status = ResultStatus.PARTIAL
        else:
            status = ResultStatus.COMPLETE
        origins = Counter(item.origin.value for item in present)
        dimensions.append(DimensionResult(
            dimension=dimension, status=status, score=None, coverage=coverage,
            missing_indicators=missing + conflicts + not_applicable,
            origin_distribution={key: _ratio(value, len(present)) for key, value in origins.items()},
            limitations=["Pesos e thresholds ainda não possuem calibração científica aprovada."],
        ))
        if status != ResultStatus.COMPLETE:
            blockers.append(f"{dimension.value}:{status.value}")

    total = len(observations)
    conflicts = sum(item.origin == DataOrigin.CONFLICTING for item in observations)
    strong = sum(item.origin in STRONG_ORIGINS and bool(set(item.evidence_ids) & verified_evidence_ids) for item in observations)
    weak = sum(item.origin in WEAK_ORIGINS for item in observations)
    measured = sum(item.origin == DataOrigin.MEASURED for item in observations)
    coverage = _ratio(sum(item.origin not in {DataOrigin.ABSENT, DataOrigin.CONFLICTING} for item in observations), total)
    evidence_coverage = _ratio(sum(bool(set(item.evidence_ids) & valid_evidence_ids) for item in observations), total)
    confidence_status = ResultStatus.INDETERMINATE if not total or conflicts else (
        ResultStatus.COMPLETE if strong == total else ResultStatus.PARTIAL
    )
    confidence = ConfidenceResult(
        status=confidence_status,
        overall_class=None if confidence_status == ResultStatus.INDETERMINATE else ("higher" if strong == total else "limited"),
        coverage=coverage,
        authority=_ratio(sum(any(evidence_by_id[eid].issuer for eid in item.evidence_ids if eid in valid_evidence_ids) for item in observations), total),
        verification=_ratio(sum(bool(set(item.evidence_ids) & verified_evidence_ids) for item in observations), total),
        recency=_ratio(sum(
            datetime.now(timezone.utc) - timedelta(days=365) <= item.period_end <= datetime.now(timezone.utc)
            for item in observations
        ), total),
        coherence=0.0 if conflicts else (1.0 if total else 0.0), specificity=_ratio(sum(bool(item.piece_id) for item in observations), total),
        uncertainty=_ratio(sum(item.uncertainty is not None for item in observations), total),
        provenance=evidence_coverage, measured_ratio=_ratio(measured, total),
        estimated_or_inferred_ratio=_ratio(weak, total), conflicts=conflicts,
        method_version="evidence-confidence-v1-experimental",
    )
    internal_coverage = evidence_coverage
    public_coverage = _ratio(sum(bool(set(item.evidence_ids) & public_evidence_ids) for item in observations), total)
    readiness = ReadinessResult(
        profile_version="1.0.0-experimental",
        internal_status=ResultStatus.COMPLETE if total and internal_coverage == 1 else (ResultStatus.PARTIAL if total else ResultStatus.INDETERMINATE),
        public_status=ResultStatus.COMPLETE if total and public_coverage == 1 else (ResultStatus.PARTIAL if public_coverage else ResultStatus.INDETERMINATE),
        internal_coverage=internal_coverage, public_coverage=public_coverage,
        gaps=[item.indicator_id for item in observations if not (set(item.evidence_ids) & valid_evidence_ids)],
    )
    status = ResultStatus.COMPLETE if dimensions and all(item.status == ResultStatus.COMPLETE for item in dimensions) else (
        ResultStatus.INDETERMINATE if any(item.status == ResultStatus.INDETERMINATE for item in dimensions) else ResultStatus.PARTIAL
    )
    first = observations[0] if observations else None
    return ImpactV2Result(
        status=status, methodology_id=method.methodology_id, methodology_version=method.version,
        piece_id=first.piece_id if first else None, lot_id=first.lot_id if first else "unknown",
        dimensions=dimensions, global_score=None, evidence_readiness=readiness,
        evidence_confidence=confidence, publication_blockers=blockers,
    )
