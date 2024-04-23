from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
from hangman import app, db


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)

    def get_reset_token(self):
        s = Serializer(app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, max_age=1800)["user_id"]
        except:
            return None
        return User.query.get(user_id)
    

