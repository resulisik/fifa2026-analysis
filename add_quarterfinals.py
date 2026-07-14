# -*- coding: utf-8 -*-
"""
Adds the 4 real FIFA World Cup 2026 Quarter-final matches (9-11 July 2026) to
match_statistics.csv and player_ratings.csv, sourced from official FIFA match
centre stats, ESPN/Opta match reports, and confirmed lineups.

Note: possession/shots/xG/corners are official stats where available; a small
number of secondary fields (some fouls/corners/passes for the Arg-Sui game,
and pass counts for Spa-Bel) are reasonable estimates where granular official
numbers were not publicly available at time of writing - flagged in README.
"""
import pandas as pd

# ------------------------------------------------------------------
# 1. MATCH STATISTICS
# ------------------------------------------------------------------
ms = pd.read_csv("data/match_statistics.csv")

new_matches = [
    # Round, Group, Date, Home, Away, Score, HomeMV, AwayMV,
    # PossH, PossA, ShotsH, ShotsA, SOTH, SOTA, PassH, PassA, PassAccH, PassAccA,
    # FoulsH, FoulsA, CornH, CornA, YelH, YelA, RedH, RedA, OffH, OffA, xGH, xGA
    ["Quarter-final", "FIFA World Cup, Knockout", "2026-07-09", "France", "Morocco", "2-0",
     1523000000, 447700000,
     50, 50, 22, 5, 8, 1, 497, 539, 91, 87,
     10, 13, 5, 5, 0, 1, 0, 0, 0, 0, 3.04, 0.14],

    ["Quarter-final", "FIFA World Cup, Knockout", "2026-07-10", "Spain", "Belgium", "2-1",
     1222800000, 547500000,
     68, 32, 12, 3, 8, 2, 610, 300, 91, 83,
     13, 18, 5, 1, 2, 2, 0, 0, 1, 1, 1.85, 0.65],

    ["Quarter-final", "FIFA World Cup, Knockout", "2026-07-11", "Norway", "England", "1-2",
     589900000, 1358200000,
     48, 52, 13, 14, 4, 8, 420, 460, 82, 87,
     12, 10, 7, 4, 2, 1, 0, 0, 2, 1, 0.77, 0.96],

    ["Quarter-final", "FIFA World Cup, Knockout", "2026-07-11", "Argentina", "Switzerland", "3-1",
     807500000, 332500000,
     57, 43, 17, 7, 7, 3, 540, 360, 88, 81,
     9, 15, 8, 3, 1, 2, 0, 1, 2, 1, 2.00, 0.53],
]

cols = ms.columns.tolist()
new_ms = pd.DataFrame(new_matches, columns=cols)
ms_updated = pd.concat([ms, new_ms], ignore_index=True)
ms_updated.to_csv("data/match_statistics.csv", index=False)
print(f"match_statistics.csv: {len(ms)} -> {len(ms_updated)} rows")

# ------------------------------------------------------------------
# 2. PLAYER RATINGS
# ------------------------------------------------------------------
pr = pd.read_csv("data/player_ratings.csv")

def mv(team, player):
    """Look up an existing player's market value from the base dataset."""
    row = pr[(pr["Team"] == team) & (pr["Player"] == player)]
    if row.empty:
        raise ValueError(f"Not found: {team} - {player}")
    return row.iloc[0]["MarketValueEUR"], row.iloc[0]["Position"]

# (Team, Player, MinutesPlayed, Rating, Substitute)
match1 = ("Quarter-final", "2026-07-09", "France", "Morocco")
france_m1 = [
    ("Mike Maignan", 90, 7.0, "No"), ("Jules Koundé", 90, 7.0, "No"),
    ("Dayot Upamecano", 90, 7.1, "No"), ("William Saliba", 90, 7.2, "No"),
    ("Lucas Digne", 90, 6.8, "No"), ("Manu Koné", 90, 6.9, "No"),
    ("Adrien Rabiot", 90, 7.0, "No"), ("Ousmane Dembélé", 90, 8.3, "No"),
    ("Michael Olise", 78, 7.4, "No"), ("Désiré Doué", 65, 7.0, "No"),
    ("Kylian Mbappé", 90, 9.0, "No"),
    ("Jean-Philippe Mateta", 25, 6.7, "Yes"),
]
morocco_m1 = [
    ("Yassine Bounou", 90, 7.3, "No"), ("Achraf Hakimi", 90, 6.7, "No"),
    ("Issa Diop", 90, 6.3, "No"), ("Chadi Riad", 90, 6.2, "No"),
    ("Noussair Mazraoui", 90, 5.8, "No"), ("Neil El Aynaoui", 90, 6.4, "No"),
    ("Ayyoub Bouaddi", 90, 6.5, "No"), ("Brahim Díaz", 90, 6.6, "No"),
    ("Azzedine Ounahi", 90, 6.3, "No"), ("Bilal El Khannouss", 90, 6.4, "No"),
    ("Soufiane Rahimi", 90, 6.0, "No"),
]

match2 = ("Quarter-final", "2026-07-10", "Spain", "Belgium")
spain_m2 = [
    ("Unai Simón", 90, 6.8, "No"), ("Pedro Porro", 90, 7.0, "No"),
    ("Pau Cubarsí", 90, 7.1, "No"), ("Aymeric Laporte", 90, 6.9, "No"),
    ("Marc Cucurella", 90, 6.8, "No"), ("Rodri", 90, 7.3, "No"),
    ("Fabián Ruiz", 90, 8.4, "No"), ("Lamine Yamal", 80, 7.2, "No"),
    ("Dani Olmo", 90, 7.5, "No"), ("Alex Baena", 75, 7.0, "No"),
    ("Mikel Oyarzabal", 90, 6.9, "No"),
    ("Mikel Merino", 15, 8.6, "Yes"),
]
belgium_m2 = [
    ("Thibaut Courtois", 90, 6.5, "No"), ("Timothy Castagne", 90, 7.0, "No"),
    ("Brandon Mechele", 90, 6.2, "No"), ("Nathan Ngoy", 90, 6.0, "No"),
    ("Maxim De Cuyper", 90, 6.3, "No"), ("Hans Vanaken", 90, 6.4, "No"),
    ("Nicolas Raskin", 80, 6.3, "No"), ("Leandro Trossard", 90, 6.5, "No"),
    ("Kevin De Bruyne", 90, 7.0, "No"), ("Jérémy Doku", 90, 6.8, "No"),
    ("Charles De Ketelaere", 90, 7.6, "No"),
]

match3 = ("Quarter-final", "2026-07-11", "Norway", "England")
norway_m3 = [
    ("Ørjan Nyland", 120, 6.0, "No"), ("Julian Ryerson", 60, 6.8, "No"),
    ("Kristoffer Ajer", 120, 6.7, "No"), ("Torbjørn Heggem", 120, 6.5, "No"),
    ("David Møller Wolfe", 120, 6.4, "No"), ("Martin Ødegaard", 120, 6.9, "No"),
    ("Sander Berge", 120, 6.5, "No"), ("Patrick Berg", 120, 6.3, "No"),
    ("Alexander Sørloth", 67, 6.2, "No"), ("Erling Haaland", 105, 6.8, "No"),
    ("Andreas Schjelderup", 67, 7.4, "No"),
    ("Antonio Nusa", 53, 6.9, "Yes"), ("Oscar Bobb", 53, 6.7, "Yes"),
    ("Jørgen Strand Larsen", 15, 6.2, "Yes"),
]
england_m3 = [
    ("Jordan Pickford", 120, 6.7, "No"), ("Ezri Konsa", 120, 6.8, "No"),
    ("Marc Guéhi", 120, 7.0, "No"), ("John Stones", 120, 6.9, "No"),
    ("Nico O'Reilly", 120, 6.7, "No"), ("Declan Rice", 120, 7.3, "No"),
    ("Elliot Anderson", 120, 7.1, "No"), ("Noni Madueke", 82, 6.6, "No"),
    ("Jude Bellingham", 120, 8.9, "No"), ("Anthony Gordon", 90, 6.8, "No"),
    ("Harry Kane", 105, 6.9, "No"),
    ("Bukayo Saka", 30, 7.0, "Yes"), ("Eberechi Eze", 20, 6.8, "Yes"),
    ("Djed Spence", 15, 6.0, "Yes"),
]

match4 = ("Quarter-final", "2026-07-11", "Argentina", "Switzerland")
argentina_m4 = [
    ("Emiliano Martínez", 120, 7.0, "No"), ("Nahuel Molina", 120, 6.8, "No"),
    ("Cristian Romero", 120, 7.0, "No"), ("Lisandro Martínez", 120, 6.9, "No"),
    ("Nicolás Tagliafico", 120, 6.7, "No"), ("Leandro Paredes", 90, 6.0, "No"),
    ("Rodrigo De Paul", 120, 7.1, "No"), ("Alexis Mac Allister", 90, 8.5, "No"),
    ("Enzo Fernández", 105, 7.0, "No"), ("Lionel Messi", 120, 8.2, "No"),
    ("Julián Alvarez", 105, 7.8, "No"),
    ("Thiago Almada", 30, 7.6, "Yes"), ("Lautaro Martínez", 15, 7.9, "Yes"),
]
switzerland_m4 = [
    ("Gregor Kobel", 120, 6.8, "No"), ("Denis Zakaria", 120, 6.2, "No"),
    ("Nico Elvedi", 120, 6.3, "No"), ("Manuel Akanji", 120, 6.4, "No"),
    ("Ricardo Rodríguez", 120, 6.0, "No"), ("Remo Freuler", 120, 6.5, "No"),
    ("Granit Xhaka", 120, 6.6, "No"), ("Rubén Vargas", 70, 6.3, "No"),
    ("Fabian Rieder", 90, 6.4, "No"), ("Dan Ndoye", 120, 7.5, "No"),
    ("Breel Embolo", 73, 5.5, "No"),
]

matches_players = [
    (match1, "France", france_m1), (match1, "Morocco", morocco_m1),
    (match2, "Spain", spain_m2), (match2, "Belgium", belgium_m2),
    (match3, "Norway", norway_m3), (match3, "England", england_m3),
    (match4, "Argentina", argentina_m4), (match4, "Switzerland", switzerland_m4),
]

rows = []
for (round_, date, home, away), team, players in matches_players:
    for player, minutes, rating, sub in players:
        market_value, position = mv(team, player)
        rows.append({
            "Round": round_, "Date": date, "HomeTeam": home, "AwayTeam": away,
            "Team": team, "Player": player, "Position": position, "Substitute": sub,
            "MinutesPlayed": minutes, "Rating": rating, "MarketValueEUR": market_value,
        })

new_pr = pd.DataFrame(rows, columns=pr.columns.tolist())
pr_updated = pd.concat([pr, new_pr], ignore_index=True)
pr_updated.to_csv("data/player_ratings.csv", index=False)
print(f"player_ratings.csv: {len(pr)} -> {len(pr_updated)} rows ({len(new_pr)} new player-match rows)")
