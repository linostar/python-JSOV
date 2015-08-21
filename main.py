#!/usr/bin/env python3

import sys
import argparse

from JSOV import generator


def main():
	parser = argparse.ArgumentParser(description='Generate a visual HTML/CSS output from a JSON file based on a JSOV template')
	parser.add_argument('-t', '--template', nargs=1, required=True, help='the JSOV template file')
	parser.add_argument('--no-output', action='store_true', help='do not write to any output files')
	parser.add_argument('--html-output', nargs=1, default='output.html', help='HTML output filename')
	parser.add_argument('--css-output', nargs=1, default='style.css', help='CSS output filename')
	parser.add_argument('-f', '--format', nargs=1, default='html', help='the visual format for the output (HTML by default)')
	parser.add_argument('--custom', action='store_true', help='allows using --html-template and --css-template')
	parser.add_argument('--html-template', nargs=1, help='uses a user-made custom html template instead of the built-in ones')
	parser.add_argument('--css-template', nargs=1, help='uses a user-made custom css template instead of the built-in ones')
	parser.add_argument('inputfile', help='input JSON file')
	check_args(parser.parse_args())
	
def check_args(args):
	if args.custom and args.html_template and args.css_template:
		pass
	elif args.custom:
		print("Option '--custom' can only be used along with '--html-template' and '--css-template'")
	else:
		visualizer = generator.Generator(args.inputfile, args.template)
		if args.no_output:
			print(visualizer.generate_htmlcss())
		else:
			visualizer.generate_htmlcss(args.html_output, args.css_output)

if __name__ == "__main__":
	main()
	sys.exit(0)
