from flask import Flask, render_template
import urllib2
import urllib
import time
import json
import errno
import os
app = Flask(__name__, static_folder='images', static_url_path='/images')

logoUrl = "http://api.steampowered.com/ISteamRemoteStorage/GetUGCFileDetails/v1/" #?key=APIKEYHERE&appid=570&ugcid="
apiKey = '567159D5C2554BBE3419B4F5244C00CF'
language = 'en_us'
heroPicSize = "sb.png"

lastFetched = 0
leaguesFetched = False
cachedHtml = json.loads('{}')

cachedLeaguesDict = dict()
cachedLeaguesResp = json.loads('{}')

heroesFetched = False
cachedHeroesDict = dict()
cachedHeroesResp = json.loads('{}')

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

def get_leagues():
	global cachedLeaguesResp, leaguesFetched, cachedLeaguesDict
	if(not leaguesFetched):
		print("Fetching leagues")
		leaguesFetched = True
		response = urllib2.urlopen('https://api.steampowered.com/IDOTA2Match_570/GetLeagueListing/v0001/?key=' + apiKey + "&language=" + language)
		cachedLeaguesResp = json.loads(response.read())
	for league in cachedLeaguesResp['result']['leagues']:
		cachedLeaguesDict[league['leagueid']] = league['name']
	return True

def get_heroes():
	global cachedHeroesResp, heroesFetched, cachedHeroesDict
	if(not heroesFetched):
		print("Fetching heroes")
		heroesFetched = True
		response = urllib2.urlopen('https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key=' + apiKey + "&language=" + language)
		cachedHeroesResp = json.loads(response.read())
	for hero in cachedHeroesResp['result']['heroes']:
		cachedHeroesDict[str(hero['id']) + "_name"] = hero['name']
		cachedHeroesDict[str(hero['id']) + "_localized"] = hero['localized_name']
	return True

def convertSteamId(id):
    if len(id) == 17:
        return int(id[3:]) - 61197960265728
    else:
        return '765' + str(int(id) + 61197960265728)

def require_dir(path):
    try:
        os.makedirs(path)
    except OSError, exc:
        if exc.errno != errno.EEXIST:
            raise

def getTeamLogoData(logoId):
	response = urllib2.urlopen(logoUrl + '?key=' + apiKey + "&appid=570&ugcid=" + str(logoId))
	return json.loads(response.read())

def getTeamLogo(directory, url, imageName):
	filename = os.path.join(directory, imageName + ".png")

	if not os.path.exists(filename):
	    urllib.urlretrieve(url, filename)

@app.route('/')
def main_page():
	global lastFetched, cachedHtml, cachedHeroesDict, cachedLeaguesDict, heroPicSize

	directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
	require_dir(directory)
	require_dir(os.path.join(directory, "teams"))

	get_leagues()
	get_heroes()
	now = long(round(time.time()))
	if now - lastFetched > 1000000L:
		lastFetched = now
		response = urllib2.urlopen('https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v0001/?key=' + apiKey + "&language=" + language)
		cachedHtml = json.loads(response.read())
		for game in testing['result']['games']:
			
			game['league_id'] = cachedLeaguesDict[game['league_id']]

			for player in game['players']:
				if player['hero_id'] == 0:
					player['hero_id'] = "Spectator"
					player['hero_img'] = ""
				else:
					player['hero_img'] = "http://cdn.dota2.com/apps/dota2/images/heroes/{}_{}".format(str.replace(str(cachedHeroesDict[str(player['hero_id']) + "_name"]), "npc_dota_hero_", ""), heroPicSize)
					player['hero_id'] = cachedHeroesDict[str(player['hero_id']) + "_localized"]
				player['account_url'] = "http://steamcommunity.com/profiles/{}".format(convertSteamId(str(player["account_id"])))

			radiant_logo_data = getTeamLogoData(game['radiant_team']['team_logo'])
			dire_logo_data = getTeamLogoData(game['dire_team']['team_logo'])

			getTeamLogo(directory, radiant_logo_data['data']['url'], radiant_logo_data['data']['filename'])
			getTeamLogo(directory, dire_logo_data['data']['url'], dire_logo_data['data']['filename'])

			game['radiant_team']['team_logo'] = os.path.join('images', radiant_logo_data['data']['filename'] + '.png')
			game['dire_team']['team_logo'] = os.path.join('images', dire_logo_data['data']['filename'] + '.png')

	return render_template('main.html', data=testing)

if __name__ == '__main__':
    app.run(debug=True)
