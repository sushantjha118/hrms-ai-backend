from flask import Blueprint, request, jsonify
from services.payslip_service import generate_payslip, get_my_payslips, get_all_payslips
from utils.auth_middleware import role_required, token_required

payslip_bp = Blueprint("payslip", __name__)


@payslip_bp.route("", methods=["GET"])
@role_required("admin", "hr")
def list_payslips(current_user):
    result, status = get_all_payslips()
    return jsonify(result), status


@payslip_bp.route("/me", methods=["GET"])
@token_required
def my_payslips(current_user):
    result, status = get_my_payslips(current_user)
    return jsonify(result), status


@payslip_bp.route("", methods=["POST"])
@role_required("admin", "hr")
def create_payslip(current_user):
    result, status = generate_payslip(request.json or {})
    return jsonify(result), status
