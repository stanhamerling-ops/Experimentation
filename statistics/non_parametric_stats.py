import numpy as np
from scipy import stats


# =========================
# CHECKS
# =========================
def normality_check(sample, alpha=0.05):
    if len(sample) < 8:
        return "too small", np.nan

    _, p = stats.normaltest(sample)
    return ("violates normality", p) if p < alpha else ("normal", p)


def srm_check(sample_a, sample_b, alpha=0.05):
    observed = [len(sample_a), len(sample_b)]
    _, p = stats.chisquare(observed)
    return "SRM mismatch" if p < alpha else "OK"


def mann_whitney_test(sample_a, sample_b):
    _, p = stats.mannwhitneyu(sample_a, sample_b, alternative="two-sided")
    return p


# =====================================================
# ANALYSIS — 0-WAARDES OPNEMEN
# =====================================================
def analyze_with_zeros(set_a, set_b, alpha=0.05):
    avg_a = set_a.mean()
    avg_b = set_b.mean()
    med_a = set_a.median()
    med_b = set_b.median()

    impact_raw = (avg_b - avg_a) / avg_a if avg_a != 0 else np.nan
    impact_pct = impact_raw * 100
    p_value = mann_whitney_test(set_a, set_b)

    return {
        "nA": len(set_a),
        "nB": len(set_b),
        "normalA": normality_check(set_a, alpha)[0],
        "normalB": normality_check(set_b, alpha)[0],
        "srm": srm_check(set_a, set_b, alpha),
        "avgA": round(avg_a, 2),
        "avgB": round(avg_b, 2),
        "medA": round(med_a, 2),
        "medB": round(med_b, 2),
        "impact": f"{round(impact_pct, 1)}%",
        "p_value": round(p_value, 3),
    }


# =====================================================
# ANALYSIS — 0-WAARDES UITSLUITEN
# =====================================================
def analyze_no_zeros(set_a, set_b, alpha=0.05):
    set_a = np.array(set_a, dtype=float)
    set_b = np.array(set_b, dtype=float)

    set_a = set_a[set_a != 0]
    set_b = set_b[set_b != 0]

    avg_a = np.mean(set_a)
    avg_b = np.mean(set_b)
    med_a = np.median(set_a)
    med_b = np.median(set_b)

    impact_raw = (avg_b - avg_a) / avg_a if avg_a != 0 else np.nan
    impact_pct = impact_raw * 100
    p_value = mann_whitney_test(set_a, set_b)

    return {
        "nA": len(set_a),
        "nB": len(set_b),
        "normalA": normality_check(set_a, alpha)[0],
        "normalB": normality_check(set_b, alpha)[0],
        "srm": srm_check(set_a, set_b, alpha),
        "avgA": round(avg_a, 2),
        "avgB": round(avg_b, 2),
        "medA": round(med_a, 2),
        "medB": round(med_b, 2),
        "impact": f"{round(impact_pct, 1)}%",
        "p_value": round(p_value, 3),
    }