import sys
import re

class Parse:
	"""class for parsing templates"""

	templated_html = ""

	@staticmethod
	def parse_custom_template(text, json_obj, root):
		"""parse statements and operations in the template"""
		indent = ""
		next_indent = ""
		block = ""
		Parse.templated_html = ""
		num_line = 0
		lines = text.splitlines()
		for line in lines:
			format_arr = []
			num_line += 1
			indent = next_indent
			if line.startswith("{% for ") and line.endswith(" %}"):
				next_indent += "\t"
				for_var = line[6:-2].strip()
				if for_var.isdigit():
					line = "for i{0} in range({1}):".format(str(num_line), for_var)
				else:
					line = Parse.parse_for_statement(for_var)
			elif line == "{% endfor %}":
				next_indent = indent[:-1]
				continue
			elif line.startswith("{% if") and line.endswith(" %}"):
				next_indent += "\t"
				new_line = Parse.parse_if_statement(line)
				if new_line:
					block += indent + new_line + "\n"
					continue
				else:
					print("Error in 'if' statement syntax.")
					sys.exit(1)
			elif line.startswith("{% elif") and line.endswith(" %}"):
				indent = indent[:-1]
				new_line = Parse.parse_if_statement(line)
				if new_line:
					block += indent + new_line + "\n"
					continue
				else:
					print("Error in 'elif' statement syntax.")
					sys.exit(1)
			elif line == "{% else %}":
				indent = indent[:-1]
				line = "else:"
			elif line == "{% endif %}":
				next_indent = indent[:-1]
				continue
			else:
				line = "Parse.templated_html += \"\"\"{}\"\"\"".format(line)
			# substituting variables
			new_line = line
			count = 0
			for matched_var in re.finditer(r"({{ ([^{]+) }})", line):
				tmpl_var, new_var = Parse.parse_variable(matched_var.group(2))
				new_line = new_line.replace(matched_var.group(1),
					"{" + tmpl_var + "}")
				format_arr.append((tmpl_var, new_var))
				count += 1
			format_arr = list(set(format_arr))
			if format_arr:
				new_line += ".format("
				for (k, v) in format_arr:
					new_line += "{}={},".format(k, v)
				new_line += ")"
			block += indent + new_line + "\n"
		exec(block)
		return Parse.templated_html

	@staticmethod
	def parse_if_statement(line):
		"""parse 'if' statements in the template"""
		matched = re.search(r"^{% (if|elif) (root|children\.\d+|children\.\d+.value) (==|!=|>|<|>=|<=) (\d+|\d+\.\d+|\".*\"|\'.*\'|True|False|None) %}$", line)
		if matched:
			tmpl_var, new_var = Parse.parse_variable(matched.group(2))
			parsed_if = matched.group(1) + " " + new_var + " " + matched.group(3) + " " + str(matched.group(4)) + ":"
			return parsed_if
		else:
			print("Syntax error in 'if' statement: {}".format(line))

	@staticmethod
	def parse_for_statement(for_var):
		"""parse 'for' statements in the template"""
		try:
			if not for_var.endswith(".value"):
				child_depth = int(for_var[-1])
				nested_dict = Parse.get_child_value(child_depth-1)
				line = "for children{0} in {1}:".format(
					str(child_depth), nested_dict)
				return line
			else:
				pass
		except Exception:
			print("Error: You can only use 'children.x' in 'for' statements where x is a number.")
			sys.exit(1)

	@staticmethod
	def get_child_value(depth):
		"""return the value of a child"""
		child_val = "json_obj[root]"
		for k in range(1, depth+1):
			child_val += "[children{}]".format(k)
		return child_val

	@staticmethod
	def parse_variable(variable):
		"""parse variables in the template"""
		tmpl_var = variable
		if variable == "root":
			return tmpl_var, "list(json_obj.keys())[0]"
		matched = re.search(r"^children\.(\d+)$", variable)
		if matched:
			return "children" + str(matched.group(1)), "children" + str(matched.group(1))
		matched = re.search(r"^children\.(\d+)\.value", variable)
		if matched:
			return "children{}val".format(matched.group(1)), Parse.get_child_value(int(matched.group(1)))
		# check for hybrid combinations recursively
		new_variable = variable
		for matched in re.finditer(r"(children\.\d+)", variable):
			tmpl_var2, new_var2 = Parse.parse_variable(matched.group(1))
			new_variable = new_variable.replace(matched.group(1), new_var2)
		if new_variable != variable:
			return Parse.parse_variable(new_variable)
		# check for non-standard variables
		matched = re.search(r"^([a-zA-Z0-9_-]+)(\.[a-zA-Z0-9_])*\.value$", variable)
		if matched:
			variable = variable[:-6]
			new_variable = "json_obj"
			for key in variable.split("."):
				new_variable += "['{}']".format(key)
			return tmpl_var, new_variable
		return tmpl_var, variable
