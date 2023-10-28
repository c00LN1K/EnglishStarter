from datetime import datetime

from flask_login import UserMixin


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# # создание бд
# with app.app_context():
#     db.create_all()


class Word(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True)


class Pole(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    rating = db.Column(db.Integer)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # def __init__(self, email='', psw=''):
    #     self.psw = psw
    #     self.email = email

    def __repr__(self):
        return f'<users {self.id}>'


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<profiles {self.id}>'
