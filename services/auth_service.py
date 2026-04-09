import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from models.user_model import User
from db.db import get_db
from config import JWT_SECRET_KEY, JWT_EXPIRY_HOURS

ALLOWED_SELF_REGISTER_ROLES = {"employee", "candidate"}


def _generate_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def register_user(data):
    required = ["name", "email", "password", "role"]
    for field in required:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    role = data["role"].lower()
    if role not in ALLOWED_SELF_REGISTER_ROLES:
        return {"error": "Invalid role. Only 'employee' or 'candidate' allowed on self-registration"}, 400

    if len(data["password"]) < 8:
        return {"error": "Password must be at least 8 characters"}, 400

    with get_db() as db:
        if db.query(User).filter(User.email == data["email"].lower()).first():
            return {"error": "Email already registered"}, 409

        hashed_pw = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
        user = User(
            name=data["name"].strip(),
            email=data["email"].lower().strip(),
            password=hashed_pw,
            role=role,
            status="active",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id

    return {"message": "User registered successfully", "user_id": user_id}, 201


def login_user(data):
    if not data.get("email") or not data.get("password"):
        return {"error": "Email and password are required"}, 400

    with get_db() as db:
        user = db.query(User).filter(User.email == data["email"].lower().strip()).first()

        if not user or not bcrypt.checkpw(data["password"].encode(), user.password.encode()):
            return {"error": "Invalid email or password"}, 401

        if not user.is_active:
            return {"error": "Account is deactivated. Contact your administrator."}, 403

        token = _generate_token(user.id, user.role)

        return {
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "status": user.status,
            }
        }, 200


def create_user_by_admin(data):
    """Admin-only: create any role including admin/hr"""
    required = ["name", "email", "password", "role"]
    for field in required:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    role = data["role"].lower()
    if role not in {"admin", "hr", "employee", "candidate"}:
        return {"error": "Invalid role"}, 400

    with get_db() as db:
        if db.query(User).filter(User.email == data["email"].lower()).first():
            return {"error": "Email already registered"}, 409

        hashed_pw = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
        user = User(
            name=data["name"].strip(),
            email=data["email"].lower().strip(),
            password=hashed_pw,
            role=role,
            status=data.get("status", "active"),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "User created successfully", "user_id": user.id}, 201


def get_all_users():
    with get_db() as db:
        users = db.query(User).order_by(User.created_at.desc()).all()
        return [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role,
                "status": u.status,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ], 200


def update_user_status(user_id, data):
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}, 404
        if "status" in data:
            user.status = data["status"]
        if "is_active" in data:
            user.is_active = data["is_active"]
        db.commit()
        return {"message": "User updated"}, 200


def delete_user(user_id):
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}, 404
        user.is_active = False
        user.status = "inactive"
        db.commit()
        return {"message": "User deactivated"}, 200
