class Utils:
	@staticmethod
	def lower_keys(dic):
		new_dic = {}
		for key, val in dic.items():
			if isinstance(dic[key], dict):
				new_dic[str(key).lower()] = Utils.lower_keys(dic[key])
			elif isinstance(dic[key], list):
				dic_list = []
				for item in dic[key]:
					dic_list.append(Utils.lower_keys(item))
				new_dic[str(key).lower()] = dic_list
			else:
				new_dic[str(key).lower()] = val
		return new_dic

	@staticmethod
	def cap_first(string):
		if len(string) > 1:
			return string[0].upper() + string[1:]
		elif len(string):
			return string.upper()
		else:
			return ""
