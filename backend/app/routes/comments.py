from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User
from app.models.project import ProjectMember
from app.models.issue import Issue
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/issues/{issue_id}/comments", tags=["comments"])


def _get_issue_and_check_membership(db: Session, issue_id: int, user_id: int) -> Issue:
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Issue not found"})
    membership = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not a member of this project"})
    return issue


@router.get("", response_model=list[CommentOut])
def list_comments(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_issue_and_check_membership(db, issue_id, current_user.id)
    comments = (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.issue_id == issue_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return comments


@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    issue_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_issue_and_check_membership(db, issue_id, current_user.id)
    comment = Comment(issue_id=issue_id, author_id=current_user.id, body=data.body)
    db.add(comment)
    db.commit()
    db.refresh(comment, ["author"])
    return comment
