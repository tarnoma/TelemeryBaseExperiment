# TelemeryBaseExperiment

Supplementary materials for the paper

> V. Wattanasoontorn, A. Prasitsupparote, and B. Chalothon, "A Gameplay Telemetry-Based Experimental Framework for Studying Player Flow in Real-Time 1v1 Combat Games: Design and Preliminary Evaluation," submitted to the 15th International Conference on Information and Education Technology (ICIET 2027).

The repository contains the analysis code, the supplementary tables (S1–S11), and the supplementary figure (Fig. S1) that the paper refers to but could not include within its 5-page limit.

## Contents

```
README.md
code/
  analysis.py                  reproduces every statistic in the paper and writes results/S1–S11
  make_figure_S1.py            builds figures/FigS1_questionnaire_flow.(pdf|png)
  make_figures_S2_S3.py        builds Fig. S2 (scatter and rank plots) and Fig. S3 (distributions)
  make_supplementary_pdf.py    builds supplementary/Supplementary_Tables.tex from results/
data/
  README.md                    expected input files and their structure
docs/
  game_parameters.md           all game parameters of the rule-based and adaptive conditions
results/                       CSV outputs (see table below)
figures/
  Fig1_gameplay_screenshot.png In-game view of the prototype (paper Fig. 1)
  FigS1_questionnaire_flow.pdf Fig. S1 (questionnaire Flow by group; T17 vs. Flow)
  FigS2a_scatter_telemetry_vs_flow.pdf  Fig. S2a scatter plots of T01–T15 vs. Flow (with r and ρ)
  FigS2b_rank_telemetry_vs_flow.pdf     Fig. S2b rank plots of the same data
  FigS3_distributions.pdf               Fig. S3 histograms of Flow and T01–T15
supplementary/
  Supplementary_Tables.pdf     Figs. S1–S3 and Tables S1–S11 in one document
  Supplementary_Tables.tex     LaTeX source of the above
```

## Supplementary tables

| Table | File | Content | Analysis step |
|---|---|---|---|
| S1 | `results/S1_dataset_summary.csv` | Participants, encounters, durations, wins, boss levels, data-quality counts | Dataset |
| S2 | `results/S2_questionnaire_reliability.csv` | Cronbach's α, mean, SD, mean inter-item r per scale and condition | Step 1 |
| S3 | `results/S3_questionnaire_item_statistics.csv` | Item mean/SD, floor/ceiling %, corrected item–total r, item–rest r, α if item deleted | Step 1 |
| S4 | `results/S4_flow_descriptives.csv` | Questionnaire Flow: mean, SD, median, IQR, min–max, skewness, kurtosis, Shapiro–Wilk p, missing %, outliers | Step 2 |
| S5 | `results/S5_telemetry_descriptives.csv` | T01–T15 at participant and encounter level: same statistics as S4 | Step 2 |
| S6 | `results/S6_correlations_pearson_spearman.csv` | Pearson r and Spearman ρ with 95% CI, p, and Benjamini–Hochberg q (15 telemetry × 2 methods); T17 separately | Step 3A |
| S7 | `results/S7_correlation_matrix_{pearson,spearman}_{rule_based,adaptive}.csv` | Correlation matrices among T01–T15 | Step 3B.1 |
| S8 | `results/S8_VIF.csv` | Variance inflation factors (complete cases) | Step 3B.2 |
| S9 | `results/S9_multiple_regression_model.csv` | Multiple regression model fit: R², adjusted R², F, p, df | Step 3B.3 |
| S10 | `results/S10_multiple_regression_coefficients.csv` | Standardized β, SE, t, p, 95% CI, VIF | Step 3B.3 |
| S11 | `results/S11_group_comparison_mann_whitney.csv` | Mann–Whitney U and rank-biserial r between groups | Group comparison |

## Supplementary figures

| Figure | File | Content | Analysis step |
|---|---|---|---|
| S1 | `figures/FigS1_questionnaire_flow.pdf` | Questionnaire Flow by group; mean T17 vs. Flow | Group comparison |
| S2a | `figures/FigS2a_scatter_telemetry_vs_flow.pdf` | Scatter plots of T01–T15 vs. Flow with least-squares lines, r and ρ | Step 3 (Pearson vs. Spearman check) |
| S2b | `figures/FigS2b_rank_telemetry_vs_flow.pdf` | Rank plots of the same data | Step 3 (Pearson vs. Spearman check) |
| S3 | `figures/FigS3_distributions.pdf` | Histograms of Flow and T01–T15 by condition | Step 2 (distribution) |

`results/participant_level_rule_based.csv` and `results/participant_level_adaptive.csv` contain the participant-level analysis datasets (one row per matched participant).

## Units of analysis

* **Encounter**: one boss fight ending in a win or a loss (one telemetry row; field names use "Session", e.g., `T15_SessionDuration`).
* **Participant**: one tester within one condition. The rule-based and adaptive conditions were run with independent groups of testers; numeric IDs were reused across the two studies, so an ID identifies a person only within a condition.
* The questionnaire was answered once per participant, after the last encounter. Telemetry indicators are therefore summarized per participant (median; win rate and T17 by mean) before any association test.

## Telemetry indicators (T01–T15)

| ID | Indicator | Unit |
|---|---|---|
| T01 | Accuracy (landed hits / attack presses) | ratio 0–1 |
| T02 | Mean reaction time | s |
| T03 | Reaction-time variability (SD) | s |
| T04 | Attack frequency | attacks/s |
| T05 | Defense frequency (dodges + blocks) | actions/s |
| T06 | Hit rate (landed hits / sword contacts) | ratio 0–1 |
| T07 | Damage efficiency | damage/attack |
| T08 | Damage taken rate | damage/s |
| T09 | Win/loss (1 = win); win rate per participant | 0–1 |
| T10 | Action density (attacks + dodges + skills) | actions/s |
| T11 | Input stability (1 / variance of input intervals) | 1/variance |
| T12 | Combo success rate | ratio 0–1 |
| T13 | Idle-time ratio | ratio 0–1 |
| T14 | Error rate (failed / total actions) | ratio 0–1 |
| T15 | Encounter duration | s |
| T17 | In-game rule-based Flow score (design heuristic, analyzed separately) | 0–1 |

T02/T03 are undefined (set to missing, not zero) when an encounter has fewer than two reaction samples.

## Questionnaire

24 items on a 5-point agreement scale, four items per dimension: Concentration (1–4), Challenge–Skill Balance (5–8), Control / System Response (9–12), Enjoyment / Motivation (13–16), Time / Deep Engagement (17–20), Pressure / Flow Experience (21–24). The Flow score is the mean of the 24 items (1–5). The questionnaire was administered in Thai.

## Reproducing the results

Requires Python 3.10+ with `pandas`, `numpy`, `scipy` (≥ 1.11, for `false_discovery_control`), `statsmodels`, `openpyxl`, and `matplotlib`.

```bash
pip install pandas numpy scipy statsmodels openpyxl matplotlib
python code/analysis.py
python code/make_figure_S1.py
python code/make_figures_S2_S3.py
python code/make_supplementary_pdf.py
cd supplementary && pdflatex Supplementary_Tables.tex
```

## Notes on interpretation

* All analyses are exploratory. FDR correction is applied within each family of 15 tests (condition × correlation method).
* The multiple regressions (S9–S10) have 4 and 2 residual degrees of freedom and are overfitted; they are reported for completeness and their coefficients should not be interpreted.
* Group differences cannot be attributed to the condition because the groups were not randomly assigned and were tested on different dates.
