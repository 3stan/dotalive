import urllib2
import urllib
import json
import errno
import os
from TeamInfo import TeamInfo
from GameInfo import GameInfo
from PlayerInfo import PlayerInfo

#Important API related shit
logoUrl = "http://api.steampowered.com/ISteamRemoteStorage/GetUGCFileDetails/v1/"
econUrl = "https://api.steampowered.com/IEconDOTA2_570/"
matchUrl = 'https://api.steampowered.com/IDOTA2Match_570/'
heroPicUrl = "http://cdn.dota2.com/apps/dota2/images/heroes/"
profileUrl = "http://steamcommunity.com/profiles/"
apiKey = '567159D5C2554BBE3419B4F5244C00CF'
language = 'en_us'
heroPicSize = "sb.png"

#OS related stuff; where to save and fetch images from
imageDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../public/team_logos")

#Variables related to the league dictionary
#Dictionary KVP is:
#   Key = LeagueId
#   Value = League object
leaguesFetched = False
cachedLeaguesDict = dict()
cachedLeaguesResp = json.loads('{}')

#Variables related to the heroes dictionary
#Dictionary KVP is:
#   Key = HeroId
#   Value = Hero object
heroesFetched = False
cachedHeroesDict = dict()
cachedHeroesResp = json.loads('{}')

#Method that converts a JSON game data into a GameInfo object
def get_live_match_info(game):

    #Create the object first
    resultGame = GameInfo()

    print("Basic game info")
    #Shit's that easy to fill in
    resultGame.leagueName = cachedLeaguesDict[game['league_id']]['name']
    resultGame.tournamentUrl = cachedLeaguesDict[game['league_id']]['tournament_url']
    resultGame.numSpectators = game['spectators']
    resultGame.towerState = game['tower_state']
    resultGame.lobbyId = game['lobby_id']
    print("Done basic info")

    print("Getting team data")
    #Fill in team data with a helper function
    resultGame.radiantTeamInfo = fillTeamData(game['radiant_team'])
    resultGame.direTeamInfo = fillTeamData(game['dire_team'])
    print("Done getting team data")

    heroesPicked = 0

    #Fill in player data
    for player in game['players']:
        playerInfo = PlayerInfo()

        if player['hero_id'] != 0:
            heroesPicked += 1
            playerInfo.heroSrcUrl = getHeroPicUrl(player['hero_id'])
            playerInfo.heroName = cachedHeroesDict[player['hero_id']]['localized_name']
        playerInfo.name = player['name']
        playerInfo.steamUrl = getPlayerProfileUrl(str(player["account_id"]))
        playerInfo.steamId = player["account_id"]

        playerTeam = player['team']
        if playerTeam == 0:
            resultGame.radiantPlayers.append(playerInfo)
        elif playerTeam == 1:
            resultGame.direPlayers.append(playerInfo)
        elif playerTeam == 2:
            resultGame.broadcastPlayers.append(playerInfo)
        else:
            resultGame.unassignedPlayers.append(playerInfo)

    if heroesPicked > 9:
        resultGame.gameStarted = True

    #Return the full object
    return resultGame

#If we need to make any calls to the econ server, we use this
def make_econ_dota2_call(callType):
    response = urllib2.urlopen(econUrl + callType + '/v0001/?key=' + apiKey + "&language=" + language)
    return json.loads(response.read())

#If we need to make any calls to the match server, we use this
def make_dota2_match_call(callType):
    response = urllib2.urlopen(matchUrl + callType + '/v0001/?key=' + apiKey + "&language=" + language)
    print(matchUrl + callType + '/v0001/?key=' + apiKey + "&language=" + language)
    return json.loads(response.read())

#Function that gets all league data from the Valve servers and fills the dictionary.
#This function caches the data.
def get_leagues():
    global cachedLeaguesResp, leaguesFetched, cachedLeaguesDict
    if(not leaguesFetched):
        print("Fetching leagues")
        leaguesFetched = True
        cachedLeaguesResp = make_dota2_match_call("GetLeagueListing")
    for league in cachedLeaguesResp['result']['leagues']:
        cachedLeaguesDict[league['leagueid']] = league
    return cachedLeaguesDict

#Function that gets all the hero data from the Valve servers and fills the dictionary
#This function is cached
def get_heroes():
    global cachedHeroesResp, heroesFetched, cachedHeroesDict
    if(not heroesFetched):
        print("Fetching heroes")
        heroesFetched = True
        cachedHeroesResp = make_econ_dota2_call("GetHeroes")
    for hero in cachedHeroesResp['result']['heroes']:
        cachedHeroesDict[hero['id']] = hero
    return cachedHeroesDict

#Useful converter that converts 32-bit steam ID's to 64-bit and vice versa.
def convertSteamId(id):
    if len(id) == 17:
        return int(id[3:]) - 61197960265728
    else:
        return '765' + str(int(id) + 61197960265728)

#Method that creates the directory at @path if it doesn't exist already
def require_dir(path):
    try:
        os.makedirs(path)
    except OSError, exc:
        if exc.errno != errno.EEXIST:
            raise

#Creates a TeamInfo object from @inputTeam, which is a JSON object
def fillTeamData(inputTeam):
    teamInfo = TeamInfo()
    teamInfo.teamName = inputTeam['team_name']
    teamInfo.isFullRoster = True if inputTeam['complete'] == "true" else False

    if inputTeam['team_logo'] != 0:
        strTeamLogo = str(inputTeam['team_logo'])
        logo_data = getTeamLogoData(imageDirectory, strTeamLogo)
        if logo_data == "no_logo":
            teamInfo.teamLogoSrc = ""
        elif logo_data == "logo_exists":
            teamInfo.teamLogoSrc = os.path.join('public/team_logos', strTeamLogo + '.png')
        else:
            getTeamLogo(imageDirectory, logo_data['data']['url'], strTeamLogo)
            teamInfo.teamLogoSrc = os.path.join('public/team_logos', strTeamLogo + '.png')

    return teamInfo

#Fetches the team's logo data. 
#@logoId is the ID of the logo itself, not the team
def getTeamLogoData(directory, logoId):
    filename = os.path.join(directory, logoId + ".png")
    if os.path.exists(filename):
        return "logo_exists"
    try:
        response = urllib2.urlopen(logoUrl + '?key=' + apiKey + "&appid=570&ugcid=" + str(logoId))
    except:
        return "no_logo"
    return json.loads(response.read())

#Downloads the team's logo from Valve's server
def getTeamLogo(directory, url, imageName):
	filename = os.path.join(directory, 'team_logos/' + imageName + ".png")

    #Only download if the file does not exist yet
	if not os.path.exists(filename):
	    urllib.urlretrieve(url, filename)

#Hero portraits are graciously hosted on Valve's servers; so we don't need to download them manually.
def getHeroPicUrl(heroId):
    return heroPicUrl + "{}_{}".format(cachedHeroesDict[heroId]["name"].replace("npc_dota_hero_", ""), heroPicSize)

#Generate a player's profile URL
#@playerId is a 32-bit version of their steamId
def getPlayerProfileUrl(playerId):
    return profileUrl + "{}".format(convertSteamId(playerId))

def str2bool(v):
  return v.lower() == "true"