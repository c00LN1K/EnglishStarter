from datetime import datetime

from flask import flash
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
    is_him = db.Column(db.Boolean, default=False)

    @staticmethod
    def add_word(word, user_id):
        if Word.query.filter_by(value=word).first():
            word_id = Word.query.filter_by(value=word).first().id
            print("Word ID:", word_id)
            if Pole.query.filter_by(word_id=word_id).first():
                flash('This word has already in your dictionary')
            else:
                p = Pole(user_id=user_id, word_id=word_id, rating=0, is_him=True)
                db.session.add(p)
                db.session.commit()
                flash('Ваше слово добавлено в pole')
        else:
            w = Word(value=word)
            db.session.add(w)
            db.session.commit()
            word_id = Word.query.filter_by(value=word).first().id
            print("Word ID:", word_id)
            if Pole.query.filter_by(word_id=word_id).first():
                flash('This word has already in your dictionary')
            else:
                p = Pole(user_id=user_id, word_id=word_id, rating=0, is_him=True)
                db.session.add(p)
                db.session.commit()
                flash('Ваше слово добавлено с добавлением самого слова в бд')

    @staticmethod
    def get_words(user_id):
        words = []
        try:
            words = Pole.query.filter_by(user_id=user_id)
        except Exception as ex:
            print("Ошибка при получении слов из словаря -", ex)
        return words


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

    @staticmethod
    def get_profile(user_id):
        profile = []
        try:
            profile = Profiles.query.filter_by(user_id=user_id).first()
        except Exception as ex:
            print('Ошибка при получении профиля -', profile)
        return profile

    def __repr__(self):
        return f'<profiles {self.id}>'


class Image(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, nullable=True)
    mimetype = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
