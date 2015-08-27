import os
import unittest

from JSOV import generator
from JSOV.utils import Utils


class Run_Tests(unittest.TestCase):
	INPUT_JSON = "tests/input/sample.json"
	INPUT_TEMPLATE = "tests/input/template.jsov"
	OUTPUT_HTML = "tests/output/output.html"
	OUTPUT_CSS = "tests/output/style.css"
	GENERATED_DIR = "tests/generated/"
	GENERATED_HTML = "tests/generated/output.html"
	GENERATED_CSS = "tests/generated/style.css"

	def create_instance(self):
		self.visualizer = generator.Generator(self.INPUT_JSON, self.INPUT_TEMPLATE)

	def generate_nocustom(self):
		self.visualizer.generate_htmlcss(self.GENERATED_HTML, self.GENERATED_CSS)

	def test_input_json_exists(self):
		self.assertTrue(os.path.exists(self.INPUT_JSON))

	def test_input_jsov_exists(self):
		self.assertTrue(os.path.exists(self.INPUT_TEMPLATE))

	def test_output_html_exists(self):
		self.assertTrue(os.path.exists(self.OUTPUT_HTML))

	def test_output_css_exists(self):
		self.assertTrue(os.path.exists(self.OUTPUT_CSS))

	def test_generated_dir_exists(self):
		self.assertTrue(os.path.exists(self.GENERATED_DIR))

	def test_nocustom_match_html(self):
		with open(self.OUTPUT_HTML, "r") as f1:
			out_html = f1.read()
		with open(self.GENERATED_HTML, "r") as f2:
			gen_html = f2.read()
		self.assertTrue(out_html == gen_html)


if __name__ == "__main__":
	unittest.main()
