from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from datetime import datetime
from models.base import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    head_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
