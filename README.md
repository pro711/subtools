# Subtools

This is a collection of scripts to manipulate SubRip files (*.srt). You will need to install [pysrt](https://pypi.python.org/pypi/pysrt) to run them.

* submerge
  
  `submerge` is a simple script to merge two srt files into a single file.

  Usage: `python submerge.py sub1.srt sub2.srt`
  
  This will create a file named `merged.srt` in the current directory. Fuzzy matching is used in case the timestamps in two files do not match exactly.
