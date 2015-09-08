import sys
import re

class Parse:
	"""class for parsing templates"""

	templated_html = ""

	@staticmethod
	def parse_custom_template(text, json_obj, root):
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
				old_variable, variable, child_depth, new_line = Parse.parse_if_statement(line)
				if new_line:
					if old_variable.endswith(".value"):
						child_val = "json_obj[root]"
						for k in range(1, child_depth+1):
							child_val += "[children{}]".format(k)
						line = new_line.replace(old_variable, child_val)
					else:
						line = new_line.replace(old_variable, variable).format("{0}={0}".format(variable))
					block += indent + line + "\n"
					continue
				else:
					print("Error in 'if' statement syntax.")
					sys.exit(1)
			elif line.startswith("{% elif") and line.endswith(" %}"):
				indent = indent[:-1]
				old_variable, variable, child_depth, new_line = Parse.parse_if_statement(line)
				if new_line:
					if old_variable.endswith(".value"):
						child_val = "json_obj[root]"
						for k in range(1, child_depth+1):
							child_val += "[children{}]".format(k)
						line = new_line.replace(old_variable, child_val)
					else:
						line = new_line.replace(old_variable, variable).format("{0}={0}".format(variable))
					block += indent + line + "\n"
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
			matched_var = re.search(r"({{\schildren\.(\d+) }})", line)
			if matched_var:
				child_depth = matched_var.group(2)
				line = line.replace(matched_var.group(1), "{children" + str(child_depth) + "}")
				format_arr.append(("children" + str(child_depth), "children" + str(child_depth)))
			matched_var = re.search(r"({{ children\.(\d+)\.value }})", line)
			if matched_var:
				child_depth = int(matched_var.group(2))
				child_val = "json_obj[root]"
				for k in range(1, child_depth+1):
					child_val += "[children{}]".format(k)
				line = line.replace(matched_var.group(1), "{children" + str(child_depth) + "val}")
				format_arr.append(("children" + str(child_depth) + "val", child_val))
			if len(format_arr) == 1:
				line += ".format({}={})".format(format_arr[0][0], format_arr[0][1])
			elif len(format_arr) == 2:
				line += ".format({}={}, {}={})".format(format_arr[0][0], format_arr[0][1],
					format_arr[1][0], format_arr[1][1])
			line = line.replace("{{ root }}", root)
			block += indent + line + "\n"
		exec(block)
		return Parse.templated_html

	@staticmethod
	def parse_if_statement(line):
		matched = re.search(r"^{% (if|elif) (root|children\.\d+|children\.\d+.value) (==|!=|>|<|>=|<=) (\d+|\d+\.\d+|\".*\"|\'.*\'|True|False|None) %}$", line)
		if matched:
			parsed_if = matched.group(1) + " " + matched.group(2) + " " + matched.group(3) + " " + str(matched.group(4)) + ":"
			if matched.group(2).endswith(".value"):
				child_depth = re.search(r"(\d+)", matched.group(2))
				variable = "children" + str(child_depth.group(1)) + "val"
			elif matched.group(2).startswith("children."):
				child_depth = re.search(r"(\d+)", matched.group(2))
				variable = "children" + str(child_depth.group(1))
			else:
				variable = "root"
				child_depth = 0
			return matched.group(2), variable, int(child_depth.group(1)), parsed_if

	@staticmethod
	def parse_for_statement(for_var):
		try:
			if not for_var.endswith(".value"):
				child_depth = int(for_var[-1])
				if child_depth == 1:
					line = "for children1 in json_obj[root]:"
				else:
					nested_dict = "json_obj[root]"
					for k in range(1, child_depth):
						nested_dict += "[children{}]".format(k)
					line = "for children{0} in {1}:".format(
						str(child_depth), nested_dict)
				return line
			else:
				pass
		except Exception:
			print("Error: You can only use 'children.x' or 'children.x.value' where x is a number.")
			sys.exit(1)
