# import sqlite3
import json

import MySQLdb
from config import HOST, PORT, USER, PASSWORD, DB

def getconnection(name):
	# conn = sqlite3.connect("database/%s.sqlite"%(name))
	conn = MySQLdb.Connection(host=HOST, port=PORT,user=USER, passwd=PASSWORD, db=DB)
	cur = conn.cursor()
	return conn, cur

def updateintotokens(name,username,token,refresh_token):
	conn, cur = getconnection(name)
	cur.execute("UPDATE tokens SET token = %s WHERE username = %s",[token,username])
	conn.commit()
	cur.execute("UPDATE tokens SET refresh_token = %s WHERE username = %s",[refresh_token,username])
	conn.commit()
	conn.close()

def insertintotokens(name,username,token,refresh_token):
	conn, cur = getconnection(name)
	cur.execute("SELECT username FROM tokens")
	data = cur.fetchall()
	conn.commit()
	if (username,) in data:
		conn.commit()
		conn.close()
		updateintotokens(name,username,token,refresh_token)
	else:
		cur.execute("INSERT INTO tokens (username,token,refresh_token) VALUES (%s,%s,%s)",[username,token,refresh_token])
		conn.commit()
		conn.close()

def adduser(name,username):
	conn, cur = getconnection(name)
	cur.execute("SELECT username FROM progressapp")
	data = cur.fetchall()
	conn.commit()
	if (username,) in data:
		conn.commit()
		conn.close()
	else:
		conn, cur = getconnection(name)	
		cur.execute("INSERT INTO progressapp (username,users) VALUES (%s,%s)",[username,json.dumps({'sus':[]})])
		conn.commit()
		conn.close()

def getuser(name,username):
	conn, cur = getconnection(name)
	cur.execute("SELECT * FROM progressapp")
	data = cur.fetchall()
	conn.commit()
	conn.close()
	for i in data:
		if username in i:
			return json.loads(i[1])


def addusersus(name,username,sus):
	conn, cur = getconnection(name)
	cur.execute("SELECT * FROM progressapp")
	data = cur.fetchall()
	conn.commit()
	conn.close()
	for i in data:
		if username in i:
			totalsus =  json.loads(i[1])
			break
	if sus in totalsus['sus']:
		pass
	else:
		totalsus['sus'].append(sus)
		conn, cur = getconnection(name)
		cur.execute("UPDATE progressapp SET users = %s WHERE username = %s",[json.dumps(totalsus),username])
		conn.commit()
		conn.close()

def removeusersus(name,username,sus):
	conn, cur = getconnection(name)
	cur.execute("SELECT * FROM progressapp")
	data = cur.fetchall()
	conn.commit()
	conn.close()
	for i in data:
		if username in i:
			totalsus =  json.loads(i[1])
			break
	if sus in totalsus['sus']:
		totalsus['sus'].remove(sus)
		conn, cur = getconnection(name)
		cur.execute("UPDATE progressapp SET users = %s WHERE username = %s",[json.dumps(totalsus),username])
		conn.commit()
		conn.close()
	else:
		pass