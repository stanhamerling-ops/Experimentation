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
    # ---------- RAW CALCULATIONS ----------
    avg_a = set_a.mean()
    avg_b = set_b.mean()
    med_a = set_a.median()
    med_b = set_b.median()

    impact_raw = (avg_b - avg_a) / avg_a if avg_a != 0 else np.nan
    impact_pct = impact_raw * 100
    p_value = mann_whitney_test(set_a, set_b)

    # ---------- FORMATTED OUTPUT ----------
    return {
        "nA": len(set_a),
        "nB": len(set_b),
        "normalA": normality_check(set_a, alpha)[0],
        "normalB": normality_check(set_b, alpha)[0],
        "srm": srm_check(set_a, set_b, alpha),

        # formatting rules
        "avgA": round(avg_a, 2),
        "avgB": round(avg_b, 2),
        "medA": round(med_a, 2),
        "medB": round(med_b, 2),
        "impact": f"{round(impact_pct, 1)}%",
        "p_value": round(p_value, 3),
    }