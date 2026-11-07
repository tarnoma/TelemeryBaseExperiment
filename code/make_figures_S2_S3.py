"""Fig. S2: scatter (a) and rank (b) plots of T01-T15 vs questionnaire Flow, by condition (participant level).
Fig. S3: distributions (histograms) of questionnaire Flow and T01-T15, by condition (participant level).
Run analysis.py first."""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '..', 'results'); F = os.path.join(HERE, '..', 'figures')
plt.rcParams.update({'font.family': 'serif', 'font.size': 7, 'axes.linewidth': 0.5})
BLUE, ORANGE = '#2a78d6', '#eb6834'
STY = {'Rule-based': (BLUE, 'o'), 'Adaptive': (ORANGE, '^')}
P = {'Rule-based': pd.read_csv(os.path.join(R, 'participant_level_rule_based.csv')),
     'Adaptive': pd.read_csv(os.path.join(R, 'participant_level_adaptive.csv'))}
C = pd.read_csv(os.path.join(R, 'S6_correlations_pearson_spearman.csv'))
T = [c for c in P['Rule-based'].columns if c[:1] == 'T' and c[1:3].isdigit() and int(c[1:3]) <= 15]

def grid(rank, fname, title):
    fig, axes = plt.subplots(3, 5, figsize=(10, 6.6))
    for ax, t in zip(axes.flat, T):
        lines = []
        for cond, (col, mk) in STY.items():
            d = P[cond][[t, 'flow']].dropna()
            x, y = (d[t].rank(), d.flow.rank()) if rank else (d[t], d.flow)
            ax.scatter(x, y, s=12, color=col, marker=mk, edgecolor='white', linewidth=0.4, alpha=0.9)
            if not rank and len(d) > 2:
                b = np.polyfit(x, y, 1); xs = np.linspace(x.min(), x.max(), 2); ax.plot(xs, np.polyval(b, xs), color=col, lw=0.8)
            c = C[(C.condition == cond) & (C.indicator == t)].iloc[0]
            lines.append(f"{'R' if cond == 'Rule-based' else 'A'}: r={c.pearson_r:.2f}, ρ={c.spearman_rho:.2f}")
        ax.set_title(t.replace('_', ' '), fontsize=7.5)
        ax.text(0.02, 0.98, '\n'.join(lines), transform=ax.transAxes, va='top', fontsize=6, color='#333')
        ax.spines[['top', 'right']].set_visible(False); ax.tick_params(width=0.4, length=2)
        if rank: ax.set_xlabel('rank (indicator)', fontsize=6)
    for ax in axes[:, 0]: ax.set_ylabel('rank (Flow)' if rank else 'Questionnaire Flow')
    h = [plt.Line2D([], [], color=c, marker=m, ls='' if rank else '-', ms=4) for c, m in STY.values()]
    fig.legend(h, [f'{k} (n = {len(P[k])})' for k in STY], loc='lower center', ncol=2, frameon=False)
    fig.suptitle(title, fontsize=9); fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(os.path.join(F, fname + '.pdf')); fig.savefig(os.path.join(F, fname + '.png'), dpi=200); plt.close(fig)

grid(False, 'FigS2a_scatter_telemetry_vs_flow', 'Fig. S2a. Participant-level scatter plots with least-squares lines (R = rule-based, A = adaptive)')
grid(True, 'FigS2b_rank_telemetry_vs_flow', 'Fig. S2b. Rank plots (ranks within condition) of the same data')

fig, axes = plt.subplots(4, 4, figsize=(10, 8))
for ax, t in zip(axes.flat, ['flow'] + T):
    allv = pd.concat([P[k][t] for k in STY]).dropna(); bins = np.histogram_bin_edges(allv, bins=10)
    for cond, (col, _) in STY.items():
        v = P[cond][t].dropna()
        ax.hist(v, bins=bins, histtype='stepfilled', alpha=0.35, color=col, edgecolor=col, linewidth=0.8)
        ax.axvline(v.median(), color=col, lw=1, ls='--')
    sk = [f"{'R' if k == 'Rule-based' else 'A'}: skew={stats.skew(P[k][t].dropna()):.2f}" for k in STY]
    ax.text(0.98, 0.98, '\n'.join(sk), transform=ax.transAxes, ha='right', va='top', fontsize=6)
    ax.set_title('Questionnaire Flow (matched)' if t == 'flow' else t.replace('_', ' '), fontsize=7.5)
    ax.spines[['top', 'right']].set_visible(False); ax.tick_params(width=0.4, length=2)
h = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.5) for c, _ in STY.values()]
fig.legend(h, list(STY), loc='lower center', ncol=2, frameon=False)
fig.suptitle('Fig. S3. Participant-level distributions (dashed line = median)', fontsize=9); fig.tight_layout(rect=(0, 0.03, 1, 0.97))
fig.savefig(os.path.join(F, 'FigS3_distributions.pdf')); fig.savefig(os.path.join(F, 'FigS3_distributions.png'), dpi=200)
print('saved Fig. S2a, S2b, S3')
