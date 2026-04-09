import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from db.db import engine
from models.base import Base

# Import all models so SQLAlchemy registers them before create_all
import models.user_model
import models.department_model
import models.employee_model
import models.attendance_model
import models.leave_model
import models.performance_model
import models.recruitment_model
import models.announcement_model
import models.payslip_model

# Import all blueprints
from routes.auth_routes import auth_bp
from routes.employee_routes import employee_bp
from routes.department_routes import department_bp
from routes.attendance_routes import attendance_bp
from routes.leave_routes import leave_bp
from routes.performance_routes import performance_bp
from routes.recruitment_routes import recruitment_bp
from routes.announcement_routes import announcement_bp
from routes.payslip_routes import payslip_bp

# Create all tables
Base.metadata.create_all(engine)

app = Flask(__name__)

# CORS — allow React frontend
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]}}, supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp,         url_prefix="/api/auth")
app.register_blueprint(employee_bp,     url_prefix="/api/employees")
app.register_blueprint(department_bp,   url_prefix="/api/departments")
app.register_blueprint(attendance_bp,   url_prefix="/api/attendance")
app.register_blueprint(leave_bp,        url_prefix="/api/leaves")
app.register_blueprint(performance_bp,  url_prefix="/api/performance")
app.register_blueprint(recruitment_bp,  url_prefix="/api/recruitment")
app.register_blueprint(announcement_bp, url_prefix="/api/announcements")
app.register_blueprint(payslip_bp,      url_prefix="/api/payslips")


# Global error handlers — always return JSON
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request", "message": str(e)}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


@app.route("/")
def home():
    return jsonify({"message": "HRMS AI Backend Running 🚀", "version": "2.0"})


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
