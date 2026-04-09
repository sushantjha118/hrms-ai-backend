from models.attendance_model import Attendance
from models.employee_model import Employee
from models.user_model import User
from models.department_model import Department
from db.db import get_db
from datetime import date, datetime


def _serialize(att, emp, user, dept):
    return {
        "id": att.id,
        "employee_id": att.employee_id,
        "name": user.name if user else None,
        "department": dept.name if dept else None,
        "date": att.date.isoformat() if att.date else None,
        "check_in": str(att.check_in) if att.check_in else None,
        "check_out": str(att.check_out) if att.check_out else None,
        "hours_worked": att.hours_worked,
        "status": att.status,
    }


def get_today_attendance():
    today = date.today()
    with get_db() as db:
        rows = (
            db.query(Attendance, Employee, User, Department)
            .join(Employee, Attendance.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id)
            .outerjoin(Department, Employee.department_id == Department.id)
            .filter(Attendance.date == today)
            .all()
        )
        return [_serialize(a, e, u, d) for a, e, u, d in rows], 200


def get_attendance_by_employee(employee_id):
    with get_db() as db:
        rows = (
            db.query(Attendance, Employee, User, Department)
            .join(Employee, Attendance.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id)
            .outerjoin(Department, Employee.department_id == Department.id)
            .filter(Attendance.employee_id == employee_id)
            .order_by(Attendance.date.desc())
            .all()
        )
        return [_serialize(a, e, u, d) for a, e, u, d in rows], 200


def mark_attendance(data):
    required = ["employee_id", "date", "status"]
    for field in required:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    with get_db() as db:
        att_date = date.fromisoformat(data["date"])
        existing = db.query(Attendance).filter(
            Attendance.employee_id == data["employee_id"],
            Attendance.date == att_date
        ).first()

        if existing:
            existing.status = data["status"]
            if data.get("check_in"):
                existing.check_in = datetime.strptime(data["check_in"], "%H:%M").time()
            if data.get("check_out"):
                existing.check_out = datetime.strptime(data["check_out"], "%H:%M").time()
            if data.get("hours_worked"):
                existing.hours_worked = data["hours_worked"]
            db.commit()
            return {"message": "Attendance updated"}, 200

        att = Attendance(
            employee_id=data["employee_id"],
            date=att_date,
            status=data["status"],
            check_in=datetime.strptime(data["check_in"], "%H:%M").time() if data.get("check_in") else None,
            check_out=datetime.strptime(data["check_out"], "%H:%M").time() if data.get("check_out") else None,
            hours_worked=data.get("hours_worked"),
        )
        db.add(att)
        db.commit()
        return {"message": "Attendance marked"}, 201


def get_attendance_stats():
    today = date.today()
    with get_db() as db:
        total_employees = db.query(Employee).filter(Employee.status == "active").count()
        today_records = db.query(Attendance).filter(Attendance.date == today).all()
        present = sum(1 for r in today_records if r.status == "present")
        absent = sum(1 for r in today_records if r.status == "absent")
        late = sum(1 for r in today_records if r.status == "late")
        return {
            "total_employees": total_employees,
            "present": present,
            "absent": absent,
            "late": late,
            "date": today.isoformat(),
        }, 200


def get_weekly_stats():
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    with get_db() as db:
        total_active = db.query(Employee).filter(Employee.status == "active").count()
        result = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            records = db.query(Attendance).filter(Attendance.date == day).all()
            present = sum(1 for r in records if r.status in ("present", "late"))
            pct = round((present / total_active * 100), 1) if total_active else 0
            result.append({"day": day.strftime("%a"), "date": day.isoformat(), "percentage": pct})
        return result, 200
