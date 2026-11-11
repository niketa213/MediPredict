from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from models import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(db.String(20))

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="patient"
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __init__(
        self,
        name=None,
        email=None,
        phone=None,
        password_hash=None,
        role="patient",
        is_active=True,
        **kwargs,
    ):
        super().__init__()
        self.name = name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        for key, value in kwargs.items():
            setattr(self, key, value)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f"<User {self.email}>"