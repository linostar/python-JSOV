import sys
import os
import json
import re
from collections import OrderedDict
from itertools import islice

import yaml
import dpath
import dpath.options

from .utils import Utils


class Generator:
	"""class for JSOV/custom template parsing and output generation"""
	TAB = "  "

	def __init__(self, jsonfile, jsovfile, custom=False):
		"""Initialization of JSON and JSOV file variables"""
		dpath.options.ALLOW_EMPTY_STRING_KEYS = True
		self.jsonfile = jsonfile
		if isinstance(jsovfile, list):
			self.jsovfile = jsovfile[0]
		else:
			self.jsovfile = jsovfile
		self.load_dicts(custom)

	def load_dicts(self, custom):
		"""load the JSON and the JSOV/custom template in their respective objects"""
		if not os.path.exists(self.jsonfile):
			print("Error: inputfile '{}' could not be found.".format(self.jsonfile))
			sys.exit(1)
		if not os.path.exists(self.jsovfile):
			print("Error: template '{}' could not be found.".format(self.jsovfile))
			sys.exit(1)
		with open(self.jsonfile, "r") as json_fp:
			self.input = Utils.lower_keys(json.load(json_fp, object_pairs_hook=OrderedDict))
		with open(self.jsovfile, "r") as jsov_fp:
			if custom:
				self.template = {}
				self.custom_template = jsov_fp.read()
			else:
				self.custom_template = ""
				self.template = Utils.lower_keys(yaml.load(jsov_fp))

	def check_jsov(self):
		"""check the top structure of a JSOV object"""
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
		"""check attributes in JSOV children objects"""
		res = True
		for param in list(child.values())[0].keys():
			if param not in Utils.children_attributes.keys():
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
		"""check for particular attributes in JSOV, like 'title' and 'default-child'"""
		for key in special.keys():
			if key not in Utils.children_attributes.keys():
				print("Error: '{}' is not a recognized attribute.".format(key))
				return False
		return True

	def parse_jsov_attributes(self, element):
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
					res &= self.parse_jsov_attributes(element[key])
		return res

	def has_defaultchild(self, jsov, node):
		"""check whether 'default-child' attribute exists"""
		try:
			dc = dpath.util.get(jsov, "/" + node + "/default-child")
			return dc
		except KeyError:
			return False

	def parse_custom_template(self, text, json_obj):
		"""parse the html_template for {{for}} statements"""
		i = 0
		html = ""
		lines = text.splitlines()
		root = str(list(json_obj.keys())[0])
		# get the "for" blocks
		for_starts = []
		for_ends = []
		for_variables = []
		found_for = 0
		for_index = 0
		for line in lines:
			line = line.strip()
			if line.startswith("{{for ") and line.endswith("}}"):
				for_starts.append(i)
				for_variables.append(line[5:-2].strip())
				found_for += 1
				html += "{{line" + str(for_index) + "}}"
				for_index += 1
			if line == "{{endfor}}":
				if found_for <= 0:
					print("Error: found {{endfor}} that does not correspond to a {{for}} at line " +
						str(i+1) + ".")
					sys.exit(1)
				for_ends.insert(0, i)
				found_for -= 1
			else:
				if found_for == 0:
					html += line
			i += 1
		if len(for_starts) != len(for_ends):
			print("Error: Number of {{for}} lines and that of {{endfor}} lines don't match.")
			sys.exit(1)
		for j in range(len(for_starts)):
			if for_starts[j] < for_ends[j]:
				html = html.replace("{{line" + str(j) + "}}", self.parse_for("\n".join(lines[for_starts[j]+1:for_ends[j]]),
					json_obj, for_variables[j], root))
		html = html.replace("{root}", root)
		return html

	def parse_for(self, block, json_obj, variable, root, depth=1):
		html = ""
		root 
		if variable.isdigit():
			for i in range(int(variable)):
				html += block + "\n"
		else:
			child_depth = re.match(r"children\.(\d+)", variable)
			child_depth = int(child_depth.group(1))
			if child_depth == 1:
				if isinstance(json_obj[root], dict):
					children = list(json_obj[root].keys())
					for child in children:
						html += block.replace("{" + variable + "}", child)
		return html

	def generate_css(self, jsov, node, parent):
		"""generate css styles for 'children' elements"""
		style = ""
		try:
			children = dpath.util.get(jsov, "/" + node + "/children")
			has_dc = self.has_defaultchild(jsov, node)
			for key in children:
				if parent:
					style += "." + str(parent) + "__" + str(key) + " {\n"
				else:
					style += "." + str(key) + " {\n"
				if "bgcolor" in children[key]:
					style += self.TAB + "background-color: " + str(children[key]['bgcolor']) + ";\n"
				if "fgcolor" in children[key]:
					style += self.TAB + "color: " + str(children[key]['fgcolor']) + ";\n"
				if "rounded-corners" in children[key]:
					style += self.TAB + "border-radius: " + str(children[key]['rounded-corners']) + ";\n"
				# add default-child attributes to each of the children
				if has_dc:
					for attribute, value in has_dc.items():
						if attribute == "bgcolor":
							style += self.TAB + "background-color: " + str(value) + ";\n"
						elif attribute == "fgcolor":
							style += self.TAB + "color: " + str(value) + ";\n"
						elif attribute == "rounded-corners":
							style += self.TAB + "border-radius: " + str(value) + ";\n"
				style += "}\n\n"
			return style + self.generate_css(children, key, key) + self.generate_css_title(children, key, key)
		except KeyError:
			return ""

	def generate_css_title(self, jsov, node, parent):
		"""generate css styles for 'title' elements"""
		style = ""
		try:
			title = dpath.util.get(jsov, "/" + node + "/title")
			if parent:
				style += "." + str(parent) + "_title" + " {\n"
			else:
				style += "." + "root_title" + " {\n"
			for attribute, value in title.items():
				if attribute == "bgcolor":
					style += self.TAB + "background-color: " + str(value) + ";\n"
				elif attribute == "fgcolor":
					style += self.TAB + "color: " + str(value) + ";\n"
				elif attribute == "rounded-corners":
					style += self.TAB + "border-radius: " + str(value) + ";\n"
			style += "}\n\n"
			return style
		except KeyError:
			return ""

	def generate_default_css(self):
		"""adding common css styles that will be frequently used"""
		style = ".jsov_div {\n"
		style += self.TAB + "display: inline-block;\n"
		style += self.TAB + "padding: 4px;\n"
		style += self.TAB + "margin: 6px;\n"
		style += "}\n\n"
		style += ".jsov_table {\n"
		style += self.TAB + "border-collapse: collapse;\n"
		style += "}\n\n"
		style += ".jsov_tr {\n"
		bgcolor = "black"
		if "block-border" in self.template['root']:
			if "bgcolor" in self.template['root']['block-border']:
				bgcolor = self.template['root']['block-border']['bgcolor']
		style += self.TAB + "border-bottom: 8px solid {};\n".format(bgcolor)
		style += "}\n\n"
		style += ".jsov_td {\n"
		style += self.TAB + "padding: 4px;\n"
		style += "}\n\n"
		style += ".jsov_linkbox a {\n"
		style += self.TAB + "width: 100%;\n"
		style += self.TAB + "height: 100%;\n"
		style += self.TAB + "display: block;\n"
		style += self.TAB + "text-decoration: none;\n"
		style += self.TAB + "color: inherit;\n"
		style += "}\n\n"
		if "block-border" in self.template['root']:
			style += ".block__border {\n"
			if "border-style" in self.template['root']['block-border']:
				style += self.TAB + "border-style: {};\n".format(
					self.template['root']['block-border']['border-style'])
			if "border-width" in self.template['root']['block-border']:
				style += self.TAB + "border-width: {};\n".format(
					self.template['root']['block-border']['border-width'])
			if "border-color" in self.template['root']['block-border']:
				style += self.TAB + "border-color: {};\n".format(
					self.template['root']['block-border']['border-color'])
			if "rounded-corners" in self.template['root']['block-border']:
				style += self.TAB + "border-radius: {};\n".format(
					self.template['root']['block-border']['rounded-corners'])
			if "bgcolor" in self.template['root']['block-border']:
				style += self.TAB + "background-color: {};\n".format(
					self.template['root']['block-border']['bgcolor'])
			if "internal-spacing" in self.template['root']['block-border']:
				style += self.TAB + "padding: {};\n".format(
					self.template['root']['block-border']['internal-spacing'])
			style += "}\n\n"
		return style

	def generate_html(self, json_obj, parent, gparent, mparent):
		"""generate html output from the JSON object based on a JSOV template"""
		html = ""
		if isinstance(json_obj, dict):
			for key in json_obj:
				if isinstance(json_obj[key], dict):
					if parent == "root":
						html += '<div class="jsov_div {}">'.format(key)
					else:
						html += '<div class="jsov_div block__border" id="{}__{}">'.format(parent, key)
					# check if this is a title
					if parent != "root":
						html += '<table class="jsov_table">'
						if "link" in self.template['root']['children'][parent]['title']:
							link = self.template['root']['children'][parent]['title']['link']
							link = link.replace("{this}", str(key)).replace("{parent}", str(parent))
							html += ('<tr class="jsov_tr"><td colspan="2" class="{parent}_title" align="center">' +
								'<div class="jsov_linkbox"><a href="{link}">{key}</a></div></td></tr>').format(
								link=link, parent=parent, key=key)
						else:
							html += ('<tr class="jsov_tr"><td colspan="2" class="{}_title" ' +
								'align="center">{}</td></tr>').format(parent, key)
						# parse images in object keys in direct children
						if "image-url" in self.template['root']['children'][parent]:
							width = Utils.DEFAULT_IMAGE_WIDTH
							height = Utils.DEFAULT_IMAGE_HEIGHT
							if "image-width" in self.template['root']['children'][parent]:
								image_source = self.template['root']['children'][parent]['image-url']
								image_source = image_source.replace("{this}", str(key)).replace("{parent}", str(parent))
								width = str(self.template['root']['children'][parent]['image-width'])
							if "image-height" in self.template['root']['children'][parent]:
								height = str(self.template['root']['children'][parent]['image-height'])
							html += ('<tr class="jsov_tr"><td colspan="2" align="center">' +
								'<img src="{}" width="{}" height="{}"/></td></tr>').format(image_source, width, height)
					else:
						gparent = key
					html += str(self.generate_html(json_obj[key], key, gparent, parent))
					if parent != "root":
						html += '</table>'
					html += '</div>'
					# parse for cascading style
					if "cascading" in self.template['root']:
						if self.template['root']['cascading'] == "vertical":
							html += "<br/>"
				else:
					html += str(self.generate_html(json_obj[key], key, gparent, parent))
			return html
		else:
			if not gparent:
				key2 = parent
			else:
				key2 = gparent + "__" + parent
			# parse values that are of resource type: image
			if "resource" in self.template['root']['children'][gparent]['children'][parent]:
				if self.template['root']['children'][gparent]['children'][parent]['resource'] == 'image':
					json_obj = '<img src="' + json_obj + '"/>'
			# parse keys that are images, in grandchildren
			if "image-url" in self.template['root']['children'][gparent]['children'][parent]:
				image_source = self.template['root']['children'][gparent]['children'][parent]['image-url']
				image_source = image_source.replace("{this}", parent).replace("{grandparent}", gparent)
				if "image-width" in self.template['root']['children'][gparent]['children'][parent]:
					width = self.template['root']['children'][gparent]['children'][parent]['image-width']
				else:
					width = str(int(Utils.DEFAULT_IMAGE_WIDTH) // 2)
				if "image-height" in self.template['root']['children'][gparent]['children'][parent]:
					height = self.template['root']['children'][gparent]['children'][parent]['image-height']
				else:
					height = str(int(Utils.DEFAULT_IMAGE_HEIGHT) // 2)
				parent2 = '<img src="{}" width="{}" height="{}" alt="{}"/>'.format(image_source, width, height, parent)
			else:
				parent2 = parent + ": "
			# parse links in grandchildren (the whole row will become a link)
			if "link" in self.template['root']['children'][gparent]['children'][parent]:
				link = self.template['root']['children'][gparent]['children'][parent]['link']
				link = link.replace("{this}", str(parent)).replace("{parent}", str(mparent)).replace("{grandparent}", str(gparent))
				element_html = ('<tr class="jsov_tr {key2}"><td class="jsov_td"><div class="jsov_linkbox"><a href="{link}">{parent2}</a></div>' +
					'</td><td class="jsov_td"><div class="jsov_linkbox"><a href="{link}">{json_obj}</a></div></td></tr>').format(
					key2=key2, parent2=parent2, json_obj=json_obj, link=link)
			else:
				element_html = '<tr class="jsov_tr {key2}"><td class="jsov_td">{parent2}</td><td class="jsov_td">{json_obj}</td></tr>'.format(
				key2=key2, parent2=parent2, json_obj=json_obj)
			return element_html

	def generate_htmlcss(self, custom, output_html=None, output_css=None):
		"""call functions that generate html and css outputs"""
		if custom:
			html_out = self.parse_custom_template(self.custom_template, self.input)
			if output_html:
				if isinstance(output_html, list):
					output_html = output_html[0]
				with open(Utils.full_path(output_html), "w") as fp:
					fp.write(Utils.add_eol(html_out))
			return html_out
		else:
			html_out = Utils.add_eol(self.generate_html(self.input, "root", "", ""))
			css_out = self.generate_default_css() + self.generate_css(self.template, "root", "")
			if output_html:
				if isinstance(output_html, list):
					output_html = output_html[0]
				with open(Utils.full_path(output_html), "w") as fp:
					fp.write(html_out)
			if output_css:
				if isinstance(output_css, list):
					output_css = output_css[0]
				with open(Utils.full_path(output_css), "w") as fp:
					fp.write(css_out)
			return html_out, css_out
