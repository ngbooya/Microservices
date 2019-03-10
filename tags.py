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
        
#TAG FUNCTIONS#

#ADD TAG TO AN ARTICLE
@app.route("/articles/<article_number>/tags/create", methods = ['POST'])
def tagArticle(article_number):
    if request.method=='POST':
        content = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        if("tag" in content):
            cur.execute("INSERT INTO tags VALUES( " + "NULL" + "," + "'" + str(article_number) + "'" + "," + "'" + content['tag'] + "'" + ')')
        conn.commit()
        return jsonify({}), 201

#RETRIEVE TAGS FOR AN ARTICLE
@app.route("/articles/<article_number>/tags", methods = ['GET'])
def getArticleTags(article_number):
    if request.method=='GET':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT tag FROM tags WHERE  article_id =" + article_number + ";")
        res = cur.fetchall()
        mergelist = []
        for list in res:
            mergelist += list            
        return jsonify(mergelist), 200

#DELETE TAG FROM AN ARTICLE
@app.route("/article/<artNum>/tags/<tag>/delete", methods= ['DELETE'])
def deleteTagFromArticle(artNum, tag):
    if request.method == 'DELETE':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM tags WHERE article_id = '" + artNum + "' AND tag = '" + tag + "'")
        conn.commit()
        return jsonify({}), 200 

#DELETE ONE OR MORE TAGS FROM AN ARTICLE
# JSON IS IN THIS FORMAT:
# {
#     "tag1": ""
#     "tag2": ""
# }
@app.route("/article/<artNum>/tags/delete", methods= ['DELETE'])
def deleteTagsFromArticle(artNum):
    if request.method == 'DELETE':
        content = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        for key in content:            
            value = content[key]        
            cur.execute("DELETE FROM tags WHERE article_id = '" + artNum + "' AND tag = '" + value + "'")
        conn.commit()
        return jsonify({}), 200 

#RETRIEVE A LIST OF ARTICLES WITH A GIVEN TAG
@app.route("/tag/<tag>/allarticles", methods = ['GET'])
def getArticleListForTags(tag):
    if request.method=='GET':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT article_id FROM tags WHERE  tag = '" + tag + "';")
        res = cur.fetchall()
        mergelist = []
        for list in res:
            mergelist += list            
        return jsonify(mergelist), 200

if __name__ == "__main__":
    app.run()

