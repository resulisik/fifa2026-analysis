# -*- coding: utf-8 -*-
"""Draws a 4-3-3 formation pitch graphic for each squad, using a vertical
(portrait) player card: a large, clearly visible national flag strip on top,
a generic silhouette avatar below it, then name / rating / value.
No real photos or team crests are used - see flag_utils.py for the
copyright rationale (flags are public-domain government symbols)."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from flag_utils import draw_flag, draw_silhouette

sns.set_theme(style="white")

PALETTE_GOOD = {"bg": "#0B3D2E", "card": "#12513C", "ring": "#F4B942", "text": "#F4B942"}
PALETTE_BAD = {"bg": "#5C1F1F", "card": "#712727", "ring": "#FF7A7A", "text": "#FFB4B4"}

# Row Y-centers spaced far enough apart for tall portrait cards (card height ~24)
POS_XY = {
    "G": [(50, 18)],
    "D": [(14, 54), (38, 50), (62, 50), (86, 54)],
    "M": [(24, 90), (50, 84), (76, 90)],
    "F": [(18, 128), (50, 134), (82, 128)],
}

CARD_W, CARD_H = 12.0, 24.0
FLAG_H = 6.5


def draw_player_card(ax, x, y, row, palette):
    bg = palette["bg"]
    card_color = palette["card"]
    ring_color = palette["ring"]
    text_color = palette["text"]

    left = x - CARD_W / 2
    bottom = y - CARD_H / 2

    # card body
    ax.add_patch(patches.FancyBboxPatch((left, bottom), CARD_W, CARD_H,
                  boxstyle="round,pad=0,rounding_size=0.9",
                  linewidth=1.8, edgecolor=ring_color, facecolor=card_color, zorder=5))

    # flag strip (top of card) - large and clearly visible
    flag_margin = 0.55
    draw_flag(ax, left + flag_margin, bottom + CARD_H - FLAG_H - flag_margin,
               CARD_W - 2 * flag_margin, FLAG_H, row["Team"])
    ax.add_patch(patches.Rectangle((left + flag_margin, bottom + CARD_H - FLAG_H - flag_margin),
                 CARD_W - 2 * flag_margin, FLAG_H, fill=False, edgecolor="white", linewidth=1.1, zorder=8))

    # silhouette avatar
    avatar_cy = bottom + CARD_H - FLAG_H - flag_margin - 3.6
    avatar_r = 3.0
    ax.add_patch(patches.Circle((x, avatar_cy), avatar_r, facecolor="#E7E7E7", edgecolor="white", linewidth=1.2, zorder=6))
    draw_silhouette(ax, x, avatar_cy, avatar_r)

    # rating badge (top-right of avatar)
    bx, by = x + avatar_r * 0.78, avatar_cy + avatar_r * 0.78
    ax.add_patch(patches.Circle((bx, by), 1.75, facecolor=ring_color, edgecolor=card_color, linewidth=1.0, zorder=9))
    ax.text(bx, by, f"{row['AvgRating']:.1f}", ha="center", va="center", fontsize=7.5,
             fontweight="bold", color=bg, zorder=10)

    # name + value
    name = row["Player"] if len(row["Player"]) < 15 else row["Player"].split()[-1]
    ax.text(x, avatar_cy - avatar_r - 1.6, name, ha="center", va="top", fontsize=9.3,
             fontweight="bold", color="white", zorder=7)
    mv = row["MarketValueEUR"] / 1e6
    label = f"{mv:.1f}M\u20ac" if mv < 10 else f"{mv:.0f}M\u20ac"
    ax.text(x, avatar_cy - avatar_r - 4.6, label, ha="center", va="top", fontsize=9, color=text_color, zorder=7)


def draw_pitch(squad_df, title, subtitle, out_path, palette):
    fig, ax = plt.subplots(figsize=(10, 17))
    bg = palette["bg"]
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(bg)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 168)
    ax.set_autoscale_on(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.add_patch(patches.Rectangle((2, 2), 96, 160, fill=False, edgecolor="white", linewidth=2, alpha=0.4))
    ax.add_patch(patches.Rectangle((25, 2), 50, 16, fill=False, edgecolor="white", linewidth=2, alpha=0.4))
    ax.add_patch(patches.Rectangle((25, 146), 50, 16, fill=False, edgecolor="white", linewidth=2, alpha=0.4))
    ax.add_patch(patches.Circle((50, 82), 12, fill=False, edgecolor="white", linewidth=2, alpha=0.4))
    ax.axhline(82, color="white", linewidth=2, alpha=0.4)

    for pos, coords in POS_XY.items():
        rows = squad_df[squad_df["Position"] == pos].reset_index(drop=True)
        for (x, y), (_, row) in zip(coords, rows.iterrows()):
            draw_player_card(ax, x, y, row, palette)

    ax.text(50, 161, title, ha="center", fontsize=15, fontweight="bold", color="white")
    ax.text(50, 157, subtitle, ha="center", fontsize=11.5, color=palette["text"])

    plt.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight", facecolor=bg)
    plt.close(fig)


worst = pd.read_csv("data/processed/squad_worst_value_xi.csv")
budget = pd.read_csv("data/processed/squad_best_budget_xi.csv")
dream = pd.read_csv("data/processed/squad_dream_xi.csv")

draw_pitch(
    worst,
    "Worst Value Squad (MV\u2265\u20ac10M & Rating<6.50)",
    f"Total Value: {worst['MarketValueEUR'].sum()/1e6:.0f}M\u20ac   \u00b7   Avg Rating: {worst['AvgRating'].mean():.2f}",
    "visuals/14_worst_value_xi.png", PALETTE_BAD,
)
draw_pitch(
    budget,
    "Best Budget Squad (Market Value \u2264 \u20ac5M)",
    f"Total Value: {budget['MarketValueEUR'].sum()/1e6:.1f}M\u20ac   \u00b7   Avg Rating: {budget['AvgRating'].mean():.2f}",
    "visuals/15_best_budget_xi.png", PALETTE_GOOD,
)
draw_pitch(
    dream,
    "Dream Squad (Best Value, No Budget Cap)",
    f"Total Value: {dream['MarketValueEUR'].sum()/1e6:.0f}M\u20ac   \u00b7   Avg Rating: {dream['AvgRating'].mean():.2f}",
    "visuals/13_best_value_squad.png", PALETTE_GOOD,
)
print("All 3 pitch graphics saved (portrait cards, larger visible flags).")
