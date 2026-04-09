from models.announcement_model import Announcement
from models.user_model import User
from db.db import get_db


def _serialize(ann, user):
    return {
        "id": ann.id,
        "title": ann.title,
        "body": ann.body,
        "category": ann.category,
        "target_role": ann.target_role,
        "created_by": ann.created_by,
        "author": user.name if user else None,
        "created_at": ann.created_at.isoformat() if ann.created_at else None,
    }


def create_announcement(data, created_by):
    if not data.get("title") or not data.get("body"):
        return {"error": "title and body are required"}, 400
    with get_db() as db:
        ann = Announcement(
            title=data["title"],
            body=data["body"],
            category=data.get("category", "Company Update"),
            target_role=data.get("target_role", "all"),
            created_by=created_by,
        )
        db.add(ann)
        db.commit()
        db.refresh(ann)
        return {"message": "Announcement created", "id": ann.id}, 201


def get_announcements(role="all"):
    with get_db() as db:
        query = (
            db.query(Announcement, User)
            .join(User, Announcement.created_by == User.id)
        )
        if role != "all":
            query = query.filter(
                (Announcement.target_role == "all") | (Announcement.target_role == role)
            )
        rows = query.order_by(Announcement.created_at.desc()).all()
        return [_serialize(a, u) for a, u in rows], 200


def delete_announcement(ann_id):
    with get_db() as db:
        ann = db.query(Announcement).filter(Announcement.id == ann_id).first()
        if not ann:
            return {"error": "Announcement not found"}, 404
        db.delete(ann)
        db.commit()
        return {"message": "Announcement deleted"}, 200
