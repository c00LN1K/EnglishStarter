from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(UserMixin, db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)

    def __repr__(self):
        return f"<{__class__.__name__}(id={self.id})>"


class User(BaseModel):
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())


class Profile(BaseModel):
    name = db.Column(db.String(50), nullable=False)
    old = db.Column(db.Integer, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def get_profile(user_id):
        profile = []
        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
        except Exception as ex:
            print('Ошибка при получении профиля -', profile)
        return profile


class Task(BaseModel):
    title = db.Column(db.String(100), nullable=True)
    text = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())

    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))


class Table(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
