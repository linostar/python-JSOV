import json


class Generator:
	def __init__(self, jsonfile, jsovfile):
		self.jsonfile = jsonfile
		self.jsovfile = jsovfile
		self.load_dict()

	def load_dict(self):
		self.dict = json.load(self.jsonfile)

	def generate_html(self, output_html, output_css):
		pass
