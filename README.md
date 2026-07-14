<div align="center">

# ⚽ FIFA World Cup 2026
## Data Analysis & Player Value Project

<img src="visuals/13_best_value_squad.png" alt="FIFA 2026 Best Value Dream Squad" width="850">

<br>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)](https://jupyter.org/)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![Purpose](https://img.shields.io/badge/Purpose-Portfolio-blueviolet)

**Created by [Resul Işık](https://github.com/resulisik)**

[LinkedIn](https://www.linkedin.com/in/resul-isik/) ·
[🇹🇷 Türkçe README](README_TR.md)

</div>

---

## 📌 Project Overview

This project presents an end-to-end data analysis of the **2026 FIFA World Cup**, covering the tournament from the group stage through the quarter-finals.

The analysis includes:

- **100 matches**
- **5,012 player-match records**
- Team and player performance analysis
- Expected goals and possession analysis
- Market value and price/performance comparisons
- Position-based player rankings
- Three custom-built 4-3-3 squads
- Automated data cleaning and visualization pipeline

The main objective is to examine the relationship between **player performance, team success, squad market value, expected goals, possession, and cost efficiency**.

> **Data note:** The project includes source-referenced match information as well as several illustrative or simulated fields. Some secondary match statistics were estimated where complete official data was unavailable.

---

## 🎯 Research Questions

1. Which teams performed best during the tournament?
2. Does having a more expensive squad lead to better results?
3. Which players delivered the best performance relative to their market value?
4. How strongly does expected goals correlate with actual goals?
5. Does higher possession always increase the chance of scoring?
6. What would the best price/performance starting eleven look like?
7. Which expensive players performed below expectations?

---

## 🔍 Key Findings

| Metric | Finding |
|---|---|
| Total goals | **317 goals in 100 matches** |
| Goals per match | **3.17** |
| Best-performing team | **France** |
| Best individual performer | **Lionel Messi — 9.03 average rating** |
| Highest market values | **Lamine Yamal and Erling Haaland — €200M** |
| Strongest goal-related metric | **Expected Goals — correlation ≈ 0.62** |
| Market value vs points | **Correlation ≈ 0.76** |
| Best value team | **Argentina** |
| Best value player | **Lionel Messi** |
| Best budget goalkeeper | **Vozinha — €50K market value** |

### Main Insights

- Expected goals had a stronger relationship with actual goals than possession.
- Squad market value showed a meaningful positive relationship with tournament points.
- Extremely high possession did not always produce more goals.
- The scoring rate increased until the **65–70% possession range**, then dropped above 70%.
- Several low-value players produced performances comparable to much more expensive players.
- Argentina generated one of the strongest team-level price/performance results.

---

## 💰 Price/Performance Methodology

Player price/performance was measured using the relationship:

```text
Average Player Rating ~ Logarithm of Market Value
```

A regression model estimates the performance expected from a player based on market value.

The difference between actual and expected performance is stored as:

```text
ValueResidual
```

- **Positive residual:** Better performance than expected for the price
- **Negative residual:** Worse performance than expected for the price
- **Residual close to zero:** Performance broadly consistent with market value

---

## 🏆 Best Price/Performance Players by Position

| Position | Player | Country | Average Rating | Market Value |
|---|---|---|---:|---:|
| Goalkeeper | Vozinha | Cabo Verde | 7.88 | €0.05M |
| Defender | Ramin Rezaeian | Iran | 7.57 | €0.25M |
| Midfielder | Elijah Just | New Zealand | 7.83 | €2.5M |
| Forward | Lionel Messi | Argentina | 9.03 | €15M |

---

## 📉 Lowest Price/Performance Players

| Position | Player | Country | Average Rating | Market Value |
|---|---|---|---:|---:|
| Goalkeeper | Uğurcan Çakır | Türkiye | 6.50 | €15M |
| Defender | Abdukodir Khusanov | Uzbekistan | 6.13 | €50M |
| Midfielder | Orkun Kökçü | Türkiye | 6.27 | €25M |
| Forward | Ferran Torres | Spain | 6.28 | €50M |

---

## 🌟 Best Value Dream Squad — 4-3-3

The squad was built by applying a minimum average rating of **7.00**, grouping players by position, and selecting the highest price/performance scores.

| Position | Player | Team | Rating | Market Value |
|---|---|---|---:|---:|
| Goalkeeper | Vozinha | Cabo Verde | 7.88 | €0.05M |
| Defender | Ramin Rezaeian | Iran | 7.57 | €0.25M |
| Defender | Aymeric Laporte | Spain | 7.52 | €8M |
| Defender | Jan Paul van Hecke | Netherlands | 7.65 | €45M |
| Defender | Richie Laryea | Canada | 7.30 | €1M |
| Midfielder | Elijah Just | New Zealand | 7.83 | €2.5M |
| Midfielder | Jude Bellingham | England | 8.03 | €130M |
| Midfielder | Vinícius Júnior | Brazil | 8.00 | €140M |
| Forward | Lionel Messi | Argentina | 9.03 | €15M |
| Forward | Kylian Mbappé | France | 8.50 | €180M |
| Forward | Erling Haaland | Norway | 7.96 | €200M |

**Total squad value:** €721.8M  
**Average player rating:** 7.93  
**Formation:** 4-3-3

<div align="center">
  <img src="visuals/13_best_value_squad.png" alt="Best Value Dream Squad" width="800">
</div>

---

## 🆚 Squad Comparison

| Squad | Total Market Value | Average Rating | Selection Rule |
|---|---:|---:|---|
| Best Value Dream Squad | €721.8M | 7.93 | Best price/performance players |
| Best Budget Squad | €18.45M | 7.46 | Players valued at €5M or below |
| Worst Value Squad | €365M | 6.25 | Expensive players with low ratings |

<div align="center">
  <img src="visuals/15_best_budget_xi.png" alt="Best Budget Squad" width="48%">
  <img src="visuals/14_worst_value_xi.png" alt="Worst Value Squad" width="48%">
</div>

---

## ⚽ Possession and Goal-Scoring Analysis

| Possession Range | Team-Matches | Average Goals | Scoring Rate |
|---|---:|---:|---:|
| Below 50% | 99 | 1.12 | 69.7% |
| 50–55% | 26 | 1.85 | 73.1% |
| 55–60% | 20 | 1.75 | 70.0% |
| 60–65% | 24 | 2.17 | 95.8% |
| 65–70% | 17 | 2.76 | 94.1% |
| 70% and above | 14 | 1.71 | 57.1% |

Goal production increased until the **65–70% possession range**. However, teams with more than 70% possession recorded the lowest scoring rate.

<div align="center">
  <img src="visuals/16_possession_goal_rate.png" alt="Possession Goal Rate" width="800">
</div>

---

## 📊 Sample Visualizations

<table>
<tr>
<td width="50%" align="center">
<b>Team Points</b><br><br>
<img src="visuals/02_top_teams_points.png" alt="Top Teams by Points" width="100%">
</td>
<td width="50%" align="center">
<b>Market Value vs Points</b><br><br>
<img src="visuals/03_marketvalue_vs_points.png" alt="Market Value vs Points" width="100%">
</td>
</tr>
<tr>
<td width="50%" align="center">
<b>Expected Goals vs Goals</b><br><br>
<img src="visuals/04_xg_vs_goals.png" alt="Expected Goals vs Actual Goals" width="100%">
</td>
<td width="50%" align="center">
<b>Correlation Heatmap</b><br><br>
<img src="visuals/10_correlation_heatmap.png" alt="Correlation Heatmap" width="100%">
</td>
</tr>
</table>

---

## 📁 Project Structure

```text
fifa2026-analysis/
├── data/
│   ├── player_ratings.csv
│   ├── match_statistics.csv
│   └── processed/
│       ├── player_ratings_clean.csv
│       ├── match_statistics_clean.csv
│       ├── team_summary.csv
│       ├── player_summary.csv
│       ├── possession_goal_rate.csv
│       ├── player_value_analysis_marketvalue.csv
│       ├── team_value_analysis_marketvalue.csv
│       ├── squad_worst_value_xi.csv
│       ├── squad_best_budget_xi.csv
│       └── squad_dream_xi.csv
├── notebooks/
│   └── FIFA2026_Analysis.ipynb
├── presentations/
│   ├── FIFA2026_UcKadro_DegerAnalizi_TR.pptx
│   └── FIFA2026_ThreeSquads_ValueAnalysis_EN.pptx
├── visuals/
├── flags_png/
├── flags_latex_src/
├── run_analysis.py
├── add_quarterfinals.py
├── add_marketvalue_analysis.py
├── add_salary_analysis.py
├── build_squads.py
├── build_squad_visuals.py
├── build_notebook.py
├── flag_utils.py
├── requirements.txt
├── README.md
└── README_TR.md
```

---

## 📂 Datasets

| Dataset | Records | Description |
|---|---:|---|
| `player_ratings.csv` | 5,012 | Player ratings, minutes, positions and market values |
| `match_statistics.csv` | 100 | Match scores, possession, shots, xG, passes, cards and corners |
| `team_summary.csv` | Team level | Aggregated tournament performance |
| `player_summary.csv` | Player level | Average player performance statistics |
| `possession_goal_rate.csv` | Possession groups | Goal production by possession range |

---

## 🧹 Data Cleaning Process

- Removed players who did not enter the pitch
- Converted percentage columns into numeric format
- Handled missing card and offside values
- Filled missing market values using the median
- Extracted home and away goals from score strings
- Converted match data into team-level long format
- Aggregated player-level performance
- Created market value and performance metrics
- Exported processed CSV and JSON files
- Automatically generated charts and squad visuals

---

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python 3.11 | Core programming language |
| pandas | Data cleaning and analysis |
| NumPy | Numerical operations |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Scikit-learn | Regression and analytical modeling |
| Jupyter Notebook | Interactive analysis |
| LaTeX / TikZ | National flag generation |
| GitHub | Version control and portfolio publishing |

---

## 🚀 Installation and Usage

```bash
git clone https://github.com/resulisik/fifa2026-analysis.git
cd fifa2026-analysis
pip install -r requirements.txt
```

Open the notebook:

```bash
jupyter notebook notebooks/FIFA2026_Analysis.ipynb
```

Run the complete pipeline:

```bash
python run_analysis.py
```

Generate squad data and visuals:

```bash
python build_squads.py
python build_squad_visuals.py
```

---

## 📽️ Presentations

| Language | Presentation |
|---|---|
| 🇹🇷 Turkish | [Download Turkish Squad Value Analysis](presentations/FIFA2026_UcKadro_DegerAnalizi_TR.pptx) |
| 🇬🇧 English | [Download English Squad Value Analysis](presentations/FIFA2026_ThreeSquads_ValueAnalysis_EN.pptx) |

---

## 📓 Main Notebook

[Open the complete FIFA 2026 analysis notebook](notebooks/FIFA2026_Analysis.ipynb)

---

## 📄 License

This project was created for educational and portfolio purposes. The underlying datasets are illustrative or simulated except where explicitly noted as source-referenced match data.
