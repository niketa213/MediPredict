from models import db


class Doctor(db.Model):
    __tablename__ = "doctors"

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

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    specialization = db.Column(
        db.String(150),
        nullable=False
    )

    qualification = db.Column(
        db.String(200)
    )

    experience = db.Column(
        db.Integer,
        default=0
    )

    availability = db.Column(
        db.String(255)
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "doctor_profile",
            uselist=False
        )
    )

    def __init__(
        self,
        user_id=None,
        department_id=None,
        specialization=None,
        qualification=None,
        experience=0,
        availability=None,
        **kwargs,
    ):
        super().__init__()
        self.user_id = user_id
        self.department_id = department_id
        self.specialization = specialization
        self.qualification = qualification
        self.experience = experience
        self.availability = availability
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Doctor {self.id}>"