from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    body: str


class CommentAuthorOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class CommentOut(BaseModel):
    id: int
    issue_id: int
    author_id: int
    body: str
    created_at: datetime
    author: CommentAuthorOut

    model_config = {"from_attributes": True}
