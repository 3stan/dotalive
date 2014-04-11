import urllib2
import urllib
import json
import errno
import os

logoUrl = "http://api.steampowered.com/ISteamRemoteStorage/GetUGCFileDetails/v1/"
apiKey = '567159D5C2554BBE3419B4F5244C00CF'
language = 'en_us'
heroPicSize = "sb.png"

directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images")

cachedLeaguesDict = dict()
cachedLeaguesResp = json.loads('{}')

leaguesFetched = False
cachedHtml = json.loads('{}')

heroesFetched = False
cachedHeroesDict = dict()
cachedHeroesResp = json.loads('{}')

teamDict = {0: 'Radiant', 1: 'Dire', 2: 'Broadcaster', 3: 'Unassigned', 4: 'Unassigned'}

def get_live_match_info(game):

    game['league_name'] = cachedLeaguesDict[game['league_id']]['name']
    game['tournament_url'] = cachedLeaguesDict[game['league_id']]['tournament_url']

    for player in game['players']:
        if player['hero_id'] == 0:
            player['hero_img'] = ""
        else:
            player['hero_img'] = getHeroPicUrl(player['hero_id'])
            player['hero_name_localized'] = cachedHeroesDict[player['hero_id']]['localized_name']
        player['account_url'] = getPlayerProfileUrl(str(player["account_id"]))
        player['team'] = teamDict[player['team']]

    if game['radiant_team']['team_logo'] != 0:
        radiant_logo_data = getTeamLogoData(game['radiant_team']['team_logo'])
        getTeamLogo(directory, radiant_logo_data['data']['url'], radiant_logo_data['data']['filename'])
        game['radiant_team']['team_logo'] = os.path.join('images', radiant_logo_data['data']['filename'] + '.png')

    if game['dire_team']['team_logo'] != 0:
        dire_logo_data = getTeamLogoData(game['dire_team']['team_logo'])
        getTeamLogo(directory, dire_logo_data['data']['url'], dire_logo_data['data']['filename'])
        game['dire_team']['team_logo'] = os.path.join('images', dire_logo_data['data']['filename'] + '.png')


def make_econ_dota2_call(callType):
    response = urllib2.urlopen('https://api.steampowered.com/IEconDOTA2_570/' + callType + '/v0001/?key=' + apiKey + "&language=" + language)
    return json.loads(response.read())

def make_dota2_match_call(callType):
    response = urllib2.urlopen('https://api.steampowered.com/IDOTA2Match_570/' + callType + '/v0001/?key=' + apiKey + "&language=" + language)
    return json.loads(response.read())

def get_leagues():
    global cachedLeaguesResp, leaguesFetched, cachedLeaguesDict
    if(not leaguesFetched):
        print("Fetching leagues")
        leaguesFetched = True
        cachedLeaguesResp = make_dota2_match_call("GetLeagueListing")
    for league in cachedLeaguesResp['result']['leagues']:
        cachedLeaguesDict[league['leagueid']] = league
    return cachedLeaguesDict

def get_heroes():
    global cachedHeroesResp, heroesFetched, cachedHeroesDict
    if(not heroesFetched):
        print("Fetching heroes")
        heroesFetched = True
        cachedHeroesResp = make_econ_dota2_call("GetHeroes")
    for hero in cachedHeroesResp['result']['heroes']:
        cachedHeroesDict[hero['id']] = hero
    return cachedHeroesDict

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

def getHeroPicUrl(heroId):
    return "http://cdn.dota2.com/apps/dota2/images/heroes/{}_{}".format(cachedHeroesDict[heroId]["name"].replace("npc_dota_hero_", ""), heroPicSize)

def getPlayerProfileUrl(playerId):
    return "http://steamcommunity.com/profiles/{}".format(convertSteamId(playerId))
