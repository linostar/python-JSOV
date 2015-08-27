import os
import unittest

from JSOV import generator


class Run_Tests(unittest.TestCase):
	INPUT_JSON = "tests/input/sample.json"
	INPUT_TEMPLATE = "tests/input/template.jsov"
	OUTPUT_HTML = "tests/output/output.html"
	OUTPUT_CSS = "tests/output/style.css"
	GENERATED_DIR = "tests/generated/"
	GENERATED_HTML = GENERATED_DIR + "output.html"
	GENERATED_CSS = GENERATED_DIR + "style.css"

	def test_input_json_exists(self):
		self.assertTrue(os.path.exists(INPUT_JSON))

	def test_input_jsov_exists(self):
		self.assertTrue(os.path.exists(INPUT_TEMPLATE))

	def test_output_html_exists(self):
		self.assertTrue(os.path.exists(OUTPUT_HTML))

	def test_output_css_exists(self):
		self.assertTrue(os.path.exists(OUTPUT_CSS))

	def test_generated_dir_exists(self):
		self.assertTrue(os.path.exists(GENERATED_DIR))


if __name__ == "__main__":
	unittest.main()
