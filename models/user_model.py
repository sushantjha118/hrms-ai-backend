from sqlalchemy import Column, Integer, String, TIMESTAMP
from db.db import engine
from datetime import datetime
from models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    token = Column(String, nullable=True)
    token_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
