from flask import Blueprint, request, jsonify
from services.announcement_service import create_announcement, get_announcements, delete_announcement
from utils.auth_middleware import role_required, token_required

announcement_bp = Blueprint("announcement", __name__)


@announcement_bp.route("", methods=["GET"])
@token_required
def list_announcements(current_user):
    result, status = get_announcements(role=current_user.role)
    return jsonify(result), status


@announcement_bp.route("", methods=["POST"])
@role_required("admin", "hr")
def create(current_user):
    result, status = create_announcement(request.json or {}, current_user.id)
    return jsonify(result), status


@announcement_bp.route("/<int:ann_id>", methods=["DELETE"])
@role_required("admin", "hr")
def delete(current_user, ann_id):
    result, status = delete_announcement(ann_id)
    return jsonify(result), status
