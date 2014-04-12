import TeamInfo

class GameInfo:
	def __init__(self):
		self.leagueName = ""
		self.tournamentUrl = ""
		self.numSpectators = 0
		self.towerState = -1

		self.radiantPlayers = list()
		self.direPlayers = list()
		self.unassignedPlayers = list()
		self.broadcastPlayers = list()

		self.direTeamInfo = TeamInfo
		self.radiantTeamInfo = TeamInfo