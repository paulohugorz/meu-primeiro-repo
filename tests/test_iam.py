import json
import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.iam import (
    accept_invitation, create_invitation, create_person, create_workspace,
    delete_membership, list_members,
)
from app.core.database import Base
from app.models.models import IamMembership, IamPerson, IamWorkspace, UsageEvent
from app.schemas.iam import InvitationCreate, PersonCreate, WorkspaceCreate


class IamIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.request = Request({"type": "http", "headers": []})
        self.env = patch.dict(os.environ, {
            "PHYLLOS_ANALYTICS_HMAC_SECRET": "test-secret-with-at-least-thirty-two-characters",
            "PHYLLOS_ENVIRONMENT": "test",
        })
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_persists_person_workspace_invitation_and_membership_with_v3_events(self):
        person = create_person(PersonCreate(
            display_name="Marina Souza", email="marina@example.com",
            category="internal_collaborator",
        ), self.request, self.db)
        workspace = create_workspace(WorkspaceCreate(
            name="Marca Horizonte", workspace_type="team",
        ), self.request, self.db)
        invitation = create_invitation(workspace.id, InvitationCreate(
            person_id=person.id, role="owner",
        ), self.request, self.db)
        accepted = accept_invitation(invitation.invitation_token, self.request, self.db)

        self.assertTrue(accepted["accepted"])
        self.assertEqual(self.db.query(IamPerson).count(), 1)
        self.assertEqual(self.db.query(IamWorkspace).count(), 1)
        self.assertEqual(self.db.query(IamMembership).count(), 1)
        names = [item.event_name for item in self.db.query(UsageEvent).all()]
        self.assertEqual(names, [
            "person_created", "workspace_created", "workspace_member_invited",
            "workspace_member_invitation_accepted",
        ])
        serialized = " ".join(item.metadata_json for item in self.db.query(UsageEvent).all())
        self.assertNotIn("marina@example.com", serialized)
        self.assertNotIn("Marina Souza", serialized)
        self.assertEqual(len(self.db.query(UsageEvent).filter(UsageEvent.workspace_id_hash.isnot(None)).first().workspace_id_hash), 64)

    def test_last_owner_cannot_be_removed_and_block_is_tracked(self):
        person = create_person(PersonCreate(display_name="Owner", email="owner@example.com"), self.request, self.db)
        workspace = create_workspace(WorkspaceCreate(name="Equipe", workspace_type="team"), self.request, self.db)
        invitation = create_invitation(workspace.id, InvitationCreate(person_id=person.id, role="owner"), self.request, self.db)
        accept_invitation(invitation.invitation_token, self.request, self.db)
        membership = list_members(workspace.id, self.db)[0]

        with self.assertRaises(HTTPException) as context:
            delete_membership(workspace.id, membership["id"], self.request, self.db)

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(self.db.query(IamMembership).count(), 1)
        blocked = self.db.query(UsageEvent).filter(UsageEvent.event_name == "last_owner_change_blocked").one()
        self.assertEqual(json.loads(blocked.metadata_json)["result"], "blocked")


if __name__ == "__main__":
    unittest.main()
