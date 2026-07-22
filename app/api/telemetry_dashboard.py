from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
import os
import secrets
import statistics

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import UsageEvent


router = APIRouter(prefix="/telemetry/dashboard", tags=["Telemetria"])
security = HTTPBasic(auto_error=False)
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

FUNNEL = [
    ("workspace_viewed", "Workspace acessado"),
    ("piece_created", "Peça criada"),
    ("technical_sheet_saved", "Ficha técnica salva"),
    ("material_sheet_saved", "Material salvo"),
    ("production_stage_added", "Etapa produtiva registrada"),
    ("dpp_publication_started", "Publicação iniciada"),
    ("dpp_published", "DPP publicado"),
    ("public_passport_viewed", "Passaporte visualizado"),
]

ERROR_EVENTS = {
    "piece_create_failed",
    "technical_sheet_save_failed",
    "material_sheet_save_failed",
    "production_stage_add_failed",
    "dpp_publication_blocked",
    "dpp_link_copy_failed",
    "qr_request_failed",
    "api_action_failed",
    "js_error",
}

WORKSPACE_FAILURE_EVENTS = {"workspace_creation_failed", "workspace_switch_failed", "workspace_settings_save_failed", "workspace_archive_failed"}
PEOPLE_FAILURE_EVENTS = {"person_creation_failed", "person_update_failed", "person_archive_failed"}
MEMBERSHIP_FAILURE_EVENTS = {"workspace_member_invitation_failed", "workspace_member_role_change_failed", "workspace_member_removal_failed"}

COLLABORATION_FUNNEL = [
    ("workspace_viewed", "Workspace acessado"),
    ("workspace_created", "Workspace de time criado"),
    ("workspace_member_invited", "Primeiro convite enviado"),
    ("workspace_member_invitation_accepted", "Primeiro convite aceito"),
    ("workspace_first_collaborative_action_completed", "Primeira ação colaborativa"),
]
PEOPLE_FUNNEL = [
    ("person_list_viewed", "Lista de pessoas acessada"),
    ("person_creation_started", "Criação iniciada"),
    ("person_created", "Pessoa criada"),
    ("person_updated", "Pessoa atualizada"),
]
TEAM_FUNNEL = [
    ("workspace_member_list_viewed", "Lista de membros acessada"),
    ("workspace_member_invitation_started", "Convite iniciado"),
    ("workspace_member_invited", "Convite enviado"),
    ("workspace_member_invitation_accepted", "Convite aceito"),
    ("workspace_member_role_changed", "Papel administrado"),
]


def require_dashboard_access(
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> str:
    expected_password = os.getenv("TELEMETRY_DASHBOARD_PASSWORD", "")
    expected_user = os.getenv("TELEMETRY_DASHBOARD_USER", "phyllos")
    if not expected_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard indisponível: credencial não configurada",
        )
    valid = bool(credentials) and secrets.compare_digest(credentials.username, expected_user)
    valid = valid and secrets.compare_digest(credentials.password, expected_password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": 'Basic realm="PHYLLOS Telemetry"'},
        )
    return expected_user


def _event_time(event: UsageEvent) -> datetime:
    value = event.occurred_at or event.received_at
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _percentage(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100, 1) if denominator else 0.0


def build_dashboard_summary(events: list[UsageEvent], days: int) -> dict:
    event_counts = Counter(event.event_name for event in events)
    sessions_by_event: dict[str, set[str]] = defaultdict(set)
    daily: dict[str, dict] = defaultdict(lambda: {
        "events": 0,
        "sessions": set(),
        "published": 0,
        "blocked": 0,
        "passport_views": 0,
    })
    error_codes = Counter()
    metadata_by_event: dict[str, list[dict]] = defaultdict(list)
    workspaces_by_event: dict[str, set[str]] = defaultdict(set)

    for event in events:
        sessions_by_event[event.event_name].add(event.session_id)
        day = _event_time(event).date().isoformat()
        bucket = daily[day]
        bucket["events"] += 1
        bucket["sessions"].add(event.session_id)
        if event.event_name == "dpp_published":
            bucket["published"] += 1
        elif event.event_name == "dpp_publication_blocked":
            bucket["blocked"] += 1
        elif event.event_name == "public_passport_viewed":
            bucket["passport_views"] += 1

        if event.event_name in ERROR_EVENTS | WORKSPACE_FAILURE_EVENTS | PEOPLE_FAILURE_EVENTS | MEMBERSHIP_FAILURE_EVENTS:
            try:
                metadata = json.loads(event.metadata_json or "{}")
            except json.JSONDecodeError:
                metadata = {}
            error_codes[metadata.get("error_code", "unknown")] += 1
        try:
            event_metadata = json.loads(event.metadata_json or "{}")
        except json.JSONDecodeError:
            event_metadata = {}
        metadata_by_event[event.event_name].append(event_metadata)
        workspace_hash = getattr(event, "workspace_id_hash", None)
        if workspace_hash:
            workspaces_by_event[event.event_name].add(workspace_hash)

    all_sessions = {event.session_id for event in events}
    workspace_sessions = len(sessions_by_event["workspace_viewed"])
    published_sessions = len(sessions_by_event["dpp_published"])
    publication_attempts = event_counts["dpp_publication_started"]
    blocked = event_counts["dpp_publication_blocked"]
    published = event_counts["dpp_published"]
    recovered = event_counts["dpp_publication_recovered"]
    total_errors = sum(event_counts[name] for name in ERROR_EVENTS)
    total_errors += sum(event_counts[name] for name in WORKSPACE_FAILURE_EVENTS | PEOPLE_FAILURE_EVENTS | MEMBERSHIP_FAILURE_EVENTS)

    funnel = []
    baseline = 0
    for event_name, label in FUNNEL:
        count = len(sessions_by_event[event_name])
        if not baseline and count:
            baseline = count
        funnel.append({
            "event": event_name,
            "label": label,
            "sessions": count,
            "conversion_from_entry": _percentage(count, baseline),
        })

    daily_series = [
        {
            "date": date,
            "events": values["events"],
            "sessions": len(values["sessions"]),
            "published": values["published"],
            "blocked": values["blocked"],
            "passport_views": values["passport_views"],
        }
        for date, values in sorted(daily.items())
    ]

    def domain_funnel(definition):
        baseline = 0
        result = []
        for event_name, label in definition:
            count = len(workspaces_by_event[event_name]) or len(sessions_by_event[event_name])
            if not baseline and count:
                baseline = count
            result.append({
                "event": event_name,
                "label": label,
                "sessions": count,
                "conversion_from_entry": _percentage(count, baseline),
            })
        return result

    created_per_workspace = Counter(
        getattr(event, "workspace_id_hash", None)
        for event in events if event.event_name == "person_created" and getattr(event, "workspace_id_hash", None)
    )
    created_counts = list(created_per_workspace.values())
    team_created = sum(
        1 for metadata in metadata_by_event["workspace_created"]
        if metadata.get("workspace_type") == "team"
    )
    invited = event_counts["workspace_member_invited"]
    accepted = event_counts["workspace_member_invitation_accepted"]
    collaborative = event_counts["workspace_first_collaborative_action_completed"]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": days,
        "overview": {
            "sessions": len(all_sessions),
            "events": len(events),
            "activation_rate": _percentage(published_sessions, workspace_sessions),
            "publication_attempts": publication_attempts,
            "publication_block_rate": _percentage(blocked, publication_attempts),
            "published": published,
            "recovery_rate": _percentage(recovered, blocked),
            "public_passport_views": event_counts["public_passport_viewed"],
            "error_rate": _percentage(total_errors, len(events)),
        },
        "funnel": funnel,
        "collaboration_funnel": domain_funnel(COLLABORATION_FUNNEL),
        "people_funnel": domain_funnel(PEOPLE_FUNNEL),
        "team_funnel": domain_funnel(TEAM_FUNNEL),
        "workspace": {
            "viewed": event_counts["workspace_viewed"],
            "individual_created": sum(1 for item in metadata_by_event["workspace_created"] if item.get("workspace_type") == "individual"),
            "team_created": team_created,
            "switched": event_counts["workspace_switched"],
            "settings_saved": event_counts["workspace_settings_saved"],
            "archived": event_counts["workspace_archived"],
            "failures": sum(event_counts[name] for name in WORKSPACE_FAILURE_EVENTS),
        },
        "people": {
            "module_viewed": event_counts["person_list_viewed"],
            "created": event_counts["person_created"],
            "updated": event_counts["person_updated"],
            "archived": event_counts["person_archived"],
            "creation_success_rate": _percentage(event_counts["person_created"], event_counts["person_created"] + event_counts["person_creation_failed"]),
            "workspaces_with_people": len(created_per_workspace),
            "people_per_workspace_mean": round(statistics.mean(created_counts), 1) if created_counts else 0.0,
            "people_per_workspace_median": statistics.median(created_counts) if created_counts else 0.0,
        },
        "collaboration": {
            "invitations_sent": invited,
            "invitations_accepted": accepted,
            "acceptance_rate": _percentage(accepted, invited),
            "first_collaborative_actions": collaborative,
            "activation_rate": _percentage(collaborative, team_created),
            "membership_failures": sum(event_counts[name] for name in MEMBERSHIP_FAILURE_EVENTS),
            "last_owner_blocks": event_counts["last_owner_change_blocked"],
        },
        "concurrency": {
            "version_conflicts": event_counts["resource_version_conflict_detected"],
            "resolved_conflicts": event_counts["resource_conflict_resolved"],
            "duplicates_prevented": event_counts["duplicate_command_prevented"],
            "idempotency_replays": event_counts["idempotency_replay_detected"],
            "sync_failures": event_counts["workspace_sync_refresh_failed"],
        },
        "daily": daily_series,
        "top_events": [
            {"event": name, "count": count}
            for name, count in event_counts.most_common(12)
        ],
        "error_codes": [
            {"code": code, "count": count}
            for code, count in error_codes.most_common(8)
        ],
        "data_quality": {
            "v3_events": sum(1 for event in events if event.schema_version == "usage-event-v3"),
            "v2_events": sum(1 for event in events if event.schema_version == "usage-event-v2"),
            "legacy_events": sum(1 for event in events if event.schema_version == "usage-event-v1"),
            "events_without_component": sum(1 for event in events if not event.component),
        },
    }


@router.get("/", response_class=HTMLResponse)
def telemetry_dashboard(
    request: Request,
    _user: str = Depends(require_dashboard_access),
):
    response = templates.TemplateResponse(request, "telemetry_dashboard.html")
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


@router.get("/data")
def telemetry_dashboard_data(
    response: Response,
    days: int = Query(30, ge=1, le=90),
    _user: str = Depends(require_dashboard_access),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    events = (
        db.query(UsageEvent)
        .filter(UsageEvent.received_at >= cutoff)
        .order_by(UsageEvent.received_at.asc())
        .all()
    )
    return build_dashboard_summary(events, days)
