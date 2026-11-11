from models import db


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    prediction_date = db.Column(
        db.Date,
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=False
    )

    predicted_patients = db.Column(
        db.Integer,
        default=0
    )

    predicted_beds = db.Column(
        db.Integer,
        default=0
    )

    predicted_icu = db.Column(
        db.Integer,
        default=0
    )

    model_version = db.Column(
        db.String(50),
        default="v1.0"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __init__(
        self,
        prediction_date=None,
        department=None,
        predicted_patients=0,
        predicted_beds=0,
        predicted_icu=0,
        model_version="v1.0",
        **kwargs,
    ):
        super().__init__()
        self.prediction_date = prediction_date
        self.department = department
        self.predicted_patients = predicted_patients
        self.predicted_beds = predicted_beds
        self.predicted_icu = predicted_icu
        self.model_version = model_version
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Prediction {self.prediction_date} - {self.department}>"