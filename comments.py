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

        
#COMMENT FUNCTIONS#

#POST A COMMENT TO AN ARTICLE
@app.route("/articles/<int:article_number>/comment/add", methods = ['POST'])
def postComment(article_number):
    if request.method=='POST':
        content = request.get_json()
        if("comment_text" in content and "article_id" in content):           
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO comments VALUES( NULL," + "'" + content['comment_text'] +  "'" + ", datetime('now'), " + "'" + content['article_id'] + "'" +  ")")
            conn.commit()
            cur.close()
            return jsonify({}), 200
        return jsonify({}), 409
        
#RETRIEVE THE N MOST RECENT COMMENTS TO AN ARTICLE       
@app.route("/articles/<int:article_number>/comments/<int:numComments>", methods = ['GET'])
def getRecentComments(article_number, numComments):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute('''SELECT * FROM comments WHERE article_id=''' + "'" + str(article_number) + "'" +  '''ORDER BY date DESC LIMIT ''' + str(numComments) + ";")
        data = res.fetchall()
        return jsonify(data), 200

#COUNT THE NUMBER OF COMMENTS FOR A GIVEN ARTICLE
@app.route("/articles/<int:article_number>/comments/count", methods = ['GET'])
def countArticleComments(article_number):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute('SELECT article_id, COUNT(article_id) FROM comments GROUP BY article_id')
        data = res.fetchall()
        return jsonify(data), 200

#DELETE AN INDIVIDUAL COMMENT
@app.route("/comments/<int:comment_id>", methods = ['DELETE'])
def deleteComment(comment_id):
    if request.method=='DELETE':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM comments WHERE comment_id = " + str(comment_id))
        conn.commit()
        return jsonify({}), 200        
if __name__ == "__main__":
    app.run()
