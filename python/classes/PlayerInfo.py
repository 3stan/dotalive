import json

#Object for information pertaining to a player
class PlayerInfo:
	def __init__(self):
		self.name = ""
		self.steamUrl = ""

		self.heroName = ""
		self.heroSrcUrl = ""

		self.streamUrl = ""

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)