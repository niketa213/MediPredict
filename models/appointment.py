from models import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )

    appointment_date = db.Column(
        db.Date,
        nullable=False
    )

    appointment_time = db.Column(
        db.Time,
        nullable=False
    )

    reason = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(20),
        default="pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "appointments",
            lazy=True
        )
    )

    doctor = db.relationship(
        "Doctor",
        backref=db.backref(
            "appointments",
            lazy=True
        )
    )

    def __init__(
        self,
        patient_id=None,
        doctor_id=None,
        appointment_date=None,
        appointment_time=None,
        reason=None,
        status="pending",
        **kwargs,
    ):
        super().__init__()
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.reason = reason
        self.status = status
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Appointment {self.id}>"