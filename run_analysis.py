"""
FIFA World Cup 2026 - Data Analysis Pipeline
Generates all cleaned datasets, statistics, and visualizations used in the
Jupyter notebook and the PowerPoint presentation.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import json
import os

sns.set_theme(style="whitegrid", font_scale=1.0)
PALETTE = ["#0B3D2E", "#1E7A46", "#4CAF7D", "#F4B942", "#D64545"]
sns.set_palette(PALETTE)

os.makedirs("visuals", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

ROUND_ORDER = ["Group Stage - Matchday 1", "Group Stage - Matchday 2",
               "Group Stage - Matchday 3", "Round of 32", "Round of 16", "Quarter-final"]

# ---------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------
pr = pd.read_csv("data/player_ratings.csv")
ms = pd.read_csv("data/match_statistics.csv")

# ---------------------------------------------------------------
# 2. CLEAN
# ---------------------------------------------------------------
# player_ratings: rows with no MinutesPlayed / Rating = player did not play (unused squad member) -> drop for rating analysis
pr_clean = pr.copy()
pr_clean["Round"] = pd.Categorical(pr_clean["Round"], categories=ROUND_ORDER, ordered=True)
pr_played = pr_clean.dropna(subset=["MinutesPlayed", "Rating"]).copy()
pr_played["MarketValueEUR"] = pr_played["MarketValueEUR"].fillna(pr_played["MarketValueEUR"].median())

# match_statistics: clean % columns, fill card/offside NaN with 0 (event didn't happen)
ms_clean = ms.copy()
for col in ["PossessionHome%", "PossessionAway%"]:
    ms_clean[col] = ms_clean[col].astype(str).str.replace("%", "").astype(float)
for col in ["YellowCardsHome", "YellowCardsAway", "RedCardsHome", "RedCardsAway",
            "OffsidesHome", "OffsidesAway"]:
    ms_clean[col] = ms_clean[col].fillna(0)
ms_clean["Round"] = pd.Categorical(ms_clean["Round"], categories=ROUND_ORDER, ordered=True)

# derive goals from score
goals = ms_clean["Score"].str.extract(r"(\d+)\s*-\s*(\d+)").astype(int)
ms_clean["HomeGoals"] = goals[0]
ms_clean["AwayGoals"] = goals[1]
ms_clean["TotalGoals"] = ms_clean["HomeGoals"] + ms_clean["AwayGoals"]
ms_clean["Winner"] = np.select(
    [ms_clean["HomeGoals"] > ms_clean["AwayGoals"], ms_clean["HomeGoals"] < ms_clean["AwayGoals"]],
    [ms_clean["HomeTeam"], ms_clean["AwayTeam"]], default="Draw")
ms_clean["xGDiffHome"] = ms_clean["HomeGoals"] - ms_clean["xGHome"]
ms_clean["xGDiffAway"] = ms_clean["AwayGoals"] - ms_clean["xGAway"]

pr_played.to_csv("data/processed/player_ratings_clean.csv", index=False)
ms_clean.to_csv("data/processed/match_statistics_clean.csv", index=False)

# ---------------------------------------------------------------
# 3. TEAM-LEVEL AGGREGATION (long format: one row per team per match)
# ---------------------------------------------------------------
home = ms_clean[["Round", "Date", "HomeTeam", "AwayTeam", "HomeGoals", "AwayGoals",
                  "PossessionHome%", "TotalShotsHome", "ShotsOnTargetHome", "PassAccuracyHome%",
                  "xGHome", "FoulsHome", "YellowCardsHome", "RedCardsHome",
                  "HomeTeamMarketValueEUR"]].copy()
home.columns = ["Round", "Date", "Team", "Opponent", "GoalsFor", "GoalsAgainst",
                "Possession", "Shots", "ShotsOnTarget", "PassAccuracy", "xG",
                "Fouls", "YellowCards", "RedCards", "MarketValue"]

away = ms_clean[["Round", "Date", "AwayTeam", "HomeTeam", "AwayGoals", "HomeGoals",
                  "PossessionAway%", "TotalShotsAway", "ShotsOnTargetAway", "PassAccuracyAway%",
                  "xGAway", "FoulsAway", "YellowCardsAway", "RedCardsAway",
                  "AwayTeamMarketValueEUR"]].copy()
away.columns = home.columns

team_matches = pd.concat([home, away], ignore_index=True)
team_matches["Result"] = np.select(
    [team_matches["GoalsFor"] > team_matches["GoalsAgainst"],
     team_matches["GoalsFor"] < team_matches["GoalsAgainst"]],
    ["Win", "Loss"], default="Draw")
team_matches["Points"] = team_matches["Result"].map({"Win": 3, "Draw": 1, "Loss": 0})

team_summary = team_matches.groupby("Team").agg(
    MatchesPlayed=("Team", "count"),
    Wins=("Result", lambda x: (x == "Win").sum()),
    Draws=("Result", lambda x: (x == "Draw").sum()),
    Losses=("Result", lambda x: (x == "Loss").sum()),
    Points=("Points", "sum"),
    GoalsFor=("GoalsFor", "sum"),
    GoalsAgainst=("GoalsAgainst", "sum"),
    AvgPossession=("Possession", "mean"),
    AvgxG=("xG", "mean"),
    AvgPassAccuracy=("PassAccuracy", "mean"),
    MarketValue=("MarketValue", "first"),
).reset_index()
team_summary["GoalDiff"] = team_summary["GoalsFor"] - team_summary["GoalsAgainst"]
team_summary = team_summary.sort_values(["Points", "GoalDiff"], ascending=False)
team_summary.to_csv("data/processed/team_summary.csv", index=False)

# ---------------------------------------------------------------
# 4. PLAYER-LEVEL AGGREGATION
# ---------------------------------------------------------------
player_summary = pr_played.groupby(["Player", "Team", "Position"]).agg(
    MatchesPlayed=("Rating", "count"),
    AvgRating=("Rating", "mean"),
    TotalMinutes=("MinutesPlayed", "sum"),
    MarketValueEUR=("MarketValueEUR", "first"),
).reset_index()
player_summary = player_summary[player_summary["MatchesPlayed"] >= 3]  # meaningful sample
player_summary.to_csv("data/processed/player_summary.csv", index=False)

# ---------------------------------------------------------------
# 5. KEY STATS (for README / PPTX)
# ---------------------------------------------------------------
stats = {}
stats["n_matches"] = int(len(ms_clean))
stats["n_teams"] = int(pr_played["Team"].nunique())
stats["n_players"] = int(pr_played["Player"].nunique())
stats["total_goals"] = int(ms_clean["TotalGoals"].sum())
stats["avg_goals_per_match"] = round(float(ms_clean["TotalGoals"].mean()), 2)
stats["highest_scoring_match"] = ms_clean.loc[ms_clean["TotalGoals"].idxmax(),
    ["HomeTeam", "AwayTeam", "Score", "Round"]].to_dict()
stats["top_team_by_points"] = team_summary.iloc[0][["Team", "Points", "Wins", "Draws", "Losses", "GoalDiff"]].to_dict()
top_rated = player_summary.sort_values("AvgRating", ascending=False).iloc[0]
stats["top_rated_player"] = top_rated[["Player", "Team", "AvgRating", "Position"]].to_dict()
most_valuable = pr_played.sort_values("MarketValueEUR", ascending=False).iloc[0]
stats["most_valuable_player"] = most_valuable[["Player", "Team", "MarketValueEUR"]].to_dict()
stats["avg_market_value_finalists_vs_r32"] = {
    "round_of_16_avg_value": round(float(team_summary[team_summary["Team"].isin(
        ms_clean[ms_clean["Round"]=="Round of 16"][["HomeTeam","AwayTeam"]].values.ravel())]["MarketValue"].mean()), 0),
    "overall_avg_value": round(float(team_summary["MarketValue"].mean()), 0),
}
corr_val_points = float(team_summary[["MarketValue", "Points"]].corr().iloc[0, 1])
stats["correlation_market_value_points"] = round(corr_val_points, 3)
corr_poss_goals = float(team_matches[["Possession", "GoalsFor"]].corr().iloc[0, 1])
stats["correlation_possession_goals"] = round(corr_poss_goals, 3)
corr_xg_goals = float(team_matches[["xG", "GoalsFor"]].corr().iloc[0, 1])
stats["correlation_xg_goals"] = round(corr_xg_goals, 3)

with open("data/processed/key_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2, ensure_ascii=False, default=str)

print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))

# ---------------------------------------------------------------
# 6. VISUALIZATIONS
# ---------------------------------------------------------------

def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"visuals/{name}.png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 6.1 Goals per round
fig, ax = plt.subplots(figsize=(8, 5))
goals_by_round = ms_clean.groupby("Round", observed=True)["TotalGoals"].agg(["sum", "mean"])
ax.bar(goals_by_round.index.astype(str), goals_by_round["sum"], color=PALETTE[1])
ax.set_ylabel("Total Goals")
ax.set_title("Total Goals by Round", fontsize=14, fontweight="bold")
plt.xticks(rotation=25, ha="right")
for i, v in enumerate(goals_by_round["sum"]):
    ax.text(i, v + 0.5, str(int(v)), ha="center", fontweight="bold")
save(fig, "01_goals_by_round")

# 6.2 Top 15 teams by points (table-like bar)
top15 = team_summary.head(15)
fig, ax = plt.subplots(figsize=(9, 7))
colors = [PALETTE[2] if t not in ms_clean[ms_clean["Round"]=="Round of 16"][["HomeTeam","AwayTeam"]].values
          else PALETTE[3] for t in top15["Team"]]
ax.barh(top15["Team"][::-1], top15["Points"][::-1], color=colors[::-1])
ax.set_xlabel("Points")
ax.set_title("Top 15 Teams by Points", fontsize=14, fontweight="bold")
save(fig, "02_top_teams_points")

# 6.3 Market value vs Points (scatter)
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(team_summary["MarketValue"]/1e6, team_summary["Points"], s=70, alpha=0.75, color=PALETTE[1], edgecolor="white")
for _, row in team_summary[team_summary["Points"] >= team_summary["Points"].quantile(0.85)].iterrows():
    ax.annotate(row["Team"], (row["MarketValue"]/1e6, row["Points"]), fontsize=8, xytext=(4,4), textcoords="offset points")
ax.set_xlabel("Squad Market Value (€ Million)")
ax.set_ylabel("Points")
ax.set_title(f"Market Value vs Points (correlation={corr_val_points:.2f})", fontsize=13, fontweight="bold")
save(fig, "03_marketvalue_vs_points")

# 6.4 xG vs Actual Goals (team level scatter with 45 degree line)
fig, ax = plt.subplots(figsize=(7, 7))
team_xg = team_matches.groupby("Team").agg(xG=("xG", "sum"), Goals=("GoalsFor", "sum")).reset_index()
ax.scatter(team_xg["xG"], team_xg["Goals"], s=60, color=PALETTE[1], alpha=0.8, edgecolor="white")
lims = [0, max(team_xg["xG"].max(), team_xg["Goals"].max()) + 1]
ax.plot(lims, lims, linestyle="--", color=PALETTE[4], label="xG = Goals (expected)")
over = team_xg.sort_values("Goals", ascending=False).head(3)
for _, row in over.iterrows():
    ax.annotate(row["Team"], (row["xG"], row["Goals"]), fontsize=8, xytext=(5,5), textcoords="offset points")
ax.set_xlabel("Total xG (Expected Goals)")
ax.set_ylabel("Total Actual Goals")
ax.set_title("Expected Goals (xG) vs Actual Goals", fontsize=14, fontweight="bold")
ax.legend()
save(fig, "04_xg_vs_goals")

# 6.5 Possession vs Goals relationship
fig, ax = plt.subplots(figsize=(8, 6))
sns.regplot(data=team_matches, x="Possession", y="GoalsFor", ax=ax,
            scatter_kws={"alpha":0.4, "color": PALETTE[1]}, line_kws={"color": PALETTE[4]})
ax.set_xlabel("Possession (%)")
ax.set_ylabel("Goals per Match")
ax.set_title(f"Possession vs Goals (correlation={corr_poss_goals:.2f})", fontsize=13, fontweight="bold")
save(fig, "05_possession_vs_goals")

# 6.6 Average rating by position
fig, ax = plt.subplots(figsize=(7, 5))
pos_order = ["G", "D", "M", "F"]
pos_labels = {"G": "Goalkeeper", "D": "Defender", "M": "Midfielder", "F": "Forward"}
avg_by_pos = pr_played.groupby("Position")["Rating"].mean().reindex(pos_order)
ax.bar([pos_labels[p] for p in pos_order], avg_by_pos.values, color=PALETTE[:4])
ax.set_ylabel("Average Rating")
ax.set_ylim(6, 7.2)
ax.set_title("Average Player Rating by Position", fontsize=14, fontweight="bold")
for i, v in enumerate(avg_by_pos.values):
    ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontweight="bold")
save(fig, "06_rating_by_position")

# 6.7 Top 15 rated players (min 3 matches)
top_players = player_summary.sort_values("AvgRating", ascending=False).head(15)
fig, ax = plt.subplots(figsize=(9, 7))
ax.barh(top_players["Player"][::-1] + " (" + top_players["Team"][::-1] + ")", top_players["AvgRating"][::-1], color=PALETTE[2])
ax.set_xlabel("Average Rating")
ax.set_xlim(7, top_players["AvgRating"].max() + 0.3)
ax.set_title("Top 15 Highest-Rated Players of the Tournament (min. 3 matches)", fontsize=13, fontweight="bold")
save(fig, "07_top_rated_players")

# 6.8 Market value distribution by position
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=pr_played, x="Position", y="MarketValueEUR", order=pos_order, ax=ax, palette=PALETTE[:4])
ax.set_xticklabels([pos_labels[p] for p in pos_order])
ax.set_ylabel("Market Value (€)")
ax.set_title("Market Value Distribution by Position", fontsize=14, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
save(fig, "08_marketvalue_by_position")

# 6.9 Cards (discipline) by team - top 10 most carded
cards = team_matches.groupby("Team").agg(Yellow=("YellowCards","sum"), Red=("RedCards","sum")).reset_index()
cards["Total"] = cards["Yellow"] + cards["Red"]*2
cards = cards.sort_values("Total", ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8,6))
ax.barh(cards["Team"][::-1], cards["Yellow"][::-1], color=PALETTE[3], label="Yellow Card")
ax.barh(cards["Team"][::-1], cards["Red"][::-1], left=cards["Yellow"][::-1], color=PALETTE[4], label="Red Card")
ax.set_xlabel("Number of Cards")
ax.set_title("Top 10 Most-Carded Teams", fontsize=14, fontweight="bold")
ax.legend()
save(fig, "09_cards_by_team")

# 6.10 Correlation heatmap of match stats
corr_cols = ["GoalsFor","Possession","Shots","ShotsOnTarget","PassAccuracy","xG","Fouls"]
fig, ax = plt.subplots(figsize=(7,6))
sns.heatmap(team_matches[corr_cols].corr(), annot=True, fmt=".2f", cmap="RdYlGn", center=0, ax=ax,
            cbar_kws={"label": "Correlation"})
ax.set_title("Correlation Between Match Statistics", fontsize=13, fontweight="bold")
save(fig, "10_correlation_heatmap")

print("\nAll visuals saved to visuals/. Processed data saved to data/processed/.")

# ---------------------------------------------------------------
# 7. POSSESSION BUCKETS vs GOAL-SCORING RATE
# ---------------------------------------------------------------
bins = [0, 50, 55, 60, 65, 70, 100]
bin_labels = ["<50%", "50-55%", "55-60%", "60-65%", "65-70%", "70%+"]
team_matches["PossessionBucket"] = pd.cut(team_matches["Possession"], bins=bins, labels=bin_labels, right=False)

poss_goal_rate = team_matches.groupby("PossessionBucket", observed=True).agg(
    Matches=("GoalsFor", "count"),
    AvgGoals=("GoalsFor", "mean"),
    ScoringRate=("GoalsFor", lambda x: (x > 0).mean() * 100),
).reindex(bin_labels)
poss_goal_rate.to_csv("data/processed/possession_goal_rate.csv")
print("\nGoal-scoring rate by possession bucket:")
print(poss_goal_rate)

fig, ax1 = plt.subplots(figsize=(9, 6))
bars = ax1.bar(poss_goal_rate.index.astype(str), poss_goal_rate["AvgGoals"], color=PALETTE[1], label="Avg Goals per Match")
ax1.set_xlabel("Possession Bucket")
ax1.set_ylabel("Average Goals per Match", color=PALETTE[1])
ax1.set_title("Goal-Scoring Rate by Possession Bucket (50% / 55% / 60% / 65% / 70% thresholds)",
              fontsize=13, fontweight="bold")
for i, v in enumerate(poss_goal_rate["AvgGoals"]):
    ax1.text(i, v + 0.03, f"{v:.2f}", ha="center", fontweight="bold", color=PALETTE[0])

ax2 = ax1.twinx()
ax2.plot(poss_goal_rate.index.astype(str), poss_goal_rate["ScoringRate"], color=PALETTE[4],
          marker="o", linewidth=2.5, label="% of Matches Scored In")
ax2.set_ylabel("% of Team-Matches with \u22651 Goal", color=PALETTE[4])
ax2.set_ylim(0, 105)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
plt.tight_layout()
fig.savefig("visuals/16_possession_goal_rate.png", dpi=160, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("Saved visuals/16_possession_goal_rate.png")
