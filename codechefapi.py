import requests
import hashlib
import json
import uuid
import time
import string
import random
from connections import insertintotokens,updateintotokens

class Codechefapi:
	API_URL = "https://api.codechef.com"
	rating_sections = {(0,1000):('easy',0),(1000,1200):('easy',10),(1200,1300):('easy',20),(1300,1400):('easy',35),(1400,1500):('easy',60),(1500,1600):('easy',80),(1600,1700):('medium',0),(1700,1800):('medium',7),(1800,1900):('medium',20),(1900,2000):('medium',30),(2000,2100):('medium',35),(2100,2200):('medium',42),(2300,2400):('medium',50),(2400,2500):('medium',75),(2600,2700):('hard',0),(2800,2900):('hard',30),(2900,3000):('hard',60),(3000,3100):('hard',80),(3200,3500):('challenge',20),(3500,4000):('challenge',35),(4000-5000):('challenge',50)}

	def __init__(self,clientid,clientsecret,redirect_uri):
		m = hashlib.md5()
		m.update(clientid.encode('utf-8') + clientsecret.encode('utf-8'))
		self.device_id = self.generateDeviceId(m.hexdigest())
		self.setApp(clientid, clientsecret, redirect_uri)
		self.isLoggedIn = False
		self.LastResponse = None
		# self.currentsession = requests.Session()
		self.code = ''
		self.state = self.state_generator()
		self.token = ''
		self.refresh_token = ''
		self.username = ''
		self.currentsession = requests.Session()
		self.headers = {'content-type' : 'application/json'}
		self.last_status_code = 0

	def generateproblemlevel(self,rating):
		# rating_sections = {[0,1000]:['easy',0],[1000,1300]:['easy',20],[1300,1500]:['easy',50],[1500,1600]:['easy',80],[1600,1700]:['medium',0],[1700,1800]:['medium',7],[1800,1900]:['medium',20],[1900,2000]:['medium',30],[2000,2100]:['medium',35],[2100,2200]:['medium',42],[2300,2400]:['medium',50],[2400,2500]:['medium',75],[2600,2700]:['hard',0],[2800,2900]:['hard',30],[2900,3000]:['hard',60],[3000,3100]:['hard',80],[3200,3500]:['challenge',20],[3500,4000]:['challenge',35],[4000-5000]:['challenge',50]}
		part = []
		for section in self.rating_sections:
			if section[0] <= rating <= section[1]:
				part = self.rating_sections[section]
				break
		return part

	def getloginurl(self):
		return "https://api.codechef.com/oauth/authorize?response_type=code&client_id=%s&state=%s&redirect_uri=%s"%(self.clientid,self.state,self.redirect_uri)

	def state_generator(self,size=12, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def setApp(self,clientid, clientsecret,redirect_uri):
		self.clientid = clientid
		self.clientsecret = clientsecret
		self.redirect_uri = redirect_uri
		self.uuid = self.generateUUID(True)

	def setcode(self,code,state):
		if self.state == state:
			self.code = code
			return True
		else:
			False

	def generateUUID(self, type):
		generated_uuid = str(uuid.uuid4())
		if (type):
			return generated_uuid
		else:
			return generated_uuid.replace('-', '')

	def generateDeviceId(self, seed):
		volatile_seed = "12345"
		m = hashlib.md5()
		m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
		return 'android-' + m.hexdigest()[:16]

	def getusername(self):
		return self.username

	def login(self):
		headers = {'content-type' : 'application/json'}
		logindata = {"grant_type" : "authorization_code",
					  "code" : self.code,
					  "client_id" : self.clientid,
					  "client_secret" : self.clientsecret,
					  "redirect_uri" : self.redirect_uri}
		
		if (self.SendRequest("/oauth/token",post = logindata,headers=headers)):
			self.isLoggedIn = True
			self.token = self.LastJson["result"]["data"]["access_token"]
			self.refresh_token = self.LastJson["result"]["data"]["refresh_token"]
			self.headers['Authorization'] = 'Bearer %s'%(self.token)
			self.getselfinfo()
			self.username = self.LastJson['result']['data']['content']['username']
			insertintotokens('data',self.username,self.token,self.refresh_token)
			# print(self.LastJson)
			# print(self.token)
			return True

	def generateNewToken(self):
		data = {"grant_type" : "refresh_token",
				"refresh_token" : self.refresh_token,
				"client_id" : self.clientid,
				"client_secret" : self.clientsecret}
		if(self.SendRequest("/oauth/token",post = data)):
			self.token = self.LastJson["result"]["data"]["access_token"]
			self.refresh_token = self.LastJson["result"]["data"]["refresh_token"]
			updateintotokens('data',self.username,self.token,self.refresh_token)
			return True
			# print(self.LastJson)


	def getuserinfo(self,user):
		headers = {"Accept":"application/json","Authorization":"Bearer %s"%(self.token)}
		# headers = {}
		# resp = requests.get(self.API_URL + "/users/%s"%(user),headers=headers)
		# print(resp.text)
		# resp = requests.get(self.API_URL + "/users/%s"%("l_returns"),headers=headers)
		# print(resp.text)		
		if(self.SendRequest("/users/%s"%(user),headers=headers)):
			return True

	def getselfinfo(self):
		self.getuserinfo('me')

	def get_problems(self,difficultyLevel,sortBy = 'successfulSubmissions',sortOrder = 'desc'):
		headers = {"Accept":"application/json","Authorization":"Bearer %s"%(self.token)}	
		if(self.SendRequest("/problems/%s?sortBy=%s&sortOrder=%s"%(difficultyLevel,sortBy,sortOrder),headers=headers)):
			return True

	def getfuturecontests(self):
		headers = {"Accept":"application/json","Authorization":"Bearer %s"%(self.token)}
		if(self.SendRequest('/contests?fields=code%2Cname%2CstartDate%2CendDate&status=future',headers = headers)):
			return True

	def SendRequest(self,endpoint,post=None,headers = None):
		while True:
			try:
				if (post is not None):
					response = self.currentsession.post(self.API_URL + endpoint,json=post,headers=headers)
				else:
					# self.currentsession.headers.update(headers)
					# print(self.currentsession.headers)
					response = self.currentsession.get(self.API_URL + endpoint,headers=headers)
				break
			except Exception as e:
				print('Pausing on SendRequest (wait 60 sec and resend): ' + str(e))
				time.sleep(60)

		if response.status_code == 200:
			self.last_status_code = 200
			self.LastResponse = response
			self.LastJson = json.loads(response.text)
			# print(self.LastJson)
			return True
		elif response.status_code==401 and len(self.refresh_token) > 0:
			self.generateNewToken()
			self.SendRequest(endpoint,post,headers)
		else:
			print("Request return " + str(response.status_code) + " error!")
            # for debugging
			try:
				self.LastResponse = response
				self.LastJson = json.loads(response.text)
				# print(self.LastJson)
			except:
				pass
			return False