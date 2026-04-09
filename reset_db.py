from dotenv import load_dotenv
load_dotenv()
from db.db import engine
from sqlalchemy import text
from models.base import Base
import models.user_model, models.department_model, models.employee_model
import models.attendance_model, models.leave_model, models.performance_model
import models.recruitment_model, models.announcement_model, models.payslip_model

with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))
    conn.commit()

Base.metadata.create_all(engine)
print("Schema reset and all tables recreated.")
