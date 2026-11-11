from datetime import date, time
from app import app
from models import (
    db, User, Department, Doctor, Patient, Bed, Appointment
)
from utils.forecast import seed_sample_demand_data, generate_forecast

ADMIN_EMAIL = "admin@medipredict.com"
ADMIN_PASSWORD = "ChangeThisAdminPassword123!"

DOCTOR_EMAIL = "doctor@medipredict.com"
DOCTOR_PASSWORD = "DoctorPassword123!"

PATIENT_EMAIL = "patient@medipredict.com"
PATIENT_PASSWORD = "PatientPassword123!"

DEPARTMENTS = [
    {
        "name": "General Medicine",
        "description": "Comprehensive primary medical care, diagnostics, and routine consultations for all acute and chronic illnesses."
    },
    {
        "name": "Cardiology",
        "description": "Specialized care for heart and cardiovascular health, arrhythmias, chest pain diagnostics, and hypertension management."
    },
    {
        "name": "Neurology",
        "description": "Expert diagnostics and treatments for neurological disorders, migraines, seizures, and nerve conditions."
    },
    {
        "name": "Orthopedics",
        "description": "Bone, joint, ligament, and musculoskeletal surgical and rehabilitative care, fractures, and sports injuries."
    },
    {
        "name": "Dermatology",
        "description": "Diagnosis and management of skin, hair, and nail conditions, allergies, and dermatological therapies."
    },
    {
        "name": "Pediatrics",
        "description": "Dedicated infant, child, and adolescent healthcare, developmental assessments, and immunization services."
    },
    {
        "name": "Pulmonology",
        "description": "Respiratory care, asthma, chronic bronchitis, lung infections, and pulmonary diagnostics."
    },
    {
        "name": "Gastroenterology",
        "description": "Digestive tract, liver, and abdominal health management, endoscopy, and gastroenterological care."
    },
    {
        "name": "ENT",
        "description": "Ear, nose, and throat diagnostic assessments, hearing care, sinus treatment, and allergy therapies."
    },
    {
        "name": "Gynecology",
        "description": "Women's healthcare, prenatal care, reproductive medicine, and obstetrics consultations."
    }
]

DOCTORS_DATA = [
    {
        "name": "Dr. Sarah Jenkins",
        "email": DOCTOR_EMAIL,
        "phone": "+1 555-0101",
        "dept": "Cardiology",
        "specialization": "Interventional Cardiology",
        "qualification": "MD, FACC - Harvard Medical School",
        "experience": 14,
        "availability": "Mon-Fri (09:00 - 15:00)"
    },
    {
        "name": "Dr. Rajesh Sharma",
        "email": "dr.sharma@medipredict.com",
        "phone": "+1 555-0102",
        "dept": "General Medicine",
        "specialization": "Internal Medicine & Diagnostics",
        "qualification": "MBBS, MD - Johns Hopkins University",
        "experience": 16,
        "availability": "Mon-Sat (08:30 - 14:00)"
    },
    {
        "name": "Dr. Emily Watson",
        "email": "dr.watson@medipredict.com",
        "phone": "+1 555-0103",
        "dept": "Neurology",
        "specialization": "Clinical Neurophysiology",
        "qualification": "MD, PhD - Stanford University",
        "experience": 11,
        "availability": "Tue-Sat (10:00 - 16:00)"
    },
    {
        "name": "Dr. Marcus Lee",
        "email": "dr.lee@medipredict.com",
        "phone": "+1 555-0104",
        "dept": "Orthopedics",
        "specialization": "Joint Reconstruction & Trauma",
        "qualification": "MS (Ortho), Fellowship in Arthroplasty",
        "experience": 12,
        "availability": "Mon, Wed, Fri (09:00 - 17:00)"
    },
    {
        "name": "Dr. Priya Patel",
        "email": "dr.patel@medipredict.com",
        "phone": "+1 555-0105",
        "dept": "Dermatology",
        "specialization": "Clinical & Cosmetic Dermatology",
        "qualification": "MD (DVL) - Oxford University",
        "experience": 9,
        "availability": "Mon-Thu (10:00 - 15:30)"
    },
    {
        "name": "Dr. David Chen",
        "email": "dr.chen@medipredict.com",
        "phone": "+1 555-0106",
        "dept": "Pulmonology",
        "specialization": "Critical Care & Respiratory Diseases",
        "qualification": "MD, FCCP - Mayo Clinic",
        "experience": 15,
        "availability": "Mon-Fri (09:00 - 14:00)"
    },
    {
        "name": "Dr. Olivia Miller",
        "email": "dr.miller@medipredict.com",
        "phone": "+1 555-0107",
        "dept": "Pediatrics",
        "specialization": "Pediatric Critical Care & Neonatology",
        "qualification": "MD (Pediatrics) - Columbia University",
        "experience": 8,
        "availability": "Mon-Fri (08:00 - 13:00)"
    }
]

BEDS_DATA = [
    # General Ward A
    {"bed_number": "GEN-101", "ward": "General Ward A", "bed_type": "General", "status": "Available"},
    {"bed_number": "GEN-102", "ward": "General Ward A", "bed_type": "General", "status": "Occupied"},
    {"bed_number": "GEN-103", "ward": "General Ward A", "bed_type": "General", "status": "Available"},
    {"bed_number": "GEN-104", "ward": "General Ward A", "bed_type": "General", "status": "Available"},
    {"bed_number": "GEN-105", "ward": "General Ward A", "bed_type": "General", "status": "Occupied"},
    # General Ward B
    {"bed_number": "GEN-201", "ward": "General Ward B", "bed_type": "General", "status": "Available"},
    {"bed_number": "GEN-202", "ward": "General Ward B", "bed_type": "General", "status": "Available"},
    {"bed_number": "GEN-203", "ward": "General Ward B", "bed_type": "General", "status": "Occupied"},
    {"bed_number": "GEN-204", "ward": "General Ward B", "bed_type": "General", "status": "Maintenance"},
    # ICU
    {"bed_number": "ICU-01", "ward": "Critical Care ICU", "bed_type": "ICU", "status": "Available"},
    {"bed_number": "ICU-02", "ward": "Critical Care ICU", "bed_type": "ICU", "status": "Occupied"},
    {"bed_number": "ICU-03", "ward": "Critical Care ICU", "bed_type": "ICU", "status": "Available"},
    {"bed_number": "ICU-04", "ward": "Cardiac ICU", "bed_type": "ICU", "status": "Available"},
    {"bed_number": "ICU-05", "ward": "Cardiac ICU", "bed_type": "ICU", "status": "Occupied"},
    # Private & Semi-Private
    {"bed_number": "PRV-301", "ward": "Executive Suite", "bed_type": "Private", "status": "Available"},
    {"bed_number": "PRV-302", "ward": "Executive Suite", "bed_type": "Private", "status": "Occupied"},
    {"bed_number": "EMG-01", "ward": "Emergency Triage", "bed_type": "Emergency", "status": "Available"},
    {"bed_number": "EMG-02", "ward": "Emergency Triage", "bed_type": "Emergency", "status": "Available"}
]


def seed_database():
    with app.app_context():
        # Ensure all tables exist
        db.create_all()

        print("--- Seeding Admin Account ---")
        admin = User.query.filter_by(email=ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                name="System Administrator",
                email=ADMIN_EMAIL,
                role="admin",
                is_active=True
            )
            admin.set_password(ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print(f"Created Admin: {ADMIN_EMAIL}")
        else:
            print("Admin already exists.")

        print("--- Seeding Departments ---")
        dept_map = {}
        for d_data in DEPARTMENTS:
            dept = Department.query.filter_by(name=d_data["name"]).first()
            if not dept:
                dept = Department(name=d_data["name"], description=d_data["description"])
                db.session.add(dept)
                db.session.commit()
                print(f"Added Department: {dept.name}")
            dept_map[dept.name] = dept

        print("--- Seeding Doctors ---")
        for doc_data in DOCTORS_DATA:
            u = User.query.filter_by(email=doc_data["email"]).first()
            if not u:
                u = User(
                    name=doc_data["name"],
                    email=doc_data["email"],
                    phone=doc_data["phone"],
                    role="doctor",
                    is_active=True
                )
                u.set_password(DOCTOR_PASSWORD)
                db.session.add(u)
                db.session.flush()

                dept = dept_map.get(doc_data["dept"])
                if not dept:
                    dept = Department.query.filter_by(name=doc_data["dept"]).first()

                doctor_profile = Doctor(
                    user_id=u.id,
                    department_id=dept.id,
                    specialization=doc_data["specialization"],
                    qualification=doc_data["qualification"],
                    experience=doc_data["experience"],
                    availability=doc_data["availability"]
                )
                db.session.add(doctor_profile)
                db.session.commit()
                print(f"Added Doctor: {u.name} ({doc_data['dept']})")

        print("--- Seeding Sample Patient ---")
        patient_user = User.query.filter_by(email=PATIENT_EMAIL).first()
        if not patient_user:
            patient_user = User(
                name="Alex Johnson",
                email=PATIENT_EMAIL,
                phone="+1 555-0199",
                role="patient",
                is_active=True
            )
            patient_user.set_password(PATIENT_PASSWORD)
            db.session.add(patient_user)
            db.session.flush()

            patient_profile = Patient(
                user_id=patient_user.id,
                date_of_birth=date(1992, 5, 14),
                gender="Male",
                address="742 Evergreen Terrace, Springfield",
                emergency_contact="+1 555-0911"
            )
            db.session.add(patient_profile)
            db.session.commit()
            print(f"Added Sample Patient: {patient_user.email}")
        else:
            patient_profile = patient_user.patient_profile
            if not patient_profile:
                patient_profile = Patient(user_id=patient_user.id)
                db.session.add(patient_profile)
                db.session.commit()

        print("--- Seeding Beds ---")
        if Bed.query.count() == 0:
            for b in BEDS_DATA:
                bed = Bed(
                    bed_number=b["bed_number"],
                    ward=b["ward"],
                    bed_type=b["bed_type"],
                    status=b["status"],
                    patient_id=patient_profile.id if b["status"] == "Occupied" and patient_profile else None
                )
                db.session.add(bed)
            db.session.commit()
            print(f"Added {len(BEDS_DATA)} hospital beds.")

        print("--- Seeding Sample Appointments ---")
        if Appointment.query.count() == 0:
            first_doc = Doctor.query.first()
            if first_doc and patient_profile:
                sample_appt = Appointment(
                    patient_id=patient_profile.id,
                    doctor_id=first_doc.id,
                    appointment_date=date.today(),
                    appointment_time=time(10, 30),
                    reason="Routine checkup and blood pressure monitoring",
                    status="confirmed"
                )
                db.session.add(sample_appt)
                db.session.commit()
                print("Added sample confirmed appointment.")

        print("--- Seeding Historical Demand & AI Forecast ---")
        seed_sample_demand_data(days=30)
        generate_forecast(days=7)
        print("Hospital demand data and AI forecasts generated.")

        print("\n=== All Database Seeding Completed Successfully! ===")


if __name__ == "__main__":
    seed_database()