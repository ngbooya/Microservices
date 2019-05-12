from flask import Flask, g, render_template, request
import sqlite3, json
from cassandra.cluster import Cluster
from flask import jsonify
import os

DATABASE = "./tags.db"


# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'

cluster = Cluster(['172.17.0.2'])
session = cluster.connect()
session.execute("""USE blog;""")
session.execute(
        """CREATE TABLE IF NOT EXISTS tag(
            tag_id int,
            article_id int,
            tag_name text,
            PRIMARY KEY(tag_id, article_id)
        );"""
)

#TAG FUNCTIONS#

#ADD TAG TO AN ARTICLE
@app.route("/tags/add/article/<article_number>", methods = ['POST'])
def tagArticle(article_number):
    if request.method=='POST':
        content = request.get_json()
        session.execute(
            """INSERT INTO blog.tag(tag_id,article_id,tag_name) VALUES(%s,%s,%s)""", (content['tag_id'],int(article_number),content['tag'])
        )
        return jsonify({}), 201

#RETRIEVE TAGS FOR AN ARTICLE
@app.route("/tags/article/<article_number>", methods = ['GET'])
def getArticleTags(article_number):
    if request.method=='GET':
        rows = session.execute(
            """SELECT tag_name FROM blog.tag WHERE article_id=%s ALLOW FILTERING""",([int(article_number)])
        )

        mergelist = []
        for row in rows:
            mergelist.append(row)

        return jsonify(mergelist), 200

#DELETE TAG FROM AN ARTICLE
# @app.route("/tags/delete/article/<artNum>/<tag>", methods= ['DELETE'])
# def deleteTagFromArticle(artNum, tag):
#     if request.method == 'DELETE':
#         session.execute(
#             """DELETE FROM blog.tag WHERE tag_id=%s AND article_id=%s ALLOW FILTERING""", (int(tag),int(artNum))
#         )
#
#         return jsonify({}), 200

#DELETE ONE OR MORE TAGS FROM AN ARTICLE
# JSON IS IN THIS FORMAT:
# {
#     "tag1": ""
#     "tag2": ""
# }
@app.route("/tags/delete/article/<artNum>/tags", methods= ['DELETE'])
def deleteTagsFromArticle(artNum):
    if request.method == 'DELETE':
        data = []
        content = request.get_json()
        for key in content:
            value = content[key]
            rows = session.execute(
                """SELECT tag_id FROM blog.tag WHERE tag_name=%s ALLOW FILTERING""",([value])
            )
            for row in rows:
                data.append(row)
    return jsonify(data), 200

#RETRIEVE A LIST OF ARTICLES WITH A GIVEN TAG
@app.route("/tags/allarticles/<tag>", methods = ['GET'])
def getArticleListForTags(tag):
    if request.method=='GET':
        rows = session.execute(
            """SELECT article_id FROM blog.tag WHERE tag_id=%s""",([int(tag)])
        )
        mergelist = []
        for row in rows:
            mergelist.append(row)
        return jsonify(mergelist), 200

if __name__ == "__main__":
    app.run()
