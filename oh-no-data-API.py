
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def hello():
	return "This is the Oh-No-Data API. If you don't know what to do next... Request <a href='help'>/help</a>"

@app.route("/help")
def help():
	return render_template('help.html')

if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')
