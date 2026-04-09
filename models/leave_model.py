from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, TIMESTAMP
from datetime import datetime
from models.base import Base


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String, nullable=False)     # vacation | sick | personal | maternity | unpaid
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    duration_days = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String, default="pending")      # pending | approved | rejected
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
