from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from models import db
from models.appointment import Appointment
from models.doctor import Doctor
from utils.decorators import doctor_required


doctor = Blueprint(
    "doctor",
    __name__,
    url_prefix="/doctor",
)


def get_doctor_profile():
    """Return the logged-in doctor's profile."""

    profile = current_user.doctor_profile

    if profile is None:
        flash(
            "Doctor profile was not found.",
            "danger",
        )
        return None

    return profile


# ============================================================
# DOCTOR DASHBOARD
# ============================================================

@doctor.route("/dashboard")
@doctor_required
def dashboard():

    profile = get_doctor_profile()

    if profile is None:
        return redirect(
            url_for("auth.logout")
        )

    today = date.today()

    total = (
        Appointment.query
        .filter_by(
            doctor_id=profile.id
        )
        .count()
    )

    pending = (
        Appointment.query
        .filter_by(
            doctor_id=profile.id,
            status="pending",
        )
        .count()
    )

    confirmed = (
        Appointment.query
        .filter_by(
            doctor_id=profile.id,
            status="confirmed",
        )
        .count()
    )

    completed = (
        Appointment.query
        .filter_by(
            doctor_id=profile.id,
            status="completed",
        )
        .count()
    )

    patients = (
        db.session.query(
            Appointment.patient_id
        )
        .filter_by(
            doctor_id=profile.id
        )
        .distinct()
        .count()
    )

    todays_appointments = (
        Appointment.query
        .filter(
            Appointment.doctor_id == profile.id,
            Appointment.appointment_date == today,
            Appointment.status.in_(
                [
                    "pending",
                    "confirmed",
                ]
            ),
        )
        .order_by(
            Appointment.appointment_time.asc()
        )
        .all()
    )

    return render_template(
        "doctor/dashboard.html",
        user=current_user,
        profile=profile,
        total=total,
        pending=pending,
        confirmed=confirmed,
        completed=completed,
        patients=patients,
        appointments=todays_appointments,
    )


# ============================================================
# DOCTOR APPOINTMENTS
# ============================================================

@doctor.route(
    "/appointments",
    methods=["GET", "POST"],
)
@doctor_required
def appointments():

    profile = get_doctor_profile()

    if profile is None:
        return redirect(
            url_for("auth.logout")
        )

    # --------------------------------------------------------
    # Update appointment status
    # --------------------------------------------------------

    if request.method == "POST":

        appointment_id = request.form.get(
            "appointment_id",
            type=int,
        )

        status = request.form.get(
            "status",
            "",
        ).strip().lower()

        appointment = (
            Appointment.query
            .filter(
                Appointment.id == appointment_id,
                Appointment.doctor_id == profile.id,
            )
            .first_or_404()
        )

        allowed_statuses = {
            "pending",
            "confirmed",
            "completed",
            "cancelled",
            "rejected",
        }

        if status not in allowed_statuses:

            flash(
                "Invalid appointment status.",
                "danger",
            )

            return redirect(
                url_for(
                    "doctor.appointments"
                )
            )

        appointment.status = status

        try:

            db.session.commit()

            flash(
                "Appointment status updated successfully.",
                "success",
            )

        except Exception:

            db.session.rollback()

            flash(
                "Could not update appointment status.",
                "danger",
            )

        return redirect(
            url_for(
                "doctor.appointments"
            )
        )

    # --------------------------------------------------------
    # Appointment list
    # --------------------------------------------------------

    rows = (
        Appointment.query
        .filter_by(
            doctor_id=profile.id
        )
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc(),
        )
        .all()
    )

    return render_template(
        "doctor/appointments.html",
        appointments=rows,
        profile=profile,
    )


# ============================================================
# DOCTOR PATIENTS
# ============================================================

@doctor.route("/patients")
@doctor_required
def patients():

    profile = get_doctor_profile()

    if profile is None:
        return redirect(
            url_for("auth.logout")
        )

    appointments = (
        Appointment.query
        .filter_by(
            doctor_id=profile.id
        )
        .order_by(
            Appointment.appointment_date.desc()
        )
        .all()
    )

    unique_patients = {}

    for appointment in appointments:

        if appointment.patient:

            unique_patients[
                appointment.patient.id
            ] = appointment.patient

    patient_list = list(
        unique_patients.values()
    )

    return render_template(
        "doctor/patients.html",
        patients=patient_list,
        profile=profile,
    )


# ============================================================
# DOCTOR PROFILE
# ============================================================

@doctor.route(
    "/profile",
    methods=["GET", "POST"],
)
@doctor_required
def profile():

    doctor_profile = get_doctor_profile()

    if doctor_profile is None:
        return redirect(
            url_for("auth.logout")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            "",
        ).strip()

        phone = request.form.get(
            "phone",
            "",
        ).strip()

        specialization = request.form.get(
            "specialization",
            "",
        ).strip()

        qualification = request.form.get(
            "qualification",
            "",
        ).strip()

        experience = request.form.get(
            "experience",
            type=int,
        )

        availability = request.form.get(
            "availability",
            "",
        ).strip()

        # ----------------------------------------------------
        # Update user information
        # ----------------------------------------------------

        if name:
            current_user.name = name

        current_user.phone = (
            phone or None
        )

        # ----------------------------------------------------
        # Update doctor information
        # ----------------------------------------------------

        if specialization:
            doctor_profile.specialization = specialization

        doctor_profile.qualification = (
            qualification or None
        )

        doctor_profile.experience = (
            max(experience, 0)
            if experience is not None
            else 0
        )

        if availability:
            doctor_profile.availability = availability

        try:

            db.session.commit()

            flash(
                "Doctor profile updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "doctor.profile"
                )
            )

        except Exception:

            db.session.rollback()

            flash(
                "Profile update failed.",
                "danger",
            )

    return render_template(
        "doctor/profile.html",
        profile=doctor_profile,
    )