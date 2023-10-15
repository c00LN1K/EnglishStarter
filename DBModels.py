from datetime import datetime

from flask_login import UserMixin

from db import db


# создание бд
# with app.app_context():
#     db.create_all()


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
