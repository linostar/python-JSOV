import os
import json

import yaml


class Generator:
	def __init__(self, jsonfile, jsovfile):
		self.jsonfile = jsonfile
		self.jsovfile = jsovfile[0]
		self.load_dicts()

	def load_dicts(self):
		if not os.path.exists(self.jsonfile):
			print("Error: inputfile '{}' could not be found.".format(self.jsonfile))
			sys.exit(1)
		if not os.path.exists(self.jsovfile):
			print("Error: template '{}' could not be found.".format(self.jsovfile))
			sys.exit(1)
		with open(self.jsonfile, "r") as json_fp:
			self.dict = json.load(json_fp)
		with open(self.jsovfile, "r") as jsov_fp:
			self.template = yaml.load(jsov_fp)

	def generate_html(self, output_html, output_css):
		pass
