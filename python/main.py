from flask import Flask, render_template
import urllib2
import time
import json
app = Flask(__name__)

apiKey = '567159D5C2554BBE3419B4F5244C00CF'
lastFetched = 0
cachedHtml = json.loads('{}')

testing = json.loads("""
					{
	"result": {
		"games": [
			{
				"players": [
					{
						"account_id": 101851949,
						"name": "WVW-Lerry",
						"hero_id": 0,
						"team": 2
					},
					{
						"account_id": 139266129,
						"name": "NE.DJ",
						"hero_id": 98,
						"team": 0
					},
					{
						"account_id": 88990397,
						"name": "Zyori",
						"hero_id": 0,
						"team": 2
					},
					{
						"account_id": 47123324,
						"name": "Basskip",
						"hero_id": 0,
						"team": 2
					},
					{
						"account_id": 142750189,
						"name": "NE.Garder",
						"hero_id": 86,
						"team": 0
					},
					{
						"account_id": 85293283,
						"name": "520",
						"hero_id": 0,
						"team": 2
					},
					{
						"account_id": 89371588,
						"name": "LGD.Taobao.DD",
						"hero_id": 16,
						"team": 1
					},
					{
						"account_id": 99460568,
						"name": "LGD.Taobao.Icy",
						"hero_id": 96,
						"team": 1
					},
					{
						"account_id": 98878010,
						"name": "LGD.Taobao.Yao",
						"hero_id": 106,
						"team": 1
					},
					{
						"account_id": 114239371,
						"name": "LGD.Taobao.ddc",
						"hero_id": 92,
						"team": 1
					},
					{
						"account_id": 131237305,
						"name": "NE.The Answer",
						"hero_id": 68,
						"team": 0
					},
					{
						"account_id": 101375717,
						"name": "NE.ShiKi",
						"hero_id": 17,
						"team": 0
					},
					{
						"account_id": 134729228,
						"name": "NE.",
						"hero_id": 100,
						"team": 0
					},
					{
						"account_id": 123854991,
						"name": "LGD.Taobao.Rabbit",
						"hero_id": 9,
						"team": 1
					}
				]
				,
				"radiant_team": {
					"team_name": "NE Gaming",
					"team_id": 633833,
					"team_logo": 3336342992235688830,
					"complete": true
				},
				"dire_team": {
					"team_name": "LGD-GAMING",
					"team_id": 15,
					"team_logo": 630787216938014761,
					"complete": true
				},
				"lobby_id": 23432170694743987,
				"spectators": 723,
				"tower_state": 4194302,
				"league_id": 1097
			}
		]
		
	}
}""")

@app.route('/')
def main_page():
	global lastFetched, cachedHtml
	now = long(round(time.time()))
	if now - lastFetched > 1L:
		lastFetched = now
		response = urllib2.urlopen('https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v0001/?key=' + apiKey)
		cachedHtml = json.loads(response.read())
	return render_template('main.html', data=testing)

if __name__ == '__main__':
    app.run(debug=True)
