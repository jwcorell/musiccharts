#!/usr/bin/env python3

"""
Handles reading in data from a plain-text file.
"""

import os
import sys

import musiccharts.data_definitions as vars


def read_file_contents(filename):
    """
    Read file line by line and return contents.

    Args:
        filename: (str) input file path, either relative or absolute

    Returns:
        list of str: lines from file

    """
    file_contents = []

    # Determine whether to treat filename as relative or absolute
    if not os.path.isfile(filename):
        filename = os.path.join(os.getcwd(), filename)

    # Open file object as read-only
    try:
        file_object = open(filename, "r")
    except FileNotFoundError:
        print(f"File not found: {filename}\nExiting...")
        sys.exit(0)

    # Read file contents line by line
    for line in file_object:
        file_contents.append(line.rstrip())

    # Close out the file
    try:
        file_object.close()
    except Exception:
        pass

    # Return a list of strings
    return file_contents
