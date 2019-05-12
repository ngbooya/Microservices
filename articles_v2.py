from flask import Flask, g, render_template, request, Response
import sqlite3, json
from cassandra.cluster import Cluster
from cassandra.query import named_tuple_factory
from flask import jsonify
import os
import datetime
import werkzeug

DATABASE = "./articles.db"


# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'

cluster = Cluster(['172.17.0.2'])
session = cluster.connect()



session.execute("""USE blog;""")
session.execute(
    """CREATE TABLE IF NOT EXISTS article(
        article_id int,
        article_title text,
        article_body text,
        article_timestamp timestamp,
        article_author text,
        PRIMARY KEY(article_timestamp,article_id))
    """
 )



#ARTICLES#

#POST AN ARTICLE
@app.route("/articles/post", methods = ['POST'])
def postArticle():
    if request.method=='POST':
        content = request.get_json()
        session.execute(
            """INSERT INTO blog.article(article_id,article_title,article_body,article_timestamp,article_author) VALUES(%s,%s,%s,%s,%s)""", (content['id'],content['title'],content['body'],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),content['author'])
        )
        return jsonify({}), 201

#GET AN ARTICLE
@app.route("/articles/article/<id>", methods = ['GET'])
def getArticle(id):
    if request.method=='GET':
        if 'If-Modified-Since' in request.headers:
            requestHeaderDate = request.headers.get('If-Modified-Since')
            dateRequest = werkzeug.http.parse_date(requestHeaderDate)
            row = session.execute(
                """SELECT * FROM blog.article WHERE article_id=%s ALLOW FILTERING""", ([int(id)])
            )
            data = row[0]
            comparisonDate = datetime.datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S')
            if (comparisonDate > dateRequest):
                resp = Response(jsonify(data), status=200, mimetype='application/json')
                resp.headers['Last-Modified'] = str(werkzeug.http.http_date(datetime.datetime.now()))
                return (jsonify(data), resp.status_code, resp.headers.items())
            else:
                return (jsonify({}), 304)
        else:
            row = session.execute(
                """SELECT * FROM blog.article WHERE article_id=%s ALLOW FILTERING""", ([int(id)])
            )
            data = row[0]
            return jsonify(data), 200

#GET THE N MOST RECENT ARTICLES
@app.route("/articles/recent/<int:number>", methods = ['GET'])
def getRecentArticle(number):
    if request.method=='GET':
        if 'If-Modified-Since' in request.headers:
            requestHeaderDate = request.headers.get('If-Modified-Since')
            dateRequest = werkzeug.http.parse_date(requestHeaderDate)
            rows = session.execute(
                """SELECT * FROM blog.article WHERE article_timestamp<%s LIMIT %s ALLOW FILTERING;""",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),number)
            )
            data = []
            returnNew = False
            for row in rows:
                data.append(row)
                if datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S') > dateRequest:
                    returnNew = True
            if(returnNew):
                resp = Response(jsonify(data), status=200, mimetype='application/json')
                resp.headers['Last-Modified'] = str(werkzeug.http.http_date(datetime.datetime.now()))
                return (jsonify(data), resp.status_code, resp.headers.items())
            else:
                return (jsonify({}), 304)
        else:
            rows = session.execute(
                """SELECT * FROM blog.article WHERE article_timestamp<%s LIMIT %s ALLOW FILTERING;""",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),number)
                )
            data = []
            for row in rows:
                data.append(row)
            resp = Response(jsonify(data), status=200, mimetype='application/json')
            resp.headers['Last-Modified'] = str(werkzeug.http.http_date(datetime.datetime.now()))
            return (jsonify(data), resp.status_code, resp.headers.items())

#DELETE AN ARTICLE
@app.route("/articles/delete/<id>", methods = ['DELETE'])
def deleteArticle(id):
    if request.method=='DELETE':
        session.row_factory = named_tuple_factory
        row = session.execute(
            """SELECT article_timestamp FROM blog.article WHERE article_id=%s ALLOW FILTERING;""", ([int(id)])
        )
        time = row[0]
        session.execute(
            """DELETE FROM blog.article WHERE article_timestamp=%s""",([time.article_timestamp])
        )
        return jsonify({}), 200

#UPDATE AN ARTICLE
@app.route("/articles/edit/<id>",methods=['POST'])
def editArticle(id):
    if request.method=='POST':
        content = request.get_json()
        session.row_factory = named_tuple_factory
        row = session.execute(
            """SELECT article_timestamp FROM blog.article WHERE article_id=%s ALLOW FILTERING;""", ([int(id)])
        )
        time = row[0]
        print(time.article_timestamp)

        session.execute(
            """UPDATE blog.article SET article_author=%s WHERE article_timestamp=%s AND article_id=%s""",(content['author'],time.article_timestamp,int(id))
        )
        return jsonify({}), 200

#RETRIEVE METADATA FOR N MOST RECENT ARTICLES
@app.route("/articles/recent/metadata/<int:number>", methods = ['GET'])
def getRecentArticleMetaData(number):
    if request.method=='GET':
        if 'If-Modified-Since' in request.headers:
            requestHeaderDate = request.headers.get('If-Modified-Since')
            dateRequest = werkzeug.http.parse_date(requestHeaderDate)
            rows = session.execute(
                """SELECT * FROM blog.article WHERE article_timestamp<%s LIMIT %s ALLOW FILTERING;""",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),number)
            )
            data = []
            returnNew = False
            for row in rows:
                data.append(row)
                if datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S') > dateRequest:
                    returnNew = True
            if(returnNew):
                resp = Response(jsonify(data), status=200, mimetype='application/json')
                resp.headers['Last-Modified'] = str(werkzeug.http.http_date(datetime.datetime.now()))
                #Have to return it this way since Response doesn't understand jsonify.
                return (jsonify(data), resp.status_code, resp.headers.items())
            else:
                return (jsonify({}), 304)
        else:
            rows = session.execute(
                """SELECT * FROM blog.article WHERE article_timestamp<%s LIMIT %s ALLOW FILTERING;""",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),number)
            )
            data = []
            for row in rows:
                data.append(row)
            return jsonify(data), 200

#RSS SUMMARY - GETS TITLE, AUTHOR, DATE, AND URL
@app.route("/articles/summary/<int:number>")
def getRecentSummary(number):
    # cur = get_db().cursor()
    # res = cur.execute('''SELECT title, author, date, article_id FROM articles ORDER BY date DESC LIMIT ''' + str(number) + ";")
    # data = res.fetchall()
    if 'If-Modified-Since' in request.headers:
        requestHeaderDate = request.headers.get('If-Modified-Since')
        dateRequest = werkzeug.http.parse_date(requestHeaderDate)
        rows = session.execute(
            """SELECT * FROM blog.article WHERE article_timestamp<%s LIMIT %s ALLOW FILTERING;""",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),number)
        )
        data = []
        returnNew = False
        for row in rows:
            data.append(row)
            if datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S') > dateRequest:
                returnNew = True
        data2 = list()
        for i, item in enumerate(data):
            data2.append(list(item))
        for i in range(len(data2)):
            data2[i][3] = "article/" + str(data2[i][3])
        if(returnNew):
            resp = Response(jsonify(data2), status=200, mimetype='application/json')
            resp.headers['Last-Modified'] = str(werkzeug.http.http_date(datetime.datetime.now()))
            #Have to return it this way since Response doesn't understand jsonify.
            return (jsonify(data2), resp.status_code, resp.headers.items())
        else:
            return (jsonify({}), 304)
    else:
        rows = session.execute(
            """SELECT * FROM blog.article WHERE article_timestamp<%s LIMIT %s ALLOW FILTERING;""",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),number)
        )
        data = []
        for row in rows:
            data.append(row)
        data2 = list()
        for i, item in enumerate(data):
            data2.append(list(item))
        for i in range(len(data2)):
            data2[i][3] = "article/" + str(data2[i][3])
        return jsonify(data2), 200

if __name__ == "__main__":
    app.run()
