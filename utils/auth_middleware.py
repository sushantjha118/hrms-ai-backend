from functools import wraps
from flask import request, jsonify
from models.user_model import User
from db.db import get_db

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"error": "Token is missing"}), 401

        with get_db() as db:
            user = db.query(User).filter(User.token == token).first()
            if not user:
                return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)
    return decorated
