from flask import Flask, g, render_template, request, make_response, jsonify
import requests

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret-key'

# GET RSS SUMMARY
@app.route("/syndication/summary")
def getSummary():
	r = requests.get('http://localhost:5001/articles/summary/10')
	text = r.json()
	return jsonify(text), 200

# GET FULL FEED
@app.route("/syndication/full/<int:number>")
def getFullFeed(number):
	articlePacket = list()
	r = requests.get('http://localhost:5001/article/' + str(number))
	text = list(r.json())[0]
	article_id = text[0]
	text.pop(0)
	articlePacket.append(text)
	r= requests.get('http://localhost:5003/articles/' + str(article_id) + '/tags')
	text2 = list(r.json())
	articlePacket.append(text2)
	r= requests.get('http://localhost:5004/articles/' + str(article_id) + '/comments/count')
	text3 = list(r.json())
	articlePacket.append(text3)
	return jsonify(articlePacket), 200


if __name__ == "__main__":
    app.run()