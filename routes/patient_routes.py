from datetime import date, datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import or_

from models import db
from models.appointment import Appointment
from models.chat_message import ChatMessage
from models.department import Department
from models.doctor import Doctor
from models.patient import Patient
from models.user import User

from utils.chatbot import chatbot_reply
from utils.decorators import patient_required
from utils.recommender import recommend_department


patient = Blueprint(
    "patient",
    __name__,
    url_prefix="/patient",
)


# ============================================================
# HELPER
# ============================================================

def get_patient_profile():
    """Get the currently logged-in patient's profile."""

    profile = getattr(
        current_user,
        "patient_profile",
        None,
    )

    if profile is None and current_user.is_authenticated and current_user.role == "patient":
        try:
            profile = Patient(user_id=current_user.id)
            db.session.add(profile)
            db.session.commit()
        except Exception:
            db.session.rollback()
            profile = None

    if profile is None:
        flash(
            "Patient profile was not found.",
            "danger",
        )
        return None

    return profile


def render_booking_page(doctor):
    """Render appointment booking page."""

    return render_template(
        "patient/book_appointment.html",
        doctor=doctor,
        current_date=date.today().isoformat(),
    )


# ============================================================
# DASHBOARD
# ============================================================

@patient.route("/dashboard")
@patient_required
def dashboard():

    profile = get_patient_profile()

    if profile is None:
        return redirect(
            url_for("auth.logout")
        )

    today = date.today()

    total = (
        Appointment.query
        .filter_by(
            patient_id=profile.id
        )
        .count()
    )

    upcoming = (
        Appointment.query
        .filter(
            Appointment.patient_id == profile.id,
            Appointment.appointment_date >= today,
            Appointment.status.in_(
                ["pending", "confirmed"]
            ),
        )
        .count()
    )

    completed = (
        Appointment.query
        .filter(
            Appointment.patient_id == profile.id,
            Appointment.status == "completed",
        )
        .count()
    )

    doctors_visited = (
        db.session.query(
            Appointment.doctor_id
        )
        .filter(
            Appointment.patient_id == profile.id
        )
        .distinct()
        .count()
    )

    upcoming_appointments = (
        Appointment.query
        .filter(
            Appointment.patient_id == profile.id,
            Appointment.appointment_date >= today,
            Appointment.status.in_(
                ["pending", "confirmed"]
            ),
        )
        .order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc(),
        )
        .limit(6)
        .all()
    )

    return render_template(
        "patient/dashboard.html",
        user=current_user,
        total=total,
        upcoming=upcoming,
        completed=completed,
        doctors_visited=doctors_visited,
        appointments=upcoming_appointments,
    )


# ============================================================
# FIND DOCTOR
# ============================================================

@patient.route("/doctors")
@patient_required
def doctors():

    search = request.args.get(
        "q",
        "",
    ).strip()

    department_id = request.args.get(
        "department",
        type=int,
    )

    query = (
        Doctor.query
        .join(
            User,
            Doctor.user_id == User.id,
        )
        .join(
            Department,
            Doctor.department_id == Department.id,
        )
        .filter(
            User.is_active.is_(True)
        )
    )

    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                User.name.ilike(
                    search_pattern
                ),
                Doctor.specialization.ilike(
                    search_pattern
                ),
                Doctor.qualification.ilike(
                    search_pattern
                ),
            )
        )

    if department_id:

        query = query.filter(
            Doctor.department_id == department_id
        )

    doctor_list = (
        query
        .order_by(
            User.name.asc()
        )
        .all()
    )

    departments = (
        Department.query
        .order_by(
            Department.name.asc()
        )
        .all()
    )

    return render_template(
        "patient/doctors.html",
        doctors=doctor_list,
        departments=departments,
        search=search,
        department_id=department_id,
    )


# ============================================================
# AI RECOMMENDATION
# ============================================================

@patient.route(
    "/recommendation",
    methods=["GET", "POST"],
)
@patient_required
def recommendation():

    result = None
    doctors = []

    if request.method == "POST":

        symptoms = request.form.get(
            "symptoms",
            "",
        ).strip()

        if not symptoms:

            flash(
                "Please describe your symptoms.",
                "warning",
            )

        else:

            result = recommend_department(
                symptoms
            )

            department = (
                Department.query
                .filter_by(
                    name=result.get(
                        "department"
                    )
                )
                .first()
            )

            if department:

                doctors = (
                    Doctor.query
                    .join(
                        User,
                        Doctor.user_id
                        == User.id,
                    )
                    .filter(
                        Doctor.department_id
                        == department.id,
                        User.is_active.is_(True),
                    )
                    .order_by(
                        Doctor.experience.desc(),
                        User.name.asc(),
                    )
                    .limit(6)
                    .all()
                )

    return render_template(
        "patient/recommendation.html",
        result=result,
        doctors=doctors,
    )


# ============================================================
# MY APPOINTMENTS
# ============================================================

@patient.route("/appointments")
@patient_required
def appointments():

    profile = get_patient_profile()

    if profile is None:
        return redirect(
            url_for("patient.dashboard")
        )

    appointment_list = (
        Appointment.query
        .filter_by(
            patient_id=profile.id
        )
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc(),
        )
        .all()
    )

    return render_template(
        "patient/appointments.html",
        appointments=appointment_list,
    )


# ============================================================
# BOOK APPOINTMENT
# ============================================================

@patient.route(
    "/appointments/book/<int:doctor_id>",
    methods=["GET", "POST"],
)
@patient_required
def book_appointment(doctor_id):

    profile = get_patient_profile()

    if profile is None:
        return redirect(
            url_for("patient.dashboard")
        )

    doctor = (
        Doctor.query
        .join(
            User,
            Doctor.user_id == User.id,
        )
        .join(
            Department,
            Doctor.department_id
            == Department.id,
        )
        .filter(
            Doctor.id == doctor_id,
            User.is_active.is_(True),
        )
        .first_or_404()
    )

    if request.method == "GET":
        return render_booking_page(doctor)

    # --------------------------------------------------------
    # Form data
    # --------------------------------------------------------

    raw_date = request.form.get(
        "appointment_date",
        "",
    ).strip()

    raw_time = request.form.get(
        "appointment_time",
        "",
    ).strip()

    reason = request.form.get(
        "reason",
        "",
    ).strip()

    # --------------------------------------------------------
    # Validate date
    # --------------------------------------------------------

    try:

        appointment_date = date.fromisoformat(
            raw_date
        )

    except ValueError:

        flash(
            "Please select a valid appointment date.",
            "danger",
        )

        return render_booking_page(doctor)

    # --------------------------------------------------------
    # Validate time
    # --------------------------------------------------------

    try:

        appointment_time = datetime.strptime(
            raw_time,
            "%H:%M",
        ).time()

    except ValueError:

        flash(
            "Please select a valid appointment time.",
            "danger",
        )

        return render_booking_page(doctor)

    # --------------------------------------------------------
    # Date cannot be in the past
    # --------------------------------------------------------

    if appointment_date < date.today():

        flash(
            "Appointment date cannot be in the past.",
            "danger",
        )

        return render_booking_page(doctor)

    # --------------------------------------------------------
    # Patient conflict
    # --------------------------------------------------------

    patient_conflict = (
        Appointment.query
        .filter(
            Appointment.patient_id == profile.id,
            Appointment.appointment_date
            == appointment_date,
            Appointment.appointment_time
            == appointment_time,
            Appointment.status.in_(
                ["pending", "confirmed"]
            ),
        )
        .first()
    )

    if patient_conflict:

        flash(
            "You already have an appointment at this time.",
            "warning",
        )

        return render_booking_page(doctor)

    # --------------------------------------------------------
    # Doctor conflict
    # --------------------------------------------------------

    doctor_conflict = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date
            == appointment_date,
            Appointment.appointment_time
            == appointment_time,
            Appointment.status.in_(
                ["pending", "confirmed"]
            ),
        )
        .first()
    )

    if doctor_conflict:

        flash(
            "This doctor already has an appointment at "
            "this time. Please choose another time.",
            "danger",
        )

        return render_booking_page(doctor)

    # --------------------------------------------------------
    # Create appointment
    # --------------------------------------------------------

    appointment = Appointment(
        patient_id=profile.id,
        doctor_id=doctor.id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        reason=reason or None,
        status="pending",
    )

    try:

        db.session.add(
            appointment
        )

        db.session.commit()

        flash(
            "Appointment request submitted successfully.",
            "success",
        )

        return redirect(
            url_for(
                "patient.appointments"
            )
        )

    except Exception:

        db.session.rollback()

        flash(
            "Appointment could not be booked. "
            "Please try again.",
            "danger",
        )

        return render_booking_page(doctor)


# ============================================================
# CANCEL APPOINTMENT
# ============================================================

@patient.route(
    "/appointments/<int:appointment_id>/cancel",
    methods=["POST"],
)
@patient_required
def cancel_appointment(appointment_id):

    profile = get_patient_profile()

    if profile is None:
        return redirect(
            url_for("patient.dashboard")
        )

    appointment = (
        Appointment.query
        .filter(
            Appointment.id == appointment_id,
            Appointment.patient_id == profile.id,
        )
        .first_or_404()
    )

    if appointment.status not in {
        "pending",
        "confirmed",
    }:

        flash(
            "This appointment cannot be cancelled.",
            "warning",
        )

        return redirect(
            url_for(
                "patient.appointments"
            )
        )

    appointment.status = "cancelled"

    try:

        db.session.commit()

        flash(
            "Appointment cancelled successfully.",
            "success",
        )

    except Exception:

        db.session.rollback()

        flash(
            "Could not cancel the appointment.",
            "danger",
        )

    return redirect(
        url_for(
            "patient.appointments"
        )
    )


# ============================================================
# PATIENT PROFILE
# ============================================================

@patient.route(
    "/profile",
    methods=["GET", "POST"],
)
@patient_required
def profile():

    patient_profile = get_patient_profile()

    if patient_profile is None:
        return redirect(
            url_for("patient.dashboard")
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

        raw_dob = request.form.get(
            "date_of_birth",
            "",
        ).strip()

        gender = request.form.get(
            "gender",
            "",
        ).strip()

        address = request.form.get(
            "address",
            "",
        ).strip()

        emergency_contact = request.form.get(
            "emergency_contact",
            "",
        ).strip()

        # User information
        if name:
            current_user.name = name

        current_user.phone = (
            phone or None
        )

        # Date of birth
        if raw_dob:

            try:

                patient_profile.date_of_birth = (
                    date.fromisoformat(raw_dob)
                )

            except ValueError:

                flash(
                    "Please enter a valid date of birth.",
                    "danger",
                )

                return render_template(
                    "patient/profile.html",
                    profile=patient_profile,
                )

        else:

            patient_profile.date_of_birth = None

        patient_profile.gender = (
            gender or None
        )

        patient_profile.address = (
            address or None
        )

        patient_profile.emergency_contact = (
            emergency_contact or None
        )

        try:

            db.session.commit()

            flash(
                "Profile updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "patient.profile"
                )
            )

        except Exception:

            db.session.rollback()

            flash(
                "Profile could not be updated.",
                "danger",
            )

    return render_template(
        "patient/profile.html",
        profile=patient_profile,
    )


# ============================================================
# AI CHATBOT
# ============================================================

@patient.route(
    "/chatbot",
    methods=["GET", "POST"],
)
@patient_required
def chatbot():

    if request.method == "POST":

        message = request.form.get(
            "message",
            "",
        ).strip()

        if not message:

            flash(
                "Please type a message.",
                "warning",
            )

            return redirect(
                url_for(
                    "patient.chatbot"
                )
            )

        bot_response = chatbot_reply(
            message
        )

        try:

            user_message = ChatMessage(
                user_id=current_user.id,
                sender="user",
                message=message,
            )

            bot_message = ChatMessage(
                user_id=current_user.id,
                sender="bot",
                message=bot_response,
            )

            db.session.add(
                user_message
            )

            db.session.add(
                bot_message
            )

            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "The AI Assistant could not save "
                "this conversation.",
                "danger",
            )

        return redirect(
            url_for(
                "patient.chatbot"
            )
        )

    messages = (
        ChatMessage.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            ChatMessage.id.asc()
        )
        .limit(100)
        .all()
    )

    return render_template(
        "patient/chatbot.html",
        messages=messages,
    )