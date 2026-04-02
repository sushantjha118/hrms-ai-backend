import secrets
import bcrypt
from models.user_model import User
from db.db import get_db

def register_user(data):
    with get_db() as db:
        if db.query(User).filter(User.email == data['email']).first():
            return {"error": "Email already registered"}, 409

        hashed_pw = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()

        user = User(
            name=data['name'],
            email=data['email'],
            password=hashed_pw,
            role=data['role']
        )

        db.add(user)
        db.commit()

    return {"message": "User registered successfully"}, 201


def login_user(data):
    with get_db() as db:
        user = db.query(User).filter(User.email == data['email']).first()

        if not user or not bcrypt.checkpw(data['password'].encode(), user.password.encode()):
            return None

        token_serial = (user.token_count or 0) + 1
        user.token_count = token_serial
        token = f"{token_serial}|{secrets.token_hex(32)}"
        user.token = token
        db.commit()

        return {
            "serial_no": user.id,
            "email": user.email,
            "role": user.role,
            "token": token
        }
