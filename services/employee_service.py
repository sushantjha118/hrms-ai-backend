from models.employee_model import Employee
from db.db import get_db
from datetime import date

def add_employee(data):
    with get_db() as db:
        employee = Employee(
            user_id=data['user_id'],
            department=data['department'],
            designation=data['designation'],
            salary=data['salary'],
            joining_date=date.fromisoformat(data['joining_date'])
        )
        db.add(employee)
        db.commit()

    return {"message": "Employee added successfully"}


def get_employees():
    with get_db() as db:
        employees = db.query(Employee).all()
        return [
            {
                "id": emp.id,
                "user_id": emp.user_id,
                "department": emp.department,
                "designation": emp.designation,
                "salary": emp.salary
            }
            for emp in employees
        ]


def update_employee(emp_id, data):
    with get_db() as db:
        emp = db.query(Employee).filter(Employee.id == emp_id).first()

        if not emp:
            return None

        emp.department = data.get('department', emp.department)
        emp.designation = data.get('designation', emp.designation)
        emp.salary = data.get('salary', emp.salary)
        db.commit()

    return {"message": "Employee updated"}
