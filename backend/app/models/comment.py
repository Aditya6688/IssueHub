from datetime import datetime, timezone

from sqlalchemy import Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")
