from models.recruitment_model import JobPosting, Application
from models.user_model import User
from models.department_model import Department
from db.db import get_db
from datetime import datetime


def _serialize_job(job, dept):
    return {
        "id": job.id,
        "title": job.title,
        "department": dept.name if dept else None,
        "department_id": job.department_id,
        "location": job.location,
        "employment_type": job.employment_type,
        "description": job.description,
        "requirements": job.requirements,
        "status": job.status,
        "created_by": job.created_by,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }


def _serialize_application(app, user, job):
    return {
        "id": app.id,
        "job_id": app.job_id,
        "job_title": job.title if job else None,
        "candidate_id": app.candidate_id,
        "candidate_name": user.name if user else None,
        "candidate_email": user.email if user else None,
        "status": app.status,
        "ai_score": app.ai_score,
        "resume_url": app.resume_url,
        "cover_letter": app.cover_letter,
        "applied_at": app.applied_at.isoformat() if app.applied_at else None,
    }


# --- Job Postings ---

def create_job(data, created_by):
    if not data.get("title"):
        return {"error": "title is required"}, 400
    with get_db() as db:
        job = JobPosting(
            title=data["title"],
            department_id=data.get("department_id"),
            location=data.get("location"),
            employment_type=data.get("employment_type", "full-time"),
            description=data.get("description"),
            requirements=data.get("requirements"),
            status=data.get("status", "open"),
            created_by=created_by,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return {"message": "Job posted", "id": job.id}, 201


def get_jobs(filters=None):
    with get_db() as db:
        query = (
            db.query(JobPosting, Department)
            .outerjoin(Department, JobPosting.department_id == Department.id)
        )
        if filters:
            if filters.get("status"):
                query = query.filter(JobPosting.status == filters["status"])
            if filters.get("department_id"):
                query = query.filter(JobPosting.department_id == filters["department_id"])
        rows = query.order_by(JobPosting.created_at.desc()).all()
        return [_serialize_job(j, d) for j, d in rows], 200


def update_job(job_id, data):
    with get_db() as db:
        job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
        if not job:
            return {"error": "Job not found"}, 404
        for field in ["title", "location", "employment_type", "description", "requirements", "status", "department_id"]:
            if field in data:
                setattr(job, field, data[field])
        db.commit()
        return {"message": "Job updated"}, 200


def delete_job(job_id):
    with get_db() as db:
        job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
        if not job:
            return {"error": "Job not found"}, 404
        job.status = "closed"
        db.commit()
        return {"message": "Job closed"}, 200


# --- Applications ---

def apply_for_job(data, candidate_id):
    if not data.get("job_id"):
        return {"error": "job_id is required"}, 400
    with get_db() as db:
        existing = db.query(Application).filter(
            Application.job_id == data["job_id"],
            Application.candidate_id == candidate_id
        ).first()
        if existing:
            return {"error": "Already applied for this job"}, 409

        app = Application(
            job_id=data["job_id"],
            candidate_id=candidate_id,
            status="applied",
            resume_url=data.get("resume_url"),
            cover_letter=data.get("cover_letter"),
        )
        db.add(app)
        db.commit()
        return {"message": "Application submitted"}, 201


def get_applications(filters=None):
    with get_db() as db:
        query = (
            db.query(Application, User, JobPosting)
            .join(User, Application.candidate_id == User.id)
            .join(JobPosting, Application.job_id == JobPosting.id)
        )
        if filters:
            if filters.get("job_id"):
                query = query.filter(Application.job_id == filters["job_id"])
            if filters.get("candidate_id"):
                query = query.filter(Application.candidate_id == filters["candidate_id"])
            if filters.get("status"):
                query = query.filter(Application.status == filters["status"])
        rows = query.order_by(Application.applied_at.desc()).all()
        return [_serialize_application(a, u, j) for a, u, j in rows], 200


def get_my_applications(candidate_id):
    return get_applications(filters={"candidate_id": candidate_id})


def update_application_status(app_id, data):
    valid_statuses = {"applied", "screening", "interviewing", "shortlisted", "offered", "rejected"}
    if data.get("status") not in valid_statuses:
        return {"error": f"status must be one of {valid_statuses}"}, 400
    with get_db() as db:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return {"error": "Application not found"}, 404
        app.status = data["status"]
        if "ai_score" in data:
            app.ai_score = data["ai_score"]
        app.updated_at = datetime.utcnow()
        db.commit()
        return {"message": "Application updated"}, 200


def get_recruitment_stats():
    with get_db() as db:
        open_jobs = db.query(JobPosting).filter(JobPosting.status == "open").count()
        total_apps = db.query(Application).count()
        shortlisted = db.query(Application).filter(Application.status == "shortlisted").count()
        interviewing = db.query(Application).filter(Application.status == "interviewing").count()
        return {
            "open_jobs": open_jobs,
            "total_applications": total_apps,
            "shortlisted": shortlisted,
            "interviewing": interviewing,
        }, 200
