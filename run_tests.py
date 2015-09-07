#!/usr/bin/env python3

import os
import unittest

from JSOV import generator
from JSOV.utils import Utils


class Run_Tests(unittest.TestCase):
	INPUT_JSON = "tests/input/sample.json"
	INPUT_TEMPLATE = "tests/input/template.jsov"
	INPUT_CUSTOM = "tests/input/custom_template.html"
	OUTPUT_HTML = "tests/output/output.html"
	OUTPUT_CSS = "tests/output/style.css"
	OUTPUT_CUSTOM = "tests/output/custom_output.html"
	GENERATED_DIR = "tests/generated/"
	GENERATED_HTML = "tests/generated/output.html"
	GENERATED_CSS = "tests/generated/style.css"
	GENERATED_CUSTOM = "tests/generated/custom_output.html"

	def create_instance_nocustom(self):
		self.visualizer = generator.Generator(self.INPUT_JSON, self.INPUT_TEMPLATE, False)

	def create_instance_custom(self):
		self.visualizer = generator.Generator(self.INPUT_JSON, self.INPUT_CUSTOM, True)

	def generate_nocustom(self):
		[html, css] = self.visualizer.generate_htmlcss(False, self.GENERATED_HTML, self.GENERATED_CSS)
		with open(self.OUTPUT_HTML, "w") as f1:
			f1.write(html)
		with open(self.OUTPUT_CSS, "w") as f1:
			f1.write(css)

	def generate_custom(self):
		html = self.visualizer.generate_htmlcss(True, self.GENERATED_CUSTOM)
		with open(self.OUTPUT_CUSTOM, "w") as f1:
			f1.write(html)

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
		self.create_instance_nocustom()
		self.generate_nocustom()
		with open(self.OUTPUT_HTML, "r") as f1:
			out_html = f1.read()
		with open(self.GENERATED_HTML, "r") as f2:
			gen_html = f2.read()
		self.assertTrue(out_html == gen_html)

	def test_nocustom_match_css(self):
		self.create_instance_nocustom()
		self.generate_nocustom()
		with open(self.OUTPUT_CSS, "r") as f1:
			out_css = f1.read()
		with open(self.GENERATED_CSS, "r") as f2:
			gen_css = f2.read()
		self.assertTrue(Utils.compare_css_outputs(out_css, gen_css))

	def test_custom_match_html(self):
		self.create_instance_custom()
		self.generate_custom()
		with open(self.OUTPUT_CUSTOM, "r") as f1:
			out_html = f1.read()
		with open(self.GENERATED_CUSTOM, "r") as f2:
			gen_html = f2.read()
		self.assertTrue(out_html == gen_html)

if __name__ == "__main__":
	unittest.main()
