#!/usr/bin/env python3

"""
Handles chord regex substitution and LaTeX processing/output
"""

import os
import re
import sys

import musiccharts.data_definitions as vars
from pylatex import Command, Document, Section, Subsection, UnsafeCommand
from pylatex.basic import NewLine
from pylatex.utils import NoEscape, italic, verbatim


def validate_keys(keys):
    """
    Input a list comma-separated list of keys, fail if invalid keys present

    Args:
        keys: (list of string) e.g. ['A','B','C','NNS']
    """
    bad_keys = []
    for key in keys:
        if key not in list(vars.CHORDS.keys()):
            bad_keys.append(key)
    if len(bad_keys) > 0:
        print(f"\nError - invalid keys found: {','.join(bad_keys)}\n")
        sys.exit(1)


def format_line(line, line_num, key, debug=False):
    """
    Input a line of text and process any of the following:
      - NNS chord notation. symbols get superscripted, plus whitespace adjustment
      - Title, which must be wrapped in "Title{<title text>}"
      - Section labels (Intro, Verse, Chorus, etc)

    Args:
        line: single line of text containing mixed lyrics, labels, chords
        line_num: used only for outputting chord syntax errors
        key: which key to transpose into
        debug: enable debug mode to print text lines pre/post changes

    Returns:
        string: formatted line of text
    """
    if debug:
        print(f"PRE: {line}")

    # Format intro in the title line
    intro_matches = vars.INTRO_REGEX.findall(line)
    for item in intro_matches:
        line = line.replace(item, r"\hfill{\textbf{" + item + "}}")

    # Format title
    title_matches = vars.TITLE_REGEX.findall(line)
    if len(title_matches) > 0:
        line = (
            r"\underline{\bigtitle{" + title_matches[0][1] + "}}" + title_matches[0][3]
        )

    # Add bold for verse/chorus labels
    label_matches = vars.LABEL_REGEX.findall(line)
    for item in label_matches:
        line = line.replace(item, r"\textbf{" + item + "}")

    # Regex searches for chord regex
    chord_matches = vars.CHORD_REGEX1.findall(line.replace("(", "").replace(")", ""))
    chords = []
    chord_errors = []
    for item in chord_matches:
        original_chord = ""
        edited_chord = ""
        item = list(item)
        remove_full_space = 0
        remove_partial_space = 0
        for i in range(0, 5):
            original_chord += item[i]
            # For NNS, pre-chord name/number accidentals (#/b) get superscripted, left-padded
            # For regular keys, convert the provided NNS [b|#][0-7] to [A-G][b|#], no superscript
            if i == 1:
                if key == "NNS":
                    if item[i] not in ["", " ", "\n"]:
                        spacing = len(item[i].replace("△", "")) * " "
                        edited_chord += r"\ts{{\thin" + spacing + "}" + item[i] + "}"
                else:
                    translation = vars.CHORDS[key][f"{item[1]}{item[2]}"]
                    if len(translation) > 1:
                        remove_full_space += 1
                    edited_chord += translation
            elif i == 2:
                if key == "NNS":
                    translation = vars.CHORDS[key][item[i]]
                    if len(translation) > 1:
                        remove_full_space += 1
                    edited_chord += translation
            # Post-chord name/number symbols/digits get superscripted, right-padded
            elif i == 3:
                if item[i] not in ["", " ", "\n"]:
                    # Check for invalid chord inversions
                    # Example: 1/3, 1sus/3 are a valid chord3, 1/34 1/sus3 are not
                    if "/" in item[i]:
                        splits = item[i].split("/")
                        if (
                            len(vars.CHORD_REGEX2.findall(f"/{splits[1]}")) == 0
                            or len(vars.CHORD_REGEX3.findall(f"/{splits[1]}")) == 1
                            or item[i].count("/") > 1
                        ):
                            chord_errors.append(
                                {"chord": "".join(item), "line_num": line_num}
                            )
                            continue
                        translation = vars.CHORDS[key][splits[1]]
                        if len(translation) > len(splits[1]):
                            remove_full_space += 1
                        item[i] = f"{splits[0]}/{translation}"
                    count = len(item[i].replace("△", "")) - remove_partial_space
                    spacing = count * " "
                    edited_chord += r"\ts{" + item[i] + r"{\thin" + spacing + "}}"
            else:
                edited_chord += item[i]
        if remove_full_space == 1:
            original_chord = f"{original_chord} "
        if (original_chord, edited_chord) not in chords:
            chords.append((original_chord, edited_chord))

    # Replace raw chords with LaTeX-formatted chords
    for chord in chords:
        line = f"{line} ".replace(chord[0], chord[1]).rstrip()

    if debug:
        print(f"POST: {line}")

    return {"edits": NoEscape(line), "errors": chord_errors}


def process_document(dest_filename, path, file_contents, font_size, keep_tex):
    """
    Create TEX document based on file input and given parameters.

    Args:
        dest_filename: name of the file without extension
        path: destination folder path
        file_contents: plain text input from file
        base_font_size: user-provided font size or default
        keep_tex: generate TEX file in addition to PDF
    """
    print(f"FILENAME:  {dest_filename}.pdf")
    print(f"FONT SIZE: {font_size}")
    # Document type
    doc = Document(
        default_filepath=dest_filename,
        documentclass="extarticle",
        document_options=[f"{vars.BASE_FONT_SIZE}pt"],
        fontenc=None,
        indent=False,
        inputenc="utf8",
        lmodern=False,
        page_numbers=False,
        textcomp=False,
    )
    font_scale_ratio = round(font_size / vars.BASE_FONT_SIZE, 2)

    # PyLatex automatically adds unneeded additional line break chars
    # Content separator has to be redefined to avoid breaking some commands
    doc.content_separator = "\n"

    # 'fontspec' package required for font scaling
    doc.preamble.append(Command(command="usepackage", arguments="fontspec,xfp"))
    # Paragraph indent settings
    doc.preamble.append(Command(command="usepackage", arguments="parskip"))
    # Font selection
    doc.preamble.append(Command(command="usepackage", arguments="courier"))
    # 'fancyvrb' allows use of monospace font with superscripts
    doc.preamble.append(Command(command="usepackage", arguments="fancyvrb"))
    # Font selection
    doc.preamble.append(Command(command="usepackage", arguments="fvextra"))
    # Use geometry to set margins
    doc.preamble.append(
        Command(
            command="usepackage",
            arguments="geometry",
            options=f"margin={vars.ALL_MARGINS}in",
        )
    )
    # 'newunicodechar' package required to map specific chars: △, ø
    doc.preamble.append(
        Command(
            command="usepackage",
            arguments="newunicodechar",
            options="verbose",
        )
    )
    # Set the monospace font
    doc.preamble.append(NoEscape(r"\setmonofont{Courier New}"))

    # Setup for font scaling
    doc.preamble.append(NoEscape(r"\makeatletter"))
    doc.preamble.append(NoEscape(r"\newcommand{\scalefont}[1]{"))
    doc.preamble.append(NoEscape(r"    \edef\scale@fontsize{\fpeval{#1*\f@size}}"))
    doc.preamble.append(
        NoEscape(r"    \edef\scale@fontbaselineskip{\fpeval{1.2*\scale@fontsize}}")
    )
    doc.preamble.append(
        NoEscape(r"    \fontsize{\scale@fontsize}{\scale@fontbaselineskip}\selectfont}")
    )
    doc.preamble.append(NoEscape(r"\makeatother"))

    # Redefine font size for superscript
    doc.preamble.append(
        NoEscape(
            r"\renewcommand{\textsuperscript}[1]{\raisebox{"
            + str(vars.SUPERSCRIPT_RAISE)
            + r"ex}{\scalefont{"
            + str(vars.SUPERSCRIPT_SCALER)
            + r"}#1}}"
        )
    )

    # Set superscripts to use monospace font as default font
    doc.preamble.append(NoEscape(r"\renewcommand{\familydefault}{\ttdefault}"))

    # Set short custom command for superscript
    doc.preamble.append(NoEscape(r"\newcommand{\ts}{\textsuperscript}"))

    # Choose font scaling for odd vs even font size
    doc.preamble.append(
        NoEscape(
            r"\newfontfamily{\thin}[Scale="
            + str(vars.SUPERSCRIPT_FILLER_SCALER)
            + r"]{Courier New}"
        )
    )

    # Define font/size for title
    title_font_cmd = [
        r"\newfontfamily\bigtitle[SizeFeatures={Size=",
        str(vars.TITLE_SIZE) + "}]{",
        str(vars.TITLE_FONT) + "}",
    ]
    doc.preamble.append(NoEscape("".join(title_font_cmd)))

    # Define extra unicode chars
    doc.preamble.append(NoEscape(r"\newunicodechar{△}{$\bigtriangleup$}"))
    doc.preamble.append(NoEscape(r"\newunicodechar{ø}{$\o$}"))

    # Use 'Verbatim' for document body to allow use of '\textsuperscript{}'
    doc.append(
        NoEscape(
            r"\begin{Verbatim}[fontsize=\scalefont{"
            + str(font_scale_ratio)
            + r"},commandchars=\\\{\}]"
        )
    )
    for line in file_contents:
        doc.append(line)
    doc.append(NoEscape(r"\end{Verbatim}"))
    doc.generate_pdf(clean_tex=keep_tex, compiler_args=["--xelatex"])
    os.remove(f"{os.getcwd()}/{dest_filename}.xdv")
