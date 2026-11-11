from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user

from config import Config
from models import db
from models.user import User
from routes import register_routes


app = Flask(__name__)
app.config.from_object(Config)

# Database
db.init_app(app)

# Flask Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please login to access this page."

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Register application routes
register_routes(app)


# Create database tables
with app.app_context():
    db.create_all()


@app.route("/")
def home():

    if current_user.is_authenticated:

        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))

        elif current_user.role == "doctor":
            return redirect(url_for("doctor.dashboard"))

        else:
            return redirect(url_for("patient.dashboard"))

    return redirect(url_for("auth.login"))


@app.errorhandler(403)
def forbidden(e):
    from flask import render_template
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def not_found(e):
    from flask import render_template
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    from flask import render_template
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )