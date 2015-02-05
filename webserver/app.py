from flask import Flask, url_for, request, session, redirect, render_template, flash
import db
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--hostname', dest='hostname', required=True, help='Host name, IP Address')
parser.add_argument('-d', '--database', dest='database', required=True, help='network location of database server')
parser.add_argument('-u', '--username', dest='username', required=True, help='connect using the indicated username')
parser.add_argument('-p', '--password', dest='password', required=True, help='use the indicated password to authenticate the connection')
parser.add_argument('-s', '--secret', dest='secret', required=True, help='file to use as server secret key')
parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='run server in debug mode')

args = parser.parse_args()

app = Flask(__name__)
database = db.DbInstance(args.database, args.username, args.password, 5)

@app.route('/')
def index():
	return render_template('index.html', number=5)

@app.route('/user/<uname>/')
def test(uname):
	return str(database.getUser(uname))

@app.route('/friends/<uname>/')
def friends(uname):
	return str(database.getUser(uname)["friends"])

if __name__ == "__main__":
	with open (args.secret, "r") as secretFile:
    		app.secret_key = secretFile.read()
	app.debug = args.debug
	app.run(host=args.hostname)
