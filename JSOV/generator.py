import json

import yaml


class Generator:
	def __init__(self, jsonfile, jsovfile):
		self.jsonfile = jsonfile
		self.jsovfile = jsovfile
		self.load_dicts()

	def load_dicts(self):
		self.dict = json.load(self.jsonfile)
		self.template = yaml.load(self.jsovfile)

	def generate_html(self, output_html, output_css):
		pass
