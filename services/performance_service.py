from models.performance_model import PerformanceReview
from models.employee_model import Employee
from models.user_model import User
from db.db import get_db
from datetime import datetime


def _serialize(review, emp, user):
    return {
        "id": review.id,
        "employee_id": review.employee_id,
        "name": user.name if user else None,
        "designation": emp.designation if emp else None,
        "reviewer_id": review.reviewer_id,
        "period": review.period,
        "score": review.score,
        "status": review.status,
        "notes": review.notes,
        "review_date": review.review_date.isoformat() if review.review_date else None,
        "created_at": review.created_at.isoformat() if review.created_at else None,
    }


def create_review(data):
    required = ["employee_id", "reviewer_id", "period"]
    for field in required:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    with get_db() as db:
        review = PerformanceReview(
            employee_id=data["employee_id"],
            reviewer_id=data["reviewer_id"],
            period=data["period"],
            score=data.get("score"),
            status=data.get("status", "scheduled"),
            notes=data.get("notes"),
            review_date=datetime.fromisoformat(data["review_date"]) if data.get("review_date") else None,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return {"message": "Review created", "id": review.id}, 201


def get_all_reviews(filters=None):
    with get_db() as db:
        query = (
            db.query(PerformanceReview, Employee, User)
            .join(Employee, PerformanceReview.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id)
        )
        if filters:
            if filters.get("status"):
                query = query.filter(PerformanceReview.status == filters["status"])
            if filters.get("employee_id"):
                query = query.filter(PerformanceReview.employee_id == filters["employee_id"])
        rows = query.order_by(PerformanceReview.created_at.desc()).all()
        return [_serialize(r, e, u) for r, e, u in rows], 200


def get_my_reviews(current_user):
    with get_db() as db:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp:
            return [], 200
        rows = (
            db.query(PerformanceReview, Employee, User)
            .join(Employee, PerformanceReview.employee_id == Employee.id)
            .join(User, Employee.user_id == User.id)
            .filter(PerformanceReview.employee_id == emp.id)
            .order_by(PerformanceReview.created_at.desc())
            .all()
        )
        return [_serialize(r, e, u) for r, e, u in rows], 200


def update_review(review_id, data):
    with get_db() as db:
        review = db.query(PerformanceReview).filter(PerformanceReview.id == review_id).first()
        if not review:
            return {"error": "Review not found"}, 404
        for field in ["score", "status", "notes", "period"]:
            if field in data:
                setattr(review, field, data[field])
        if data.get("review_date"):
            review.review_date = datetime.fromisoformat(data["review_date"])
        db.commit()
        return {"message": "Review updated"}, 200


def get_performance_stats():
    with get_db() as db:
        total = db.query(PerformanceReview).count()
        completed = db.query(PerformanceReview).filter(PerformanceReview.status == "completed").count()
        scores = [r.score for r in db.query(PerformanceReview).filter(
            PerformanceReview.score.isnot(None)).all()]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0
        return {"total": total, "completed": completed, "avg_score": avg_score}, 200
