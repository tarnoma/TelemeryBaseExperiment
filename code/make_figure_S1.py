"""Fig. S1: (a) questionnaire Flow by group; (b) participant-level mean in-game T17 vs questionnaire Flow.
Run analysis.py first (uses results/participant_level_*.csv and data/flow_questionnaire.xlsx)."""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '..', 'results'); F = os.path.join(HERE, '..', 'figures')
os.makedirs(F, exist_ok=True)
plt.rcParams.update({'font.family': 'serif', 'font.size': 7.5, 'axes.linewidth': 0.6})
BLUE, ORANGE, INK = '#2a78d6', '#eb6834', '#222222'
fx = pd.ExcelFile(os.path.join(HERE, '..', 'data', 'flow_questionnaire.xlsx')); S = {}
for c, idx in (('Adaptive', 0), ('Rule-based', 1)):
    d = fx.parse(fx.sheet_names[idx]); d.columns = ['ts', 'id'] + [f'q{i}' for i in range(1, 25)]; d['ts'] = pd.to_datetime(d.ts)
    if c == 'Rule-based': d = d[~((d.id == 10446) & (d.ts.dt.date.astype(str) == '2026-07-05'))]
    S[c] = d.iloc[:, 2:26].mean(axis=1)
P = {'Rule-based': pd.read_csv(os.path.join(R, 'participant_level_rule_based.csv')),
     'Adaptive': pd.read_csv(os.path.join(R, 'participant_level_adaptive.csv'))}
fig, ax = plt.subplots(1, 2, figsize=(3.45, 2.0), gridspec_kw={'width_ratios': [1, 1.25]})
rng = np.random.default_rng(1)
for i, (c, col, m) in enumerate((('Rule-based', BLUE, 'o'), ('Adaptive', ORANGE, '^'))):
    v = S[c]; ax[0].scatter(i + rng.uniform(-.12, .12, len(v)), v, s=14, color=col, marker=m, edgecolor='white', linewidth=.5, zorder=3)
    q1, md, q3 = np.percentile(v, [25, 50, 75]); ax[0].plot([i - .22, i + .36], [md, md], color=INK, lw=1.6, zorder=4)
    ax[0].plot([i + .3, i + .3], [q1, q3], color=INK, lw=1.0)
    ax[1].scatter(P[c].T17_mean, P[c].flow, s=16, color=col, marker=m, edgecolor='white', linewidth=.5, label=f'{c} (n = {len(P[c])})')
ax[0].set_xticks([0, 1]); ax[0].set_xticklabels(['Rule-based', 'Adaptive']); ax[0].set_xlim(-.5, 1.5)
ax[0].set_ylabel('Questionnaire Flow (1-5)'); ax[0].set_title('(a) By group (n = 22, 22)', fontsize=7.5)
ax[1].set_xlabel('Mean in-game T17 score'); ax[1].set_title('(b) Participant level', fontsize=7.5)
for a in ax:
    a.set_ylim(1, 5.2); a.spines[['top', 'right']].set_visible(False); a.grid(axis='y', color='#e6e6e6', lw=.5); a.set_axisbelow(True)
fig.legend(*ax[1].get_legend_handles_labels(), frameon=False, fontsize=6.5, loc='lower center', ncol=2, bbox_to_anchor=(.5, -.01))
fig.tight_layout(pad=.3, w_pad=.8, rect=(0, .08, 1, 1))
fig.savefig(os.path.join(F, 'FigS1_questionnaire_flow.pdf')); fig.savefig(os.path.join(F, 'FigS1_questionnaire_flow.png'), dpi=300)
print('saved Fig. S1')
