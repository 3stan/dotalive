import TeamInfo
import json

#Object for information pertaining to a live game
class GameInfo:
	def __init__(self):
		self.leagueName = ""
		self.tournamentUrl = ""
		self.numSpectators = 0
		self.towerState = -1
		self.gameStarted = False
		self.lobbyId = -1

		self.radiantPlayers = list()
		self.direPlayers = list()
		self.unassignedPlayers = list()
		self.broadcastPlayers = list()

		self.direTeamInfo = TeamInfo
		self.radiantTeamInfo = TeamInfo

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)