from flask import Flask, g, render_template, request, Response
import sqlite3, json
from cassandra.cluster import Cluster
from flask import jsonify
from functools import wraps
import os

DATABASE = "./users.db"


#INITIALIZATION#

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'

cluster = Cluster(['172.17.0.2'])
session = cluster.connect()

#Auth code from: http://flask.pocoo.org/snippets/8/
# AUTHORIZATION
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    # conn = get_db()
    # cur = conn.cursor()
    # cur.execute("SELECT COUNT (1) FROM users WHERE email='" + str(username) + "' AND password= '" + str(password) + "'")
    print(repr(username))
    row = session.execute(
        """SELECT user_email, user_password FROM user WHERE user_email=%s""",
        ([username])

    )
    # Check = cur.fetchall()
    # print(Check.user_email)
    # print(Check.user_password)
    # conn.commit()
    # conn.close()
    user = row[0]
    if str(user.user_email) == str(username) and str(user.user_password) == str(password):
        return True
    else:
        return False
    # String_Check = str(Check)
    # print(String_Check)
    # if(String_Check.find("1") != -1):
    #     return True
    # else:
    #     return False
#
def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})
#
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
#
# if not os.path.exists(DATABASE):
#     conn = sqlite3.connect(DATABASE)
#     cur = conn.cursor()
#     conn.execute("PRAGMA foreign_keys = ON;")
#     conn.commit()
#     cur.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, email TEXT, password TEXT);")
#     conn.commit()
#     conn.commit()
#     conn.close()
session.execute("""USE blog;""")
session.execute(
    """CREATE TABLE IF NOT EXISTS user(
        user_id int,
        user_email text,
        user_password text,
        PRIMARY KEY (user_email, user_password)
        );"""
)
#
#
# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE)
#     return db
#
#
# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


#USERS#

#CREATE A USER
@app.route("/users/create", methods = ['POST'])
def createUser():
    if request.method == 'POST':
        content = request.get_json()
    #     conn = get_db()
    #     cur = conn.cursor()
    #     cur.execute("INSERT INTO users VALUES( " + "NULL" + "," + "'" + content['email'] + "', " + "'" + content['password'] + "'"  + " );")
        session.execute(
            """INSERT INTO blog.user(user_id,user_email,user_password) VALUES(%s,%s,%s)""", (content['id'],content["email"],content['password'])
        )
    #     conn.commit()
    #     #show = cur.execute("SELECT * FROM users")
    #     #data = show.fetchall()
    #     conn.close()
    #     #return jsonify(data), 201
        return jsonify({}), 201

#CHANGE THE PASSWORD OF A USER
@app.route("/users/changepassword",methods=['POST'])
def changePassword():
    # if request.method == 'POST':
    content = request.get_json()
#     conn = get_db()
#     cur = conn.cursor()
#     if("user_id" in content and "password" in content):
#         cur.execute('UPDATE users SET password="' + content['password'] + '" WHERE user_id=' + content['user_id'] + ';')
#         conn.commit()
    session.execute(
        """UPDATE blog.user SET user_password=%s WHERE user_email=%s""",
        (content['password'],content['email'],)
    )
#     conn.close()
    return jsonify({}), 200
#
# #DELETE A USER
@app.route("/users/delete/<email>", methods =['DELETE'])
def deleteUser(email):
    if request.method == 'DELETE':
#         conn = get_db()
#         cur = conn.cursor()
#         cur.execute('DELETE FROM users WHERE user_id=' + id)
        session.execute(
            """DELETE FROM user WHERE user_email=%s""",
            ([email])
        )
#         conn.commit()
#         conn.close()
        return jsonify({}),200
#
# #AUTHENTICATION ROUTE
@app.route("/users/auth")
@requires_auth
def authUser():
    return jsonify({}),200


#APP RUN
if __name__ == "__main__":
    app.run()
