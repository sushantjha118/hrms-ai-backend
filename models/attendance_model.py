from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, TIMESTAMP
from datetime import datetime
from models.base import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)
    status = Column(String, default="present")   # present | absent | late | half-day
    hours_worked = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
