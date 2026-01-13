# statistics/non_parametric_stats.py

import numpy as np
from scipy import stats


def normality_check(sample, alpha=0.05):
    if len(sample) < 8:
        return "too small", np.nan

    k2, p = stats.normaltest(sample)
    return ("violates normality", p) if p < alpha else ("normal", p)


def srm_check(sample_a, sample_b, alpha=0.05):
    observed = [len(sample_a), len(sample_b)]
    chi2, p = stats.chisquare(observed)
    return "SRM mismatch" if p < alpha else "OK"


def mann_whitney_test(sample_a, sample_b):
    u, p = stats.mannwhitneyu(sample_a, sample_b, alternative="two-sided")
    return p


def run_non_parametric_analysis(set_a, set_b, alpha=0.05):
    avg_a = set_a.mean()
    avg_b = set_b.mean()

    impact = ((avg_b - avg_a) / avg_a) * 100 if avg_a != 0 else np.inf

    return {
        "nA": len(set_a),
        "nB": len(set_b),
        "normalA": normality_check(set_a, alpha)[0],
        "normalB": normality_check(set_b, alpha)[0],
        "srm": srm_check(set_a, set_b, alpha),
        "avgA": avg_a,
        "avgB": avg_b,
        "medA": round(set_a.median(), 1),
        "medB": round(set_b.median(), 1),
        "impact": impact,
        "p_value": mann_whitney_test(set_a, set_b),
    }