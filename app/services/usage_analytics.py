"""Emissão confiável de eventos v3 por operações confirmadas no backend."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
import uuid

from sqlalchemy.orm import Session

from app.models.models import UsageEvent
from app.telemetry_contract import validate_v3_properties


def analytics_hash(identifier: str) -> str:
    secret = os.getenv("PHYLLOS_ANALYTICS_HMAC_SECRET", "").encode("utf-8")
    if len(secret) < 32:
        raise RuntimeError("PHYLLOS_ANALYTICS_HMAC_SECRET não configurado ou muito curto")
    return hmac.new(secret, identifier.encode("utf-8"), hashlib.sha256).hexdigest()


def emit_backend_event(
    db: Session,
    event_name: str,
    *,
    workspace_id: str | None = None,
    person_id: str | None = None,
    properties: dict | None = None,
    request_id: str | None = None,
) -> UsageEvent:
    """Persiste após a transação de domínio; nunca recebe conteúdo livre."""
    safe_properties = validate_v3_properties(event_name, properties or {})
    event = UsageEvent(
        event_id=str(uuid.uuid4()),
        schema_version="usage-event-v3",
        event_version=1,
        session_id=request_id or str(uuid.uuid4()),
        event_name=event_name,
        page="/api",
        component=event_name.rsplit("_", 1)[0][:80],
        action="complete" if not event_name.endswith("failed") else "failed",
        metadata_json=json.dumps(safe_properties, ensure_ascii=False, sort_keys=True),
        occurred_at=datetime.now(timezone.utc),
        user_id_hash=analytics_hash(person_id) if person_id else None,
        workspace_id_hash=analytics_hash(workspace_id) if workspace_id else None,
        source="backend",
        environment=os.getenv("PHYLLOS_ENVIRONMENT", "production"),
        application_version=os.getenv("RENDER_GIT_COMMIT"),
        request_id=request_id,
    )
    db.add(event)
    db.commit()
    return event

