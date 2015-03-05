from flask import Flask, url_for, request, session, redirect, render_template, flash
from googleInterface import ApiInterface
import db
from db import FriendNotFoundException, AuthException
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--hostname', dest='hostname', required=True, help='Host name, IP Address')
parser.add_argument('-d', '--database', dest='database', required=True, help='network location of database server')
parser.add_argument('-u', '--username', dest='username', required=True, help='connect using the indicated username')
parser.add_argument('-p', '--password', dest='password', required=True, help='use the indicated password to authenticate the connection')
parser.add_argument('-s', '--secret', dest='secret', required=True, help='file to use as server secret key')
parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='run server in debug mode')

args = parser.parse_args()

app = Flask(__name__)
database = db.DbInstance(args.database, args.username, args.password)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/checkin/<token>/')
def checkin(token):
	try:
		api = ApiInterface(token)
		id = api.getId()
		email = api.getEmail()
		name = api.getName()
		database.checkin(id, email, name)
		return id
	except:
		return "401.  Bad auth.", 401

@app.route('/friends/add/<token>/<friendEmail>/')
def friendRequest(token, friendEmail):
	try:
		id = ApiInterface(token).getId()
		friendEmail = friendEmail.decode("hex")
		database.requestFriend(id, friendEmail)
	except FriendNotFoundException:
		return "404.  Email not found.", 404
	except AuthException:
		return "401.  Bad auth.", 401
	except TypeError:
		return "400.  Bad hex encoding.", 400	

@app.route('/friends/status/<token>/')
def friendStatus(token):
	try:
		id = ApiInterface(token).getId()
		friends = database.getFriends(id)
		return json.dumps(friends)
	except FriendNotFoundException:
		return "404.  Email not found.", 404
	except AuthException:
		return "401.  Bad auth.", 401

if args.debug:
	@app.route('/token/<token>/')
	def useToken(token):
		return str(ApiInterface(token).getJSON())

if __name__ == "__main__":
	with open (args.secret, "r") as secretFile:
    		app.secret_key = secretFile.read()
	app.debug = args.debug
	app.run(host=args.hostname)
