from flask import Blueprint, request, jsonify
from services.attendance_service import (
    get_today_attendance, get_attendance_by_employee,
    mark_attendance, get_attendance_stats, get_weekly_stats
)
from utils.auth_middleware import role_required, token_required

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/today", methods=["GET"])
@role_required("admin", "hr")
def today_attendance(current_user):
    result, status = get_today_attendance()
    return jsonify(result), status


@attendance_bp.route("/stats", methods=["GET"])
@role_required("admin", "hr")
def attendance_stats(current_user):
    result, status = get_attendance_stats()
    return jsonify(result), status


@attendance_bp.route("/weekly", methods=["GET"])
@role_required("admin", "hr")
def weekly_stats(current_user):
    result, status = get_weekly_stats()
    return jsonify(result), status


@attendance_bp.route("/employee/<int:employee_id>", methods=["GET"])
@role_required("admin", "hr")
def employee_attendance(current_user, employee_id):
    result, status = get_attendance_by_employee(employee_id)
    return jsonify(result), status


@attendance_bp.route("/me", methods=["GET"])
@token_required
def my_attendance(current_user):
    from models.employee_model import Employee
    from db.db import get_db
    with get_db() as db:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp:
            return jsonify({"error": "Employee profile not found"}), 404
        emp_id = emp.id
    result, status = get_attendance_by_employee(emp_id)
    return jsonify(result), status


@attendance_bp.route("", methods=["POST"])
@role_required("admin", "hr")
def mark(current_user):
    result, status = mark_attendance(request.json or {})
    return jsonify(result), status
