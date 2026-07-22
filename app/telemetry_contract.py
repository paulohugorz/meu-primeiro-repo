"""Contrato analítico usage-event-v3 para Workspace, Pessoas e Colaboração."""

from __future__ import annotations

from typing import Any
import re

from fastapi import HTTPException


COMMON_FAILURE_PROPERTIES = {"reason_code", "failure_stage", "is_retryable", "http_status_group"}

EVENT_PROPERTIES: dict[str, set[str]] = {
    "workspace_viewed": {"workspace_type", "entry_source", "is_first_workspace_view"},
    "workspace_creation_started": {"workspace_type", "creation_source"},
    "workspace_created": {"workspace_type", "creation_source"},
    "workspace_creation_failed": COMMON_FAILURE_PROPERTIES | {"workspace_type"},
    "workspace_switch_started": {"switch_source"},
    "workspace_switched": {"source_workspace_type", "target_workspace_type", "switch_source"},
    "workspace_switch_failed": COMMON_FAILURE_PROPERTIES,
    "workspace_settings_viewed": set(),
    "workspace_settings_saved": {"changed_field_categories"},
    "workspace_settings_save_failed": COMMON_FAILURE_PROPERTIES,
    "workspace_archived": set(),
    "workspace_archive_failed": COMMON_FAILURE_PROPERTIES,
    "workspace_restored": set(),
    "workspace_deletion_requested": set(),
    "workspace_deleted": set(),
    "person_list_viewed": {"result_count_bucket", "filter_category"},
    "person_creation_started": {"creation_source"},
    "person_created": {"person_category", "creation_source", "has_workspace_role_reference"},
    "person_creation_failed": COMMON_FAILURE_PROPERTIES,
    "person_viewed": {"person_category"},
    "person_updated": {"changed_field_categories"},
    "person_update_failed": COMMON_FAILURE_PROPERTIES,
    "person_archived": set(),
    "person_archive_failed": COMMON_FAILURE_PROPERTIES,
    "person_restored": set(),
    "person_search_performed": {"result_count_bucket", "search_source"},
    "workspace_member_list_viewed": set(),
    "workspace_member_invitation_started": {"invited_role", "invitation_source"},
    "workspace_member_invited": {"invited_role", "invitation_source", "is_first_team_invitation"},
    "workspace_member_invitation_failed": COMMON_FAILURE_PROPERTIES,
    "workspace_member_invitation_resent": set(),
    "workspace_member_invitation_revoked": set(),
    "workspace_invitation_opened": set(),
    "workspace_member_invitation_accepted": {"accepted_role", "time_to_accept_bucket"},
    "workspace_member_invitation_expired": set(),
    "workspace_member_role_changed": {"previous_role", "new_role", "change_source"},
    "workspace_member_role_change_failed": COMMON_FAILURE_PROPERTIES,
    "workspace_member_removed": {"removed_role", "removal_source"},
    "workspace_member_removal_failed": COMMON_FAILURE_PROPERTIES,
    "workspace_first_collaborative_action_completed": {"action_category", "participant_count_bucket"},
    "resource_version_conflict_detected": {"resource_type", "conflict_type"},
    "resource_conflict_resolution_started": {"resource_type", "conflict_type", "resolution_strategy"},
    "resource_conflict_resolved": {"resource_type", "conflict_type", "resolution_strategy", "duration_bucket", "result"},
    "idempotency_replay_detected": {"resource_type", "result"},
    "duplicate_command_prevented": {"resource_type", "result"},
    "membership_concurrency_conflict_detected": {"conflict_type", "result"},
    "last_owner_change_blocked": {"conflict_type", "result"},
    "workspace_sync_refresh_completed": {"duration_bucket", "result"},
    "workspace_sync_refresh_failed": COMMON_FAILURE_PROPERTIES | {"duration_bucket"},
}

ENUMS = {
    "workspace_type": {"individual", "team"},
    "source_workspace_type": {"individual", "team"},
    "target_workspace_type": {"individual", "team"},
    "result_count_bucket": {"0", "1-5", "6-20", "21-50", "51+"},
    "person_category": {"internal_collaborator", "supplier_contact", "production_contact", "review_contact", "other"},
    "time_to_accept_bucket": {"under_10_minutes", "10_minutes_to_1_hour", "1_to_24_hours", "1_to_7_days", "over_7_days"},
    "participant_count_bucket": {"1", "2", "3-5", "6-20", "21+"},
    "http_status_group": {"4xx", "5xx", "network", "timeout"},
    "changed_field_categories": {
        "general", "branding", "notifications", "privacy", "production_defaults",
        "basic_profile", "operational_role", "organization", "contact_channels", "status", "notes",
    },
    "action_category": {
        "resource_created_by_second_member", "resource_updated_by_second_member",
        "evidence_submitted_by_second_member", "review_completed",
        "production_action_completed", "comment_or_assignment_completed",
    },
    "reason_code": {
        "AUTH_REQUIRED", "SESSION_EXPIRED", "USER_SUSPENDED", "WORKSPACE_NOT_FOUND",
        "WORKSPACE_NOT_ACTIVE", "WORKSPACE_LIMIT_REACHED", "WORKSPACE_CREATION_CONFLICT",
        "WORKSPACE_SWITCH_NOT_ALLOWED", "PERSON_NOT_FOUND", "PERSON_ALREADY_ARCHIVED",
        "PERSON_VALIDATION_FAILED", "PERSON_VERSION_CONFLICT", "MEMBERSHIP_NOT_FOUND",
        "MEMBERSHIP_NOT_ACTIVE", "INVITATION_EXPIRED", "INVITATION_REVOKED",
        "INVITATION_ALREADY_ACCEPTED", "INVITATION_EMAIL_MISMATCH", "ROLE_CHANGE_NOT_ALLOWED",
        "LAST_OWNER_PROTECTED", "CONCURRENT_MEMBERSHIP_CHANGE", "DATABASE_UNAVAILABLE",
        "AUTH_PROVIDER_UNAVAILABLE", "EMAIL_PROVIDER_UNAVAILABLE", "RATE_LIMITED",
        "REQUEST_TIMEOUT", "UNKNOWN_ERROR",
    },
}

PROHIBITED_KEYS = {
    "name", "nome", "email", "phone", "telefone", "address", "endereco", "document",
    "documento", "job_title", "organization_name", "workspace_name", "notes", "observacoes",
    "search_text", "query", "invitation_token", "token", "evidence_content", "payload",
}


def validate_v3_properties(event_name: str, properties: dict[str, Any]) -> dict[str, Any]:
    allowed = EVENT_PROPERTIES.get(event_name)
    if allowed is None:
        raise HTTPException(status_code=422, detail="Nome de evento não permitido")
    prohibited = set(properties) & PROHIBITED_KEYS
    if prohibited:
        raise HTTPException(status_code=422, detail="Dado pessoal ou conteúdo proibido no evento")
    unknown = set(properties) - allowed
    if unknown:
        raise HTTPException(status_code=422, detail="Propriedade de evento não permitida")
    if len(str(properties)) > 2048:
        raise HTTPException(status_code=422, detail="Payload de evento acima do limite")

    safe: dict[str, Any] = {}
    for key, value in properties.items():
        values = value if isinstance(value, list) else [value]
        if not values or any(not isinstance(item, (str, bool, int, float)) for item in values):
            raise HTTPException(status_code=422, detail=f"Valor inválido para {key}")
        if key in ENUMS and any(item not in ENUMS[key] for item in values):
            raise HTTPException(status_code=422, detail=f"Valor inválido para {key}")
        if any(isinstance(item, str) and len(item) > 80 for item in values):
            raise HTTPException(status_code=422, detail=f"Valor muito longo para {key}")
        if any(isinstance(item, str) and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_+.-]{0,79}", item) for item in values):
            raise HTTPException(status_code=422, detail=f"Valor inválido para {key}")
        safe[key] = value
    return safe
