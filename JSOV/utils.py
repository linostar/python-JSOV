import os
import re
from collections import OrderedDict

import cssutils


class Utils:
	DEFAULT_IMAGE_WIDTH = "100"
	DEFAULT_IMAGE_HEIGHT = "100"

	children_attributes = {
	"bgcolor": r"^\#[0-9a-f]{1,6}$",
	"fgcolor": r"^\#[0-9a-f]{1,6}$",
	"rounded-corners": r"^\d+.*$",
	"cascading": r"^(vertical|horizontal)$",
	"link": r".+",
	"image-url": r".+",
	"image-width": r"^\d+.*$",
	"image-height": r"^\d+.*$",
	"resource": r"^image$",
	"title": "",
	"default-child": "",
	"children": "",
	"block-border": "",
	}

	@staticmethod
	def lower_keys(dic):
		new_dic = OrderedDict()
		for key, val in dic.items():
			if isinstance(dic[key], dict):
				if str(key).lower() in list(Utils.children_attributes):
					new_dic[str(key).lower()] = Utils.lower_keys(dic[key])
				else:
					new_dic[str(key)] = Utils.lower_keys(dic[key])
			elif isinstance(dic[key], list):
				dic_list = []
				for item in dic[key]:
					dic_list.append(Utils.lower_keys(item))
				if str(key).lower() in list(Utils.children_attributes):
					new_dic[str(key).lower()] = dic_list
				else:
					new_dic[str(key)] = dic_list
			else:
				if str(key).lower() in list(Utils.children_attributes):
					new_dic[str(key).lower()] = val
				else:
					new_dic[str(key)] = val
		return new_dic

	@staticmethod
	def cap_first(string):
		if len(string) > 1:
			return string[0].upper() + string[1:]
		elif len(string):
			return string.upper()
		else:
			return ""

	@staticmethod
	def full_path(path):
		fdir = os.path.dirname(os.path.dirname(__file__))
		return os.path.join(fdir, path)

	@staticmethod
	def add_eol(string):
		new_string = re.sub(r"><", r">\n<", string)
		return new_string + "\n"

	@staticmethod
	def compare_css_outputs(css1, css2):
		css_dicts = [{}, {}]
		i = 0
		for css in (css1, css2):
			sheet = cssutils.parseString(css)
			for rule in sheet:
				selector = rule.selectorText
				style = rule.style.cssText
				style_list = sorted(style.split(";\n"))
				css_dicts[i][selector] = style_list
			i += 1
		return css_dicts[0] == css_dicts[1]
