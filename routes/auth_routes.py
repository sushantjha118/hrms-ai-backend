from flask import Blueprint, request, jsonify
from services.auth_service import register_user, login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    result, status = register_user(data)
    return jsonify(result), status


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = login_user(data)

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify(user)