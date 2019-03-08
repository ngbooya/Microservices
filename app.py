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
    #conn.execute("DROP TABLE IF EXISTS articles;")
    #conn.commit()
    conn.execute("CREATE TABLE articles (id INTEGER PRIMARY KEY, title TEXT, body TEXT, date DATETIME);")
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
        res = cur.execute("INSERT INTO articles VALUES( " + "NULL"+ ", 'Article1', 'Body text.', date('now'));")
        conn.commit()
        res = cur.execute("select * from articles")
        data = res.fetchall()
        return jsonify(data), 201

@app.route("/post", methods = ['GET','POST'])
def postArticle():
    if request.method=='POST':
        content = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        res = cur.execute("INSERT INTO articles VALUES( " + "NULL" + "," + "'" + content['title'] + "'" + "," + "'" + content['body'] + "'" + ", date('now'));")
        conn.commit()
        print (content)
        return jsonify(content), 201

 
if __name__ == "__main__":
    app.run()
