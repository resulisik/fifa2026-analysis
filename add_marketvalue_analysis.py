# -*- coding: utf-8 -*-
"""
Price-performance ("value") analysis based on REAL Transfermarkt market values
(already present in the dataset's MarketValueEUR column) instead of the earlier
modeled salary approach.

Why the switch: team-level MarketValueEUR figures in this dataset were
cross-checked against three independent, current (2026) sources reporting
Transfermarkt's official World Cup 2026 squad valuations (planetfootball.com,
onefootball.com, fansided.com) and matched almost exactly for all 14 teams
spot-checked (France, England, Spain, Portugal, Germany, Brazil, Argentina,
Netherlands, Norway, Belgium, Senegal, Turkiye, Morocco, Switzerland).
Player-level spot checks (Yamal, Haaland, Mbappe, Vinicius, Bellingham, Rice,
Saka) were also very close to current real values (Yamal and Haaland matched
exactly at EUR 200M; a few - Mbappe, Rice, Saka - were 10-20% below the very
latest reported figures, likely due to valuation-snapshot timing).

This means MarketValueEUR is real, sourced data - not a model - which makes it
a much more defensible basis for "price" than the previous salary estimate.
"Performance" is still each player's average match rating / each team's
tournament points.
"""
import pandas as pd
import numpy as np

pr = pd.read_csv("data/player_ratings.csv")
ms = pd.read_csv("data/match_statistics.csv")

# ------------------------------------------------------------------
# 1. PLAYER-LEVEL PRICE-PERFORMANCE (>= 3 matches played, real market value)
# ------------------------------------------------------------------
played = pr.dropna(subset=["MinutesPlayed", "Rating"]).copy()

player_summary = played.groupby(["Player", "Team"]).agg(
    Position=("Position", "first"),
    MatchesPlayed=("Rating", "count"),
    AvgRating=("Rating", "mean"),
    TotalMinutes=("MinutesPlayed", "sum"),
    MarketValueEUR=("MarketValueEUR", "first"),
).reset_index()

player_summary = player_summary[player_summary["MatchesPlayed"] >= 3].copy()
player_summary = player_summary.dropna(subset=["MarketValueEUR"])
player_summary = player_summary[player_summary["MarketValueEUR"] > 0]

# Regression-based value score: AvgRating ~ log10(MarketValue)
x = np.log10(player_summary["MarketValueEUR"])
y = player_summary["AvgRating"]
slope, intercept = np.polyfit(x, y, 1)
player_summary["PredictedRating"] = slope * x + intercept
player_summary["ValueResidual"] = player_summary["AvgRating"] - player_summary["PredictedRating"]
player_summary["RatingPer10M"] = player_summary["AvgRating"] / (player_summary["MarketValueEUR"] / 10_000_000)

player_summary = player_summary.sort_values("ValueResidual", ascending=False)
player_summary.to_csv("data/processed/player_value_analysis_marketvalue.csv", index=False)

print(f"Players analyzed (>=3 matches, real market value): {len(player_summary)}")
print(f"Regression: AvgRating = {slope:.3f} * log10(MarketValueEUR) + {intercept:.3f}")

print("\n=== TOP 10 EN IYI FIYAT/PERFORMANS (gercek piyasa degeri) ===")
print(player_summary.head(10)[["Player","Team","MatchesPlayed","AvgRating","MarketValueEUR","ValueResidual"]].to_string(index=False))

print("\n=== 5M+ PIYASA DEGERLI OYUNCULAR ARASINDA EN KOTU DEGER ===")
expensive = player_summary[player_summary["MarketValueEUR"] > 5_000_000].sort_values("ValueResidual")
print(expensive.head(10)[["Player","Team","MatchesPlayed","AvgRating","MarketValueEUR","ValueResidual"]].to_string(index=False))

# ------------------------------------------------------------------
# 2. TEAM-LEVEL PRICE-PERFORMANCE (real Transfermarkt squad value)
# ------------------------------------------------------------------
ROUND_ORDER = ["Group Stage - Matchday 1", "Group Stage - Matchday 2",
               "Group Stage - Matchday 3", "Round of 32", "Round of 16", "Quarter-final"]
ms["Round"] = pd.Categorical(ms["Round"], categories=ROUND_ORDER, ordered=True)

goals = ms["Score"].str.extract(r"(\d+)\s*-\s*(\d+)").astype(int)
ms["HomeGoals"], ms["AwayGoals"] = goals[0], goals[1]

home = ms[["HomeTeam","AwayTeam","HomeGoals","AwayGoals","HomeTeamMarketValueEUR"]].copy()
home.columns = ["Team","Opponent","GoalsFor","GoalsAgainst","MarketValue"]
away = ms[["AwayTeam","HomeTeam","AwayGoals","HomeGoals","AwayTeamMarketValueEUR"]].copy()
away.columns = home.columns
team_matches = pd.concat([home, away], ignore_index=True)
team_matches["Result"] = np.select(
    [team_matches["GoalsFor"] > team_matches["GoalsAgainst"],
     team_matches["GoalsFor"] < team_matches["GoalsAgainst"]],
    ["Win","Loss"], default="Draw")
team_matches["Points"] = team_matches["Result"].map({"Win":3,"Draw":1,"Loss":0})

team_value = team_matches.groupby("Team").agg(
    Points=("Points","sum"), MarketValueEUR=("MarketValue","first")
).reset_index()
team_value = team_value[team_value["MarketValueEUR"] > 0]

x = np.log10(team_value["MarketValueEUR"])
y = team_value["Points"]
slope_t, intercept_t = np.polyfit(x, y, 1)
team_value["PredictedPoints"] = slope_t * x + intercept_t
team_value["ValueResidual"] = team_value["Points"] - team_value["PredictedPoints"]
team_value["PointsPer100M"] = team_value["Points"] / (team_value["MarketValueEUR"] / 100_000_000)

team_value = team_value.sort_values("ValueResidual", ascending=False)
team_value.to_csv("data/processed/team_value_analysis_marketvalue.csv", index=False)

print("\n=== EN IYI FIYAT/PERFORMANS TAKIMLARI (gercek Transfermarkt degeri) ===")
print(team_value.head(6)[["Team","Points","MarketValueEUR","ValueResidual"]].to_string(index=False))

print("\n=== FIYATININ KARSILIGINI VEREMEYEN TAKIMLAR ===")
print(team_value.tail(6)[["Team","Points","MarketValueEUR","ValueResidual"]].to_string(index=False))
