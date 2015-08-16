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
	parser.add_argument('inputfile', help='input JSON file')
	args = parser.parse_args()
	visualizer = generator.Generator(args.inputfile, args.template)
	print(visualizer.generate_html())
	

if __name__ == "__main__":
	main()
	sys.exit(0)
