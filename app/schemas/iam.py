from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PersonCategory = Literal["internal_collaborator", "supplier_contact", "production_contact", "review_contact", "other"]
PersonStatus = Literal["pending", "active", "archived"]
WorkspaceType = Literal["individual", "team"]
MemberRole = Literal["viewer", "member", "admin", "owner"]


class PersonCreate(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    category: PersonCategory = "internal_collaborator"


class PersonUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=120)
    category: PersonCategory | None = None
    status: PersonStatus | None = None


class PersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    display_name: str
    email: str
    category: str
    status: str
    created_at: datetime


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    workspace_type: WorkspaceType = "team"


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    status: Literal["active", "archived"] | None = None


class WorkspaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    workspace_type: str
    status: str
    created_at: datetime


class InvitationCreate(BaseModel):
    person_id: str
    role: MemberRole


class InvitationOut(BaseModel):
    invitation_id: str
    invitation_token: str
    workspace_id: str
    person_id: str
    role: str
    status: str


class MembershipUpdate(BaseModel):
    role: MemberRole
