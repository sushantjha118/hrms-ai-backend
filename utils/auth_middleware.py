from functools import wraps
import jwt
from flask import request, jsonify
from models.user_model import User
from db.db import get_db
from config import JWT_SECRET_KEY


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        with get_db() as db:
            user = db.query(User).filter(User.id == payload["user_id"]).first()
            if not user or not user.is_active:
                return jsonify({"error": "User not found or inactive"}), 401
            # Detach from session so it can be used outside context
            db.expunge(user)

        return f(current_user=user, *args, **kwargs)
    return decorated


def role_required(*roles):
    """Usage: @role_required('admin') or @role_required('admin', 'hr')"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
            if not token:
                return jsonify({"error": "Token is missing"}), 401
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401

            with get_db() as db:
                user = db.query(User).filter(User.id == payload["user_id"]).first()
                if not user or not user.is_active:
                    return jsonify({"error": "User not found or inactive"}), 401
                if user.role not in roles:
                    return jsonify({"error": "Access denied: insufficient permissions"}), 403
                db.expunge(user)

            return f(current_user=user, *args, **kwargs)
        return decorated
    return decorator
