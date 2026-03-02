from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User
from app.models.project import ProjectMember, MemberRole
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.schemas.issue import IssueCreate, IssueUpdate, IssueOut, IssuePaginatedOut
from app.dependencies import get_current_user

router = APIRouter(tags=["issues"])


def _require_membership(db: Session, project_id: int, user_id: int) -> ProjectMember:
    m = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if not m:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not a member of this project"})
    return m


@router.get("/api/projects/{project_id}/issues", response_model=IssuePaginatedOut)
def list_issues(
    project_id: int,
    q: Optional[str] = Query(None, description="Text search in title"),
    issue_status: Optional[IssueStatus] = Query(None, alias="status"),
    priority: Optional[IssuePriority] = None,
    assignee: Optional[int] = None,
    sort: Optional[str] = Query("created_at", pattern="^(created_at|priority|status)$"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_membership(db, project_id, current_user.id)
    query = db.query(Issue).filter(Issue.project_id == project_id)

    if q:
        query = query.filter(Issue.title.ilike(f"%{q}%"))
    if issue_status:
        query = query.filter(Issue.status == issue_status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if assignee:
        query = query.filter(Issue.assignee_id == assignee)

    total = query.count()

    sort_col = getattr(Issue, sort, Issue.created_at)
    if order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    items = (
        query.options(joinedload(Issue.reporter), joinedload(Issue.assignee))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return IssuePaginatedOut(items=items, total=total, page=page, page_size=page_size)


@router.post("/api/projects/{project_id}/issues", response_model=IssueOut, status_code=status.HTTP_201_CREATED)
def create_issue(
    project_id: int,
    data: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_membership(db, project_id, current_user.id)
    issue = Issue(
        project_id=project_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        reporter_id=current_user.id,
        assignee_id=data.assignee_id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    # Eager load relationships
    db.refresh(issue, ["reporter", "assignee"])
    return issue


@router.get("/api/issues/{issue_id}", response_model=IssueOut)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = (
        db.query(Issue)
        .options(joinedload(Issue.reporter), joinedload(Issue.assignee))
        .filter(Issue.id == issue_id)
        .first()
    )
    if not issue:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Issue not found"})
    _require_membership(db, issue.project_id, current_user.id)
    return issue


@router.patch("/api/issues/{issue_id}", response_model=IssueOut)
def update_issue(
    issue_id: int,
    data: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Issue not found"})

    membership = _require_membership(db, issue.project_id, current_user.id)

    # Only reporter can update title/description; maintainers can update anything
    is_maintainer = membership.role == MemberRole.maintainer
    is_reporter = issue.reporter_id == current_user.id

    if not is_maintainer and not is_reporter:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not allowed to update this issue"})

    update_data = data.model_dump(exclude_unset=True)

    # Non-maintainers can only update title, description, and priority
    if not is_maintainer:
        restricted = {"status", "assignee_id"}
        if restricted & update_data.keys():
            raise HTTPException(
                status_code=403,
                detail={"code": "FORBIDDEN", "message": "Only maintainers can change status or assignee"},
            )

    for key, value in update_data.items():
        setattr(issue, key, value)

    db.commit()
    db.refresh(issue, ["reporter", "assignee"])
    return issue


@router.delete("/api/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Issue not found"})

    membership = _require_membership(db, issue.project_id, current_user.id)
    is_maintainer = membership.role == MemberRole.maintainer
    is_reporter = issue.reporter_id == current_user.id

    if not is_maintainer and not is_reporter:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not allowed to delete this issue"})

    db.delete(issue)
    db.commit()
