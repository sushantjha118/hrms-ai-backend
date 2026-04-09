from models.employee_model import Employee
from models.user_model import User
from models.department_model import Department
from db.db import get_db
from datetime import date


def _serialize(emp, user, dept):
    return {
        "id": emp.id,
        "user_id": emp.user_id,
        "name": user.name if user else None,
        "email": user.email if user else None,
        "department": dept.name if dept else None,
        "department_id": emp.department_id,
        "designation": emp.designation,
        "employment_type": emp.employment_type,
        "salary": emp.salary,
        "joining_date": emp.joining_date.isoformat() if emp.joining_date else None,
        "phone": emp.phone,
        "location": emp.location,
        "address": emp.address,
        "skills": emp.skills.split(",") if emp.skills else [],
        "profile_photo": emp.profile_photo,
        "manager_id": emp.manager_id,
        "status": emp.status,
    }


def add_employee(data):
    required = ["user_id", "designation"]
    for field in required:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    with get_db() as db:
        if db.query(Employee).filter(Employee.user_id == data["user_id"]).first():
            return {"error": "Employee profile already exists for this user"}, 409

        emp = Employee(
            user_id=data["user_id"],
            department_id=data.get("department_id"),
            designation=data["designation"],
            employment_type=data.get("employment_type", "full-time"),
            salary=data.get("salary", 0),
            joining_date=date.fromisoformat(data["joining_date"]) if data.get("joining_date") else None,
            phone=data.get("phone"),
            location=data.get("location"),
            address=data.get("address"),
            skills=",".join(data["skills"]) if isinstance(data.get("skills"), list) else data.get("skills"),
            manager_id=data.get("manager_id"),
            status=data.get("status", "active"),
        )
        db.add(emp)
        db.commit()
        db.refresh(emp)
        return {"message": "Employee added successfully", "id": emp.id}, 201


def get_employees(filters=None):
    with get_db() as db:
        query = (
            db.query(Employee, User, Department)
            .join(User, Employee.user_id == User.id)
            .outerjoin(Department, Employee.department_id == Department.id)
        )
        if filters:
            if filters.get("department_id"):
                query = query.filter(Employee.department_id == filters["department_id"])
            if filters.get("status"):
                query = query.filter(Employee.status == filters["status"])
            if filters.get("location"):
                query = query.filter(Employee.location.ilike(f"%{filters['location']}%"))
        results = query.all()
        return [_serialize(emp, user, dept) for emp, user, dept in results], 200


def get_employee_by_user_id(user_id):
    with get_db() as db:
        row = (
            db.query(Employee, User, Department)
            .join(User, Employee.user_id == User.id)
            .outerjoin(Department, Employee.department_id == Department.id)
            .filter(Employee.user_id == user_id)
            .first()
        )
        if not row:
            return {"error": "Employee not found"}, 404
        emp, user, dept = row
        return _serialize(emp, user, dept), 200


def get_employee_by_id(emp_id):
    with get_db() as db:
        row = (
            db.query(Employee, User, Department)
            .join(User, Employee.user_id == User.id)
            .outerjoin(Department, Employee.department_id == Department.id)
            .filter(Employee.id == emp_id)
            .first()
        )
        if not row:
            return {"error": "Employee not found"}, 404
        emp, user, dept = row
        return _serialize(emp, user, dept), 200


def update_employee(emp_id, data):
    with get_db() as db:
        emp = db.query(Employee).filter(Employee.id == emp_id).first()
        if not emp:
            return {"error": "Employee not found"}, 404

        fields = ["department_id", "designation", "employment_type", "salary",
                  "phone", "location", "address", "manager_id", "status", "profile_photo"]
        for field in fields:
            if field in data:
                setattr(emp, field, data[field])

        if "skills" in data:
            emp.skills = ",".join(data["skills"]) if isinstance(data["skills"], list) else data["skills"]
        if "joining_date" in data and data["joining_date"]:
            emp.joining_date = date.fromisoformat(data["joining_date"])

        db.commit()
        return {"message": "Employee updated"}, 200


def delete_employee(emp_id):
    with get_db() as db:
        emp = db.query(Employee).filter(Employee.id == emp_id).first()
        if not emp:
            return {"error": "Employee not found"}, 404
        emp.status = "inactive"
        db.commit()
        return {"message": "Employee deactivated"}, 200


def get_employee_stats():
    with get_db() as db:
        total = db.query(Employee).count()
        active = db.query(Employee).filter(Employee.status == "active").count()
        return {"total": total, "active": active}, 200
