from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, TIMESTAMP
from datetime import datetime
from models.base import Base


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    location = Column(String, nullable=True)
    employment_type = Column(String, default="full-time")
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    status = Column(String, default="open")         # open | closed | draft
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="applied")      # applied | screening | interviewing | shortlisted | offered | rejected
    ai_score = Column(Float, nullable=True)
    resume_url = Column(String, nullable=True)
    cover_letter = Column(Text, nullable=True)
    applied_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
