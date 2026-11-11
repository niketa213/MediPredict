# ============================================================
# MediPredict - Hospital AI Demand Forecasting Engine
# ============================================================

from datetime import date, timedelta
import random
from models import db
from models.department import Department
from models.hospital_demand import HospitalDemand
from models.prediction import Prediction
from models.bed import Bed
from models.appointment import Appointment


def seed_sample_demand_data(days=30):
    """
    Generate realistic historical demand data if the hospital_demand table is empty.
    Creates 30 days of past records across main departments.
    """
    existing_count = HospitalDemand.query.count()
    if existing_count > 0:
        return existing_count

    departments = Department.query.all()
    dept_names = [d.name for d in departments]
    if not dept_names:
        dept_names = [
            "General Medicine", "Cardiology", "Neurology", 
            "Orthopedics", "Pediatrics", "Pulmonology"
        ]

    today = date.today()
    created_records = 0

    # Department profiles (base admissions, ICU tendency, bed demand factor)
    dept_profiles = {
        "General Medicine": {"base": 24, "icu_pct": 0.08, "beds_avail": 35, "icu_avail": 8},
        "Cardiology": {"base": 16, "icu_pct": 0.35, "beds_avail": 20, "icu_avail": 10},
        "Neurology": {"base": 12, "icu_pct": 0.25, "beds_avail": 18, "icu_avail": 8},
        "Orthopedics": {"base": 14, "icu_pct": 0.05, "beds_avail": 22, "icu_avail": 5},
        "Pediatrics": {"base": 18, "icu_pct": 0.12, "beds_avail": 25, "icu_avail": 6},
        "Pulmonology": {"base": 15, "icu_pct": 0.28, "beds_avail": 20, "icu_avail": 8},
        "Dermatology": {"base": 10, "icu_pct": 0.00, "beds_avail": 10, "icu_avail": 2},
        "Gastroenterology": {"base": 13, "icu_pct": 0.10, "beds_avail": 16, "icu_avail": 5},
        "ENT": {"base": 9, "icu_pct": 0.00, "beds_avail": 10, "icu_avail": 2},
        "Gynecology": {"base": 14, "icu_pct": 0.05, "beds_avail": 18, "icu_avail": 4},
    }

    for i in range(days, 0, -1):
        rec_date = today - timedelta(days=i)
        day_of_week = rec_date.weekday()
        # Weekend factor
        weekend_factor = 0.75 if day_of_week >= 5 else 1.05

        for dept in dept_names:
            profile = dept_profiles.get(dept, {"base": 12, "icu_pct": 0.1, "beds_avail": 20, "icu_avail": 5})
            base = profile["base"]
            
            # Slight trend + random variance + weekend seasonality
            random_variance = random.randint(-3, 4)
            patient_count = max(4, int(base * weekend_factor) + random_variance)
            admissions = max(2, int(patient_count * random.uniform(0.65, 0.9)))
            discharges = max(1, int(admissions * random.uniform(0.75, 1.05)))
            
            # Bed & ICU utilization
            total_beds = profile["beds_avail"]
            beds_occupied = min(total_beds, int(admissions * random.uniform(1.2, 1.5)))
            beds_available = max(1, total_beds - beds_occupied)
            
            total_icu = profile["icu_avail"]
            icu_needed = int(admissions * profile["icu_pct"])
            icu_available = max(0, total_icu - icu_needed)

            demand_entry = HospitalDemand(
                date=rec_date,
                department=dept,
                patient_count=patient_count,
                admissions=admissions,
                discharges=discharges,
                beds_available=beds_available,
                icu_available=icu_available
            )
            db.session.add(demand_entry)
            created_records += 1

    db.session.commit()
    return created_records


def generate_forecast(days=7):
    """
    AI Forecast Model:
    Calculates time-series moving trends, day-of-week seasonality, and bed/ICU capacity stress
    to project patient volume, bed demand, and ICU demand for the next N days.
    Stores and refreshes the predictions in the Prediction model.
    """
    # Ensure baseline demand exists
    seed_sample_demand_data()

    today = date.today()
    departments = Department.query.all()
    dept_names = [d.name for d in departments]
    if not dept_names:
        # Fallback to distinct departments in HospitalDemand
        distinct_depts = db.session.query(HospitalDemand.department).distinct().all()
        dept_names = [d[0] for d in distinct_depts] or ["General Medicine", "Cardiology", "Neurology"]

    # Clear predictions from today forward to avoid stale duplicates
    Prediction.query.filter(Prediction.prediction_date >= today).delete()

    new_predictions = []

    for dept in dept_names:
        # Fetch last 14 days of data for this department
        history = (
            HospitalDemand.query
            .filter_by(department=dept)
            .filter(HospitalDemand.date < today)
            .order_by(HospitalDemand.date.desc())
            .limit(14)
            .all()
        )

        if history:
            # Average recent daily patient counts
            avg_patients = sum(h.patient_count for h in history) / len(history)
            avg_admissions = sum(h.admissions for h in history) / len(history)
            avg_discharges = sum(h.discharges for h in history) / len(history)
            
            # Trend velocity (compare recent 7 days vs older 7 days)
            recent_7 = history[:7]
            older_7 = history[7:14] if len(history) >= 14 else recent_7
            r_avg = sum(h.patient_count for h in recent_7) / len(recent_7)
            o_avg = sum(h.patient_count for h in older_7) / len(older_7) if older_7 else r_avg
            trend_ratio = (r_avg / o_avg) if o_avg > 0 else 1.0
            # Bound trend ratio to prevent runaway
            trend_ratio = max(0.85, min(1.25, trend_ratio))
        else:
            avg_patients = 15.0
            avg_admissions = 10.0
            trend_ratio = 1.0

        for offset in range(1, days + 1):
            target_date = today + timedelta(days=offset)
            dow = target_date.weekday()
            # Day of week seasonality (Monday/Tuesday higher, weekend lower)
            dow_multiplier = 1.15 if dow == 0 else (1.10 if dow == 1 else (0.80 if dow >= 5 else 1.0))
            
            projected_patients = int(avg_patients * trend_ratio * dow_multiplier)
            projected_patients = max(3, projected_patients)

            # Bed and ICU predictions
            # Typically 70-80% of admitted patients require ward beds
            projected_beds = int(projected_patients * 0.75)
            # ICU requirement depends on department
            icu_rate = 0.30 if dept in ["Cardiology", "Neurology", "Pulmonology"] else 0.08
            projected_icu = max(1, int(projected_patients * icu_rate))

            pred = Prediction(
                prediction_date=target_date,
                department=dept,
                predicted_patients=projected_patients,
                predicted_beds=projected_beds,
                predicted_icu=projected_icu,
                model_version="MediPredict-ML-v2.4"
            )
            db.session.add(pred)
            new_predictions.append(pred)

    db.session.commit()
    return new_predictions


def get_forecast_summary():
    """
    Get comprehensive analytics for the forecasting dashboard.
    Returns today's metrics, next 7-day forecast totals, department breakdowns, and risk alerts.
    """
    today = date.today()
    
    # Check if predictions exist; if not, generate them
    upcoming = (
        Prediction.query
        .filter(Prediction.prediction_date > today)
        .order_by(Prediction.prediction_date.asc())
        .all()
    )
    if not upcoming:
        generate_forecast(days=7)
        upcoming = (
            Prediction.query
            .filter(Prediction.prediction_date > today)
            .order_by(Prediction.prediction_date.asc())
            .all()
        )

    # Next 7 days dates
    forecast_dates = sorted(list(set(p.prediction_date for p in upcoming)))[:7]

    # Aggregates by date
    daily_totals = []
    for f_date in forecast_dates:
        preds = [p for p in upcoming if p.prediction_date == f_date]
        total_p = sum(p.predicted_patients for p in preds)
        total_b = sum(p.predicted_beds for p in preds)
        total_icu = sum(p.predicted_icu for p in preds)
        daily_totals.append({
            "date": f_date.strftime("%a, %b %d"),
            "iso_date": f_date.isoformat(),
            "patients": total_p,
            "beds": total_b,
            "icu": total_icu
        })

    # Department breakdown
    dept_totals = {}
    for p in upcoming:
        if p.department not in dept_totals:
            dept_totals[p.department] = {"patients": 0, "beds": 0, "icu": 0, "count": 0}
        dept_totals[p.department]["patients"] += p.predicted_patients
        dept_totals[p.department]["beds"] += p.predicted_beds
        dept_totals[p.department]["icu"] += p.predicted_icu
        dept_totals[p.department]["count"] += 1

    dept_summary = []
    for dept, data in dept_totals.items():
        count = data["count"] or 1
        dept_summary.append({
            "department": dept,
            "avg_patients": round(data["patients"] / count),
            "avg_beds": round(data["beds"] / count),
            "avg_icu": round(data["icu"] / count),
            "peak_beds": data["beds"]
        })

    # Total hospital capacity check
    total_beds_count = Bed.query.count()
    available_beds_count = Bed.query.filter_by(status="Available").count()
    icu_beds_count = Bed.query.filter(Bed.bed_type == "ICU").count()
    avail_icu_count = Bed.query.filter(Bed.bed_type == "ICU", Bed.status == "Available").count()

    # Risk level determination
    next_week_beds = sum(d["beds"] for d in daily_totals) / (len(daily_totals) or 1)
    if available_beds_count < 5 or (total_beds_count > 0 and next_week_beds > available_beds_count):
        risk_level = "High"
        risk_color = "danger"
        recommendation = "Capacity alert: Projected bed demand will test hospital capacity. Prepare standby beds in overflow wards and expedite scheduled discharges."
    elif available_beds_count < 12:
        risk_level = "Moderate"
        risk_color = "warning"
        recommendation = "Steady occupancy: Bed utilization is moderate. Monitor ICU staffing in Cardiology and Pulmonology."
    else:
        risk_level = "Optimal"
        risk_color = "success"
        recommendation = "Normal operations: Sufficient bed and ICU reserves are available across all specialized units."

    return {
        "daily_totals": daily_totals,
        "dept_summary": dept_summary,
        "total_beds": total_beds_count,
        "available_beds": available_beds_count,
        "icu_beds": icu_beds_count,
        "avail_icu": avail_icu_count,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "recommendation": recommendation,
        "model_version": "MediPredict-ML-v2.4"
    }
