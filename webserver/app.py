from flask import Flask, url_for, request, session, redirect, render_template, flash
from googleInterface import ApiInterface
import db
from db import FriendNotFoundException
from googleInterface import AuthException
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
	except AuthException:
		return "401.  Bad auth.", 401

@app.route('/friends/add/<token>/<friendEmail>/')
def friendRequest(token, friendEmail):
	try:
		id = ApiInterface(token).getId()
		database.requestFriend(id, friendEmail)
		return "Success", 200
	except FriendNotFoundException:
		return "404.  Email not found.", 404
	except AuthException:
		return "401.  Bad auth.", 401

@app.route('/friends/accept/<token>/<friendId>/')
def acceptRequest(token, friendId):
	try:
		id = ApiInterface(token).getId()
		database.acceptFriend(id, friendId)
		return "Success", 200
	except FriendNotFoundException:
		return "404.  Email not found.", 404
	except AuthException:
		return "401.  Bad auth.", 401

@app.route('/friends/reject/<token>/<friendId>/')
def rejectRequest(token, friendId):
	try:
		id = ApiInterface(token).getId()
		database.rejectFriend(id, friendId)
		return "Success", 200
	except FriendNotFoundException:
		return "404.  Email not found.", 404
	except AuthException:
		return "401.  Bad auth.", 401

@app.route('/friends/delete/<token>/<friendId>/')
def deleteFriend(token, friendId):
	try:
		id = ApiInterface(token).getId()
		database.deleteFriend(id, friendId)
		return "Success", 200
	except FriendNotFoundException:
		return "404.  Email not found.", 404
	except AuthException:
		return "401.  Bad auth.", 401

@app.route('/friends/status/<token>/')
def friendStatus(token):
	try:
		id = ApiInterface(token).getId()
		friends = database.getFriends(id)
		return json.dumps(friends)
	except AuthException:
		return "401.  Bad auth.", 401

@app.route('/friends/requests/<token>/')
def pendingRequests(token):
	try:
		id = ApiInterface(token).getId()
		requests = database.getRequests(id)
		return json.dumps(requests)
	except AuthException:
		return "401.  Bad auth.", 401

if args.debug:
	@app.route('/token/<token>/')
	def useToken(token):
		try:
			return str(ApiInterface(token).getJSON())
		except AuthException as e:
			return str(e.json)
			
	@app.route('/friends/forceadd/<myEmail>/<friendEmail>/')
	def forceAddFriend(myEmail, friendEmail):
		try:
			database.forceAcceptFriend(myEmail, friendEmail)
			return "Done.  Now turn this off." 
		except FriendNotFoundException:
			return "404.  Email not found.", 404
		except AuthException:
			return "401.  Bad auth.", 401

if __name__ == "__main__":
	with open (args.secret, "r") as secretFile:
    		app.secret_key = secretFile.read()
	app.debug = args.debug
	app.run(host=args.hostname)
