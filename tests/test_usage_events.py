import json
import unittest
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import registrar_evento_uso
from app.core.database import Base
from app.models.models import UsageEvent
from app.schemas.schemas import UsageEventCreate


class UsageEventTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.db = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def _event(self, **overrides):
        payload = {
            "event_id": "event-1",
            "schema_version": "usage-event-v1",
            "session_id": "session-1",
            "event_name": "ui_click",
            "page": "/atelier",
            "component": "btn-publicar",
            "action": "activate",
            "metadata": {"target_type": "button"},
            "occurred_at": datetime.now(timezone.utc),
        }
        payload.update(overrides)
        return UsageEventCreate(**payload)

    def test_records_minimized_usage_event_and_deduplicates(self):
        result = registrar_evento_uso(self._event(), db=self.db)
        duplicate = registrar_evento_uso(self._event(), db=self.db)

        self.assertEqual(result, {"accepted": True, "duplicate": False})
        self.assertEqual(duplicate, {"accepted": True, "duplicate": True})
        record = self.db.query(UsageEvent).one()
        self.assertEqual(json.loads(record.metadata_json), {"target_type": "button"})

    def test_discards_unapproved_metadata_and_user_content(self):
        registrar_evento_uso(self._event(metadata={
            "field_type": "textarea",
            "value": "conteudo confidencial digitado",
            "email": "pessoa@example.com",
        }), db=self.db)

        record = self.db.query(UsageEvent).one()
        self.assertEqual(json.loads(record.metadata_json), {"field_type": "textarea"})

    def test_rejects_unknown_event_name(self):
        with self.assertRaises(HTTPException) as context:
            registrar_evento_uso(self._event(event_name="raw_input_capture"), db=self.db)
        self.assertEqual(context.exception.status_code, 422)

    def test_records_v2_semantic_event_with_minimized_metadata(self):
        result = registrar_evento_uso(self._event(
            schema_version="usage-event-v2",
            event_name="dpp_publication_blocked",
            component="dpp_publication",
            action="blocked",
            metadata={
                "surface": "atelier",
                "flow": "dpp_publication",
                "step": "validation",
                "outcome": "blocked",
                "error_code": "validation_failed",
                "status_code": 422,
                "validation_issue_count": 3,
                "method": "POST",
            },
        ), db=self.db)

        self.assertEqual(result, {"accepted": True, "duplicate": False})
        record = self.db.query(UsageEvent).one()
        metadata = json.loads(record.metadata_json)
        self.assertEqual(metadata["validation_issue_count"], 3)
        self.assertNotIn("value", metadata)

    def test_v2_rejects_unknown_metadata_instead_of_storing_content(self):
        with self.assertRaises(HTTPException) as context:
            registrar_evento_uso(self._event(
                schema_version="usage-event-v2",
                event_name="piece_created",
                metadata={"surface": "atelier", "piece_name": "Segredo comercial"},
            ), db=self.db)
        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(self.db.query(UsageEvent).count(), 0)

    def test_v2_rejects_invalid_enum(self):
        with self.assertRaises(HTTPException) as context:
            registrar_evento_uso(self._event(
                schema_version="usage-event-v2",
                event_name="workspace_viewed",
                metadata={"surface": "unknown_surface"},
            ), db=self.db)
        self.assertEqual(context.exception.status_code, 422)

    def test_v3_records_workspace_event_with_pseudonymous_context(self):
        registrar_evento_uso(self._event(
            schema_version="usage-event-v3",
            event_name="workspace_created",
            component="workspace_creation",
            action="complete",
            metadata={"workspace_type": "team", "creation_source": "onboarding"},
            workspace_id_hash="workspace_hash_123456",
            anonymous_id="anonymous_123456",
            source="backend",
            environment="test",
        ), db=self.db)

        record = self.db.query(UsageEvent).one()
        self.assertEqual(record.workspace_id_hash, "workspace_hash_123456")
        self.assertEqual(record.source, "backend")
        self.assertEqual(json.loads(record.metadata_json)["workspace_type"], "team")

    def test_v3_rejects_personal_data_and_unknown_properties(self):
        for metadata in ({"email": "pessoa@example.com"}, {"workspace_type": "team", "workspace_name": "Segredo"}):
            with self.assertRaises(HTTPException) as context:
                registrar_evento_uso(self._event(
                    event_id=f"event-{len(metadata)}-{next(iter(metadata))}",
                    schema_version="usage-event-v3",
                    event_name="workspace_created",
                    metadata=metadata,
                    source="backend",
                    environment="test",
                ), db=self.db)
            self.assertEqual(context.exception.status_code, 422)

    def test_v3_rejects_unknown_event(self):
        with self.assertRaises(HTTPException) as context:
            registrar_evento_uso(self._event(
                schema_version="usage-event-v3",
                event_name="person_email_captured",
                metadata={},
            ), db=self.db)
        self.assertEqual(context.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
