# <--=====================================libraries import ==========================================================-->	
from flask import Flask, redirect, url_for, request, render_template, session, flash
import os
import requests
import uuid
import random
# <--========================================================================================================================-->


# <--======================================support files=============================================================-->
from codechefapi import Codechefapi   # class to manage and send api requests
from connections import adduser,getuser,addusersus,removeusersus # sql connections
from config import secretkey,clientid,clientsecret,redirect_uri
# <--========================================================================================================================-->


# <--=====================================configuration LINE17-23 ==========================================================-->	
# 
# 
#    <------------imported files ------>
# 

# <--========================================================================================================================-->



# <--===================================App Declaration line 27-31===========================================================-->
app = Flask(__name__)
app.secret_key = secretkey

# <--========================================================================================================================-->

api_sessions = {}  # created to store classes - codechefapi of sessions created

# <--========================================================================================================================-->


# <--=============================app routes line 38-end ================================================================-->
@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route('/')
def home():
	if 'loggedin' in session:
		if not session['loggedin']:
			return render_template("home.html")
		else:
			try:
				return render_template("home.html",username = api_sessions[session['id']].getusername())
			except:
				return redirect(url_for('sessionexit'))

	else:
		session['loggedin'] = False
		return redirect(url_for('home'))

@app.route('/menus')
def menus():
	if 'loggedin' in session:
		if session['loggedin'] == True:
			try:
				return render_template("menus.html",username = api_sessions[session['id']].getusername())
			except:
				return redirect(url_for('sessionexit'))
		else:
			return redirect(url_for('home'))
	else:
		session['loggedin'] = False
		return redirect(url_for('menus'))

@app.route('/problemfinder')
def problemfinder():
	if 'loggedin' in session:
		if session['loggedin'] == True:
			try:
				api_sessions[session['id']].getselfinfo()
				ownrating = str(api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['allContest'])
				return render_template('problemfinder.html',username = api_sessions[session['id']].getusername(),ownrating = ownrating,nproblems = '20')
			except:
				return redirect(url_for('sessionexit'))
		else:
			return redirect(url_for('home'))
	else:
		session['loggedin'] = False
		return redirect(url_for('menus'))

@app.route('/progressapp')
def progressapp():
	if 'loggedin' in session:
		if session['loggedin'] == True:
			try:
				username = api_sessions[session['id']].getusername()
				adduser('data',username)
				users = getuser('data',username)['sus']
				availablecolorcodes = ['#CD5C5C',"#228B22","#BA55D3","#F4A460","#696969","#FFFF00","#808000","#00FFFF","#0000FF","#000000"]
				colorcodes = []
				usernames = []
				ratings = []
				api_sessions[session['id']].getselfinfo()
				usernames.append(api_sessions[session['id']].getusername())
				ratings.append([api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['allContest'],api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['long'],api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['short'],api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['lTime']])
				colorcodes.append('#007bff')
				for user,index in zip(users,list(range(len(users)))):
					try:
						api_sessions[session['id']].getuserinfo(user)
						usernames.append(api_sessions[session['id']].LastJson['result']['data']['content']['username'])
						ratings.append([api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['allContest'],api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['long'],api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['short'],api_sessions[session['id']].LastJson['result']['data']['content']['ratings']['lTime']])
						colorcodes.append(availablecolorcodes[index])
					except:
						pass
				return render_template('dashboard.html',numberofusers = len(users), usernames_ratings_colorcodes = zip(usernames,ratings,colorcodes))
			except:
				return redirect(url_for('sessionexit'))
		else:
			return redirect(url_for('home'))
	else:
		session['loggedin'] = False
		return redirect(url_for('menus'))

@app.route('/adduser',methods = ['GET'])
def adduserflask():
	if 'loggedin' in session:
		if session['loggedin'] == True:
			try:
				sus = request.args.get('usersus')
				api_sessions[session['id']].getuserinfo(sus)
				try:
					usercode = api_sessions[session['id']].LastJson["result"]["data"]["code"]
				except:
					usercode = 9003
				if usercode == 9001 and len(getuser('data',api_sessions[session['id']].getusername())['sus']) <= 9 and api_sessions[session['id']].getusername() != sus :
					addusersus('data',api_sessions[session['id']].getusername(),sus)
				else:
					pass
				return redirect(url_for('dashboardconfig'))
			except:
				return redirect(url_for('sessionexit'))
		else:
			return redirect(url_for('home'))
	else:
		session['loggedin'] = False
		return redirect(url_for('menus'))

@app.route('/removeuser',methods = ['GET'])
def removeuserflask():
	if 'loggedin' in session:
		if session['loggedin'] == True:
			try:
				sus = request.args.get('usersus')
				removeusersus('data',api_sessions[session['id']].getusername(),sus)
				return redirect(url_for('dashboardconfig'))
			except:
				return redirect(url_for('sessionexit'))
		else:
			return redirect(url_for('home'))
	else:
		session['loggedin'] = False
		return redirect(url_for('menus'))

@app.route('/dashboardconfig')
def dashboardconfig():
	if 'loggedin' in session:
		if session['loggedin'] == True:
			try:
				sus = getuser('data',api_sessions[session['id']].getusername())['sus']
				return render_template('dashboardconfig.html',sus = sus)
			except:
				return redirect(url_for('sessionexit'))
		else:
			return redirect(url_for('home'))
	else:
		session['loggedin'] = False
		return redirect(url_for('menus'))

@app.route('/problemfinderroute',methods=['GET'])
def problemfinderroute():
	if 'loggedin' in session:
		if session['loggedin'] == True:
			try:
				userrating = int(request.args.get('rating'))
				part = api_sessions[session['id']].generateproblemlevel(userrating)
				api_sessions[session['id']].get_problems(part[0])
				problems = api_sessions[session['id']].LastJson['result']['data']['content']
				startingIndex = int((part[1]/100)*len(problems))
				lensums = int(request.args.get('nproblems'))
				finalproblems = random.sample(problems[startingIndex:startingIndex + int((2.5)*lensums)],lensums)
				finalproblems2 = []
				for problem in finalproblems:
					smallist = list(problem.values())
					finalproblems2.append(smallist)
				return render_template('displayproblems.html',username = api_sessions[session['id']].getusername(), finalproblems2 = finalproblems2)
			except:
				return redirect(url_for('sessionexit'))
		else:
			return redirect(url_for('home'))
	else:
		session['loggedin'] = False
		return redirect(url_for('menus'))

@app.route("/sessionexit")
def sessionexit():
	session.clear()
	return redirect(url_for('home'))

@app.route('/login')
def login():
	if session['loggedin'] == False:
		if 'id' in session:
			pass
		else:
			session['id'] = os.urandom(24)
		api_sessions[session['id']] = Codechefapi(clientid,clientsecret,redirect_uri)
		url = api_sessions[session['id']].getloginurl()
		return redirect(url)
	else:
		return redirect(url_for('home'))

@app.route('/gettoken',methods = ["GET"])
def gettoken():
	if request.method == "GET":
		code = request.args.get('code')
		state = request.args.get('state')
		try:
			api_sessions[session['id']].setcode(code,state)
			if api_sessions[session['id']].login() :
				session['loggedin'] = True
				return redirect(url_for('home'))
			else:
				session['loggedin'] = False
				return 'Some temporary error in app please try again after some time or try clearing cache.'
		except Exception as e:
			session['loggedin'] = False
			return 'exception occurred while logging in. Please try again after some time or try clearing cache. ' + 'Excpetion - ' + str(e)

@app.route("/logout")
def logout():
	session['loggedin'] = False
	return redirect(url_for('home'))



#app.run(debug = True)
