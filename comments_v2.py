from flask import Flask, g, render_template, request
import sqlite3, json
from flask import jsonify
import os
import datetime
from cassandra.cluster import Cluster
from cassandra.query import named_tuple_factory

DATABASE = "./comments.db"

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'

cluster = Cluster(['172.17.0.2'])
session = cluster.connect()

session.execute("""USE blog;""")
session.execute(
    """CREATE TABLE IF NOT EXISTS comments(
        comment_id int,
        article_id int,
        comment_text text,
        comment_timestamp timestamp,
        comment_author text,
        PRIMARY KEY (comment_id))
    """
 )


#COMMENT FUNCTIONS#

#POST A COMMENT TO AN ARTICLE
@app.route("/comments/article/post/<int:article_number>", methods = ['POST'])
def postComment(article_number):
    if request.method=='POST':
        content = request.get_json()
        session.execute(
            """INSERT INTO blog.comments(comment_id,article_id,comment_text,comment_timestamp,comment_author) VALUES(%s,%s,%s,%s,%s)""", (content['comment_id'],article_number,content['comment_text'],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),content['comment_author'])
        )
        return jsonify({}), 201

#RETRIEVE THE N MOST RECENT COMMENTS TO AN ARTICLE
@app.route("/comments/article_number/<int:article_number>/recent/<int:numComments>", methods = ['GET'])
def getRecentComments(article_number, numComments):
    if request.method=='GET':
        rows = session.execute(
            """SELECT * FROM blog.comments WHERE comment_timestamp<%s AND article_id = %s LIMIT %s ALLOW FILTERING;""",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),article_number, numComments)
        )
        data = []
        for row in rows:
            data.append(row)
        return jsonify(data), 200

#COUNT THE NUMBER OF COMMENTS FOR A GIVEN ARTICLE
@app.route("/comments/article/count/<int:article_number>", methods = ['GET'])
def countArticleComments(article_number):
    if request.method=='GET':
        rows = session.execute(
            """SELECT * FROM blog.comments WHERE comment_timestamp<%s AND article_id = %s ALLOW FILTERING;""",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),article_number)
        )
        data = []
        for row in rows:
            data.append(row)
        number = len(data)
        array_data = []
        array_data.append(number)
        outterarray=[]
        outterarray.append(array_data)
        return jsonify(outterarray), 200

#DELETE AN INDIVIDUAL COMMENT
@app.route("/comments/delete/<int:comment_id>", methods = ['DELETE'])
def deleteComment(comment_id):
    if request.method=='DELETE':
        session.execute(
            """DELETE FROM blog.comments WHERE comment_id=%s""",([comment_id])
        )
        return jsonify({}), 200

if __name__ == "__main__":
    app.run()
