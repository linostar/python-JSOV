# python-JSOV
Python generator for JSOV (Javascript Object Visualization).

**JSOV** is a template system used for visualizing JSON objects.

**python-JSOV** is an implementation of JSOV-based visual generator in Python3.

This generator takes object(s) from a JSON file, and generate a visual representation of them (the output is in HTML/CSS for example), based on a JSOV template. the JSOV template is responsible for how the object(s), along with their different children and parameters, will be graphically represented.

There are two ways to generate visual outputs, of JSON object(s) using python-JSOV:

1. using JSOV templates that are built-in, flexible and easy to use;

2. using user-made custom templates, in case the flexibility of the JSOV templates in not enough.


## Requirements

Project requirements can be installed by running `pip3 install -r requirements.txt`

## Examples of usage

### JSOV templates

Syntax: `./main.py -t template.jsov file.json`

### User-made custom templates

Syntax: `./main.py --custom -t template.html file.json`
