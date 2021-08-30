#!/usr/bin/env python3

"""
Take in a music chart in raw text form.
Output 13 PDF's:
- One in the Nashville Number System
- One in each of the lettered keys

Dependencies:
- pylatex package
"""

import argparse
import os
import re
import signal
import sys

from musiccharts import __version__
from musiccharts import data_definitions as vars
from musiccharts.data_processing import (format_line, process_document,
                                         validate_keys)
from musiccharts.read_file import read_file_contents


def main():
    """Execute main function."""

    # ArgParse setup
    formatter_class = argparse.RawDescriptionHelpFormatter
    description = "Description..."
    epilog = f"Version: {__version__}\n "
    parser = argparse.ArgumentParser(
        formatter_class=formatter_class, description=description, epilog=epilog
    )
    parser.add_argument("input", nargs="*", help="Input file")
    parser.add_argument(
        "-k",
        "--key",
        default="NNS,Ab,A,Bb,B,C,Db,D,Eb,E,F,Gb,G",
        dest="keys",
        help='Desired keys, default is "NNS,Ab,A,Bb,B,C,Db,D,Eb,E,F,Gb,G"',
        metavar="",
        type=str,
    )
    parser.add_argument(
        "-n",
        "--name",
        dest="dest_filename",
        help="Destination filename",
        metavar="",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--size",
        default=vars.BASE_FONT_SIZE,
        choices=vars.ALL_FONT_SIZES,
        dest="font_size",
        help=f"Available font sizes: {vars.ALL_FONT_SIZES}",
        metavar="",
        type=float,
    )
    parser.add_argument(
        "--tex",
        dest="keep_tex",
        action="store_false",
        help="Output LaTeX file in addition to PDFs",
    )
    args = parser.parse_args()
    if len(args.input) > 1:
        print("\nError: more than one source file provided for processing!\n")
        sys.exit(1)
    elif len(args.input) < 1:
        parser.print_help()
        sys.exit(1)
    else:
        src_filename = args.input[0]

    # Process provided filename
    file_contents = read_file_contents(filename=src_filename)

    if args.dest_filename:
        dest_filename = args.dest_filename
    else:
        dest_filename = re.sub(r"(.*/)*([^.]*)(\..*)", r"\2", src_filename)

    # Save and validate user-provided keys
    keys = args.keys.split(",")
    validate_keys(keys)

    # Process formatting for each individual line of text
    for key in keys:
        formatted_lines = []
        chord_errors = []
        i = 0
        next_line_after_intro = False
        for line in file_contents:
            results = format_line(
                line=line,
                line_num=i,
                key=key,
                next_line_after_intro=next_line_after_intro,
                debug=False,
            )
            next_line_after_intro = results.get("next_line_after_intro")
            formatted_lines.append(results.get("edits"))
            chord_errors.extend(results.get("errors"))
            i += 1

        # Display specific invalid chord errors
        if len(chord_errors) > 0:
            print("\nError: invalid chord syntax found")
            print("----------------------------------")
            for match in chord_errors:
                print(
                    f"Line {str(match.get('line_num')).ljust(3)}: {match.get('chord')}"
                )
            print("")
            sys.exit(1)

        # Create the document
        process_document(
            dest_filename=f"{dest_filename} ({key})",
            path=os.getcwd(),
            file_contents=formatted_lines,
            font_size=args.font_size,
            keep_tex=args.keep_tex,
        )


# Call main function
if __name__ == "__main__":
    main()
