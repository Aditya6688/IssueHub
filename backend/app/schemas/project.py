from datetime import datetime

from pydantic import BaseModel

from app.models.project import MemberRole


class ProjectCreate(BaseModel):
    name: str
    key: str
    description: str = ""


class ProjectOut(BaseModel):
    id: int
    name: str
    key: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberAdd(BaseModel):
    email: str
    role: MemberRole = MemberRole.member


class MemberOut(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    role: MemberRole


class ProjectDetailOut(ProjectOut):
    members: list[MemberOut] = []
