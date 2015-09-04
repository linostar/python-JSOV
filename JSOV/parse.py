import re

class Parse:
	"""class for parsing templates"""

	@staticmethod
	def parse_custom_template(text, json_obj):
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
				html = html.replace("{{line" + str(j) + "}}", Parse.parse_for("\n".join(lines[for_starts[j]+1:for_ends[j]]),
					json_obj, for_variables[j], root, int(for_variables[j][-1])))
		html = html.replace("{root}", root)
		return html

	@staticmethod
	def parse_for(block, json_obj, variable, root, depth=1):
		if depth == 1:
			if isinstance(json_obj[root], dict):
				children = list(json_obj[root].keys())
				return children
		elif depth > 1:
			grandchildren = []
			if isinstance(json_obj[root], dict):
				children = list(json_obj[root].keys())
				for child in children:
					grandchildren.extend(Parse.parse_for(json_obj[root], variable, child, depth-1))
				return grandchildren
