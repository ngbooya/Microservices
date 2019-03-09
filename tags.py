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
    conn.execute("CREATE TABLE tags (id INTEGER PRIMARY KEY, title TEXT, body TEXT, date DATETIME);")
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




# Add an article with a new tag




# List all articles with the new tag




# Add another tag to the article




# Delete one of the tags from the article






# Add a tag to an article that doesn’t exist








if __name__ == "__main__":
    app.run()
