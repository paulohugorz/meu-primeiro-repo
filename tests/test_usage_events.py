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


if __name__ == "__main__":
    unittest.main()
