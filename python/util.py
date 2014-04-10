import urllib2
import urllib
import json
import errno
import os

logoUrl = "http://api.steampowered.com/ISteamRemoteStorage/GetUGCFileDetails/v1/"
apiKey = '567159D5C2554BBE3419B4F5244C00CF'
language = 'en_us'
heroPicSize = "sb.png"

cachedLeaguesDict = dict()
cachedLeaguesResp = json.loads('{}')

leaguesFetched = False
cachedHtml = json.loads('{}')

heroesFetched = False
cachedHeroesDict = dict()
cachedHeroesResp = json.loads('{}')

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
    print(cachedHeroesDict[heroId]["name"])
    return "http://cdn.dota2.com/apps/dota2/images/heroes/{}_{}".format(cachedHeroesDict[heroId]["name"].replace("npc_dota_hero_", ""), heroPicSize)

def getPlayerProfileUrl(playerId):
    return "http://steamcommunity.com/profiles/{}".format(convertSteamId(playerId))
