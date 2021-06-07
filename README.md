## musiccharts

Generate music chart PDFs in multiple keys plus Nashville Number System (NNS).  User provides a plain text document in NNS adhering to the formatting standards, output is formatted PDF documents in all keys (default) or only user-requested keys.

### Environment Requirements
* Tested on python3.7, PyLaTeX 1.4.1

### Setup
* Download repo and run `pip3 install .` from the folder.

### CLI Usage & Examples
```
> musiccharts test_lyrics2.txt -k A,Bb,B
> musiccharts test_lyrics2.txt --tex --name "newfile"

> musiccharts
usage: musiccharts [-h] [-k] [-n] [-s] [--tex] [input [input ...]]

Description...

positional arguments:
  input         Input file

optional arguments:
  -h, --help   show this help message and exit
  -k, --key    Desired keys, default is 
  -n, --name   Destination filename
  -s, --size   Available font sizes: [8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13,
               13.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20]
  --tex        Output LaTeX file in addition to PDFs
```

### Design
* Title formatting tag: `Title{Lorem Ipsum}`
* Right-adjusted intro labels: **`Intro:`**, **`Intro/Interlude:`**, **`Intro/Outro:`**
* Section labels: **`Bridge:`**, **`Chorus:`**, **`Interlude:`**, **`Outro:`**, **`Prechorus:`**, **`Tag:`**, **`Verse:`**
* All chords must have at least 2 spaces between them
* Margins (0.25in), superscript scaling (75%), and other parameters are adjustable in `data_definitions.py`

### Chord Symbols
```
Chord regex - (^|\n| )([#b]?)(\d)([0-9susb#+-/oø△Δ]*)( |$|\n)
sus = suspended
-   = minor
-7  = minor 7th
△   = major 7th
ø   = half diminished 7th
o   = full-diminished 7th
+   = augmented
```

### Feedback
* This tool is in alpha with fairly limited testing so far
* Feedback, bug fixes, or improvements are welcomed
* Please submit an Issue via GitHub, drop an email to github@jamesw.us
