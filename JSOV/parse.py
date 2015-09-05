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
		parent = ""
		for line in lines:
			line = line.strip()
			if line.startswith("{{for ") and line.endswith("}}"):
				for_starts.append(i)
				var_end = line.find("}}")
				for_variables.append(line[5:var_end].strip())
				parent_start = line.find("{{", var_end)
				if parent_start != -1:
					parent = line[parent_start+9:-2]
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
				loop_block = "\n".join(lines[for_starts[j]+1:for_ends[j]])
				if for_variables[j].isdigit():
					html += Parse.repeat_block(loop_block, int(for_variables[j]))
				else:
					child_depth = int(for_variables[j][-1])
					replacement = Parse.repeat_block(loop_block, json_obj, for_variables[j],
						root, child_depth, parent)
					html = html.replace("{{line" + str(j) + "}}", replacement)
		html = html.replace("{root}", root)
		return html

	@staticmethod
	def repeat_block(block, json_obj, variable, root, depth=1, parent=None):
		new_block = ""
		if variable.isdigit():
			count = int(variable)
			for i in range(len(count)):
				new_block += block + "\n"
			return new_block
		if depth >= 1:
			for key in json_obj[root]:
				next_variable = variable[:-1] + str(depth+1)
				new_block += block.replace("{" + variable + "}", str(key)).replace(
					"{{for " + next_variable + "}}", "{{for " + next_variable + "}}{{parent:" +
					str(key) + "}}") + "\n"
			return new_block
		elif depth < 1:
			pass
