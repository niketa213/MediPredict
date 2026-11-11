from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from models import db
from models.user import User
from models.patient import Patient


auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic validation
        if not name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.register"))

        # Check existing email
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email is already registered.", "warning")
            return redirect(url_for("auth.register"))

        # Create patient user
        user = User(
            name=name,
            email=email,
            phone=phone,
            role="patient"
        )

        user.set_password(password)

        try:
            db.session.add(user)
            db.session.flush()

            patient_profile = Patient(user_id=user.id)
            db.session.add(patient_profile)
            db.session.commit()

            # Automatically log in the new patient for seamless UX
            login_user(user)

            flash(f"Welcome to MediPredict, {user.name}! Your patient account has been created successfully.", "success")
            return redirect(url_for("patient.dashboard"))

        except Exception:
            db.session.rollback()
            flash("An unexpected error occurred during registration. Please try again.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            if not user.is_active:
                flash("Your account is inactive.", "danger")
                return redirect(url_for("auth.login"))

            login_user(user)

            flash("Login successful.", "success")

            # Role-based redirect
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))

            elif user.role == "doctor":
                return redirect(url_for("doctor.dashboard"))

            else:
                return redirect(url_for("patient.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("You have been logged out.", "success")

    return redirect(url_for("auth.login"))