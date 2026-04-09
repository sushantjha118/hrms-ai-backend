from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from datetime import datetime
from models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)          # admin | hr | employee | candidate
    status = Column(String, default="active")      # active | inactive | pending
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
