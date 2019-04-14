from flask import Flask, g, render_template, request, make_response, jsonify
from requests.auth import HTTPBasicAuth
import requests

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'

# GET RSS SUMMARY
@app.route("/syndication/summary")
def getSummary():
	return jsonify(requests.get("http://localhost/articles/summary/10").json()), 200

# GET FULL FEED
@app.route("/syndication/full/<int:number>")
def getFullFeed(number):
	articlePacket = list()
	r = requests.get('http://localhost/articles/article/' + str(number))
	text = list(r.json())[0]
	article_id = text[0]
	text.pop(0)
	articlePacket.append(text)
	r= requests.get('http://localhost/tags/article/' + str(article_id))
	text2 = list(r.json())
	articlePacket.append(text2)
	r= requests.get('http://localhost/comments/article/count/' + str(article_id))
	text3 = list(r.json())[0]
	articlePacket.append(text3)
	return jsonify(articlePacket), 200

# GET COMMENT FEED
@app.route("/syndication/comments/<int:article_id>")
def getCommentFeed(article_id):
	r= requests.get('http://localhost/comments/article/count/' + str(article_id))
	text = r.json()
	commentCount = text[0][0]
	r = requests.get('http://localhost/comments/article_number/' + str(article_id) + '/recent/' + str(commentCount))
	comments = list(r.json())
	return jsonify(comments), 200


if __name__ == "__main__":
    app.run()