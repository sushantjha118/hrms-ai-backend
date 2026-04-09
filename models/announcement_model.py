from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from datetime import datetime
from models.base import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String, default="Company Update")   # Company Update | Events | Policy | Alert
    target_role = Column(String, default="all")           # all | employee | hr | admin | candidate
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
