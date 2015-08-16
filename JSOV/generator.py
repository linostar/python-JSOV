import os
import json

import yaml


class Generator:
	children_attributes = ["bgcolor", "fgcolor", "rounded-corners", "cascading", "title",
	"default-child", "children"]

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
			self.input = json.load(json_fp)
		with open(self.jsovfile, "r") as jsov_fp:
			self.template = yaml.load(jsov_fp)

	def check_jsov(self):
		if not "root" in self.template:
			print("Error: object 'root' is missing from the top.")
			return False
		if not "children" in self.template['root']:
			print("Error: object 'root' lacks a child called 'children'.")
			return False
		if not isinstance(self.template['root']['children'], list):
			print("Error: 'children' must be a list of objects.")
			return False
		res = True
		for child in self.template['root']['children']:
			res &= self.check_jsov_children(child)
		return res

	def check_jsov_children(self, child):
		for param in list(child.values())[0].keys():
			if param not in self.children_attributes:
				print("Error: '{}' is not a recognized attribute.".format(param))
				return False
		return True


	def generate_html(self, output_html=None, output_css=None):
		return self.check_jsov()
