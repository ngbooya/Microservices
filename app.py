from flask import Flask, g, render_template, request
import sqlite3, json
from flask import jsonify
import os

DATABASE = "./database.db"

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

# check if the database exist, if not create the table and insert a few lines of data
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (title TEXT, body TEXT, date DATE);")
    conn.commit()
    cur.execute("INSERT INTO users VALUES('Article1', 'Body text.', '2019-03-05');")
    cur.execute("INSERT INTO users VALUES('Article2', 'Body text.', '2019-03-05');")
    #cur.execute("INSERT INTO users VALUES('Jerry', 'Mouse', '40');")
    #cur.execute("INSERT INTO users VALUES('Peter', 'Pan', '40');")
    conn.commit()
    conn.close()


# helper method to get the database since calls are per thread,
# and everything function is a new thread when called
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# helper to close
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    cur = get_db().cursor()
    res = cur.execute("select * from users")
    return render_template("index.html", users=res)

@app.route("/test", methods = ['GET','POST'])
def test():
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute("select * from users")
        data = res.fetchall()
        return jsonify(data), 200
    if request.method=='POST':
        conn = get_db()
        cur = conn.cursor()
        #res = cur.execute("select * from users")
        res = cur.execute("INSERT INTO users VALUES('Article1', 'Body text.', '2019-03-05');")
        conn.commit()
        res = cur.execute("select * from users")
        data = res.fetchall()
        return jsonify(data), 201


        


if __name__ == "__main__":
    """
	Use python sqlite3 to create a local database, insert some basic data and then
	display the data using the flask templating.
	
	http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
    """
    app.run()