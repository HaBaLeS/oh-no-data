
from flask import Flask
from flask import render_template
from flask import g
from flask import json
import time
import datetime
import psycopg2


app = Flask(__name__)

@app.route("/oh-no-data")
def hello():
	return "This is the Oh-No-Data API. If you don't know what to do next... Request <a href='/oh-no-data/help'>/oh-no-data/help</a>"

@app.route("/oh-no-data/help")
def help():
	return render_template('help.html')

@app.route('/oh-no-data/<apikey>/addValue/<value>')
def addValue(apikey,value):
	pair= apikey.split('-',1)
	if(len(pair) != 2 or pair[0] == None or pair[1] == None):
		return "Please provide a Valid API key"
	pod_id = getOrCreatePot(pair[0], pair[1])
	if(pod_id == -1):
		return "Wrong Secret for API"
	db = get_db()
	cur = db.cursor()		
	cur.execute("insert into timebased_data ( time, value , pot_fk) VALUES (%s, %s, %s)", (datetime.datetime.now(),value,pod_id))
	cur.close()
	db.commit()
	return "ok"

@app.route('/oh-no-data/<podname>/getall')
def getAll(podname):
	data = getPod(podname)
	if(data == None):
		return "0,unknown api"
	db = get_db()
	cur = db.cursor()
	cur.execute("select * from timebased_data where pot_fk = %s", (data[0],))
	allData = cur.fetchall()
	cur.close()
	out = ""	
	for l in allData:
		out+=str(l[0])+","+str(l[1])+"\n"
	return out


def getOrCreatePot(key,secret):
	data = getPod(key)
	if(data == None):
		db = get_db()
		cur = db.cursor()		
		cur.execute(" insert into pod (name, key) VALUES (%s, %s) ", (key, secret))
		db.commit()
		return getOrCreatePot(key,secret)
	if(data[2] == secret):
		return data[0]
	return -1


def getPod(key):
	db = get_db()
	cur = db.cursor()		
	cur.execute("SELECT * FROM pod where name = %s ", (key,))
	data = cur.fetchone()
	cur.close()
	return data

	
def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = psycopg2.connect("dbname=falko user=falko")
	return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().execute(f.read())
        db.commit()

if __name__ == "__main__":
	app.debug=True
	app.config['APPLICATION_ROOT']='oh-no-data'
	app.run(host='0.0.0.0')



