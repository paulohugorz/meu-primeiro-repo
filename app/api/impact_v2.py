import os
from fastapi import APIRouter, HTTPException
from app.schemas.impact_v2 import ImpactV2EvaluationRequest, ImpactV2Result
from app.services.impact_v2 import calculate_impact_v2

router = APIRouter(prefix="/api/v2", tags=["PI5 v2 — experimental"])

def _enabled() -> bool:
    return os.getenv("PI5_V2_ENABLED", "false").lower() == "true"

@router.post("/impact/evaluate", response_model=ImpactV2Result)
def evaluate_impact_v2(payload: ImpactV2EvaluationRequest):
    if not _enabled():
        raise HTTPException(status_code=404, detail="PI5 v2 disabled")
    return calculate_impact_v2(payload.observations, payload.evidence_records)
