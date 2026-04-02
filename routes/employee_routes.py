from flask import Blueprint, request, jsonify
from services.employee_service import add_employee, get_employees, update_employee
from utils.auth_middleware import token_required

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/add', methods=['POST'])
@token_required
def create_employee():
    data = request.json
    return jsonify(add_employee(data))


@employee_bp.route('/list', methods=['GET'])
@token_required
def list_employees():
    return jsonify(get_employees())


@employee_bp.route('/update/<int:emp_id>', methods=['PUT'])
@token_required
def edit_employee(emp_id):
    data = request.json
    result = update_employee(emp_id, data)

    if not result:
        return jsonify({"message": "Employee not found"}), 404

    return jsonify(result)
