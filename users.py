from flask import Flask, g, render_template, request
import sqlite3, json
from flask import jsonify
import os
from functools import wraps
DATABASE = "./database.db"


#INITIALIZATION#

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'


def auth_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if auth and auth.username == 'username' and auth.password == 'password':
			return f(*args,**kwargs)
		return make_response('Could not verify your login!', 401, {'WWW-Authenicate':'Basic realm="Login Required"'})
	return decorated


if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.execute("CREATE TABLE articles (article_id INTEGER PRIMARY KEY, title TEXT, body TEXT, date DATETIME, user_id INTEGER REFERENCES users)")
    cur.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, email TEXT, password TEXT);")
    conn.commit()
    cur.execute("CREATE TABLE comments (comment_id INTEGER PRIMARY KEY, comment_text TEXT, date DATETIME, article_id REFERENCES articles);")
    conn.commit()
    conn.execute("CREATE TABLE tags (tag_id INTEGER PRIMARY KEY, article_id INTEGER REFERENCES articles, tag TEXT)")
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


#USERS#

#CREATE A USER
@app.route("/users/create", methods = ['POST'])
@auth_required
def createUser():
    if request.method == 'POST':
        content = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES( " + "NULL" + "," + "'" + content['email'] + "', " + "'" + content['password'] + "'"  + " );")
        conn.commit()
        #show = cur.execute("SELECT * FROM users")
        #data = show.fetchall()
        conn.close()
        #return jsonify(data), 201
        return jsonify({}), 201

#CHANGE THE PASSWORD OF A USER
@app.route("/users/changepassword",methods=['POST'])
@auth_required
def changePassword():
    content = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    if("user_id" in content and "password" in content):
        cur.execute('UPDATE users SET password="' + content['password'] + '" WHERE user_id=' + content['user_id'] + ';')
        conn.commit()
    conn.close()
    return jsonify({}), 200

#DELETE A USER
@app.route("/users/delete/<id>", methods =['DELETE'])
@auth_required
def deleteUser(id):
    if request.method == 'DELETE':
        conn = get_db()
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE user_id=' + id)
        conn.commit()
        conn.close()
        return jsonify({}),200

#APP RUN
if __name__ == "__main__":
    app.run()
