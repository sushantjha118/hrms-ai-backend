import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from db.db import engine
from models.base import Base
import models.user_model
import models.employee_model
from routes.auth_routes import auth_bp
from routes.employee_routes import employee_bp

Base.metadata.create_all(engine)

app = Flask(__name__)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(employee_bp, url_prefix='/api/employee')

@app.route('/')
def home():
    return "HRMS AI Backend Running 🚀"

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')