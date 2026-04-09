from sqlalchemy import Column, Integer, String, ForeignKey, Date, TIMESTAMP, Text
from datetime import datetime
from models.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    designation = Column(String, nullable=False)
    employment_type = Column(String, default="full-time")   # full-time | part-time | contract
    salary = Column(Integer, default=0)
    joining_date = Column(Date, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)                    # comma-separated
    profile_photo = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="active")               # active | inactive
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
