# -*- coding: utf-8 -*-
"""
Draws real, accurate national flags using pre-rendered PNG images. The PNGs
were generated locally (no internet access) by compiling the LaTeX
`worldflags` package (Wilhelm Haager, CTAN - a TikZ-based flag library
already present in this environment's TeX Live distribution) to PDF and
rasterizing with pdftoppm. National flags are public-domain government
symbols, not copyrighted works, so they are safe to reproduce (unlike player
photos or official team crests/badges, which are not used here).

Regenerating the flag PNGs (if a new country needs to be added):
    cd flags_png_src/  (a .tex file per country, see generate_flags.sh)
    pdflatex flag_XX.tex && pdftoppm -png -r 250 flag_XX.pdf XX

Each flag is drawn at data coordinates (x, y) with size (w, h) on a given
matplotlib Axes, preserving the flag's own aspect ratio (never stretched).
"""
import os
import matplotlib.image as mpimg
import matplotlib.patches as patches

_FLAG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flags_png")
_CACHE = {}


def _load_flag(country):
    if country in _CACHE:
        return _CACHE[country]
    path = os.path.join(_FLAG_DIR, f"{country}.png")
    img = mpimg.imread(path) if os.path.exists(path) else None
    _CACHE[country] = img
    return img


def draw_flag(ax, x, y, w, h, country):
    """Draws the real flag for `country` inside the box (x, y, w, h) given
    in the axes' data coordinates, centered and aspect-ratio-preserved
    (letterboxed) within that box."""
    img = _load_flag(country)
    if img is None:
        ax.add_patch(patches.Rectangle((x, y), w, h, facecolor="#888888", edgecolor="white", linewidth=0.8))
        ax.text(x + w / 2, y + h / 2, (country[:2] if country else "??").upper(),
                 ha="center", va="center", fontsize=6, color="white", fontweight="bold")
        return

    img_h, img_w = img.shape[0], img.shape[1]
    img_aspect = img_w / img_h
    box_aspect = w / h

    if img_aspect > box_aspect:
        draw_w, draw_h = w, w / img_aspect
    else:
        draw_h, draw_w = h, h * img_aspect

    left = x + (w - draw_w) / 2
    bottom = y + (h - draw_h) / 2
    ax.imshow(img, extent=(left, left + draw_w, bottom, bottom + draw_h), zorder=8, aspect="auto")


def draw_silhouette(ax, x, y, r, face_color="#D9D9D9", body_color="#BFBFBF"):
    """A generic anonymous player silhouette (head + shoulders) - no real
    person's likeness, just a placeholder avatar shape."""
    ax.add_patch(patches.Circle((x, y + r * 0.35), r * 0.55, facecolor=face_color, edgecolor="none", zorder=7))
    ax.add_patch(patches.Wedge((x, y - r * 0.55), r * 0.95, 0, 180, facecolor=body_color, edgecolor="none", zorder=6))
