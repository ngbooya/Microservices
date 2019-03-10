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


#ARTICLES#

#POST AN ARTICLE
@app.route("/article", methods = ['POST'])
def postArticle():
    if request.method=='POST':
        content = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        if("title" in content and "body" in content and "user_id" in content):
            cur.execute("INSERT INTO articles VALUES( " + "NULL" + "," + "'" + content['title'] + "'" + "," + "'" + content['body'] + "'" + ", datetime('now'), " + str(content['user_id']) + " );")
        conn.commit()
        return jsonify({}), 201
                
#GET AN ARTICLE
@app.route("/article/<id>", methods = ['GET'])
def getArticle(id):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute("SELECT * FROM articles WHERE  article_id =" + id + ";")
        data = res.fetchall()
        return jsonify(data), 200

#GET THE N MOST RECENT ARTICLES
@app.route("/articles/recent/<int:number>", methods = ['GET'])
def getRecentArticle(number):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute('''SELECT * FROM articles 
                             ORDER BY date DESC
                             LIMIT ''' + str(number) + ";")
        data = res.fetchall()
        return jsonify(data), 200

#DELETE AN ARTICLE  
@app.route("/article/<id>", methods = ['DELETE'])
def deleteArticle(id):
    if request.method=='DELETE':
        conn = get_db()
        cur = get_db()
        cur.execute("DELETE FROM articles WHERE article_id = " + id)
        conn.commit()
        return jsonify({}), 200
        
#UPDATE AN ARTICLE
@app.route("/article/<id>/edit",methods=['POST'])
def editArticle(id):
    content = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    if("title" in content and "body" in content):
        cur.execute('UPDATE articles SET title="' + content['title'] + '" WHERE article_id=' + id + ';')
        cur.execute('UPDATE articles SET body="' + content['body'] + '" WHERE article_id=' + id + ';')
        cur.execute("UPDATE articles SET date=datetime('now') WHERE article_id= " + id )
        conn.commit()
    conn.close()
    return jsonify({}), 200

#RETRIEVE METADATA FOR N MOST RECENT ARTICLES
@app.route("/articles/recent/metadata/<int:number>", methods = ['GET'])
def getRecentArticleMetaData(number):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute('''SELECT title, body, user_id, date, article_id FROM articles 
                             ORDER BY date DESC
                             LIMIT ''' + str(number) + ";")
        data = res.fetchall()
        return jsonify(data), 200

if __name__ == "__main__":
    app.run()
