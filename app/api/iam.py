from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.telemetry_dashboard import require_dashboard_access
from app.core.database import get_db
from app.models.models import IamInvitation, IamMembership, IamPerson, IamWorkspace
from app.schemas.iam import (
    InvitationCreate, InvitationOut, MembershipUpdate, PersonCreate, PersonOut,
    PersonUpdate, WorkspaceCreate, WorkspaceOut, WorkspaceUpdate,
)
from app.services.usage_analytics import emit_backend_event


router = APIRouter(tags=["IAM"], dependencies=[Depends(require_dashboard_access)])


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))[:128]


def _person_or_404(db: Session, person_id: str) -> IamPerson:
    person = db.get(IamPerson, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return person


def _workspace_or_404(db: Session, workspace_id: str) -> IamWorkspace:
    workspace = db.get(IamWorkspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return workspace


@router.get("/pessoas", response_model=list[PersonOut])
def list_people(db: Session = Depends(get_db)):
    return db.query(IamPerson).order_by(IamPerson.created_at.desc()).all()


@router.post("/pessoas", response_model=PersonOut, status_code=201)
def create_person(data: PersonCreate, request: Request, db: Session = Depends(get_db)):
    person = IamPerson(
        id=str(uuid.uuid4()), display_name=data.display_name.strip(),
        email=data.email.strip().lower(), category=data.category, status="pending",
    )
    db.add(person)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Pessoa já cadastrada")
    db.refresh(person)
    emit_backend_event(db, "person_created", person_id=person.id, properties={
        "person_category": person.category,
        "creation_source": "admin_console",
        "has_workspace_role_reference": False,
    }, request_id=_request_id(request))
    return person


@router.patch("/pessoas/{person_id}", response_model=PersonOut)
def update_person(person_id: str, data: PersonUpdate, request: Request, db: Session = Depends(get_db)):
    person = _person_or_404(db, person_id)
    changed = []
    if data.display_name is not None:
        person.display_name = data.display_name.strip(); changed.append("basic_profile")
    if data.category is not None:
        person.category = data.category; changed.append("operational_role")
    if data.status is not None:
        person.status = data.status; changed.append("status")
    db.commit(); db.refresh(person)
    event_name = "person_archived" if data.status == "archived" else "person_updated"
    properties = {} if event_name == "person_archived" else {"changed_field_categories": sorted(set(changed))}
    emit_backend_event(db, event_name, person_id=person.id, properties=properties, request_id=_request_id(request))
    return person


@router.get("/workspaces", response_model=list[WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db)):
    return db.query(IamWorkspace).order_by(IamWorkspace.created_at.desc()).all()


@router.post("/workspaces", response_model=WorkspaceOut, status_code=201)
def create_workspace(data: WorkspaceCreate, request: Request, db: Session = Depends(get_db)):
    workspace = IamWorkspace(id=str(uuid.uuid4()), name=data.name.strip(), workspace_type=data.workspace_type, status="active")
    db.add(workspace); db.commit(); db.refresh(workspace)
    emit_backend_event(db, "workspace_created", workspace_id=workspace.id, properties={
        "workspace_type": workspace.workspace_type, "creation_source": "admin_console",
    }, request_id=_request_id(request))
    return workspace


@router.patch("/workspaces/{workspace_id}", response_model=WorkspaceOut)
def update_workspace(workspace_id: str, data: WorkspaceUpdate, request: Request, db: Session = Depends(get_db)):
    workspace = _workspace_or_404(db, workspace_id)
    changed = []
    if data.name is not None:
        workspace.name = data.name.strip(); changed.append("general")
    if data.status is not None:
        workspace.status = data.status; changed.append("general")
    db.commit(); db.refresh(workspace)
    event_name = "workspace_archived" if data.status == "archived" else "workspace_settings_saved"
    properties = {} if event_name == "workspace_archived" else {"changed_field_categories": sorted(set(changed))}
    emit_backend_event(db, event_name, workspace_id=workspace.id, properties=properties, request_id=_request_id(request))
    return workspace


@router.get("/workspaces/{workspace_id}/members")
def list_members(workspace_id: str, db: Session = Depends(get_db)):
    _workspace_or_404(db, workspace_id)
    memberships = db.query(IamMembership).filter(IamMembership.workspace_id == workspace_id).all()
    return [{
        "id": item.id, "workspace_id": item.workspace_id, "person_id": item.person_id,
        "role": item.role, "status": item.status,
        "person": {"display_name": item.person.display_name, "email": item.person.email},
    } for item in memberships]


@router.post("/workspaces/{workspace_id}/invitations", response_model=InvitationOut, status_code=201)
def create_invitation(workspace_id: str, data: InvitationCreate, request: Request, db: Session = Depends(get_db)):
    _workspace_or_404(db, workspace_id)
    person = _person_or_404(db, data.person_id)
    if person.status == "archived":
        raise HTTPException(status_code=409, detail="Pessoa arquivada")
    token = secrets.token_urlsafe(32)
    invitation = IamInvitation(
        id=str(uuid.uuid4()), workspace_id=workspace_id, person_id=person.id, role=data.role,
        token_hash=hashlib.sha256(token.encode()).hexdigest(), status="pending",
    )
    db.add(invitation); db.commit(); db.refresh(invitation)
    emit_backend_event(db, "workspace_member_invited", workspace_id=workspace_id, person_id=person.id, properties={
        "invited_role": data.role, "invitation_source": "admin_console",
        "is_first_team_invitation": db.query(IamInvitation).filter(IamInvitation.workspace_id == workspace_id).count() == 1,
    }, request_id=_request_id(request))
    return InvitationOut(
        invitation_id=invitation.id, invitation_token=token, workspace_id=workspace_id,
        person_id=person.id, role=data.role, status=invitation.status,
    )


@router.post("/invitations/{token}/accept")
def accept_invitation(token: str, request: Request, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    invitation = db.query(IamInvitation).filter(IamInvitation.token_hash == token_hash).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Convite não encontrado")
    if invitation.status != "pending":
        raise HTTPException(status_code=409, detail="Convite não está pendente")
    membership = db.query(IamMembership).filter(
        IamMembership.workspace_id == invitation.workspace_id,
        IamMembership.person_id == invitation.person_id,
    ).first()
    if membership:
        membership.role = invitation.role; membership.status = "active"
    else:
        membership = IamMembership(
            id=str(uuid.uuid4()), workspace_id=invitation.workspace_id,
            person_id=invitation.person_id, role=invitation.role, status="active",
        )
        db.add(membership)
    invitation.status = "accepted"; invitation.accepted_at = datetime.now(timezone.utc)
    invitation.person.status = "active"
    db.commit(); db.refresh(membership)
    accepted_at = invitation.accepted_at if invitation.accepted_at.tzinfo else invitation.accepted_at.replace(tzinfo=timezone.utc)
    created_at = invitation.created_at if invitation.created_at.tzinfo else invitation.created_at.replace(tzinfo=timezone.utc)
    elapsed = (accepted_at - created_at).total_seconds()
    bucket = "under_10_minutes" if elapsed < 600 else "10_minutes_to_1_hour" if elapsed < 3600 else "1_to_24_hours" if elapsed < 86400 else "1_to_7_days" if elapsed < 604800 else "over_7_days"
    emit_backend_event(db, "workspace_member_invitation_accepted", workspace_id=invitation.workspace_id, person_id=invitation.person_id, properties={
        "accepted_role": invitation.role, "time_to_accept_bucket": bucket,
    }, request_id=_request_id(request))
    return {"accepted": True, "membership_id": membership.id}


@router.patch("/workspaces/{workspace_id}/members/{membership_id}")
def update_membership(workspace_id: str, membership_id: str, data: MembershipUpdate, request: Request, db: Session = Depends(get_db)):
    membership = db.query(IamMembership).filter(IamMembership.id == membership_id, IamMembership.workspace_id == workspace_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership não encontrada")
    previous = membership.role
    if previous == "owner" and data.role != "owner":
        owners = db.query(IamMembership).filter(IamMembership.workspace_id == workspace_id, IamMembership.role == "owner", IamMembership.status == "active").count()
        if owners == 1:
            emit_backend_event(db, "last_owner_change_blocked", workspace_id=workspace_id, person_id=membership.person_id, properties={"conflict_type": "last_owner", "result": "blocked"}, request_id=_request_id(request))
            raise HTTPException(status_code=409, detail="O último owner não pode perder o papel")
    membership.role = data.role; db.commit(); db.refresh(membership)
    emit_backend_event(db, "workspace_member_role_changed", workspace_id=workspace_id, person_id=membership.person_id, properties={
        "previous_role": previous, "new_role": data.role, "change_source": "admin_console",
    }, request_id=_request_id(request))
    return {"id": membership.id, "role": membership.role, "status": membership.status}


@router.delete("/workspaces/{workspace_id}/members/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(workspace_id: str, membership_id: str, request: Request, db: Session = Depends(get_db)):
    membership = db.query(IamMembership).filter(IamMembership.id == membership_id, IamMembership.workspace_id == workspace_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership não encontrada")
    if membership.role == "owner":
        owners = db.query(IamMembership).filter(IamMembership.workspace_id == workspace_id, IamMembership.role == "owner", IamMembership.status == "active").count()
        if owners == 1:
            emit_backend_event(db, "last_owner_change_blocked", workspace_id=workspace_id, person_id=membership.person_id, properties={"conflict_type": "last_owner", "result": "blocked"}, request_id=_request_id(request))
            raise HTTPException(status_code=409, detail="O último owner não pode ser removido")
    role, person_id = membership.role, membership.person_id
    db.delete(membership); db.commit()
    emit_backend_event(db, "workspace_member_removed", workspace_id=workspace_id, person_id=person_id, properties={
        "removed_role": role, "removal_source": "admin_console",
    }, request_id=_request_id(request))
