import os
import json
import re
from itertools import islice

import yaml
import dpath
import dpath.options

from .utils import Utils


class Generator:
	TAB = "  "
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

	def has_defaultchild(self, jsov, node):
		try:
			dc = dpath.util.get(jsov, "/" + node + "/default-child")
			return dc
		except KeyError:
			return False

	def generate_css(self, jsov, node, parent):
		# for 'children' elements
		style = ""
		try:
			children = dpath.util.get(jsov, "/" + node + "/children")
			has_dc = self.has_defaultchild(jsov, node)
			if not isinstance(children, list):
				children = [children]
			for child in children:
				key = list(islice(child, 1))[0]
				if parent:
					style += "." + str(parent) + "__" + str(key) + " {\n"
				else:
					style += "." + str(key) + " {\n"
				if "bgcolor" in child[key]:
					style += self.TAB + "background-color: " + str(child[key]['bgcolor']) + ";\n"
				if "fgcolor" in child[key]:
					style += self.TAB + "color: " + str(child[key]['fgcolor']) + ";\n"
				if "rounded-corners" in child[key]:
					style += self.TAB + "border-radius: " + str(child[key]['rounded-corners']) + "px;\n"
				# add default-child attributes to each of the children
				if has_dc:
					for attribute, value in has_dc.items():
						if attribute == "bgcolor":
							style += self.TAB + "background-color: " + str(value) + ";\n"
						elif attribute == "fgcolor":
							style += self.TAB + "color: " + str(value) + ";\n"
						elif attribute == "rounded-corners":
							style += self.TAB + "border-radius: " + str(value) + "px;\n"
				style += "}\n\n"
			return style + self.generate_css(child, key, key) + self.generate_css_title(child, key, key)
		except KeyError:
			return ""

	def generate_css_title(self, jsov, node, parent):
		# for 'title' elements
		style = ""
		try:
			title = dpath.util.get(jsov, "/" + node + "/title")
			if parent:
				style += "." + str(parent) + "_title" + "{\n"
			else:
				style += "." + "root_title" + " {\n"
			for attribute, value in title.items():
				if attribute == "bgcolor":
					style += self.TAB + "background-color: " + str(value) + ";\n"
				elif attribute == "fgcolor":
					style += self.TAB + "color: " + str(value) + ";\n"
				elif attribute == "rounded-corners":
					style += self.TAB + "border-radius: " + str(value) + "px;\n"
			style += "}\n\n"
			return style
		except KeyError:
			return ""

	def generate_htmlcss(self, output_html=None, output_css=None):
		if "display" in self.template['root']:
			if not self.template['root']['display']:
				print(self.generate_css(self.template, "root", ""))
