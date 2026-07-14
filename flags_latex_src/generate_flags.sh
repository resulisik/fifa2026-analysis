#!/bin/bash
# Regenerates flags_png/*.png from these LaTeX sources.
# Requires: texlive (with the `worldflags` package - CTAN, Wilhelm Haager),
# pdflatex, and pdftoppm (poppler-utils). No internet connection needed.
set -e
mkdir -p ../flags_png
for f in flag_*.tex; do
    pdflatex -interaction=nonstopmode "$f" >/dev/null
done
for f in flag_*.pdf; do
    name="${f%.pdf}"
    name="${name#flag_}"
    pdftoppm -png -r 250 "$f" "../flags_png/${name}"
done
echo "Done. Rename the numbered PNGs (e.g. FR-1.png -> France.png) to match"
echo "the country names used in data/player_ratings.csv's Team column."
