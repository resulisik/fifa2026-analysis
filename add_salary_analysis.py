# -*- coding: utf-8 -*-
"""
Adds an estimated annual gross club salary (EUR) for every player, then
computes price-performance ("value") analysis at player and team level.

Methodology
-----------
Real, publicly reported annual club salaries (source: Capology.com, Forbes,
cross-checked with news reports) were collected for a calibration set of
players spanning a wide market-value range:

    Marc Guehi      MV  70M -> Salary 15.2M
    Jude Bellingham MV 130M -> Salary 20.83M
    Vinicius Jr     MV 140M -> Salary 25.0M
    Kylian Mbappe   MV 180M -> Salary 31.25M
    Erling Haaland  MV 200M -> Salary 31.9M

A power-law curve Salary = k * MarketValue^b was fit to this calibration set
(k=0.754, b=0.707, both in millions of EUR), reflecting the well-documented
fact that wages scale *sub-linearly* with market value (squads have wage
minimums at the low end, and commercial/marketability value inflates market
value faster than base wages at the very top).

For players with a directly reported real salary (the calibration set above,
plus Lionel Messi at Inter Miami, whose $23M club salary is a known outlier
far above what his current market value would imply, given his brand value)
the REAL figure is used directly instead of the model. Everyone else gets
the model estimate. This is clearly flagged in a `SalarySource` column
("Reported" vs "Estimated") so the analysis never hides which numbers are
real and which are modelled.

Because individually verifying real club salaries for 800+ international
players is not feasible, this model-based approach is the only workable way
to produce a full-coverage, directionally-sound salary column - but it means
the player-level "who's overpaid / underpaid" results should be read as
indicative, not as ground truth for any single player outside the
calibration set.
"""
import pandas as pd
import numpy as np

pr = pd.read_csv("data/player_ratings.csv")

# ------------------------------------------------------------------
# 1. SALARY MODEL
# ------------------------------------------------------------------
K, B = 0.754, 0.707  # calibrated power-law parameters (millions of EUR)

def estimate_salary(market_value_eur):
    mv_m = market_value_eur / 1_000_000
    mv_m = max(mv_m, 0.2)  # floor to avoid absurd near-zero salaries
    salary_m = K * (mv_m ** B)
    return round(salary_m * 1_000_000, -3)  # round to nearest 1,000 EUR

# Real reported salaries (EUR/year) - override the model for these players
REPORTED_SALARIES = {
    ("England", "Marc Guéhi"): 15_200_000,
    ("England", "Jude Bellingham"): 20_830_000,
    ("Brazil", "Vinícius Júnior"): 25_000_000,
    ("France", "Kylian Mbappé"): 31_250_000,
    ("Norway", "Erling Haaland"): 31_900_000,
    ("Argentina", "Lionel Messi"): 23_000_000,
    ("Spain", "Lamine Yamal"): 20_830_000,
    ("Türkiye", "Arda Güler"): 5_210_000,
    ("Türkiye", "Kenan Yıldız"): 6_000_000,
}

def salary_row(row):
    key = (row["Team"], row["Player"])
    if key in REPORTED_SALARIES:
        return pd.Series([REPORTED_SALARIES[key], "Reported"])
    if pd.isna(row["MarketValueEUR"]):
        return pd.Series([np.nan, "Estimated"])
    return pd.Series([estimate_salary(row["MarketValueEUR"]), "Estimated"])

pr[["SalaryEUR", "SalarySource"]] = pr.apply(salary_row, axis=1)
pr.to_csv("data/player_ratings.csv", index=False)
print(f"Added SalaryEUR / SalarySource columns to {len(pr)} rows.")
print(f"Reported (real) salaries: {(pr['SalarySource']=='Reported').sum()}")

# ------------------------------------------------------------------
# 2. PLAYER-LEVEL PRICE-PERFORMANCE (>= 2 matches played)
# ------------------------------------------------------------------
played = pr.dropna(subset=["MinutesPlayed", "Rating"]).copy()

player_summary = played.groupby(["Player", "Team"]).agg(
    Position=("Position", "first"),
    MatchesPlayed=("Rating", "count"),
    AvgRating=("Rating", "mean"),
    TotalMinutes=("MinutesPlayed", "sum"),
    MarketValueEUR=("MarketValueEUR", "first"),
    SalaryEUR=("SalaryEUR", "first"),
    SalarySource=("SalarySource", "first"),
).reset_index()

player_summary = player_summary[player_summary["MatchesPlayed"] >= 3].copy()
player_summary = player_summary.dropna(subset=["SalaryEUR"])
player_summary = player_summary[player_summary["SalaryEUR"] > 0]

# Regression-based value score: AvgRating ~ log10(Salary)
# Positive residual = overperforming pay (best value); negative = underperforming (overpaid)
x = np.log10(player_summary["SalaryEUR"])
y = player_summary["AvgRating"]
slope, intercept = np.polyfit(x, y, 1)
player_summary["PredictedRating"] = slope * x + intercept
player_summary["ValueResidual"] = player_summary["AvgRating"] - player_summary["PredictedRating"]
# Also a simple, intuitive ratio: rating points per EUR 1M of salary
player_summary["RatingPerMillion"] = player_summary["AvgRating"] / (player_summary["SalaryEUR"] / 1_000_000)

player_summary = player_summary.sort_values("ValueResidual", ascending=False)
player_summary.to_csv("data/processed/player_value_analysis.csv", index=False)

print("\n=== TOP 10 EN IYI FIYAT/PERFORMANS (en cok deger ureten) ===")
print(player_summary.head(10)[["Player","Team","AvgRating","SalaryEUR","ValueResidual"]].to_string(index=False))

print("\n=== TOP 10 FIYATININ KARSILIGINI VEREMEYEN (en dusuk deger) ===")
print(player_summary.tail(10)[["Player","Team","AvgRating","SalaryEUR","ValueResidual"]].to_string(index=False))

# ------------------------------------------------------------------
# 3. TEAM-LEVEL PRICE-PERFORMANCE
# ------------------------------------------------------------------
ms = pd.read_csv("data/match_statistics.csv")

ROUND_ORDER = ["Group Stage - Matchday 1", "Group Stage - Matchday 2",
               "Group Stage - Matchday 3", "Round of 32", "Round of 16", "Quarter-final"]
ms["Round"] = pd.Categorical(ms["Round"], categories=ROUND_ORDER, ordered=True)

goals = ms["Score"].str.extract(r"(\d+)\s*-\s*(\d+)").astype(int)
ms["HomeGoals"], ms["AwayGoals"] = goals[0], goals[1]

home = ms[["HomeTeam","AwayTeam","HomeGoals","AwayGoals"]].copy()
home.columns = ["Team","Opponent","GoalsFor","GoalsAgainst"]
away = ms[["AwayTeam","HomeTeam","AwayGoals","HomeGoals"]].copy()
away.columns = home.columns
team_matches = pd.concat([home, away], ignore_index=True)
team_matches["Result"] = np.select(
    [team_matches["GoalsFor"] > team_matches["GoalsAgainst"],
     team_matches["GoalsFor"] < team_matches["GoalsAgainst"]],
    ["Win","Loss"], default="Draw")
team_matches["Points"] = team_matches["Result"].map({"Win":3,"Draw":1,"Loss":0})
team_points = team_matches.groupby("Team")["Points"].sum().reset_index()

# Squad wage bill = sum of salaries of all players who actually played >=1 match for the team
team_wagebill = played.dropna(subset=["MarketValueEUR", "SalaryEUR"]).copy()
team_wagebill = team_wagebill.drop_duplicates(subset=["Team","Player"])
team_wagebill = team_wagebill.groupby("Team")["SalaryEUR"].sum().reset_index()
team_wagebill.columns = ["Team", "TotalWageBillEUR"]

team_value = team_points.merge(team_wagebill, on="Team", how="inner")
team_value = team_value[team_value["TotalWageBillEUR"] > 0]

x = np.log10(team_value["TotalWageBillEUR"])
y = team_value["Points"]
slope_t, intercept_t = np.polyfit(x, y, 1)
team_value["PredictedPoints"] = slope_t * x + intercept_t
team_value["ValueResidual"] = team_value["Points"] - team_value["PredictedPoints"]
team_value["PointsPer10M"] = team_value["Points"] / (team_value["TotalWageBillEUR"] / 10_000_000)

team_value = team_value.sort_values("ValueResidual", ascending=False)
team_value.to_csv("data/processed/team_value_analysis.csv", index=False)

print("\n=== EN IYI FIYAT/PERFORMANS TAKIMLARI (Top 5) ===")
print(team_value.head(5)[["Team","Points","TotalWageBillEUR","ValueResidual"]].to_string(index=False))

print("\n=== FIYATININ KARSILIGINI VEREMEYEN TAKIMLAR (Bottom 5) ===")
print(team_value.tail(5)[["Team","Points","TotalWageBillEUR","ValueResidual"]].to_string(index=False))
