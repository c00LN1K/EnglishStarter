import os
import random
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for, session, make_response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from googletrans import Translator
from DBModels import db, Word, Image

# Конфигурация
DEBUG = True
SECRET_KEY = '4fc189e327ecca72'
MAX_CONTENT_LENGTH = 1024 * 1024
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(__name__)

db.init_app(app)

app.jinja_env.filters['zip'] = zip

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для просмотра страницы авторизуйтесь'
login_manager.login_message_category = 'failed'
login_manager.init_app(app)

menu = [
    {'url': 'index', 'title': 'Главная страница'},
    {'url': 'exercise', 'title': 'Тренировка'},
    {'url': 'dictionary', 'title': 'Мой словарь'},
    {'url': 'profile', 'title': 'Профиль'}
]


@app.route('/')
def index():
    return render_template('index.html', menu=menu, title='Главная страница')


@app.route('/exercise', methods=['POST', 'GET'])
def exercise():
    if not current_user.is_authenticated:
        flash('Похоже вы не авторизованы. Ваш прогресс не будет сохранен(')
    if request.method == 'POST':
        is_add = request.form.get('add')
        print(is_add)
        if is_add:
            try:
                id_word = Word.query.filter_by(value=session['last_word']).first().id
                p = Pole(user_id=current_user.id, word_id=id_word, rating=0)
                db.session.add(p)
                db.session.flush()
                db.session.commit()
                print('Слово успешно добавлено в Post')
                flash(f'Слово {session["last_word"]} успешно добавлено в ваш словарь!', category='success')
            except Exception as ex:
                print('Ошибка при добавлении слова в Post')
                flash('Ошибка при добавлении слова', category='failed')
                print(ex)
                db.session.rollback()

        translation = request.form['translation'].title()
        print(translation)
        current_word = session['current_word']
        print(translation, translate_to_russian(current_word))
        if current_word and translation == translate_to_russian(current_word).title():
            flash(f"Nicecook - {translation}", category='success')
            session['last_word'] = None
        else:
            if not current_user.is_authenticated:
                flash(
                    f'{session["current_word"].title()} - {translate_to_russian(session["current_word"]).title()}',
                    category='failed')
            else:
                id_word = Word.query.filter_by(value=session['current_word']).first().id
                pole = Pole.query.filter_by(word_id=id_word).first()
                if pole:
                    flash(f'Ну ты лох!) - {translate_to_russian(session["current_word"]).title()}', category='failed')
                    pole.rating -= 5
                    session['last_word'] = None
                else:
                    flash(
                        f'{session["current_word"].title()} - {translate_to_russian(session["current_word"]).title()}',
                        category='failed')
                    session['last_word'] = current_word
    else:
        session['last_word'] = None
    session['current_word'] = get_random_word()
    return render_template('exercise.html', word=session['current_word'], menu=menu, last_word=session['last_word'],
                           title='Тренировка')


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
    if request.method == 'POST':
        word = request.form['word'].lower()
        print("Received word:", word)
        Pole.add_word(word, current_user.id)

    records = Pole.get_words(current_user.id)
    words = []
    for rec in records:
        word = Word.query.get(rec.word_id).value
        words.append({
            'name': word,
            'translate': translate_to_russian(word),
            'rating': rec.rating,
            'is_him': bool(rec.is_him),
        })

    return render_template('dictionary.html', menu=menu, title='Мой словарь', words=words, zip=zip)


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
            # flash("Успешый вход")
            return redirect(url_for('profile'))
        else:
            flash('Неверный логин или пароль или такого пользователя не существует')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    prof = Profiles.get_profile(current_user.id)
    num_words = Pole.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', menu=menu, title='Профиль', profile=prof, num_words=num_words)


@app.route('/delete_word', methods=["POST", "GET"])
@login_required
def delete_word():
    print(request.form)
    if request.method == 'POST':
        if request.form.get('word'):
            word = request.form['word']
            word_id = Word.query.filter_by(value=word).first().id
            Pole.query.filter_by(user_id=current_user.id, word_id=word_id).delete()
            db.session.commit()
            flash(f'Слово {word} успешно удалено из вашего словаря', category='success')
    return redirect(url_for('dictionary'))


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            try:
                img = Image(img=file.read(), user_id=current_user.id, mimetype=file.mimetype)
                db.session.add(img)
                db.session.flush()
                db.session.commit()
                flash("Изображение успешно добавлено", category='success')
            except Exception as ex:
                print("Ошибка при загрузке изображения -", ex)
                flash('Ошибка при добавлении изображения. Попробуйте позже.', category='failed')

    return redirect(url_for('profile'))


@app.route('/get_image')
def get_image():
    image = Image.query.filter_by(user_id=current_user.id).first()
    if not image:
        # TODO: получение стандартного изображения должно быть из static
        with app.open_resource(app.root_path + url_for('static', filename='media/default.jpg')) as f:
            image = f.read()
            resp = make_response(image)
        resp.headers['Content-Type'] = 'image/jpg'
    else:
        resp = make_response(image.img)
        resp.headers['Content-Type'] = image.mimetype
    return resp


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, user_id)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    from DBModels import Users, Profiles, Pole

    app.run(debug=True, port=7000)
