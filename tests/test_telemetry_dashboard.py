import json
import os
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from app.api.telemetry_dashboard import build_dashboard_summary, require_dashboard_access


def event(name, session, *, error_code=None, schema="usage-event-v2", metadata=None, workspace=None):
    metadata = metadata or ({"error_code": error_code} if error_code else {})
    return SimpleNamespace(
        event_name=name,
        session_id=session,
        occurred_at=datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc),
        received_at=datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc),
        metadata_json=json.dumps(metadata),
        schema_version=schema,
        component="workspace",
        workspace_id_hash=workspace,
    )


class TelemetryDashboardTests(unittest.TestCase):
    def test_builds_aggregated_product_metrics(self):
        events = [
            event("workspace_viewed", "session-a"),
            event("workspace_viewed", "session-b"),
            event("piece_created", "session-a"),
            event("dpp_publication_started", "session-a"),
            event("dpp_publication_blocked", "session-a", error_code="validation_failed"),
            event("dpp_publication_recovered", "session-a"),
            event("dpp_published", "session-a"),
            event("public_passport_viewed", "session-b"),
        ]

        result = build_dashboard_summary(events, 30)

        self.assertEqual(result["overview"]["sessions"], 2)
        self.assertEqual(result["overview"]["activation_rate"], 50.0)
        self.assertEqual(result["overview"]["publication_block_rate"], 100.0)
        self.assertEqual(result["overview"]["recovery_rate"], 100.0)
        self.assertEqual(result["error_codes"], [{"code": "validation_failed", "count": 1}])
        self.assertEqual(result["data_quality"]["v2_events"], 8)

    def test_summary_never_exposes_session_identifiers(self):
        result = build_dashboard_summary([
            event("workspace_viewed", "sensitive-session-id"),
        ], 7)

        self.assertNotIn("sensitive-session-id", json.dumps(result))

    def test_builds_workspace_people_and_collaboration_metrics(self):
        events = [
            event("workspace_viewed", "s1", schema="usage-event-v3", workspace="workspace_hash_a"),
            event("workspace_created", "s1", schema="usage-event-v3", workspace="workspace_hash_a", metadata={"workspace_type": "team"}),
            event("person_list_viewed", "s1", schema="usage-event-v3", workspace="workspace_hash_a"),
            event("person_creation_started", "s1", schema="usage-event-v3", workspace="workspace_hash_a"),
            event("person_created", "s1", schema="usage-event-v3", workspace="workspace_hash_a"),
            event("workspace_member_invited", "s1", schema="usage-event-v3", workspace="workspace_hash_a"),
            event("workspace_member_invitation_accepted", "s2", schema="usage-event-v3", workspace="workspace_hash_a"),
            event("workspace_first_collaborative_action_completed", "s2", schema="usage-event-v3", workspace="workspace_hash_a"),
            event("duplicate_command_prevented", "s2", schema="usage-event-v3", workspace="workspace_hash_a"),
        ]

        result = build_dashboard_summary(events, 30)

        self.assertEqual(result["workspace"]["team_created"], 1)
        self.assertEqual(result["people"]["workspaces_with_people"], 1)
        self.assertEqual(result["collaboration"]["acceptance_rate"], 100.0)
        self.assertEqual(result["collaboration"]["activation_rate"], 100.0)
        self.assertEqual(result["concurrency"]["duplicates_prevented"], 1)
        self.assertEqual(result["data_quality"]["v3_events"], 9)

    def test_dashboard_is_disabled_without_password(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as context:
                require_dashboard_access(None)
        self.assertEqual(context.exception.status_code, 503)

    def test_dashboard_accepts_configured_basic_credentials(self):
        credentials = HTTPBasicCredentials(username="analytics", password="strong-secret")
        with patch.dict(os.environ, {
            "TELEMETRY_DASHBOARD_USER": "analytics",
            "TELEMETRY_DASHBOARD_PASSWORD": "strong-secret",
        }, clear=True):
            result = require_dashboard_access(credentials)
        self.assertEqual(result, "analytics")

    def test_dashboard_rejects_invalid_credentials(self):
        credentials = HTTPBasicCredentials(username="analytics", password="wrong")
        with patch.dict(os.environ, {
            "TELEMETRY_DASHBOARD_USER": "analytics",
            "TELEMETRY_DASHBOARD_PASSWORD": "strong-secret",
        }, clear=True):
            with self.assertRaises(HTTPException) as context:
                require_dashboard_access(credentials)
        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
