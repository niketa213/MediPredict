from models import db


class Bed(db.Model):
    __tablename__ = "beds"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    bed_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    ward = db.Column(
        db.String(100),
        nullable=False
    )

    bed_type = db.Column(
        db.String(20),
        nullable=False,
        default="General"
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Available"
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "assigned_bed",
            uselist=False
        )
    )

    def __init__(
        self,
        bed_number=None,
        ward=None,
        bed_type="General",
        status="Available",
        patient_id=None,
        notes=None,
        **kwargs,
    ):
        super().__init__()
        self.bed_number = bed_number
        self.ward = ward
        self.bed_type = bed_type
        self.status = status
        self.patient_id = patient_id
        self.notes = notes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Bed {self.bed_number}>"