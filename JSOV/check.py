import re

import dpath
import dpath.options

from .utils import Utils

class Check
	"""class for checking templates and their attributes"""

	@staticmethod
	def check_jsov(template):
		"""check the top structure of a JSOV object"""
		if not "root" in template:
			print("Error: object 'root' is missing from the top.")
			return False
		if not "children" in template['root']:
			print("Error: object 'root' lacks a child called 'children'.")
			return False
		if not isinstance(template['root']['children'], list):
			print("Error: 'children' must be a list of objects.")
			return False
		res = True
		for child in template['root']['children']:
			res &= Check.check_jsov_children(child)
		return res

	@staticmethod
	def check_jsov_children(child):
		"""check attributes in JSOV children objects"""
		res = True
		for param in list(child.values())[0].keys():
			if param not in Utils.children_attributes.keys():
				print("Error: '{}' is not a recognized attribute.".format(param))
				return False
			if param == "children":
				for onlykey in child.keys():
					for newchild in child[onlykey]['children']:
						res &= Check.check_jsov_children(newchild)
			if param == "title":
				for onlykey in child.keys():
					res &= Check.check_jsov_special(child[onlykey]['title'])
			if param == "default-child":
				for onlykey in child.keys():
					res &= Check.check_jsov_special(child[onlykey]['default-child'])
		return res

	@staticmethod
	def check_jsov_special(special):
		"""check for particular attributes in JSOV, like 'title' and 'default-child'"""
		for key in special.keys():
			if key not in Utils.children_attributes.keys():
				print("Error: '{}' is not a recognized attribute.".format(key))
				return False
		return True

	@staticmethod
	def check_jsov_attributes(element):
		"""check if it's a proper JSOV object with proper attributes"""
		res = True
		if isinstance(element, dict):
			for key in element.keys():
				if key in Utils.children_attributes:
					if not Utils.children_attributes[key] and not isinstance(element[key], dict):
						print("Error: element '{}' must be a JSOV object.".format(key))
						return False
					if isinstance(element[key], str):
						if not re.match(Utils.children_attributes[key], element[key], re.IGNORECASE):
							print("Error: attribute '{}' has an unaccepted value: '{}'."
								.format(key, element[key]))
							return False
				if isinstance(element[key], dict):
					res &= Check.check_jsov_attributes(element[key])
		return res

	@staticmethod
	def has_defaultchild(jsov, node):
		"""check whether 'default-child' attribute exists"""
		try:
			dpath.options.ALLOW_EMPTY_STRING_KEYS = True
			dc = dpath.util.get(jsov, "/" + node + "/default-child")
			return dc
		except KeyError:
			return False
