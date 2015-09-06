import re

class Parse:
	"""class for parsing templates"""

	templated_html = ""

	@staticmethod
	def parse_custom_template(text, json_obj, root):
		indent = ""
		next_indent = ""
		block = ""
		Parse.templated_html = "b"
		num_line = 0
		lines = text.splitlines()
		for line in lines:
			num_line += 1
			indent = next_indent
			if line.startswith("{{for "):
				next_indent += "\t"
				for_var = line[5:-2].strip()
				if for_var.isdigit():
					line = "for i{0} in range({1}):".format(str(num_line), for_var)
				else:
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
						else:
							pass
					except Exception:
						print("Error: You can only use 'children.x' or 'children.x.value' where x is a number.")
			elif line == "{{endfor}}":
				next_indent = indent[:-1]
				continue
			elif line.startswith("{{if") and line.endswith("}}"):
				pass
			elif line == "{{endif}}":
				pass
			else:
				line = "Parse.templated_html += \"\"\"{}\"\"\"".format(line)
			format_arr = []
			matched_var = re.search(r"({children\.(\d+)})", line)
			if matched_var:
				child_depth = matched_var.group(2)
				line = line.replace(matched_var.group(1), "{children" + str(child_depth) + "}")
				#line += ".format({0}={0})".format("children" + str(child_depth))
				format_arr.append(("children" + str(child_depth), "children" + str(child_depth)))
			matched_var = re.search(r"({children\.(\d+)\.value})", line)
			if matched_var:
				child_depth = int(matched_var.group(2))
				child_val = "json_obj[root]"
				for k in range(1, child_depth+1):
					child_val += "[children{}]".format(k)
				line = line.replace(matched_var.group(1), "{children" + str(child_depth) + "val}")
				#line += ".format({0}={1})".format("children" + str(child_depth) + "val", child_val)
				format_arr.append(("children" + str(child_depth) + "val", child_val))
			if len(format_arr) == 1:
				line += ".format({}={})".format(format_arr[0][0], format_arr[0][1])
			elif len(format_arr) == 2:
				line += ".format({}={}, {}={})".format(format_arr[0][0], format_arr[0][1],
					format_arr[1][0], format_arr[1][1])
			line = line.replace("{root}", root)
			block += indent + line + "\n"
		exec(block)
		return Parse.templated_html
