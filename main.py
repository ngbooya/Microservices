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
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.execute("CREATE TABLE articles (article_id INTEGER PRIMARY KEY, title TEXT, body TEXT, date DATETIME, user_id INTEGER REFERENCES users)")
    cur.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, email TEXT, password TEXT);")
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

@app.route("/test", methods = ['GET','POST'])
def test():
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute("select * from articles")
        data = res.fetchall()
        return jsonify(data), 200
    if request.method=='POST':
        conn = get_db()
        cur = conn.cursor()
        res = cur.execute("INSERT INTO articles VALUES( " + "NULL"+ ", 'Article1', 'Body text.', datetime('now'), 1);")
        conn.commit()
        res = cur.execute("select * from articles")
        data = res.fetchall()
        return jsonify(data), 201

@app.route("/post", methods = ['POST'])
def postArticle():
    if request.method=='POST':
        content = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        if("title" in content and "body" in content and "user_id" in content):
            cur.execute("INSERT INTO articles VALUES( " + "NULL" + "," + "'" + content['title'] + "'" + "," + "'" + content['body'] + "'" + ", datetime('now'), " + str(content['user_id']) + " );")
        conn.commit()
        #print (content)
        return jsonify({}), 201



@app.route("/post/<id>", methods = ['GET'])
def getArticle(id):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute("SELECT * FROM articles WHERE  id =" + id + ";")
        data = res.fetchall()
        return jsonify(data), 200

@app.route("/posts/recent/<int:number>", methods = ['GET'])
def getRecentArticle(number):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute('''SELECT * FROM articles
                             ORDER BY date DESC
                             LIMIT ''' + str(number) + ";")
        data = res.fetchall()
        return jsonify(data), 200

@app.route("/post/<id>", methods = ['DELETE'])
def deleteArticle(id):
    if request.method=='DELETE':
        conn = get_db()
        cur = get_db()
        cur.execute("DELETE FROM articles WHERE id = " + id)
        conn.commit()
        return jsonify({}), 200
######################################################################################USERS*###############################################################################
@app.route("/users/create", methods = ['POST'])
def createUser():
    if request.method == 'POST':
        content = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES( " + "NULL" + "," + "'" + content['email'] + "', " + "'" + content['password'] + "'"  + " );")
        conn.commit()
        show = cur.execute("SELECT * FROM users")
        data = show.fetchall()
        print(data)
        conn.close()
        return jsonify(data), 201

@app.route("/users/delete", methods =['GET','POST','DELETE'])
def deleteUser():
	if request.method == 'DELETE':
    content = request == ['DELETE']
		conn = get_db()
		cur = conn.cursor()
		# cur.execute('SELECT * FROM users WHERE EXISTS(DELETE FROM users WHERE user_id = 1)')
		cur.execute('DELETE FROM users WHERE user_id' + content['user_id'])
		conn.commit()

		show = cur.execute("SELECT * FROM users")
		data = show.fetchall()
		print(data)
		conn.close()
		return jsonify(data),201

@app.route("/users/changepassword",methods=['POST'])
def changePassword():
    content = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    # cur.execute('SELECT * FROM users WHERE EXISTS(DELETE FROM users WHERE user_id = 1)')
    cur.execute('UPDATE users SET password="' + str(content['password']) + '" WHERE user_id=' + str(content['user_id']) + ';')
    #cur.execute('UPDATE users SET password="thispasshasbeenchangedAGAIN" WHERE user_id=3')
    conn.commit()
    return jsonify({}), 200

	# show = cur.execute("SELECT * FROM users")
	# data = show.fetchall()
	# print(data)
	# conn.close()
	# return jsonify(data),201


if __name__ == "__main__":
    app.run()
