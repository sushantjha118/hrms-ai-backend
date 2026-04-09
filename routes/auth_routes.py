from flask import Blueprint, request, jsonify
from services.auth_service import (
    register_user, login_user, create_user_by_admin,
    get_all_users, update_user_status, delete_user
)
from utils.auth_middleware import role_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    result, status = register_user(request.json or {})
    return jsonify(result), status


@auth_bp.route("/login", methods=["POST"])
def login():
    result, status = login_user(request.json or {})
    return jsonify(result), status


# Admin-only: create any role
@auth_bp.route("/users", methods=["POST"])
@role_required("admin")
def admin_create_user(current_user):
    result, status = create_user_by_admin(request.json or {})
    return jsonify(result), status


@auth_bp.route("/users", methods=["GET"])
@role_required("admin")
def admin_list_users(current_user):
    result, status = get_all_users()
    return jsonify(result), status


@auth_bp.route("/users/<int:user_id>", methods=["PUT"])
@role_required("admin")
def admin_update_user(current_user, user_id):
    result, status = update_user_status(user_id, request.json or {})
    return jsonify(result), status


@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@role_required("admin")
def admin_delete_user(current_user, user_id):
    result, status = delete_user(user_id)
    return jsonify(result), status
