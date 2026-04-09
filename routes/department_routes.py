from flask import Blueprint, request, jsonify
from services.department_service import get_departments, add_department, update_department, delete_department
from utils.auth_middleware import role_required, token_required

department_bp = Blueprint("department", __name__)


@department_bp.route("", methods=["GET"])
@token_required
def list_departments(current_user):
    result, status = get_departments()
    return jsonify(result), status


@department_bp.route("", methods=["POST"])
@role_required("admin")
def create_department(current_user):
    result, status = add_department(request.json or {})
    return jsonify(result), status


@department_bp.route("/<int:dept_id>", methods=["PUT"])
@role_required("admin")
def edit_department(current_user, dept_id):
    result, status = update_department(dept_id, request.json or {})
    return jsonify(result), status


@department_bp.route("/<int:dept_id>", methods=["DELETE"])
@role_required("admin")
def remove_department(current_user, dept_id):
    result, status = delete_department(dept_id)
    return jsonify(result), status
