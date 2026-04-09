from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, TIMESTAMP
from datetime import datetime
from models.base import Base


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    period = Column(String, nullable=False)         # e.g. "Q3-2024"
    score = Column(Float, nullable=True)            # 0.0 - 5.0
    status = Column(String, default="scheduled")    # scheduled | in-draft | completed
    notes = Column(Text, nullable=True)
    review_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
