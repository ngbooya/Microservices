from flask import Flask, g, render_template, request, make_response
import sqlite3, json
from flask import jsonify
import os
from functools import wraps

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
DATABASE = "./database.db"

# HTTP Basic Auth declaration
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
	cur.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, email TEXT, password TEXT );")
	conn.commit()
	conn.close()

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
		db.row_factory = dict_factory
	return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/users/create", methods = ['POST'])
def createUser():
	if request.method == 'POST':
		conn = get_db()
		cur = conn.cursor()
		cur.execute('INSERT INTO users VALUES( NULL,"ngbooya@gmail.com","password")')
		conn.commit()

		show = cur.execute("SELECT * FROM users")
		data = show.fetchone()
		print(data)
		data.update({"location":"http://locahost:5000/users"})
		conn.close()
		return jsonify(data),201

@app.route("/users/delete", methods =['DELETE'])
def deleteUser():
	if request.method == 'DELETE':
		print("REMOVE")
