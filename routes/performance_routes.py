from flask import Blueprint, request, jsonify
from services.performance_service import (
    create_review, get_all_reviews, get_my_reviews, update_review, get_performance_stats
)
from utils.auth_middleware import role_required, token_required

performance_bp = Blueprint("performance", __name__)


@performance_bp.route("", methods=["GET"])
@role_required("admin", "hr")
def list_reviews(current_user):
    filters = {
        "status": request.args.get("status"),
        "employee_id": request.args.get("employee_id"),
    }
    result, status = get_all_reviews({k: v for k, v in filters.items() if v})
    return jsonify(result), status


@performance_bp.route("/stats", methods=["GET"])
@role_required("admin", "hr")
def perf_stats(current_user):
    result, status = get_performance_stats()
    return jsonify(result), status


@performance_bp.route("/me", methods=["GET"])
@token_required
def my_reviews(current_user):
    result, status = get_my_reviews(current_user)
    return jsonify(result), status


@performance_bp.route("", methods=["POST"])
@role_required("admin", "hr")
def create(current_user):
    result, status = create_review(request.json or {})
    return jsonify(result), status


@performance_bp.route("/<int:review_id>", methods=["PUT"])
@role_required("admin", "hr")
def update(current_user, review_id):
    result, status = update_review(review_id, request.json or {})
    return jsonify(result), status
