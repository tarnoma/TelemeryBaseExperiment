"""
Reproduces every statistic reported in the paper
"A Gameplay Telemetry-Based Experimental Framework for Studying Player Flow in
Real-Time 1v1 Combat Games: Design and Preliminary Evaluation" (ICIET 2027).

Inputs (place in ../data):
  telemetry.xlsx           sheets '(01)Rule Based 20 คน', '(02)22คน Adaptive'
  flow_questionnaire.xlsx  sheet 0 = adaptive responses, sheet 1 = rule-based responses
Outputs: ../results/S1 ... S11 (CSV)

Units of analysis
  encounter   = one boss fight (one telemetry row)
  participant = one tester within one condition (IDs were reused across the two
                independent groups, so an ID identifies a person only within a condition)
Questionnaire Flow exists once per participant, so telemetry is summarized per
participant (median; win rate and T17 by mean) before any association test.
"""
import os, warnings
import numpy as np, pandas as pd
from scipy import stats
from scipy.stats import false_discovery_control as bh
import statsmodels.api as sm
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data'); OUT = os.path.join(HERE, '..', 'results')
os.makedirs(OUT, exist_ok=True)

T = ['T01_Accuracy', 'T02_ReactionTime', 'T03_RTVariability', 'T04_AttackFrequency', 'T05_DefenseFrequency',
     'T06_HitRate', 'T07_DamageEfficiency', 'T08_DamageTakenRate', 'T09_WinLoss', 'T10_ActionDensity',
     'T11_InputStability', 'T12_ComboSuccessRate', 'T13_IdleTimeRatio', 'T14_ErrorRate', 'T15_SessionDuration']
UNITS = {'T01': 'ratio 0-1', 'T02': 's', 'T03': 's', 'T04': 'attacks/s', 'T05': 'actions/s', 'T06': 'ratio 0-1',
         'T07': 'damage/attack', 'T08': 'damage/s', 'T09': 'win rate (0-1)', 'T10': 'actions/s', 'T11': '1/variance (s^-2)',
         'T12': 'ratio 0-1', 'T13': 'ratio 0-1', 'T14': 'ratio 0-1', 'T15': 's'}
ITEMS = [f'q{i}' for i in range(1, 25)]
DIMS = {'Concentration': ITEMS[0:4], 'Challenge-skill balance': ITEMS[4:8], 'Control / system response': ITEMS[8:12],
        'Enjoyment / motivation': ITEMS[12:16], 'Time / deep engagement': ITEMS[16:20], 'Pressure / flow experience': ITEMS[20:24]}
COND = {'Rule-based': '(01)Rule Based 20 คน', 'Adaptive': '(02)22คน Adaptive'}

# ---------------- load ----------------
tx = pd.ExcelFile(os.path.join(DATA, 'telemetry.xlsx'))
enc = {}
for c, sheet in COND.items():
    d = tx.parse(sheet).iloc[1:].copy()                                   # row 0 = header description
    d = d[~d['encounter'].astype(str).str.startswith('รวม')]               # drop per-participant summary rows
    for col in T + ['userID', 'raw_reactionSamples', 'T17_FlowScore', 'BossLevel', 'encounter']:
        d[col] = pd.to_numeric(d[col], errors='coerce')
    d['T02_T03_undefined'] = d['raw_reactionSamples'] < 2                  # T02/T03 undefined, not zero
    d.loc[d['T02_T03_undefined'], ['T02_ReactionTime', 'T03_RTVariability']] = np.nan
    enc[c] = d

fx = pd.ExcelFile(os.path.join(DATA, 'flow_questionnaire.xlsx'))
surv = {}
for c, idx in (('Adaptive', 0), ('Rule-based', 1)):
    d = fx.parse(fx.sheet_names[idx]); d.columns = ['timestamp', 'userID'] + ITEMS
    d['timestamp'] = pd.to_datetime(d['timestamp'])
    if c == 'Rule-based':   # duplicate ID 10446: keep the response on the session date (2026-07-27)
        d = d[~((d['userID'] == 10446) & (d['timestamp'].dt.date.astype(str) == '2026-07-05'))]
    d['flow'] = d[ITEMS].mean(axis=1)
    surv[c] = d.reset_index(drop=True)

def alpha(m):
    m = np.asarray(m, float); k = m.shape[1]
    return k / (k - 1) * (1 - m.var(axis=0, ddof=1).sum() / m.sum(axis=1).var(ddof=1))

def fisher_ci(r, n, spearman=False):
    se = np.sqrt((1 + r * r / 2) / (n - 3)) if spearman else 1 / np.sqrt(n - 3)   # Bonett-Wright for rho
    z = np.arctanh(r); return np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)

def participant_table(c):
    d = enc[c]; g = d.groupby('userID')
    m = g[T].median(); m['T09_WinLoss'] = g['T09_WinLoss'].mean(); m['T17_mean'] = g['T17_FlowScore'].mean()
    m['n_encounters'] = g.size()
    return m.join(surv[c].set_index('userID')['flow'], how='inner')     # matched participants only

P = {c: participant_table(c) for c in COND}
P['Rule-based'].to_csv(os.path.join(OUT, 'participant_level_rule_based.csv'))
P['Adaptive'].to_csv(os.path.join(OUT, 'participant_level_adaptive.csv'))

# ---------------- S1 dataset summary ----------------
rows = []
for c in COND:
    d = enc[c]; g = d.groupby('userID').size()
    rows.append({'condition': c, 'participants_telemetry': d.userID.nunique(), 'questionnaire_responses': len(surv[c]),
                 'participants_matched': len(P[c]), 'encounters': len(d),
                 'encounters_per_participant_median': g.median(), 'min': g.min(), 'max': g.max(),
                 'duration_median_s': d.T15_SessionDuration.median(), 'duration_q1': d.T15_SessionDuration.quantile(.25),
                 'duration_q3': d.T15_SessionDuration.quantile(.75), 'wins': int((d.status == 'WIN').sum()),
                 'win_pct': 100 * (d.status == 'WIN').mean(), 'max_boss_level': d.BossLevel.max(),
                 'T17_zero': int((d.T17_FlowScore == 0).sum()), 'reaction_samples_lt2': int(d.T02_T03_undefined.sum()),
                 'T11_gt50': int((d.T11_InputStability > 50).sum())})
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'S1_dataset_summary.csv'), index=False)

# ---------------- S2/S3 questionnaire quality (step 1) ----------------
rel, items_out = [], []
for c in COND:
    d = surv[c]
    rel.append({'condition': c, 'scale': 'All 24 items', 'alpha': alpha(d[ITEMS]), 'mean': d.flow.mean(), 'sd': d.flow.std(),
                'mean_inter_item_r': d[ITEMS].corr().values[np.triu_indices(24, 1)].mean()})
    for name, it in DIMS.items():
        s = d[it].mean(axis=1)
        rel.append({'condition': c, 'scale': name, 'alpha': alpha(d[it]), 'mean': s.mean(), 'sd': s.std(),
                    'mean_inter_item_r': d[it].corr().values[np.triu_indices(4, 1)].mean()})
        for q in it:
            rest = d[[x for x in it if x != q]]
            items_out.append({'condition': c, 'dimension': name, 'item': q, 'mean': d[q].mean(), 'sd': d[q].std(),
                              'floor_pct': 100 * (d[q] == 1).mean(), 'ceiling_pct': 100 * (d[q] == 5).mean(),
                              'corrected_item_total_r_scale': np.corrcoef(d[q], d[ITEMS].sum(axis=1) - d[q])[0, 1],
                              'item_rest_r_dimension': np.corrcoef(d[q], rest.sum(axis=1))[0, 1],
                              'alpha_if_deleted_dimension': alpha(rest)})
pd.DataFrame(rel).to_csv(os.path.join(OUT, 'S2_questionnaire_reliability.csv'), index=False)
pd.DataFrame(items_out).to_csv(os.path.join(OUT, 'S3_questionnaire_item_statistics.csv'), index=False)

# ---------------- S4/S5 descriptive statistics (step 2) ----------------
def describe(x, n_total=None):
    x = pd.Series(x, dtype=float); v = x.dropna(); q1, q3 = v.quantile([.25, .75]); iqr = q3 - q1
    return {'n': len(v), 'mean': v.mean(), 'sd': v.std(), 'median': v.median(), 'q1': q1, 'q3': q3,
            'min': v.min(), 'max': v.max(), 'skewness': stats.skew(v), 'kurtosis_excess': stats.kurtosis(v),
            'shapiro_p': stats.shapiro(v).pvalue if len(v) >= 3 else np.nan,
            'missing_pct': 100 * x.isna().mean(),
            'outliers_tukey_n': int(((v < q1 - 1.5 * iqr) | (v > q3 + 1.5 * iqr)).sum())}
flow_desc = [dict(condition=c, **describe(surv[c].flow)) for c in COND]
pd.DataFrame(flow_desc).to_csv(os.path.join(OUT, 'S4_flow_descriptives.csv'), index=False)
desc = []
for c in COND:
    for t in T:
        desc.append(dict(condition=c, level='participant (median per participant)', indicator=t, unit=UNITS[t[:3]], **describe(P[c][t])))
        desc.append(dict(condition=c, level='encounter', indicator=t, unit=UNITS[t[:3]], **describe(enc[c][t])))
pd.DataFrame(desc).to_csv(os.path.join(OUT, 'S5_telemetry_descriptives.csv'), index=False)

# ---------------- S6 correlations (step 3A: 15 telemetry x 2 methods) ----------------
corr = []
for c in COND:
    m = P[c]; rows = []
    for t in T + ['T17_mean']:
        mm = m[[t, 'flow']].dropna(); n = len(mm)
        r, pr = stats.pearsonr(mm[t], mm.flow); rho, ps = stats.spearmanr(mm[t], mm.flow)
        rl, rh = fisher_ci(r, n); sl, sh = fisher_ci(rho, n, True)
        rows.append({'condition': c, 'indicator': t, 'n': n, 'pearson_r': r, 'pearson_ci_low': rl, 'pearson_ci_high': rh,
                     'pearson_p': pr, 'spearman_rho': rho, 'spearman_ci_low': sl, 'spearman_ci_high': sh, 'spearman_p': ps})
    R = pd.DataFrame(rows); fam = R.indicator.isin(T)   # FDR family = 15 tests per condition and method; T17 excluded
    R.loc[fam, 'pearson_q_BH'] = bh(R.loc[fam, 'pearson_p']); R.loc[fam, 'spearman_q_BH'] = bh(R.loc[fam, 'spearman_p'])
    corr.append(R)
pd.concat(corr).to_csv(os.path.join(OUT, 'S6_correlations_pearson_spearman.csv'), index=False)

# ---------------- S7-S10 multicollinearity + multiple regression (step 3B) ----------------
vif_rows, model_rows, coef_rows = [], [], []
for c in COND:
    m = P[c]
    tag = c.lower().replace('-', '_')
    m[T].corr(method='pearson').to_csv(os.path.join(OUT, f'S7_correlation_matrix_pearson_{tag}.csv'))
    m[T].corr(method='spearman').to_csv(os.path.join(OUT, f'S7_correlation_matrix_spearman_{tag}.csv'))
    cc = m[T + ['flow']].dropna()                                    # complete cases (T02/T03 undefined for some)
    Z = (cc[T] - cc[T].mean()) / cc[T].std()                         # standardized predictors -> standardized beta
    yz = (cc.flow - cc.flow.mean()) / cc.flow.std()
    inv = np.linalg.inv(np.corrcoef(Z.T.values)); vif = np.diag(inv)
    for t, v in zip(T, vif): vif_rows.append({'condition': c, 'indicator': t, 'VIF': v, 'n_complete': len(cc)})
    fit = sm.OLS(yz, sm.add_constant(Z)).fit()
    model_rows.append({'condition': c, 'n_complete_cases': len(cc), 'predictors': len(T), 'df_resid': fit.df_resid,
                       'R2': fit.rsquared, 'adj_R2': fit.rsquared_adj, 'F': fit.fvalue, 'model_p': fit.f_pvalue,
                       'max_VIF': vif.max(), 'condition_number': np.linalg.cond(np.corrcoef(Z.T.values))})
    ci = fit.conf_int()
    for i, t in enumerate(T):
        coef_rows.append({'condition': c, 'indicator': t, 'beta_std': fit.params[t], 'SE': fit.bse[t], 't': fit.tvalues[t],
                          'p': fit.pvalues[t], 'ci_low': ci.loc[t, 0], 'ci_high': ci.loc[t, 1], 'VIF': vif[i]})
pd.DataFrame(vif_rows).to_csv(os.path.join(OUT, 'S8_VIF.csv'), index=False)
pd.DataFrame(model_rows).to_csv(os.path.join(OUT, 'S9_multiple_regression_model.csv'), index=False)
pd.DataFrame(coef_rows).to_csv(os.path.join(OUT, 'S10_multiple_regression_coefficients.csv'), index=False)

# ---------------- S11 group comparison ----------------
a, b = surv['Rule-based'], surv['Adaptive']; comp = []
for name, it in [('Flow (24 items)', ITEMS)] + list(DIMS.items()):
    xa, xb = a[it].mean(axis=1), b[it].mean(axis=1); u = stats.mannwhitneyu(xa, xb, alternative='two-sided')
    comp.append({'scale': name, 'rule_median': xa.median(), 'adaptive_median': xb.median(), 'U': u.statistic,
                 'p': u.pvalue, 'rank_biserial_r': 2 * u.statistic / (len(xa) * len(xb)) - 1})
pd.DataFrame(comp).to_csv(os.path.join(OUT, 'S11_group_comparison_mann_whitney.csv'), index=False)
print('Done. Results written to', os.path.abspath(OUT))
