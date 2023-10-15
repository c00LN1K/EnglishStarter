import os
import random

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, current_user, login_required, login_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm

from db import db

# Конфигурация
DEBUG = True
SECRET_KEY = '4fc189e327ecca72'
MAX_CONTENT_LENGTH = 1024 * 1024
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(__name__)


db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для просмотра страницы авторизуйтесь'
login_manager.login_message_category = 'failed'
login_manager.init_app(app)

menu = [
    {'url': 'index', 'title': 'Главная страница'},
    {'url': 'lessons', 'title': 'Уроки'},
    {'url': 'exercise', 'title': 'Упражнения'},
    {'url': 'dictionary', 'title': 'Словарь'},
    {'url': 'login', 'title': 'Авторизация'}

]

dct = {
    "apple": "яблоко",
    "book": "книга",
    "car": "машина",
    "dog": "собака",
    "cat": "кошка",
    "house": "дом",
    "tree": "дерево",
    "computer": "компьютер",
    "friend": "друг",
    "family": "семья",
    "school": "школа",
    "pen": "ручка",
    "pencil": "карандаш",
    "sun": "солнце",
    "moon": "луна",
    "flower": "цветок",
    "water": "вода",
    "air": "воздух",
    "food": "пища",
    "music": "музыка"
}


@app.route('/')
def index():
    return render_template('index.html', menu=menu, title='Главная страница')


@app.route('/lessons')
def lessons():
    return render_template('lessons.html')


@app.route('/exercise', methods=['POST', 'GET'])
@login_required
def exercise():
    if current_user.is_authenticated:
        flash('Вы уже вошли в свой профиль')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        answer = request.form.get('answer')
        word = request.form.get('word')
        if word.lower() == answer.lower():
            flash("Well done!")
        else:
            flash(f"Wrong answer! The correct answer - {word}")
    key = random.choice(list(dct.keys()))
    word = dct[key]
    return render_template('exercise.html', word=word, answer=key)


@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Realization of addition user in db
        try:
            # Проверка на уже существующего пользователя
            user = Users.query.filter_by(email=form.email.data).first()
            if user:
                flash('Пользователь с таким email уже существует')
                return redirect(url_for('register'))

            hash = generate_password_hash(form.password.data)
            u = Users(email=form.email.data, psw=hash)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=form.name.data, old=form.old.data, user_id=u.id)
            db.session.add(p)
            db.session.flush()

            db.session.commit()

            flash('Успешная регистрация!')
            return redirect(url_for('login'))

        except Exception as ex:
            db.session.rollback()
            flash('Ошибка добавления')
            print('Ошибка при добавлении пользователя в БД - ', ex)

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('profile')
    form = LoginForm()
    # Нужно ли проверять запрос на POST?
    if form.validate_on_submit():
        # Realization checking data and entering
        user = Users.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.psw, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('profile'))
        else:
            flash('Неверный логин или пароль или такого пользователя не существует')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/profile')
def profile():
    return 'Profile'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


if __name__ == '__main__':
    from DBModels import Users, Profiles

    app.run(debug=True)
