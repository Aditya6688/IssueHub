from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    memberships = relationship("ProjectMember", back_populates="user")
    reported_issues = relationship(
        "Issue", back_populates="reporter", foreign_keys="Issue.reporter_id"
    )
    assigned_issues = relationship(
        "Issue", back_populates="assignee", foreign_keys="Issue.assignee_id"
    )
    comments = relationship("Comment", back_populates="author")
