from flask import Flask, g, render_template, request
import sqlite3, json
from flask import jsonify
import os

DATABASE = "./articles.db"


# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'


if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.execute("CREATE TABLE articles (article_id INTEGER PRIMARY KEY, title TEXT, body TEXT, date DATETIME, author TEXT)")
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
        if("title" in content and "body" in content and "author" in content):
            cur.execute("INSERT INTO articles VALUES( " + "NULL" + "," + "'" + content['title'] + "'" + "," + "'" + content['body'] + "'" + ", datetime('now'), '" + content['author'] + "' );")
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
        res = cur.execute('''SELECT title, body, author, date, article_id FROM articles 
                             ORDER BY date DESC
                             LIMIT ''' + str(number) + ";")
        data = res.fetchall()
        return jsonify(data), 200

#RSS SUMMARY - GETS TITLE, AUTHOR, DATE, AND URL
@app.route("/articles/summary/<int:number>")
def getRecentSummary(number):
    cur = get_db().cursor()
    res = cur.execute('''SELECT title, author, date, article_id FROM articles ORDER BY date DESC LIMIT ''' + str(number) + ";")
    data = res.fetchall()
    data2 = list()
    for i, item in enumerate(data):
        data2.append(list(item))
    for i in range(len(data2)):
        data2[i][3] = "article/" + str(data2[i][3])
        print(i)
        print(data2[i][3])
    return jsonify(data2), 200

if __name__ == "__main__":
    app.run()
