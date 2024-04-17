from flask import Flask, render_template, flash, url_for, redirect
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from Tasker import config
from db import *

from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config.from_object(config.__name__)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для просмотра страницы авторизуйтесь'
login_manager.login_message_category = 'failed'
login_manager.init_app(app)

menu = [

]


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html', title='Main')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('Пользователь с таким email уже существует')
                return redirect(url_for('register'))

            hash = generate_password_hash(form.password.data)
            u = User(email=form.email.data, psw=hash)
            db.session.add(u)
            db.session.flush()

            p = Profile(name=form.name.data, old=form.old.data, user_id=u.id)
            db.session.add(p)
            db.session.flush()

            table = Table(user_id=u.id)
            db.session.add(table)
            db.session.flush()

            db.session.commit()
            flash('Успешная регистрация!')
            return redirect(url_for('login'))

        except Exception as ex:
            db.session.rollback()
            flash('Ошибка добавления')
            print('register: Ошибка при добавлении пользователя в БД - ', ex)

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.psw, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('profile'))
        else:
            flash('Неверный логин или пароль или такого пользователя не существует')

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    p = Profile.get_profile(current_user.id)
    return render_template('profile.html', title='Профиль', menu=menu, profile=profile)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(port=7001, debug=True)
