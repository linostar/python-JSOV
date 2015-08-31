#!/usr/bin/env python3

import sys
import argparse

from JSOV import generator


def main():
	parser = argparse.ArgumentParser(description='Generate a visual HTML/CSS output from a JSON file based on a JSOV template')
	parser.add_argument('-t', '--template', nargs=1, required=True, help='the JSOV template file, or a custom HTML template in case of --custom')
	parser.add_argument('--no-output', action='store_true', help='do not write to any output files')
	parser.add_argument('--html-output', nargs=1, help='HTML output filename')
	parser.add_argument('--css-output', nargs=1, help='CSS output filename')
	parser.add_argument('-f', '--format', nargs=1, default='html', help='the visual format for the output (HTML by default)')
	parser.add_argument('--custom', action='store_true', help='uses a user-made custom html template instead of a JSOV one')
	parser.add_argument('inputfile', help='input JSON file')
	check_args(parser.parse_args())
	
def check_args(args):
	if args.custom:
		if args.no_output and (args.html_output or args.css_output):
			print("Error: Option '--no-output' does not allow '--html-output' or '--css-output'.")
			sys.exit(1)
		# to be changed
		visualizer = generator.Generator(args.inputfile, args.template)
		html = visualizer.read_html_template(args.template)
		if not args.no_output:
			html_out = args.html_output if args.html_output else ["output.html"]
			css_out = args.css_output if args.css_output else ["style.css"]
			visualizer.generate_htmlcss(html_out, css_out)
		else:
			print(visualizer.generate_htmlcss())
	else:
		if args.no_output and not args.html_output and not args.css_output:
			visualizer = generator.Generator(args.inputfile, args.template)
			print(visualizer.generate_htmlcss())
		elif args.no_output:
			print("Error: Option '--no-output' does not allow '--html-output' or '--css-output'.")
			sys.exit(1)
		else:
			visualizer = generator.Generator(args.inputfile, args.template)
			html_out = args.html_output if args.html_output else ["output.html"]
			css_out = args.css_output if args.css_output else ["style.css"]
			visualizer.generate_htmlcss(html_out, css_out)

if __name__ == "__main__":
	main()
	sys.exit(0)
