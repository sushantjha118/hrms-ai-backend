from models.department_model import Department
from models.user_model import User
from db.db import get_db


def get_departments():
    with get_db() as db:
        depts = db.query(Department).all()
        return [
            {"id": d.id, "name": d.name, "head_id": d.head_id}
            for d in depts
        ], 200


def add_department(data):
    if not data.get("name"):
        return {"error": "name is required"}, 400
    with get_db() as db:
        if db.query(Department).filter(Department.name == data["name"]).first():
            return {"error": "Department already exists"}, 409
        dept = Department(name=data["name"], head_id=data.get("head_id"))
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return {"message": "Department created", "id": dept.id}, 201


def update_department(dept_id, data):
    with get_db() as db:
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if not dept:
            return {"error": "Department not found"}, 404
        if "name" in data:
            dept.name = data["name"]
        if "head_id" in data:
            dept.head_id = data["head_id"]
        db.commit()
        return {"message": "Department updated"}, 200


def delete_department(dept_id):
    with get_db() as db:
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if not dept:
            return {"error": "Department not found"}, 404
        db.delete(dept)
        db.commit()
        return {"message": "Department deleted"}, 200
