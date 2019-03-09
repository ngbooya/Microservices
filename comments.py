from flask import Flask, g, render_template, request
import sqlite3, json
from flask import jsonify
import os

DATABASE = "./database.db"


# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'


if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    conn.execute("CREATE TABLE comments (id INTEGER PRIMARY KEY, title TEXT, body TEXT, date DATETIME);")
    conn.commit()
    conn.commit()
    conn.close()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()




# Try to add a comment to an article that doesn’t exist






# Post an anonymous comment on an article






# Post an authenticated comment on an article






# Check that the comments on the article were returned in order









if __name__ == "__main__":
    app.run()
