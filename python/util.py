import urllib2
import urllib
import json
import errno
import os
from TeamInfo import TeamInfo
from GameInfo import GameInfo
from PlayerInfo import PlayerInfo

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

    resultGame = GameInfo()

    resultGame.leagueName = cachedLeaguesDict[game['league_id']]['name']
    resultGame.tournamentUrl = cachedLeaguesDict[game['league_id']]['tournament_url']
    resultGame.numSpectators = game['spectators']
    resultGame.towerState = game['tower_state']

    resultGame.radiantTeamInfo = fillTeamData(game['radiant_team'])
    resultGame.direTeamInfo = fillTeamData(game['dire_team'])

    for player in game['players']:
        playerInfo = PlayerInfo()

        if player['hero_id'] != 0:
            playerInfo.heroSrcUrl = getHeroPicUrl(player['hero_id'])
            playerInfo.heroName= cachedHeroesDict[player['hero_id']]['localized_name']
        playerInfo.name = player['name']
        playerInfo.steamUrl = getPlayerProfileUrl(str(player["account_id"]))

        playerTeam = player['team']
        if playerTeam == 0:
            resultGame.radiantPlayers.append(playerInfo)
        elif playerTeam == 1:
            resultGame.direPlayers.append(playerInfo)
        elif playerTeam == 2:
            resultGame.broadcastPlayers.append(playerInfo)
        else:
            resultGame.unassignedPlayers.append(playerInfo)
    for a in resultGame.radiantPlayers:
                print(a.name)
    return resultGame

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

def fillTeamData(inputTeam):
    teamInfo = TeamInfo()
    teamInfo.teamName = inputTeam['team_name']
    print(teamInfo.teamName)
    teamInfo.isFullRoster = True if inputTeam['complete'] == "true" else False

    if inputTeam['team_logo'] != 0:
        logo_data = getTeamLogoData(inputTeam['team_logo'])
        if logo_data != -1:
            getTeamLogo(directory, logo_data['data']['url'], logo_data['data']['filename'])
            teamInfo.teamLogoSrc = os.path.join('images', logo_data['data']['filename'] + '.png')
        else:
            teamInfo.teamLogoSrc = "none"

    return teamInfo

def getTeamLogoData(logoId):
    print(logoUrl + '?key=' + apiKey + "&appid=570&ugcid=" + str(logoId))
    try:
        response = urllib2.urlopen(logoUrl + '?key=' + apiKey + "&appid=570&ugcid=" + str(logoId))
    except:
        return -1
    return json.loads(response.read())

def getTeamLogo(directory, url, imageName):
	filename = os.path.join(directory, imageName + ".png")

	if not os.path.exists(filename):
	    urllib.urlretrieve(url, filename)

def getHeroPicUrl(heroId):
    return "http://cdn.dota2.com/apps/dota2/images/heroes/{}_{}".format(cachedHeroesDict[heroId]["name"].replace("npc_dota_hero_", ""), heroPicSize)

def getPlayerProfileUrl(playerId):
    return "http://steamcommunity.com/profiles/{}".format(convertSteamId(playerId))
