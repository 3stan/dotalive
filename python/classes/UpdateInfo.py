import json

class UpdateInfo:
	def __init__(self):
		#List of Update objects
		self.updates = list()
		#List of GameInfo objects
		self.newGames = list()
		#List of GameInfo objects
		self.startedGames = list()
		#List of longs
		self.finishedGames = list()

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class Update:
	def __init__(self):
		self.lobbyId = -1
		self.towerStatus = -1
		self.numSpectators = -1

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)