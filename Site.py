import os
import random
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_login import LoginManager, current_user, login_required, login_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from googletrans import Translator
from DBModels import db, Word

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
def exercise():
    flag = 'dk' in request.form

    if request.method == 'POST' and 'ch' in request.form:
        translation = request.form['translation'].title()
        print(translation)
        current_word = session['current_word']
        print(translation, translate_to_russian(current_word))
        if current_word and translation == translate_to_russian(current_word).title():
            flash(f"Nicecook - {translation}", category='success')
        else:
            flag = 1
    print(flag)
    if flag:
        if current_user.is_authenticated:
            try:
                id_word = Word.query.filter_by(value=session['current_word']).first().id
                pole = Pole.query.filter_by(word_id=id_word).first()
                if pole:
                    flash(f'Ну ты лох!) - {translate_to_russian(session["current_word"]).title()}', category='failed')
                    pole.rating -= 5
                else:
                    print('Dont know')
                    flash(
                        f'{session["current_word"].title()} - {translate_to_russian(session["current_word"]).title()}',
                        category='failed')
                    p = Pole(user_id=current_user.id, word_id=id_word, rating=0)
                    db.session.add(p)
                db.session.flush()
                db.session.commit()

            except Exception as ex:
                db.session.rollback()
                flash('Ошибка')
                print('Ошибка - ', ex)
        else:
            flash(
                f'{session["current_word"].title()} - {translate_to_russian(session["current_word"]).title()}',
                category='failed')
    session['current_word'] = get_random_word()
    return render_template('exercise.html', word=session['current_word'], menu=menu)


# Функция для получения случайного слова из БД
def get_random_word():
    return random.choice(Word.query.all()).value


# Функция для перевода слова на русский
def translate_to_russian(word):
    translator = Translator()
    translation = translator.translate(word, src='en', dest='ru')
    return translation.text


@app.route('/dictionary', methods=['POST', 'GET'])
@login_required
def dictionary():
    return render_template('dictionary.html', word=session['current_word'], menu=menu)


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
        # Realization \ing data and entering
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
    return db.session.get(Users, user_id)


if __name__ == '__main__':
    from DBModels import Users, Profiles, Pole

    app.run(debug=True)
