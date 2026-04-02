from sqlalchemy import Column, Integer, String, ForeignKey, Date
from db.db import engine
from models.base import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    department = Column(String)
    designation = Column(String)
    salary = Column(Integer)
    joining_date = Column(Date)
