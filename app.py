from flask import Flask, g, render_template, request
import sqlite3, json
from flask import jsonify
import os

DATABASE = "./database.db"


#INITIALIZATION#

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


#TESTING#
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




#USERS#

#CREATE A USER
@app.route("/users/create", methods = ['POST'])
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
def deleteUser(id):
    if request.method == 'DELETE':
        conn = get_db()
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE user_id=' + id)
        conn.commit()
        conn.close()
        return jsonify({}),200




#COMMENT FUNCTIONS#

#POST A COMMENT TO AN ARTICLE
@app.route("/articles/<int:article_number>/comment/add", methods = ['POST'])
def postComment(article_number):
    if request.method=='POST':
        content = request.get_json()
        if("comment_text" in content and "article_id" in content):           
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO comments VALUES( NULL," + "'" + content['comment_text'] +  "'" + ", datetime('now'), "  + content['article_id']  +  ")")
            conn.commit()
            cur.close()
            return jsonify({}), 201
        return jsonify({}), 409
        
#RETRIEVE THE N MOST RECENT COMMENTS TO AN ARTICLE       
@app.route("/articles/<int:article_number>/comments/<int:numComments>", methods = ['GET'])
def getRecentComments(article_number, numComments):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute("SELECT * FROM comments WHERE article_id=" + str(article_number)  +  " ORDER BY date DESC LIMIT " + str(numComments))
        data = res.fetchall()
        return jsonify(data), 200

#COUNT THE NUMBER OF COMMENTS FOR A GIVEN ARTICLE
@app.route("/articles/<int:article_number>/comments/count", methods = ['GET'])
def countArticleComments(article_number):
    if request.method=='GET':
        cur = get_db().cursor()
        res = cur.execute('SELECT COUNT(article_id) FROM comments GROUP BY article_id')
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


#APP RUN
if __name__ == "__main__":
    app.run()


