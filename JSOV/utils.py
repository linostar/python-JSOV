class Utils:
	@staticmethod
	def lower_keys(dic):
		new_dic = {}
		for key, val in dic.items():
			if isinstance(dic[key], dict):
				new_dic[str(key).lower()] = Utils.lower_keys(dic[key])
			else:
				new_dic[str(key).lower()] = val
		return new_dic

	@staticmethod
	def cap_first(string):
		if len(string) > 1:
			return string[0].upper() + string[1:]
		elif len(string):
			return string.upper()
