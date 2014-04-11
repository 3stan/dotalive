from flask import Flask, render_template
import urllib2
import urllib
import time
import json
import os
import util
app = Flask(__name__, static_folder='../images', static_url_path='/images', template_folder='../templates')

lastFetched = 0

cachedLeaguesDict = dict()
cachedHeroesDict = dict()

teamDict = {0: 'Radiant', 1: 'Dire', 2: 'Broadcaster', 3: 'Unassigned', 4: 'Unassigned'}

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
	global lastFetched, cachedHtml, heroPicSize, teamDict
	directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images")

	now = long(round(time.time()))
	if now - lastFetched > 1000000L:
		lastFetched = now
		cachedHtml = util.make_dota2_match_call("GetLiveLeagueGames")
		for game in testing['result']['games']:
			
			game['league_name'] = cachedLeaguesDict[game['league_id']]['name']
			game['tournament_url'] = cachedLeaguesDict[game['league_id']]['tournament_url']

			for player in game['players']:
				if player['hero_id'] == 0:
					player['hero_img'] = ""
				else:
					player['hero_img'] = util.getHeroPicUrl(player['hero_id'])
					player['hero_name_localized'] = cachedHeroesDict[player['hero_id']]['localized_name']
				player['account_url'] = util.getPlayerProfileUrl(str(player["account_id"]))
				player['team'] = teamDict[player['team']]

			if game['radiant_team']['team_logo'] != 0:
				radiant_logo_data = util.getTeamLogoData(game['radiant_team']['team_logo'])
				util.getTeamLogo(directory, radiant_logo_data['data']['url'], radiant_logo_data['data']['filename'])
				game['radiant_team']['team_logo'] = os.path.join('images', radiant_logo_data['data']['filename'] + '.png')

			if game['dire_team']['team_logo'] != 0:
				dire_logo_data = util.getTeamLogoData(game['dire_team']['team_logo'])
				util.getTeamLogo(directory, dire_logo_data['data']['url'], dire_logo_data['data']['filename'])
				game['dire_team']['team_logo'] = os.path.join('images', dire_logo_data['data']['filename'] + '.png')

	return render_template('main.html', data=testing)

if __name__ == '__main__':
    app.run(debug=True)
