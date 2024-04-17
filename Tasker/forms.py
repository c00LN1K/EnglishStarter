from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import Email, DataRequired, Length, EqualTo, NumberRange, Optional


class RegisterForm(FlaskForm):
    name = StringField('Имя: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[Email(message='Некорректный email'), DataRequired()])
    old = IntegerField('Возраст', validators=[Optional(strip_whitespace=True),
                                              NumberRange(min=0, max=120, message='Введите корректный возраст')])

    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=5, max=100,
                                                                            message='Неверный пароль. Длина должна пароля от 5 до 100 символов')])
    password2 = PasswordField('Повтор пароля: ',
                              validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')])
    submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
    email = StringField('Логин (email) : ', validators=[Email(message='Некорректный email'), DataRequired()])
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=5, max=100,
                                                                            message='Неверный пароль. Длина должна пароля от 5 до 100 символов')])
    remember = BooleanField('Запомнить', default=False)
    submit = SubmitField('Войти')
