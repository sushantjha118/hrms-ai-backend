from flask import Blueprint, request, jsonify
from services.leave_service import (
    apply_leave, get_all_leaves, get_my_leaves, review_leave, get_leave_stats
)
from utils.auth_middleware import role_required, token_required

leave_bp = Blueprint("leave", __name__)


@leave_bp.route("", methods=["GET"])
@role_required("admin", "hr")
def list_leaves(current_user):
    filters = {
        "status": request.args.get("status"),
        "employee_id": request.args.get("employee_id"),
    }
    result, status = get_all_leaves({k: v for k, v in filters.items() if v})
    return jsonify(result), status


@leave_bp.route("/stats", methods=["GET"])
@role_required("admin", "hr")
def leave_stats(current_user):
    result, status = get_leave_stats()
    return jsonify(result), status


@leave_bp.route("/me", methods=["GET"])
@token_required
def my_leaves(current_user):
    result, status = get_my_leaves(current_user)
    return jsonify(result), status


@leave_bp.route("", methods=["POST"])
@token_required
def apply(current_user):
    result, status = apply_leave(request.json or {}, current_user)
    return jsonify(result), status


@leave_bp.route("/<int:leave_id>/review", methods=["PUT"])
@role_required("admin", "hr")
def review(current_user, leave_id):
    data = request.json or {}
    action = data.get("action")
    result, status = review_leave(leave_id, action, current_user.id)
    return jsonify(result), status
                                                                                                                                                                                                                                            