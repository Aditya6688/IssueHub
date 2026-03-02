from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectMember, MemberRole
from app.schemas.project import ProjectCreate, ProjectOut, ProjectDetailOut, MemberAdd, MemberOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _get_membership(db: Session, project_id: int, user_id: int) -> ProjectMember | None:
    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.query(Project).filter(Project.key == data.key.upper()).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "KEY_EXISTS", "message": "Project key already in use"},
        )
    project = Project(name=data.name, key=data.key.upper(), description=data.description)
    db.add(project)
    db.flush()
    membership = ProjectMember(
        project_id=project.id, user_id=current_user.id, role=MemberRole.maintainer
    )
    db.add(membership)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_ids = (
        db.query(ProjectMember.project_id)
        .filter(ProjectMember.user_id == current_user.id)
        .scalar_subquery()
    )
    projects = db.query(Project).filter(Project.id.in_(project_ids)).order_by(Project.created_at.desc()).all()
    return projects


@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Project not found"})
    membership = _get_membership(db, project_id, current_user.id)
    if not membership:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not a member of this project"})
    members = []
    for m in project.members:
        members.append(
            MemberOut(user_id=m.user.id, user_name=m.user.name, user_email=m.user.email, role=m.role)
        )
    return ProjectDetailOut(
        id=project.id,
        name=project.name,
        key=project.key,
        description=project.description,
        created_at=project.created_at,
        members=members,
    )


@router.post("/{project_id}/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: int,
    data: MemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = _get_membership(db, project_id, current_user.id)
    if not membership or membership.role != MemberRole.maintainer:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only maintainers can add members"})

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "No user with that email"})

    existing = _get_membership(db, project_id, user.id)
    if existing:
        raise HTTPException(status_code=409, detail={"code": "ALREADY_MEMBER", "message": "User is already a member"})

    pm = ProjectMember(project_id=project_id, user_id=user.id, role=data.role)
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return MemberOut(user_id=user.id, user_name=user.name, user_email=user.email, role=pm.role)
