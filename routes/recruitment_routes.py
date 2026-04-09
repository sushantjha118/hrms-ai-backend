from flask import Blueprint, request, jsonify
from services.recruitment_service import (
    create_job, get_jobs, update_job, delete_job,
    apply_for_job, get_applications, get_my_applications,
    update_application_status, get_recruitment_stats
)
from utils.auth_middleware import role_required, token_required

recruitment_bp = Blueprint("recruitment", __name__)


# --- Job Postings ---

@recruitment_bp.route("/jobs", methods=["GET"])
@token_required
def list_jobs(current_user):
    filters = {
        "status": request.args.get("status", "open"),
        "department_id": request.args.get("department_id"),
    }
    result, status = get_jobs({k: v for k, v in filters.items() if v})
    return jsonify(result), status


@recruitment_bp.route("/jobs/stats", methods=["GET"])
@role_required("admin", "hr")
def recruitment_stats(current_user):
    result, status = get_recruitment_stats()
    return jsonify(result), status


@recruitment_bp.route("/jobs", methods=["POST"])
@role_required("admin", "hr")
def post_job(current_user):
    result, status = create_job(request.json or {}, current_user.id)
    return jsonify(result), status


@recruitment_bp.route("/jobs/<int:job_id>", methods=["PUT"])
@role_required("admin", "hr")
def edit_job(current_user, job_id):
    result, status = update_job(job_id, request.json or {})
    return jsonify(result), status


@recruitment_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
@role_required("admin", "hr")
def close_job(current_user, job_id):
    result, status = delete_job(job_id)
    return jsonify(result), status


# --- Applications ---

@recruitment_bp.route("/applications", methods=["GET"])
@role_required("admin", "hr")
def list_applications(current_user):
    filters = {
        "job_id": request.args.get("job_id"),
        "status": request.args.get("status"),
    }
    result, status = get_applications({k: v for k, v in filters.items() if v})
    return jsonify(result), status


@recruitment_bp.route("/applications/me", methods=["GET"])
@role_required("candidate")
def my_applications(current_user):
    result, status = get_my_applications(current_user.id)
    return jsonify(result), status


@recruitment_bp.route("/applications", methods=["POST"])
@role_required("candidate")
def apply(current_user):
    result, status = apply_for_job(request.json or {}, current_user.id)
    return jsonify(result), status


@recruitment_bp.route("/applications/<int:app_id>", methods=["PUT"])
@role_required("admin", "hr")
def update_status(current_user, app_id):
    result, status = update_application_status(app_id, request.json or {})
    return jsonify(result), status
