from flask import Flask, render_template, request
import urllib2
import urllib
import time
import json
import os

import sys
sys.path.append(os.path.dirname(__file__) + '/classes/')

from UpdateInfo import UpdateInfo, Update

import util

app = Flask(__name__, static_folder='../images', static_url_path='/images', template_folder='../templates')

#Time that we last fetched data from Valve's web endpoint (GetLiveLeagueGames)
lastFetched = 0

#Dictionary of all the leagues that are available in the client
cachedLeaguesDict = dict()
#Dictionary of all heroes in the game
cachedHeroesDict = dict()

#Cached result of live games
gameResults = list()
gameStatuses = dict()

#For testing purposes; will remove once we deploy to prod
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

#Stuff to do before out first request; created images directory if it doesn't exist,
#fill the dictionaries with the needed data.
@app.before_first_request
def initialize():
	global cachedLeaguesDict, cachedHeroesDict
	directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images")
	util.require_dir(directory)
	util.require_dir(os.path.join(directory, "teams"))

	cachedLeaguesDict = util.get_leagues()
	cachedHeroesDict = util.get_heroes()

#What we do when we hit the main page
@app.route('/')
def main_page():
	global lastFetched, gameResults

	now = long(round(time.time()))
	#Make sure we throttle calls to Valve's endpoint
	if now - lastFetched > 1000000L:
		lastFetched = now
		intermediateGameResults = list()
		cachedHtml = util.make_dota2_match_call("GetLiveLeagueGames")

		#All the important shit is done in util.py
		for game in cachedHtml['result']['games']:
			gameInfo = util.get_live_match_info(game)
			gameStatuses[gameInfo.lobbyId] = gameInfo
			intermediateGameResults.append(gameInfo)

		gameResults = intermediateGameResults

	return render_template('main.html', data=gameResults)

#How we give back updates to the page.
#@matches is in the form of:
#	gameId:gameStarted
#Comma delimited.
@app.route('/getUpdates/<matches>')
def get_updates(matches):
	global lastFetched, gameResults, gameStatuses

	now = long(round(time.time()))
	intermediateGameResults = list()
	intermediateGameStatuses = dict()
	#Make sure we throttle calls to Valve's endpoint
	if now - lastFetched > 1L:
		lastFetched = now
		cachedHtml = util.make_dota2_match_call("GetLiveLeagueGames")

		#All the important shit is done in util.py
		for game in cachedHtml['result']['games']:
			intermediateGameResults.append(util.get_live_match_info(game))

		gameResults = intermediateGameResults

	updateInfo = UpdateInfo()

	newGamesRemoved = list()

	for match in matches.split(","):
		matchInfo = match.split(":")
		matchId = matchInfo[0]
		matchStatus = matchInfo[1]

		print(matchId)
		print(gameStatuses.keys())

		#This is where shit gets tricky
		#If it's not in the dictionary, then it's a new game
		if not long(matchId) in gameStatuses:
			updateInfo.newGames.append(matchId)
		else:
			newGamesRemoved.append(match)

	for game in intermediateGameResults:
		intermediateGameStatuses[game.lobbyId] = game

	gameStatuses = intermediateGameStatuses

	for match in newGamesRemoved:
		matchInfo = match.split(":")
		matchId = matchInfo[0]
		matchStatus = matchInfo[1]

		#If it still does not exist in the dictionary, that means the game is done
		if not long(matchId) in gameStatuses:
			updateInfo.finishedGames.append(matchId)
		else:
			#This means that the game started
			if bool(matchStatus) != gameStatuses[long(matchId)].gameStarted:
				updateInfo.startedGames.append(gameStatuses[long(matchId)])
			#Nothing, the game is still happenin'
			else:
				update = Update()
				update.lobbyId = gameStatuses[long(matchId)].lobbyId
				update.towerStatus = gameStatuses[long(matchId)].towerState
				update.numSpectators = gameStatuses[long(matchId)].numSpectators

				updateInfo.updates.append(update)

	return updateInfo.to_JSON()

if __name__ == '__main__':
    app.run(debug=True)
