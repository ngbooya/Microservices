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

    print(repr(username))
    row = session.execute(
        """SELECT user_email, user_password FROM user WHERE user_email=%s""",
        ([username])

    )

    user = row[0]
    if str(user.user_email) == str(username) and str(user.user_password) == str(password):
        return True
    else:
        return False

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

session.execute("""USE blog;""")
session.execute(
    """CREATE TABLE IF NOT EXISTS user(
        user_id int,
        user_email text,
        user_password text,
        PRIMARY KEY (user_email)
        );"""
)


#USERS#

#CREATE A USER
@app.route("/users/create", methods = ['POST'])
def createUser():
    if request.method == 'POST':
        content = request.get_json()

        session.execute(
            """INSERT INTO blog.user(user_id,user_email,user_password) VALUES(%s,%s,%s)""", (content['id'],content["email"],content['password'])
        )

        return jsonify({}), 201

#CHANGE THE PASSWORD OF A USER
@app.route("/users/changepassword",methods=['POST'])
def changePassword():
    # if request.method == 'POST':
    content = request.get_json()
#
    session.execute(
        """UPDATE blog.user SET user_password=%s WHERE user_email=%s""",
        (content['password'],content['email'])
    )
#     conn.close()
    return jsonify({}), 200
#
# #DELETE A USER
@app.route("/users/delete/<email>", methods =['DELETE'])
def deleteUser(email):
    if request.method == 'DELETE':
#
        session.execute(
            """DELETE FROM user WHERE user_email=%s""",
            ([email])
        )

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
