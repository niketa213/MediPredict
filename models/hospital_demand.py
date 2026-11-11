from models import db


class HospitalDemand(db.Model):
    __tablename__ = "hospital_demand"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=False
    )

    patient_count = db.Column(
        db.Integer,
        default=0
    )

    admissions = db.Column(
        db.Integer,
        default=0
    )

    discharges = db.Column(
        db.Integer,
        default=0
    )

    beds_available = db.Column(
        db.Integer,
        default=0
    )

    icu_available = db.Column(
        db.Integer,
        default=0
    )

    def __init__(
        self,
        date=None,
        department=None,
        patient_count=0,
        admissions=0,
        discharges=0,
        beds_available=0,
        icu_available=0,
        **kwargs,
    ):
        super().__init__()
        self.date = date
        self.department = department
        self.patient_count = patient_count
        self.admissions = admissions
        self.discharges = discharges
        self.beds_available = beds_available
        self.icu_available = icu_available
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<HospitalDemand {self.date} - {self.department}>"