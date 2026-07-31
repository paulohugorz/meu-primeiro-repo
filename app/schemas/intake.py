"""Contrato de intake assistido do DPP (B0/B1).

O perfil de 49 pontos e operacional e provisório. Ele não representa o ato
delegado setorial de têxteis do ESPR, que ainda não foi adotado.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


EvidenceStatus = Literal["ausente", "declarado", "calculado", "documentado", "verificado"]


class FiberComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fibra: str = Field(min_length=1)
    pct: float = Field(gt=0, le=100)


class EvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1)
    field: str = Field(min_length=1)
    status: EvidenceStatus
    source: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    collected_at: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    retention_until: str = Field(min_length=1)


class DppIntakePayload(BaseModel):
    """Payload permissivo; a completude e validada com erros JRC por campo."""

    model_config = ConfigDict(extra="forbid")

    # Identidade (JRC-01..09)
    product_id: str | None = None
    product_name: str | None = None
    product_description: str | None = None
    product_category: str | None = None
    gtin: str | None = None
    sku: str | None = None
    batch_id: str | None = None
    model_id: str | None = None
    product_image_urls: list[str] | None = None

    # Operador econômico (JRC-10..15)
    brand_name: str | None = None
    economic_operator_name: str | None = None
    economic_operator_identifier: str | None = None
    economic_operator_address: str | None = None
    economic_operator_country: str | None = None
    economic_operator_contact: str | None = None

    # Materiais e substâncias (JRC-16..23)
    fiber_composition: list[FiberComponent] | None = None
    product_parts: list[dict[str, Any]] | None = None
    material_weight_g: float | None = None
    fabric_weight_g_m2: float | None = None
    substances_of_concern: list[dict[str, Any]] | None = None
    recycled_content_pct: float | None = None
    renewable_content_pct: float | None = None
    material_origin: list[dict[str, Any]] | None = None

    # Fabricação e cadeia (JRC-24..29)
    country_of_manufacture: str | None = None
    manufacturing_sites: list[dict[str, Any]] | None = None
    supply_chain_steps: list[dict[str, Any]] | None = None
    production_date: str | None = None
    supplier_identifiers: list[str] | None = None
    certifications: list[dict[str, Any]] | None = None

    # Circularidade, uso e fim de vida (JRC-30..37)
    care_instructions: str | None = None
    repair_instructions: str | None = None
    durability_information: str | None = None
    spare_parts_information: str | None = None
    disassembly_instructions: str | None = None
    reuse_instructions: str | None = None
    recycling_instructions: str | None = None
    end_of_life_instructions: str | None = None

    # Desempenho ambiental (JRC-38..43)
    carbon_footprint_kgco2e: float | None = None
    water_use_liters: float | None = None
    energy_use_kwh: float | None = None
    microplastic_release_information: str | None = None
    environmental_method: str | None = None
    environmental_source_versions: list[str] | None = None

    # Governança e evidência (JRC-44..49)
    evidence_references: list[EvidenceReference] | None = None
    data_carrier_identifier: str | None = None
    public_dpp_url: str | None = None
    applicable_market: list[str] | None = None
    declaration_owner: str | None = None
    declaration_date: str | None = None


class IntakeIssue(BaseModel):
    field: str
    jrc_point: str
    code: str
    message: str


class IntakeValidationResult(BaseModel):
    valid: bool
    profile_id: str
    profile_status: Literal["provisional"] = "provisional"
    profile_version: str
    source: str
    scope: str
    limitation: str
    issues: list[IntakeIssue]
    received_points: int
    total_points: int = 49


class IntakeRowResult(BaseModel):
    row_number: int
    product_reference: str | None = None
    validation: IntakeValidationResult


class IntakeImportResult(BaseModel):
    filename: str
    format: Literal["csv", "xlsx", "json"]
    mode: Literal["preview"] = "preview"
    total_rows: int
    valid_rows: int
    invalid_rows: int
    mapped_columns: dict[str, str]
    unmapped_columns: list[str]
    rows: list[IntakeRowResult]
    persisted: bool = False
