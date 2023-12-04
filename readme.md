import mysql.connector,sys
import datetime
from mysql.connector import Error
from flask import Flask, request, jsonify, render_template
from random import randint

app = Flask(__name__)

@app.route('/')
def renderLoginPage():
    return render_template('login.html')


@app.route('/login', methods = ['POST'])
def verifyAndRenderRespective():
	username = request.form['username']
	password = request.form['password']

	try:
		if username == 'abcd' and password == '123456':

			res = runQuery('call delete_old()')
			return render_template('cashier.html')

		elif username == 'manager' and password == '1234':

			res = runQuery('call delete_old()')
			return render_template('manager.html')

		else:
			return render_template('loginfail.html')
	except Exception as e:
		print(e)
		return render_template('loginfail.html')


# Routes for cashier
@app.route('/getEventsShowingOnDate', methods = ['POST'])
def eventsOnDate():
	date = request.form['date']

	res = runQuery("SELECT DISTINCT event_id,event_name,type FROM events NATURAL JOIN shows WHERE Date = '"+date+"'")

	if res == []:
		return '<h4>No Events Showing</h4>'
	else:
		return render_template('events.html',events = res)


@app.route('/getTimings', methods = ['POST'])
def timingsForevent():
	date = request.form['date']
	eventID = request.form['eventID']
	eventType = request.form['type']

	res = runQuery("SELECT time FROM shows WHERE Date='"+date+"' and event_id = "+eventID+" and type ='"+eventType+"'")
	
	list = []

	for i in res:
		list.append( (i[0], int(i[0]/100), i[0]%100 if i[0]%100 != 0 else '00' ) )

	return render_template('timings.html',timings = list) 


@app.route('/getShowID', methods = ['POST'])
def getShowID():
	date = request.form['date']
	eventID = request.form['eventID']
	eventType = request.form['type']
	time = request.form['time']

	res = runQuery("SELECT show_id FROM shows WHERE Date='"+date+"' and event_id = "+eventID+" and type ='"+eventType+"' and time = "+time)
	return jsonify({"showID" : res[0][0]})


@app.route('/getAvailableSeats', methods = ['POST'])
def getSeating():
	showID = request.form['showID']

	res = runQuery("SELECT class,no_of_seats FROM shows NATURAL JOIN halls WHERE show_id = "+showID)

	totalGold = 0
	totalStandard = 0

	for i in res:
		if i[0] == 'gold':
			totalGold = i[1]
		if i[0] == 'standard':
			totalStandard = i[1]

	res = runQuery("SELECT seat_no FROM booked_tickets WHERE show_id = "+showID)

	goldSeats = []
	standardSeats = []