from flask import Flask, render_template
import urllib2
import urllib
import time
import json
import os

import sys
sys.path.append(os.path.dirname(__file__) + '/classes/')

import util


app = Flask(__name__, static_folder='../images', static_url_path='/images', template_folder='../templates')

lastFetched = 0

cachedLeaguesDict = dict()
cachedHeroesDict = dict()

gameResults = list()

testing = json.loads("""
					{
	"result": {
		"games": [
			{
				"players": [
					{
						"account_id": 22743308,
						"name": "joinDOTA|KF91",
						"hero_id": 0,
						"team": 4
					},
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
			},
			{
				"players": [
					{
						"account_id": 22743308,
						"name": "joinDOTA|KF92",
						"hero_id": 0,
						"team": 4
					},
					{
						"account_id": 101851949,
						"name": "TEST",
						"hero_id": 0,
						"team": 2
					},
					{
						"account_id": 139266129,
						"name": "TEST1",
						"hero_id": 98,
						"team": 0
					},
					{
						"account_id": 88990397,
						"name": "TEST2",
						"hero_id": 0,
						"team": 2
					},
					{
						"account_id": 47123324,
						"name": "TEST3",
						"hero_id": 0,
						"team": 2
					},
					{
						"account_id": 142750189,
						"name": "TEST4",
						"hero_id": 86,
						"team": 0
					},
					{
						"account_id": 85293283,
						"name": "TEST5",
						"hero_id": 0,
						"team": 2
					},
					{
						"account_id": 89371588,
						"name": "TEST6",
						"hero_id": 16,
						"team": 1
					},
					{
						"account_id": 99460568,
						"name": "TEST7",
						"hero_id": 96,
						"team": 1
					},
					{
						"account_id": 98878010,
						"name": "TEST8",
						"hero_id": 106,
						"team": 1
					},
					{
						"account_id": 114239371,
						"name": "TEST9",
						"hero_id": 92,
						"team": 1
					},
					{
						"account_id": 131237305,
						"name": "TEST10",
						"hero_id": 68,
						"team": 0
					},
					{
						"account_id": 101375717,
						"name": "TEST11",
						"hero_id": 17,
						"team": 0
					},
					{
						"account_id": 134729228,
						"name": "TEST12",
						"hero_id": 100,
						"team": 0
					},
					{
						"account_id": 123854991,
						"name": "TEST13",
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
				"spectators": 111111,
				"tower_state": 4194302,
				"league_id": 1097
			}
		]
		
	}
}""")

@app.before_first_request
def initialize():
	global cachedLeaguesDict, cachedHeroesDict
	directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images")
	util.require_dir(directory)
	util.require_dir(os.path.join(directory, "teams"))

	cachedLeaguesDict = util.get_leagues()
	cachedHeroesDict = util.get_heroes()

@app.route('/')
def main_page():
	global lastFetched, gameResults

	now = long(round(time.time()))
	if now - lastFetched > 1000000L:
		lastFetched = now
		cachedHtml = util.make_dota2_match_call("GetLiveLeagueGames")

		for game in testing['result']['games']:
			gameResults.append(util.get_live_match_info(game))

	return render_template('main.html', data=gameResults)

if __name__ == '__main__':
    app.run(debug=True)
