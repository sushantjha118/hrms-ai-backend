from models.leave_model import LeaveRequest
from models.employee_model import Employee
from models.user_model import User
from db.db import get_db
from datetime import date, datetime


def _serialize(leave, emp, user):
    return {
        "id": leave.id,
        "employee_id": leave.employee_id,
        "name": user.name if user else None,
        "designation": emp.designation if emp else None,
        "leave_type": leave.leave_type,
        "start_date": leave.start_date.isoformat() if leave.start_date else None,
        "end_date": leave.end_date.isoformat() if leave.end_date else None,
        "duration_days": leave.duration_days,
        "reason": leave.reason,
        "status": leave.status,
        "reviewed_by": leave.reviewed_by,
        "reviewed_at": leave.reviewed_at.isoformat() if leave.reviewed_at else None,
        "created_at": leave.created_at.isoformat() if leave.created_at else None,
    }


def apply_leave(data, current_user):
    required = ["leave_type", "start_date", "end_date"]
    for field in required:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    with get_db() as db:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp:
            return {"error": "Employee profile not found"}, 404

        start = date.fromisoformat(data["start_date"])
        end = date.fromisoformat(data["end_date"])
        if end < start:
            return {"error": "end_date must be after start_date"}, 400

        duration = (end - start).days + 1
        leave = LeaveRequest(
            employee_id=emp.id,
            leave_type=data["leave_type"],
            start_date=start,
            end_date=end,
            duration_days=duration,
            reason=data.get("reason"),
            status="pending",
        )
        db.add(leave)
        db.commit()
        return {"message": "Leave request submitted", "duration_days": duration}, 201


def get_all_leaves(filters=None):
    with get_db() as db:
        query = (
            db.query(LeaveRequest, Employee, User)
            .join(Employee, LeaveRequest.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id)
        )
        if filters:
            if filters.get("status"):
                query = query.filter(LeaveRequest.status == filters["status"])
            if filters.get("employee_id"):
                query = query.filter(LeaveRequest.employee_id == filters["employee_id"])
        rows = query.order_by(LeaveRequest.created_at.desc()).all()
        return [_serialize(l, e, u) for l, e, u in rows], 200


def get_my_leaves(current_user):
    with get_db() as db:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp:
            return [], 200
        rows = (
            db.query(LeaveRequest, Employee, User)
            .join(Employee, LeaveRequest.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id)
            .filter(LeaveRequest.employee_id == emp.id)
            .order_by(LeaveRequest.created_at.desc())
            .all()
        )
        return [_serialize(l, e, u) for l, e, u in rows], 200


def review_leave(leave_id, action, reviewer_id):
    if action not in ("approved", "rejected"):
        return {"error": "action must be 'approved' or 'rejected'"}, 400
    with get_db() as db:
        leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
        if not leave:
            return {"error": "Leave request not found"}, 404
        if leave.status != "pending":
            return {"error": "Only pending requests can be reviewed"}, 400
        leave.status = action
        leave.reviewed_by = reviewer_id
        leave.reviewed_at = datetime.utcnow()
        db.commit()
        return {"message": f"Leave {action}"}, 200


def get_leave_stats():
    with get_db() as db:
        today = date.today()
        pending = db.query(LeaveRequest).filter(LeaveRequest.status == "pending").count()
        on_leave_today = db.query(LeaveRequest).filter(
            LeaveRequest.status == "approved",
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today,
        ).count()
        monthly = db.query(LeaveRequest).filter(
            LeaveRequest.created_at >= date(today.year, today.month, 1)
        ).count()
        return {"pending": pending, "on_leave_today": on_leave_today, "monthly_requests": monthly}, 200
