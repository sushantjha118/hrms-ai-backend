from sqlalchemy import Column, Integer, String, ForeignKey, Float, TIMESTAMP
from datetime import datetime
from models.base import Base


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month = Column(Integer, nullable=False)         # 1-12
    year = Column(Integer, nullable=False)
    basic_salary = Column(Float, nullable=False)
    allowances = Column(Float, default=0)
    deductions = Column(Float, default=0)
    net_salary = Column(Float, nullable=False)
    status = Column(String, default="generated")    # generated | paid
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)
