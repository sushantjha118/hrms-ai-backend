"""
Seed script — run once: python seed.py
Creates 4 role users + realistic data for all tables.
"""
import sys
from dotenv import load_dotenv
load_dotenv()

import bcrypt
from datetime import date, datetime, time, timedelta
from db.db import get_db
from models.base import Base
from db.db import engine

import models.user_model, models.department_model, models.employee_model
import models.attendance_model, models.leave_model, models.performance_model
import models.recruitment_model, models.announcement_model, models.payslip_model

from models.user_model import User
from models.department_model import Department
from models.employee_model import Employee
from models.attendance_model import Attendance
from models.leave_model import LeaveRequest
from models.performance_model import PerformanceReview
from models.recruitment_model import JobPosting, Application
from models.announcement_model import Announcement
from models.payslip_model import Payslip

Base.metadata.create_all(engine)

def hash_pw(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

PASSWORD = "Admin@123"

def seed():
    with get_db() as db:

        # ── Clear existing data (order matters for FK) ──────────────────────
        db.query(Payslip).delete()
        db.query(Application).delete()
        db.query(JobPosting).delete()
        db.query(Announcement).delete()
        db.query(PerformanceReview).delete()
        db.query(LeaveRequest).delete()
        db.query(Attendance).delete()
        db.query(Employee).delete()
        db.query(Department).delete()
        db.query(User).delete()
        db.commit()
        print("Cleared existing data.")

        # ── Users ────────────────────────────────────────────────────────────
        users_data = [
            ("Admin User",     "admin@gmail.com",     "admin"),
            ("Sarah Jenkins",  "hr@gmail.com",        "hr"),
            ("Alex Rivera",    "employee@gmail.com",  "employee"),
            ("Jordan Lee",     "candidate@gmail.com", "candidate"),
            # Extra employees for realistic data
            ("Maya Chen",      "maya.chen@hrms.ai",   "employee"),
            ("Thomas Wright",  "thomas.w@hrms.ai",    "employee"),
            ("Elena Vasquez",  "elena.v@hrms.ai",     "employee"),
            ("Marcus Holloway","marcus.h@hrms.ai",    "employee"),
            ("Rachel Kim",     "rachel.k@hrms.ai",    "employee"),
            ("James Huang",    "james.h@hrms.ai",     "employee"),
        ]
        users = []
        for name, email, role in users_data:
            u = User(name=name, email=email, password=hash_pw(PASSWORD),
                     role=role, status="active", is_active=True)
            db.add(u)
            users.append(u)
        db.commit()
        for u in users: db.refresh(u)
        print(f"Created {len(users)} users.")

        admin_u, hr_u, emp_u, cand_u, maya_u, thomas_u, elena_u, marcus_u, rachel_u, james_u = users

        # ── Departments ──────────────────────────────────────────────────────
        dept_names = ["Engineering", "Design", "Marketing", "Sales", "People & Culture", "Finance"]
        depts = []
        for name in dept_names:
            d = Department(name=name, head_id=admin_u.id)
            db.add(d)
            depts.append(d)
        db.commit()
        for d in depts: db.refresh(d)
        eng_d, design_d, mkt_d, sales_d, hr_d, fin_d = depts
        print(f"Created {len(depts)} departments.")

        # ── Employees ────────────────────────────────────────────────────────
        emp_profiles = [
            (emp_u.id,     eng_d.id,    "Senior Product Designer",  "full-time", 95000,  "2022-03-15", "+1-555-0101", "San Francisco, CA", "React,Figma,Tailwind,UI Design"),
            (maya_u.id,    design_d.id, "Senior UX Designer",       "full-time", 90000,  "2021-07-01", "+1-555-0102", "New York, NY",      "Figma,Prototyping,User Research"),
            (thomas_u.id,  sales_d.id,  "Sales Operations Lead",    "full-time", 85000,  "2020-11-20", "+1-555-0103", "Austin, TX",        "Salesforce,Forecasting,CRM"),
            (elena_u.id,   mkt_d.id,    "Head of Marketing",        "full-time", 105000, "2019-05-10", "+1-555-0104", "London, UK",        "Strategy,Analytics,SEO,Growth"),
            (marcus_u.id,  eng_d.id,    "Tech Lead",                "full-time", 115000, "2018-09-01", "+1-555-0105", "Seattle, WA",       "TypeScript,Kubernetes,AWS,Node.js"),
            (rachel_u.id,  eng_d.id,    "Software Engineer",        "full-time", 88000,  "2023-01-10", "+1-555-0106", "Remote",            "Python,Django,PostgreSQL"),
            (james_u.id,   fin_d.id,    "Financial Analyst",        "full-time", 80000,  "2022-06-15", "+1-555-0107", "Chicago, IL",       "Excel,PowerBI,Finance,Accounting"),
            (hr_u.id,      hr_d.id,     "HR Director",              "full-time", 100000, "2017-04-01", "+1-555-0108", "San Francisco, CA", "Employee Relations,Coaching,HRIS"),
        ]
        emps = []
        for user_id, dept_id, desig, emp_type, sal, join_dt, phone, loc, skills in emp_profiles:
            e = Employee(user_id=user_id, department_id=dept_id, designation=desig,
                         employment_type=emp_type, salary=sal,
                         joining_date=date.fromisoformat(join_dt),
                         phone=phone, location=loc, skills=skills, status="active")
            db.add(e)
            emps.append(e)
        db.commit()
        for e in emps: db.refresh(e)
        alex_e, maya_e, thomas_e, elena_e, marcus_e, rachel_e, james_e, hr_e = emps
        print(f"Created {len(emps)} employee profiles.")

        # ── Attendance (last 7 days) ──────────────────────────────────────────
        today = date.today()
        att_records = []
        for emp in emps:
            for i in range(7):
                day = today - timedelta(days=i)
                if day.weekday() >= 5:  # skip weekends
                    continue
                if i == 0 and emp.id == rachel_e.id:
                    status = "absent"
                    att = Attendance(employee_id=emp.id, date=day, status=status)
                elif emp.id == marcus_e.id and i < 3:
                    status = "late"
                    att = Attendance(employee_id=emp.id, date=day, status=status,
                                     check_in=time(9, 45), check_out=time(18, 30), hours_worked="8h 45m")
                else:
                    status = "present"
                    att = Attendance(employee_id=emp.id, date=day, status=status,
                                     check_in=time(8, 55), check_out=time(18, 0), hours_worked="9h 05m")
                db.add(att)
                att_records.append(att)
        db.commit()
        print(f"Created {len(att_records)} attendance records.")

        # ── Leave Requests ───────────────────────────────────────────────────
        leaves = [
            (alex_e.id,   "vacation", "2024-12-20", "2024-12-27", "Year-end vacation",   "pending",  None),
            (maya_e.id,   "sick",     "2024-11-10", "2024-11-11", "Flu recovery",        "approved", hr_u.id),
            (thomas_e.id, "personal", "2024-12-14", "2024-12-14", "Personal errand",     "pending",  None),
            (elena_e.id,  "vacation", "2024-10-01", "2024-10-05", "Annual leave",        "rejected", hr_u.id),
            (marcus_e.id, "sick",     "2024-11-25", "2024-11-26", "Medical appointment", "approved", hr_u.id),
            (rachel_e.id, "vacation", "2025-01-06", "2025-01-10", "New year break",      "pending",  None),
        ]
        for emp_id, ltype, start, end, reason, status, reviewer in leaves:
            s, e_ = date.fromisoformat(start), date.fromisoformat(end)
            lr = LeaveRequest(employee_id=emp_id, leave_type=ltype, start_date=s, end_date=e_,
                              duration_days=(e_ - s).days + 1, reason=reason, status=status,
                              reviewed_by=reviewer,
                              reviewed_at=datetime.utcnow() if reviewer else None)
            db.add(lr)
        db.commit()
        print(f"Created {len(leaves)} leave requests.")

        # ── Performance Reviews ──────────────────────────────────────────────
        reviews = [
            (marcus_e.id, hr_u.id, "Q3-2024", 4.9, "completed",  "Exceeds expectations in technical leadership."),
            (maya_e.id,   hr_u.id, "Q3-2024", None,"scheduled",  None),
            (elena_e.id,  hr_u.id, "Q3-2024", 4.2, "completed",  "Strong strategic thinking, great cross-team collaboration."),
            (alex_e.id,   hr_u.id, "Q3-2024", None,"in-draft",   "Review in progress."),
            (thomas_e.id, hr_u.id, "Q2-2024", 3.8, "completed",  "Meets expectations. Needs improvement in forecasting accuracy."),
            (rachel_e.id, hr_u.id, "Q3-2024", 4.5, "completed",  "Excellent backend work, proactive problem solver."),
        ]
        for emp_id, rev_id, period, score, status, notes in reviews:
            pr = PerformanceReview(employee_id=emp_id, reviewer_id=rev_id, period=period,
                                   score=score, status=status, notes=notes,
                                   review_date=datetime.utcnow() if status == "completed" else None)
            db.add(pr)
        db.commit()
        print(f"Created {len(reviews)} performance reviews.")

        # ── Job Postings ─────────────────────────────────────────────────────
        jobs_data = [
            ("Senior Frontend Architect", eng_d.id,    "Remote (Global)",   "full-time", "open"),
            ("Lead AI Research Engineer", eng_d.id,    "San Francisco, CA", "full-time", "open"),
            ("UI/UX Designer (Product)",  design_d.id, "London, UK",        "hybrid",    "open"),
            ("Marketing Manager",         mkt_d.id,    "New York, NY",      "full-time", "open"),
            ("Sales Development Rep",     sales_d.id,  "Austin, TX",        "full-time", "open"),
            ("DevOps Engineer",           eng_d.id,    "Remote",            "full-time", "closed"),
        ]
        jobs = []
        for title, dept_id, loc, emp_type, status in jobs_data:
            j = JobPosting(title=title, department_id=dept_id, location=loc,
                           employment_type=emp_type, status=status,
                           description=f"We are looking for a talented {title} to join our team.",
                           requirements="3+ years experience, strong communication skills.",
                           created_by=hr_u.id)
            db.add(j)
            jobs.append(j)
        db.commit()
        for j in jobs: db.refresh(j)
        print(f"Created {len(jobs)} job postings.")

        # ── Applications ─────────────────────────────────────────────────────
        apps_data = [
            (cand_u.id, jobs[0].id, "shortlisted", 94.0),
            (cand_u.id, jobs[1].id, "applied",     88.0),
            (cand_u.id, jobs[2].id, "interviewing",75.0),
        ]
        for cand_id, job_id, status, score in apps_data:
            a = Application(candidate_id=cand_id, job_id=job_id, status=status, ai_score=score)
            db.add(a)
        db.commit()
        print(f"Created {len(apps_data)} applications.")

        # ── Announcements ────────────────────────────────────────────────────
        ann_data = [
            ("New Quarterly Benefits & Health Program",
             "We are excited to announce a range of new health and wellness benefits starting next month. All employees are eligible.",
             "Company Update", "all"),
            ("Hackathon 2024: Innovate with Generative AI",
             "Join the annual engineering hackathon and win prizes up to $5000 and direct project funding.",
             "Events", "employee"),
            ("Q4 Performance Review Cycle Begins",
             "HR will be scheduling Q4 performance reviews starting next week. Please prepare your self-assessments.",
             "Policy", "employee"),
            ("New Leave Policy Effective January 2025",
             "Updated leave policy with 5 additional personal days per year. Full details in the HR portal.",
             "Policy", "all"),
            ("System Maintenance — Dec 28, 2024",
             "The HRMS platform will be down for maintenance on Dec 28 from 2 AM to 5 AM UTC.",
             "Alert", "all"),
        ]
        for title, body, category, target in ann_data:
            db.add(Announcement(title=title, body=body, category=category,
                                target_role=target, created_by=hr_u.id))
        db.commit()
        print(f"Created {len(ann_data)} announcements.")

        # ── Payslips ─────────────────────────────────────────────────────────
        payslip_emps = [alex_e, maya_e, thomas_e, elena_e, marcus_e, rachel_e, james_e, hr_e]
        for emp in payslip_emps:
            for month in [10, 11]:
                net = emp.salary / 12
                basic = net * 0.7
                allowances = net * 0.2
                deductions = net * 0.1
                db.add(Payslip(employee_id=emp.id, month=month, year=2024,
                               basic_salary=round(basic, 2),
                               allowances=round(allowances, 2),
                               deductions=round(deductions, 2),
                               net_salary=round(net, 2),
                               status="paid"))
        db.commit()
        print(f"Created {len(payslip_emps) * 2} payslips.")

        print("\n✅ Seed complete!")
        print("─" * 40)
        print("Login credentials (all password: Admin@123)")
        print("  admin@gmail.com     → Admin")
        print("  hr@gmail.com        → HR")
        print("  employee@gmail.com  → Employee")
        print("  candidate@gmail.com → Candidate")

if __name__ == "__main__":
    seed()
