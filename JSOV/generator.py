import os
import json
import re
from itertools import islice

import yaml
import dpath
import dpath.options

from .utils import Utils


class Generator:
	children_attributes = {
	"bgcolor": r"^\#[0-9a-f]{1,6}$",
	"fgcolor": r"^\#[0-9a-f]{1,6}$",
	"rounded-corners": r"^\d+$",
	"cascading": r"^(vertical|horizontal|tabular)$",
	"title": "",
	"default-child": "",
	"children": "",
	}

	def __init__(self, jsonfile, jsovfile):
		dpath.options.ALLOW_EMPTY_STRING_KEYS = True
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
			self.input = Utils.lower_keys(json.load(json_fp))
		with open(self.jsovfile, "r") as jsov_fp:
			self.template = Utils.lower_keys(yaml.load(jsov_fp))

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
		res = True
		for param in list(child.values())[0].keys():
			if param not in self.children_attributes.keys():
				print("Error: '{}' is not a recognized attribute.".format(param))
				return False
			if param == "children":
				for onlykey in child.keys():
					for newchild in child[onlykey]['children']:
						res &= self.check_jsov_children(newchild)
			if param == "title":
				for onlykey in child.keys():
					res &= self.check_jsov_special(child[onlykey]['title'])
			if param == "default-child":
				for onlykey in child.keys():
					res &= self.check_jsov_special(child[onlykey]['default-child'])
		return res

	def check_jsov_special(self, special):
		for key in special.keys():
			if key not in self.children_attributes.keys():
				print("Error: '{}' is not a recognized attribute.".format(key))
				return False
		return True

	def parse_jsov_attributes(self, element):
		res = True
		if isinstance(element, list):
			for item in element:
				res &= self.parse_jsov_attributes(item)
		if isinstance(element, dict):
			for key in element.keys():
				if key in self.children_attributes:
					if not self.children_attributes[key] and not (isinstance(element[key], dict) \
						or isinstance(element[key], list)):
						print("Error: element '{}' must be a JSOV object.".format(key))
						return False
					if isinstance(element[key], str):
						if not re.match(self.children_attributes[key], element[key], re.IGNORECASE):
							print("Error: attribute '{}' has an unaccepted value: '{}'."
								.format(key, element[key]))
							return False
				if isinstance(element[key], dict) or isinstance(element[key], list):
					res &= self.parse_jsov_attributes(element[key])
		return res

	def generate_css(self):
		style = ""
		children = dpath.util.get(self.template, "/root/children")
		for child in children:
			key = list(islice(child, 1))[0]
			style += "." + str(key) + " {\n"
			if "bgcolor" in child[key]:
				style += "background-color: " + child[key]['bgcolor'] + ";\n"
			if "fgcolor" in child[key]:
				style += "color: " + child[key]['fgcolor'] + ";\n"
			if "rounded-corners" in child[key]:
				style += "border-radius: " + child[key]['rounded-corners'] + "px;\n"
			style += "}\n"
		print(style)

	def generate_htmlcss(self, output_html=None, output_css=None):
		if "display" in self.template['root']:
			if not self.template['root']['display']:
				self.generate_css()
