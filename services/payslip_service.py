from models.payslip_model import Payslip
from models.employee_model import Employee
from models.user_model import User
from db.db import get_db


def _serialize(payslip, emp, user):
    return {
        "id": payslip.id,
        "employee_id": payslip.employee_id,
        "name": user.name if user else None,
        "designation": emp.designation if emp else None,
        "month": payslip.month,
        "year": payslip.year,
        "basic_salary": payslip.basic_salary,
        "allowances": payslip.allowances,
        "deductions": payslip.deductions,
        "net_salary": payslip.net_salary,
        "status": payslip.status,
        "generated_at": payslip.generated_at.isoformat() if payslip.generated_at else None,
    }


def generate_payslip(data):
    required = ["employee_id", "month", "year", "basic_salary", "net_salary"]
    for field in required:
        if data.get(field) is None:
            return {"error": f"{field} is required"}, 400

    with get_db() as db:
        existing = db.query(Payslip).filter(
            Payslip.employee_id == data["employee_id"],
            Payslip.month == data["month"],
            Payslip.year == data["year"],
        ).first()
        if existing:
            return {"error": "Payslip already generated for this period"}, 409

        payslip = Payslip(
            employee_id=data["employee_id"],
            month=data["month"],
            year=data["year"],
            basic_salary=data["basic_salary"],
            allowances=data.get("allowances", 0),
            deductions=data.get("deductions", 0),
            net_salary=data["net_salary"],
            status=data.get("status", "generated"),
        )
        db.add(payslip)
        db.commit()
        return {"message": "Payslip generated"}, 201


def get_my_payslips(current_user):
    with get_db() as db:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp:
            return [], 200
        rows = (
            db.query(Payslip, Employee, User)
            .join(Employee, Payslip.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id)
            .filter(Payslip.employee_id == emp.id)
            .order_by(Payslip.year.desc(), Payslip.month.desc())
            .all()
        )
        return [_serialize(p, e, u) for p, e, u in rows], 200


def get_all_payslips():
    with get_db() as db:
        rows = (
            db.query(Payslip, Employee, User)
            .join(Employee, Payslip.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id)
            .order_by(Payslip.year.desc(), Payslip.month.desc())
            .all()
        )
        return [_serialize(p, e, u) for p, e, u in rows], 200
