from DBModels import Word
from Site import db, app

file = open('words.txt')

words = file.readlines()

for word in words:
    with app.app_context():
        w = Word(value=word)
        db.session.add(w)
        db.session.flush()
        db.session.commit()
