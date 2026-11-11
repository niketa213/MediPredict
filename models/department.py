from models import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    doctors = db.relationship(
        "Doctor",
        backref="department",
        lazy=True
    )

    def __init__(
        self,
        name=None,
        description=None,
        **kwargs,
    ):
        super().__init__()
        self.name = name
        self.description = description
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Department {self.name}>"