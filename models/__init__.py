from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please login to access this page."

# Import all models to ensure they are registered with SQLAlchemy
from models.user import User
from models.department import Department
from models.doctor import Doctor
from models.patient import Patient
from models.appointment import Appointment
from models.bed import Bed
from models.hospital_demand import HospitalDemand
from models.prediction import Prediction
from models.chat_message import ChatMessage