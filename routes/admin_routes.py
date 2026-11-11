from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy import or_

from models import (
    db, User, Doctor, Patient, Department, Appointment, Bed, HospitalDemand, Prediction
)
from utils.decorators import admin_required
from utils.forecast import get_forecast_summary, generate_forecast


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ============================================================
# ADMIN DASHBOARD
# ============================================================
@admin.route("/dashboard")
@admin_required
def dashboard():
    today = date.today()

    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    available_beds = Bed.query.filter_by(status="Available").count()
    total_beds = Bed.query.count()
    icu_available = Bed.query.filter(Bed.bed_type == "ICU", Bed.status == "Available").count()

    # Today's activity from latest hospital demand or today's appointments
    today_demand = HospitalDemand.query.filter_by(date=today).all()
    if today_demand:
        admissions_today = sum(d.admissions for d in today_demand)
        discharges_today = sum(d.discharges for d in today_demand)
    else:
        # Fallback to recent demand averages
        recent_demands = HospitalDemand.query.order_by(HospitalDemand.date.desc()).limit(10).all()
        admissions_today = round(sum(d.admissions for d in recent_demands) / (len(recent_demands) or 1)) if recent_demands else 12
        discharges_today = round(sum(d.discharges for d in recent_demands) / (len(recent_demands) or 1)) if recent_demands else 9

    recent_appointments = (
        Appointment.query
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        .limit(6)
        .all()
    )

    departments = Department.query.all()

    return render_template(
        "admin/dashboard.html",
        user=current_user,
        total_doctors=total_doctors,
        total_patients=total_patients,
        total_appointments=total_appointments,
        available_beds=available_beds,
        total_beds=total_beds,
        icu_available=icu_available,
        admissions_today=admissions_today,
        discharges_today=discharges_today,
        recent_appointments=recent_appointments,
        departments=departments,
    )


# ============================================================
# MANAGE DOCTORS
# ============================================================
@admin.route("/doctors", methods=["GET", "POST"])
@admin_required
def doctors():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        department_id = request.form.get("department_id", type=int)
        specialization = request.form.get("specialization", "").strip()
        qualification = request.form.get("qualification", "").strip()
        experience = request.form.get("experience", type=int) or 0
        availability = request.form.get("availability", "").strip()

        if not name or not email or not password or not department_id or not specialization:
            flash("Please fill in all required fields to register a doctor.", "danger")
            return redirect(url_for("admin.doctors"))

        if User.query.filter_by(email=email).first():
            flash("A user with this email address already exists.", "warning")
            return redirect(url_for("admin.doctors"))

        try:
            user = User(
                name=name,
                email=email,
                phone=phone or None,
                role="doctor",
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            doctor_profile = Doctor(
                user_id=user.id,
                department_id=department_id,
                specialization=specialization,
                qualification=qualification or None,
                experience=max(0, experience),
                availability=availability or "Mon-Fri (09:00 - 16:00)"
            )
            db.session.add(doctor_profile)
            db.session.commit()
            flash(f"Doctor {name} added successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating doctor: {str(e)}", "danger")

        return redirect(url_for("admin.doctors"))

    # GET
    search = request.args.get("q", "").strip()
    dept_filter = request.args.get("dept", type=int)

    query = Doctor.query.join(User, Doctor.user_id == User.id).join(Department, Doctor.department_id == Department.id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(
            User.name.ilike(pattern),
            User.email.ilike(pattern),
            Doctor.specialization.ilike(pattern)
        ))

    if dept_filter:
        query = query.filter(Doctor.department_id == dept_filter)

    doctor_list = query.order_by(User.name.asc()).all()
    departments = Department.query.order_by(Department.name.asc()).all()

    return render_template(
        "admin/doctors.html",
        user=current_user,
        doctors=doctor_list,
        departments=departments,
        search=search,
        dept_filter=dept_filter
    )


@admin.route("/doctors/<int:doctor_id>/toggle", methods=["POST"])
@admin_required
def toggle_doctor_status(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.user.is_active = not doctor.user.is_active
    db.session.commit()
    status_str = "activated" if doctor.user.is_active else "deactivated"
    flash(f"Doctor {doctor.user.name} has been {status_str}.", "info")
    return redirect(url_for("admin.doctors"))


# ============================================================
# MANAGE PATIENTS
# ============================================================
@admin.route("/patients")
@admin_required
def patients():
    search = request.args.get("q", "").strip()
    query = Patient.query.join(User, Patient.user_id == User.id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(
            User.name.ilike(pattern),
            User.email.ilike(pattern),
            User.phone.ilike(pattern)
        ))

    patient_list = query.order_by(User.name.asc()).all()
    return render_template(
        "admin/patients.html",
        user=current_user,
        patients=patient_list,
        search=search
    )


# ============================================================
# DEPARTMENTS
# ============================================================
@admin.route("/departments", methods=["GET", "POST"])
@admin_required
def departments():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Department name is required.", "danger")
            return redirect(url_for("admin.departments"))

        if Department.query.filter_by(name=name).first():
            flash("Department with this name already exists.", "warning")
            return redirect(url_for("admin.departments"))

        dept = Department(name=name, description=description or None)
        db.session.add(dept)
        db.session.commit()
        flash(f"Department '{name}' created successfully.", "success")
        return redirect(url_for("admin.departments"))

    dept_list = Department.query.order_by(Department.name.asc()).all()
    return render_template(
        "admin/departments.html",
        user=current_user,
        departments=dept_list
    )


# ============================================================
# APPOINTMENTS
# ============================================================
@admin.route("/appointments", methods=["GET", "POST"])
@admin_required
def appointments():
    if request.method == "POST":
        appointment_id = request.form.get("appointment_id", type=int)
        status = request.form.get("status", "").strip().lower()

        appt = Appointment.query.get_or_404(appointment_id)
        if status in ["pending", "confirmed", "completed", "cancelled"]:
            appt.status = status
            db.session.commit()
            flash(f"Appointment #{appt.id} status updated to {status}.", "success")
        else:
            flash("Invalid appointment status.", "danger")
        return redirect(url_for("admin.appointments"))

    status_filter = request.args.get("status", "").strip().lower()
    query = Appointment.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    appt_list = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    return render_template(
        "admin/appointments.html",
        user=current_user,
        appointments=appt_list,
        status_filter=status_filter
    )


# ============================================================
# BEDS & ICU MANAGEMENT
# ============================================================
@admin.route("/beds", methods=["GET", "POST"])
@admin_required
def beds():
    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "add":
            bed_number = request.form.get("bed_number", "").strip().upper()
            ward = request.form.get("ward", "").strip()
            bed_type = request.form.get("bed_type", "General")
            notes = request.form.get("notes", "").strip()

            if not bed_number or not ward:
                flash("Bed number and Ward are required.", "danger")
                return redirect(url_for("admin.beds"))

            if Bed.query.filter_by(bed_number=bed_number).first():
                flash(f"Bed number {bed_number} already exists.", "warning")
                return redirect(url_for("admin.beds"))

            bed = Bed(
                bed_number=bed_number,
                ward=ward,
                bed_type=bed_type,
                status="Available",
                notes=notes or None
            )
            db.session.add(bed)
            db.session.commit()
            flash(f"Bed {bed_number} added successfully.", "success")

        elif action == "update_status":
            bed_id = request.form.get("bed_id", type=int)
            new_status = request.form.get("status", "Available")
            patient_id = request.form.get("patient_id", type=int)

            bed = Bed.query.get_or_404(bed_id)
            if new_status == "Occupied":
                if not patient_id:
                    flash("Please select a patient to admit to this bed.", "warning")
                    return redirect(url_for("admin.beds"))

                # Reassign patient safely if they were assigned to another bed
                prev_beds = Bed.query.filter(Bed.patient_id == patient_id, Bed.id != bed.id).all()
                for pb in prev_beds:
                    pb.patient_id = None
                    pb.status = "Available"

                bed.status = "Occupied"
                bed.patient_id = patient_id
                patient = Patient.query.get(patient_id)
                patient_name = patient.user.name if (patient and patient.user) else f"Patient #{patient_id}"
                flash(f"Bed {bed.bed_number} ({bed.ward}) successfully assigned to {patient_name}.", "success")
            elif new_status == "Available":
                bed.status = "Available"
                bed.patient_id = None
                flash(f"Bed {bed.bed_number} is now Available.", "info")
            else:
                bed.status = new_status
                if new_status != "Occupied":
                    bed.patient_id = None
                flash(f"Bed {bed.bed_number} updated to {new_status}.", "success")

            db.session.commit()

        elif action == "discharge":
            bed_id = request.form.get("bed_id", type=int)
            bed = Bed.query.get_or_404(bed_id)
            patient_name = bed.patient.user.name if (bed.patient and bed.patient.user) else "Patient"
            bed.status = "Available"
            bed.patient_id = None
            db.session.commit()
            flash(f"{patient_name} discharged. Bed {bed.bed_number} is now Available.", "info")

        return redirect(url_for("admin.beds"))

    bed_type_filter = request.args.get("type", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = Bed.query
    if bed_type_filter:
        query = query.filter_by(bed_type=bed_type_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    beds_list = query.order_by(Bed.ward.asc(), Bed.bed_number.asc()).all()
    patients_list = Patient.query.join(User).order_by(User.name.asc()).all()

    # Counts
    total_beds = Bed.query.count()
    available_count = Bed.query.filter_by(status="Available").count()
    occupied_count = Bed.query.filter_by(status="Occupied").count()
    icu_available = Bed.query.filter_by(bed_type="ICU", status="Available").count()

    return render_template(
        "admin/beds.html",
        user=current_user,
        beds=beds_list,
        patients=patients_list,
        total_beds=total_beds,
        available_count=available_count,
        occupied_count=occupied_count,
        icu_available=icu_available,
        bed_type_filter=bed_type_filter,
        status_filter=status_filter
    )


# ============================================================
# HOSPITAL DEMAND DATA
# ============================================================
@admin.route("/demand", methods=["GET", "POST"])
@admin_required
def demand():
    if request.method == "POST":
        rec_date = request.form.get("date", "")
        department = request.form.get("department", "").strip()
        patient_count = request.form.get("patient_count", type=int) or 0
        admissions = request.form.get("admissions", type=int) or 0
        discharges = request.form.get("discharges", type=int) or 0
        beds_available = request.form.get("beds_available", type=int) or 0
        icu_available = request.form.get("icu_available", type=int) or 0

        try:
            parsed_date = date.fromisoformat(rec_date)
            entry = HospitalDemand(
                date=parsed_date,
                department=department,
                patient_count=patient_count,
                admissions=admissions,
                discharges=discharges,
                beds_available=beds_available,
                icu_available=icu_available
            )
            db.session.add(entry)
            db.session.commit()
            flash("Demand data recorded successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to record demand data: {str(e)}", "danger")

        return redirect(url_for("admin.demand"))

    records = HospitalDemand.query.order_by(HospitalDemand.date.desc()).limit(100).all()
    departments = Department.query.order_by(Department.name.asc()).all()

    return render_template(
        "admin/demand.html",
        user=current_user,
        records=records,
        departments=departments,
        today=date.today().isoformat()
    )


# ============================================================
# AI FORECAST REPORT
# ============================================================
@admin.route("/forecast", methods=["GET", "POST"])
@admin_required
def forecast():
    if request.method == "POST":
        # Recalculate AI forecast
        days = request.form.get("days", type=int) or 7
        generate_forecast(days=days)
        flash(f"AI Demand Forecast recalculated successfully for the next {days} days.", "success")
        return redirect(url_for("admin.forecast"))

    summary = get_forecast_summary()
    return render_template(
        "admin/forecast.html",
        user=current_user,
        summary=summary
    )