#!/usr/bin/env python3

import sys
import argparse

def main():
	parser = argparse.ArgumentParser(description='Generate a visual HTML/CSS output from a JSON file based on a JSOV template')
	parser.add_argument('-t', '--template', nargs=1, type=file)
	parser.add_argument('--no-output', nargs=0, action='store_true')
	parser.add_argument('--html-output', nargs=1, type=file)
	parser.add_argument('--css-output', nargs=1, type=file)


if __name__ == "__main__":
	pass
