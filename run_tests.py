from JSOV import generator


def run_tests():
	INPUT_JSON = "tests/input/sample.json"
	INPUT_TEMPLATE = "tests/input/template.jsov"
	OUTPUT_HTML = "tests/output/output.html"
	OUTPUT_CSS = "tests/output/style.css"
	GENERATED_HTML = "tests/generated/output.html"
	GENERATED_CSS = "tests/generated/style.css"
	visualizer = generator.Generator(INPUT_JSON, INPUT_TEMPLATE)

if __name__ == "__main__":
	run_tests()
