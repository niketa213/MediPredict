from routes.auth_routes import auth
from routes.patient_routes import patient
from routes.doctor_routes import doctor
from routes.admin_routes import admin


def register_routes(app):

    app.register_blueprint(auth)
    app.register_blueprint(patient)
    app.register_blueprint(doctor)
    app.register_blueprint(admin)