from flask import Blueprint, request, jsonify
from services.employee_service import (
    add_employee, get_employees, get_employee_by_id,
    get_employee_by_user_id, update_employee, delete_employee, get_employee_stats
)
from utils.auth_middleware import role_required, token_required

employee_bp = Blueprint("employee", __name__)


@employee_bp.route("", methods=["GET"])
@role_required("admin", "hr")
def list_employees(current_user):
    filters = {
        "department_id": request.args.get("department_id"),
        "status": request.args.get("status"),
        "location": request.args.get("location"),
    }
    result, status = get_employees({k: v for k, v in filters.items() if v})
    return jsonify(result), status


@employee_bp.route("/stats", methods=["GET"])
@role_required("admin", "hr")
def employee_stats(current_user):
    result, status = get_employee_stats()
    return jsonify(result), status


@employee_bp.route("/me", methods=["GET"])
@token_required
def my_profile(current_user):
    result, status = get_employee_by_user_id(current_user.id)
    return jsonify(result), status


@employee_bp.route("/<int:emp_id>", methods=["GET"])
@role_required("admin", "hr")
def get_employee(current_user, emp_id):
    result, status = get_employee_by_id(emp_id)
    return jsonify(result), status


@employee_bp.route("", methods=["POST"])
@role_required("admin", "hr")
def create_employee(current_user):
    result, status = add_employee(request.json or {})
    return jsonify(result), status


@employee_bp.route("/<int:emp_id>", methods=["PUT"])
@role_required("admin", "hr")
def edit_employee(current_user, emp_id):
    result, status = update_employee(emp_id, request.json or {})
    return jsonify(result), status


@employee_bp.route("/<int:emp_id>", methods=["DELETE"])
@role_required("admin")
def remove_employee(current_user, emp_id):
    result, status = delete_employee(emp_id)
    return jsonify(result), status
