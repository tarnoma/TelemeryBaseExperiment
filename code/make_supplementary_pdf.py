"""Builds supplementary/Supplementary_Tables.tex from results/*.csv (compile with pdflatex)."""
import os, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '..', 'results'); O = os.path.join(HERE, '..', 'supplementary')
os.makedirs(O, exist_ok=True)
def esc(x): return str(x).replace('^', r'\textasciicircum{}').replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')
def tab(df, title, note=''):
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind == 'f': df[c] = df[c].map(lambda v: '' if pd.isna(v) else (f'{v:.3f}' if abs(v) < 1000 else f'{v:.0f}'))
    cols = 'l' * 1 + 'r' * (len(df.columns) - 1)
    head = ' & '.join(esc(c) for c in df.columns) + r' \\'
    body = '\n'.join(' & '.join(esc(v) for v in row) + r' \\' for row in df.astype(str).values)
    return (r'\section*{' + title + '}\n' + (note + '\n\n' if note else '') + r'{\scriptsize\setlength{\tabcolsep}{3pt}' +
            r'\begin{longtable}{' + cols + '}\n\\toprule\n' + head + '\n\\midrule\n\\endhead\n' + body + '\n\\bottomrule\n\\end{longtable}}\n')
S = []
s1 = pd.read_csv(f'{R}/S1_dataset_summary.csv').round(2).set_index('condition').T.reset_index().rename(columns={'index': 'measure'})
S.append(tab(s1, 'Table S1. Dataset summary by condition', 'Encounter = one boss fight; participant = one tester within one condition.'))
S.append(tab(pd.read_csv(f'{R}/S2_questionnaire_reliability.csv'), 'Table S2. Questionnaire reliability (Cronbach alpha) by scale and condition'))
S.append(tab(pd.read_csv(f'{R}/S3_questionnaire_item_statistics.csv'), 'Table S3. Questionnaire item statistics',
             'Floor/ceiling = \\% of responses at 1/5. Corrected item--total r uses the 24-item total; item--rest r and alpha if deleted use the item\'s dimension.'))
S.append(tab(pd.read_csv(f'{R}/S4_flow_descriptives.csv'), 'Table S4. Descriptive statistics of questionnaire Flow (mean of 24 items)',
             'Outliers: Tukey rule (beyond 1.5 IQR).'))
d = pd.read_csv(f'{R}/S5_telemetry_descriptives.csv'); d['level'] = d.level.str.split(' ').str[0]
S.append(tab(d, 'Table S5. Descriptive statistics of telemetry indicators T01--T15',
             'Participant level = median per participant (T09 = win rate); encounter level = all encounters. Missing = undefined values (T02/T03 with fewer than 2 reaction samples).'))
S.append(tab(pd.read_csv(f'{R}/S6_correlations_pearson_spearman.csv'), 'Table S6. Correlations of telemetry indicators with questionnaire Flow (step 3A)',
             'Participant level, within condition. 95\\% CI by Fisher z (Bonett--Wright SE for Spearman). q = Benjamini--Hochberg FDR within each family of 15 tests (condition x method); T17 not included.'))
for c in ['rule_based', 'adaptive']:
    m = pd.read_csv(f'{R}/S7_correlation_matrix_spearman_{c}.csv', index_col=0)
    m.index = [i[:3] for i in m.index]; m.columns = [i[:3] for i in m.columns]
    S.append(tab(m.reset_index().rename(columns={'index': ''}), f'Table S7. Spearman correlation matrix among T01--T15 ({c.replace("_", "-")})',
                 'Pearson matrices are provided as CSV files in results/.'))
S.append(tab(pd.read_csv(f'{R}/S8_VIF.csv'), 'Table S8. Variance inflation factors (complete cases)'))
S.append(tab(pd.read_csv(f'{R}/S9_multiple_regression_model.csv'), 'Table S9. Multiple linear regression of Flow on T01--T15: model fit (step 3B)',
             'Standardized variables, complete cases. With 4 and 2 residual degrees of freedom the models are overfitted and are reported for completeness only.'))
S.append(tab(pd.read_csv(f'{R}/S10_multiple_regression_coefficients.csv'), 'Table S10. Multiple linear regression coefficients (standardized beta)',
             'Not interpretable because of overfitting and collinearity; see Table S9.'))
S.append(tab(pd.read_csv(f'{R}/S11_group_comparison_mann_whitney.csv'), 'Table S11. Questionnaire Flow by group (Mann--Whitney U, rank-biserial r)'))
doc = (r'\documentclass[10pt]{article}' '\n' r'\usepackage[landscape,margin=1.5cm]{geometry}' '\n' r'\usepackage{booktabs,longtable,graphicx,times}' '\n'
       r'\begin{document}' '\n' r'\begin{center}\Large Supplementary Materials\\[2pt]\normalsize A Gameplay Telemetry-Based Experimental Framework for Studying Player Flow in Real-Time 1v1 Combat Games: Design and Preliminary Evaluation (ICIET 2027)\end{center}' '\n'
       r'\section*{Fig. S1. Questionnaire Flow}(a) Each point is one questionnaire response; horizontal bar = median, vertical bar = IQR. (b) Participant-level mean in-game T17 score vs. questionnaire Flow.\\[4pt]\includegraphics[width=0.6\linewidth]{../figures/FigS1_questionnaire_flow.pdf}' '\n'       r'\clearpage\section*{Fig. S2. Telemetry indicators vs.\ questionnaire Flow}Participant level, by condition. (a) Scatter plots with least-squares lines; (b) rank plots (ranks within condition). Used to inspect differences between Pearson $r$ and Spearman $\rho$.\\[4pt]\includegraphics[width=0.92\linewidth]{../figures/FigS2a_scatter_telemetry_vs_flow.pdf}\clearpage\includegraphics[width=0.92\linewidth]{../figures/FigS2b_rank_telemetry_vs_flow.pdf}' '\n'
       r'\clearpage\section*{Fig. S3. Distributions}Participant-level histograms of questionnaire Flow (matched participants) and T01--T15 by condition; dashed lines = medians.\\[4pt]\includegraphics[width=0.85\linewidth]{../figures/FigS3_distributions.pdf}\clearpage' '\n'

       + '\n'.join(S) + r'\end{document}')
open(os.path.join(O, 'Supplementary_Tables.tex'), 'w').write(doc); print('written')
