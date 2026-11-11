from models import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    date_of_birth = db.Column(
        db.Date
    )

    gender = db.Column(
        db.String(20)
    )

    address = db.Column(
        db.Text
    )

    emergency_contact = db.Column(
        db.String(20)
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "patient_profile",
            uselist=False
        )
    )

    def __init__(
        self,
        user_id=None,
        date_of_birth=None,
        gender=None,
        address=None,
        emergency_contact=None,
        **kwargs,
    ):
        super().__init__()
        self.user_id = user_id
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.address = address
        self.emergency_contact = emergency_contact
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Patient {self.id}>"