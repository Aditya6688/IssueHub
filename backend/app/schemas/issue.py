from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.issue import IssueStatus, IssuePriority


class IssueCreate(BaseModel):
    title: str
    description: str = ""
    priority: IssuePriority = IssuePriority.medium
    assignee_id: Optional[int] = None


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[int] = None


class IssueUserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class IssueOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: str
    status: IssueStatus
    priority: IssuePriority
    reporter_id: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    reporter: IssueUserOut
    assignee: Optional[IssueUserOut] = None

    model_config = {"from_attributes": True}


class IssuePaginatedOut(BaseModel):
    items: list[IssueOut]
    total: int
    page: int
    page_size: int
