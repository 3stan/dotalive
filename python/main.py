from flask import Flask, render_template
import urllib2
import time
import json
app = Flask(__name__)

apiKey = '567159D5C2554BBE3419B4F5244C00CF'
lastFetched = 0
cachedHtml = json.loads('{}')

@app.route('/')
def main_page():
	global lastFetched, cachedHtml
	now = long(round(time.time()))
	if now - lastFetched > 1L:
		lastFetched = now
		response = urllib2.urlopen('https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v0001/?key=' + apiKey)
		cachedHtml = json.loads(response.read())
	return render_template('main.html', data=cachedHtml)

if __name__ == '__main__':
    app.run(debug=True)
