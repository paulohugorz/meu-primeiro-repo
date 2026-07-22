from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
import os
import secrets

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

        if event.event_name in ERROR_EVENTS:
            try:
                metadata = json.loads(event.metadata_json or "{}")
            except json.JSONDecodeError:
                metadata = {}
            error_codes[metadata.get("error_code", "unknown")] += 1

    all_sessions = {event.session_id for event in events}
    workspace_sessions = len(sessions_by_event["workspace_viewed"])
    published_sessions = len(sessions_by_event["dpp_published"])
    publication_attempts = event_counts["dpp_publication_started"]
    blocked = event_counts["dpp_publication_blocked"]
    published = event_counts["dpp_published"]
    recovered = event_counts["dpp_publication_recovered"]
    total_errors = sum(event_counts[name] for name in ERROR_EVENTS)

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
            "v2_events": sum(1 for event in events if event.schema_version == "usage-event-v2"),
            "legacy_events": sum(1 for event in events if event.schema_version != "usage-event-v2"),
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
