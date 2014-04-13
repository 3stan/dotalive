import json

#Object for information pertaining to a team
class TeamInfo:
	def __init__(self):
		self.teamName = ""
		self.teamLogoSrc = ""
		self.isFullRoster = False

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)