from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'  # Имя вашей SQLite базы данных
db = SQLAlchemy(app)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100))
    translation = db.Column(db.String(100))
    rating = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    random_word = Word.query.order_by(db.func.random()).first()
    return render_template('index.html', word=random_word)

@app.route('/check_translation', methods=['POST'])
def check_translation():
    word_id = request.form['word_id']
    user_translation = request.form['user_translation']
    word = Word.query.get(word_id)

    if user_translation.lower() == word.translation.lower():
        word.rating += 1
        db.session.commit()
        flash('Правильно! Рейтинг увеличен.')
    else:
        word.rating -= 5
        db.session.commit()
        flash('Неправильно. Рейтинг уменьшен.')

    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.secret_key = 'your_secret_key'
    app.run(debug=True)


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100))
    translation = db.Column(db.String(100))
    rating = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    random_word = Word.query.order_by(db.func.random()).first()
    return render_template('index.html', word=random_word)

@app.route('/check_translation', methods=['POST'])
def check_translation():
    word_id = request.form['word_id']
    user_translation = request.form['user_translation']
    word = Word.query.get(word_id)

    if user_translation.lower() == word.translation.lower():
        word.rating += 1
        db.session.commit()
        flash('Правильно! Рейтинг увеличен.')
    else:
        word.rating -= 5
        db.session.commit()
        flash('Неправильно. Рейтинг уменьшен.')

    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
