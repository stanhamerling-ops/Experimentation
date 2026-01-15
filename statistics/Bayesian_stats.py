# statistics/bayesian_stats.py

import numpy as np
from math import lgamma
from scipy.stats import beta

# ------------------------------
# Internal helpers (PURE)
# ------------------------------

def _h(a, b, c, d):
    num = lgamma(a + c) + lgamma(b + d) + lgamma(a + b) + lgamma(c + d)
    den = (
        lgamma(a)
        + lgamma(b)
        + lgamma(c)
        + lgamma(d)
        + lgamma(a + b + c + d)
    )
    return np.exp(num - den)

def _g0(a, b, c):
    return np.exp(
        lgamma(a + b) + lgamma(a + c)
        - (lgamma(a + b + c) + lgamma(a))
    )

def _g(a, b, c, d):
    total = _g0(a, b, c)
    while d > 1:
        d -= 1
        total += _h(a, b, c, d) / d
    return total

# ------------------------------
# PUBLIC API (ONLY THIS)
# ------------------------------

def prob_variant_beats_control(
    control_success: float,
    control_total: float,
    variant_success: float,
    variant_total: float,
) -> float:
    """
    Returns P(Variant > Control) using Beta-Binomial model
    with uniform Beta(1,1) priors.
    """

    a_c = control_success + 1
    b_c = control_total - control_success + 1
    a_v = variant_success + 1
    b_v = variant_total - variant_success + 1

    beta_c = beta(a_c, b_c)
    beta_v = beta(a_v, b_v)

    return _g(
        beta_v.args[0],
        beta_v.args[1],
        beta_c.args[0],
        beta_c.args[1],
    )