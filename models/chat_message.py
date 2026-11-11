from models import db


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    sender = db.Column(
        db.String(20),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "chat_messages",
            lazy=True
        )
    )

    def __init__(
        self,
        user_id=None,
        sender=None,
        message=None,
        **kwargs,
    ):
        super().__init__()
        self.user_id = user_id
        self.sender = sender
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return (
            f"<ChatMessage "
            f"{self.id} - {self.sender}>"
        )