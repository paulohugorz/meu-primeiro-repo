"""Validação determinística do intake e rastreio dos 49 pontos operacionais."""

from __future__ import annotations

from pydantic import ValidationError

from app.schemas.intake import DppIntakePayload, IntakeIssue, IntakeValidationResult


PROFILE_ID = "phyllos-jrc-textile-intake-provisional-v1"
PROFILE_VERSION = "1.0.0"
PROFILE_SOURCE = (
    "PHYLLOS DPP data contract v0; JRC145830 methodology; "
    "founder-provided DPP Assistido specification"
)
PROFILE_SCOPE = "Operational intake completeness for the PHYLLOS assisted textile DPP pilot."
PROFILE_LIMITATION = (
    "Provisional operational mapping, not a legal conformity determination. "
    "Textile-specific ESPR delegated requirements are not yet final."
)


FIELD_NAMES = tuple(DppIntakePayload.model_fields)
FIELD_TO_POINT = {field: f"JRC-{index:02d}" for index, field in enumerate(FIELD_NAMES, 1)}


def _is_missing(value: object) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _issue(field: str, code: str, message: str) -> IntakeIssue:
    return IntakeIssue(
        field=field,
        jrc_point=FIELD_TO_POINT.get(field, "JRC-UNMAPPED"),
        code=code,
        message=message,
    )


def validate_intake(payload: dict) -> IntakeValidationResult:
    issues: list[IntakeIssue] = []
    try:
        intake = DppIntakePayload.model_validate(payload)
    except ValidationError as exc:
        invalid_fields: set[str] = set()
        for error in exc.errors():
            field = str(error["loc"][0]) if error["loc"] else "payload"
            invalid_fields.add(field)
            issues.append(_issue(field, "invalid", f"Valor inválido: {error['msg']}"))
        # Continue the completeness pass using only values that can be inspected.
        clean_payload = {key: value for key, value in payload.items() if key not in invalid_fields}
        intake = DppIntakePayload.model_construct(**clean_payload)

    values = {field: getattr(intake, field, None) for field in FIELD_NAMES}
    already_invalid = {issue.field for issue in issues}
    for field, value in values.items():
        if field not in already_invalid and _is_missing(value):
            issues.append(_issue(field, "missing", f"Campo obrigatório ausente: {field}"))

    composition = values.get("fiber_composition")
    if composition and "fiber_composition" not in already_invalid:
        total = sum(component.pct for component in composition)
        if abs(total - 100.0) > 0.01:
            issues.append(
                _issue(
                    "fiber_composition",
                    "percentage_total",
                    f"A composição deve somar 100%; total recebido: {total:g}%",
                )
            )

    for field in (
        "material_weight_g", "fabric_weight_g_m2", "carbon_footprint_kgco2e",
        "water_use_liters", "energy_use_kwh", "recycled_content_pct", "renewable_content_pct",
    ):
        value = values.get(field)
        if value is not None and isinstance(value, (int, float)) and value < 0:
            issues.append(_issue(field, "out_of_range", "O valor não pode ser negativo"))

    for field in ("recycled_content_pct", "renewable_content_pct"):
        value = values.get(field)
        if value is not None and isinstance(value, (int, float)) and value > 100:
            issues.append(_issue(field, "out_of_range", "O percentual não pode exceder 100"))

    issues.sort(key=lambda item: (item.jrc_point, item.code))
    received = sum(not _is_missing(values[field]) for field in FIELD_NAMES)
    return IntakeValidationResult(
        valid=not issues,
        profile_id=PROFILE_ID,
        profile_version=PROFILE_VERSION,
        source=PROFILE_SOURCE,
        scope=PROFILE_SCOPE,
        limitation=PROFILE_LIMITATION,
        issues=issues,
        received_points=received,
    )
