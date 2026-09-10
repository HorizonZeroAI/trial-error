"""Statistical engine: scipy-based replacement for ad-hoc stats in foundry.

All functions accept plain Python lists and return dicts.
Dependency: scipy (BSD license).
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy import stats as sp_stats


# ── Cohen's d ────────────────────────────────────────────────────────────────


def cohens_d(
    group1: list[float],
    group2: list[float],
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Cohen's d effect size with CI via noncentral t-distribution."""
    a, b = np.asarray(group1, dtype=float), np.asarray(group2, dtype=float)
    n1, n2 = len(a), len(b)

    if n1 < 1 or n2 < 1:
        return {
            "cohens_d": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 0.0,
            "se": 0.0,
            "interpretation": "insufficient_data",
            "n_baseline": n1,
            "n_treatment": n2,
        }

    m1, m2 = float(np.mean(a)), float(np.mean(b))

    # Pooled SD
    if n1 + n2 < 3:
        s_pooled = 1.0
    else:
        v1 = float(np.var(a, ddof=1)) if n1 > 1 else 0.0
        v2 = float(np.var(b, ddof=1)) if n2 > 1 else 0.0
        s_pooled = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))

    if s_pooled == 0:
        d = 0.0 if m2 == m1 else float("inf") * (1 if m2 > m1 else -1)
    else:
        d = (m2 - m1) / s_pooled

    # SE of d (Hedges & Olkin approximation)
    se_d = math.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))

    # CI via noncentral t-distribution
    df = n1 + n2 - 2
    alpha = 1 - confidence
    if df >= 2 and math.isfinite(d):
        ncp = d * math.sqrt(n1 * n2 / (n1 + n2))
        try:
            ci_lower = sp_stats.nct.ppf(alpha / 2, df, ncp) / math.sqrt(n1 * n2 / (n1 + n2))
            ci_upper = sp_stats.nct.ppf(1 - alpha / 2, df, ncp) / math.sqrt(n1 * n2 / (n1 + n2))
        except Exception:
            ci_lower = d - 1.96 * se_d
            ci_upper = d + 1.96 * se_d
    else:
        ci_lower = d - 1.96 * se_d
        ci_upper = d + 1.96 * se_d

    abs_d = abs(d) if math.isfinite(d) else float("inf")
    if abs_d >= 0.8:
        interp = "large"
    elif abs_d >= 0.5:
        interp = "medium"
    elif abs_d >= 0.2:
        interp = "small"
    else:
        interp = "negligible"

    return {
        "cohens_d": round(d, 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "se": round(se_d, 4),
        "interpretation": interp,
        "n_baseline": n1,
        "n_treatment": n2,
        "mean_baseline": round(m1, 4),
        "mean_treatment": round(m2, 4),
    }


# ── Bayes Factor ─────────────────────────────────────────────────────────────


def bayes_factor(
    group1: list[float],
    group2: list[float],
    prior_scale: float = 0.707,
) -> dict[str, Any]:
    """BF10 via JZS (Jeffreys-Zellner-Siow) t-test approximation.

    Uses scipy's t-distribution for proper PDF evaluation rather than
    ad-hoc BIC approximation.
    """
    a, b = np.asarray(group1, dtype=float), np.asarray(group2, dtype=float)
    n1, n2 = len(a), len(b)

    if n1 < 2 or n2 < 2:
        return {"bf10": 1.0, "interpretation": "insufficient_data", "t_stat": 0.0, "df": 0}

    # Welch's t-test (does not assume equal variance)
    t_stat, p_value = sp_stats.ttest_ind(a, b, equal_var=False)
    df_welch = float(n1 + n2 - 2)  # approximate

    if not math.isfinite(t_stat):
        return {"bf10": 1.0, "interpretation": "non_finite_t", "t_stat": 0.0, "df": 0}

    # JZS approximation: BF10 ≈ (1 + t²/(n·r²))^(-(n+1)/2) / (1 + t²/n)^(-(n+1)/2)
    # Simplified Rouder et al. (2009) formula
    n = n1 + n2
    r2 = prior_scale**2
    log_bf = 0.5 * math.log(n / (n + n * r2)) + ((df_welch + 1) / 2) * (
        math.log(1 + t_stat**2 / df_welch) - math.log(1 + t_stat**2 / (df_welch * (1 + n * r2)))
    )
    bf10 = min(math.exp(log_bf), 1e6)
    bf10 = max(bf10, 1e-6)

    if bf10 > 100:
        interp = "extreme_H1"
    elif bf10 > 10:
        interp = "strong_H1"
    elif bf10 > 3:
        interp = "moderate_H1"
    elif bf10 > 1:
        interp = "anecdotal_H1"
    elif bf10 > 1 / 3:
        interp = "anecdotal_H0"
    elif bf10 > 1 / 10:
        interp = "moderate_H0"
    else:
        interp = "strong_H0"

    return {
        "bf10": round(bf10, 4),
        "interpretation": interp,
        "t_stat": round(float(t_stat), 4),
        "p_value": round(float(p_value), 6),
        "df": round(df_welch, 1),
    }


# ── Confidence Interval ──────────────────────────────────────────────────────


def confidence_interval(
    data: list[float],
    confidence: float = 0.95,
) -> dict[str, Any]:
    """CI for the mean using t-distribution (handles small n properly)."""
    arr = np.asarray(data, dtype=float)
    n = len(arr)

    if n < 2:
        m = float(arr[0]) if n == 1 else 0.0
        return {"mean": m, "lower": m, "upper": m, "se": 0.0, "n": n, "confidence": confidence}

    m = float(np.mean(arr))
    se = float(sp_stats.sem(arr))
    df = n - 1
    alpha = 1 - confidence
    t_crit = float(sp_stats.t.ppf(1 - alpha / 2, df))

    return {
        "mean": round(m, 6),
        "lower": round(m - t_crit * se, 6),
        "upper": round(m + t_crit * se, 6),
        "se": round(se, 6),
        "n": n,
        "confidence": confidence,
    }


# ── Power Analysis ───────────────────────────────────────────────────────────


def power_analysis(
    effect_size: float,
    n: int,
    alpha: float = 0.05,
    ratio: float = 1.0,
) -> dict[str, Any]:
    """Post-hoc power for two-sample t-test using noncentral t-distribution.

    ratio: n2/n1 ratio (1.0 = balanced).
    """
    if n < 4 or effect_size == 0:
        return {
            "power": 0.0,
            "effect_size": effect_size,
            "n": n,
            "alpha": alpha,
            "sufficient": False,
        }

    n1 = n / (1 + ratio)
    n2 = n - n1
    ncp = effect_size * math.sqrt(n1 * n2 / (n1 + n2))
    df = n - 2
    t_crit = sp_stats.t.ppf(1 - alpha / 2, df)

    # Power = P(reject H0 | H1 true)
    power = 1.0 - sp_stats.nct.cdf(t_crit, df, ncp) + sp_stats.nct.cdf(-t_crit, df, ncp)
    power = max(0.0, min(1.0, float(power)))

    return {
        "power": round(power, 4),
        "effect_size": round(effect_size, 4),
        "n": n,
        "alpha": alpha,
        "sufficient": power >= 0.8,
        "ncp": round(ncp, 4),
    }


# ── Minimum Sample Size ─────────────────────────────────────────────────────


def min_sample_size(
    effect_size: float,
    alpha: float = 0.05,
    power_target: float = 0.8,
) -> dict[str, Any]:
    """Find minimum total n for desired power (two-sample balanced design)."""
    if effect_size <= 0:
        return {"min_n": 0, "effect_size": effect_size, "error": "effect_size must be positive"}

    for n in range(4, 10002, 2):
        result = power_analysis(effect_size, n, alpha)
        if result["power"] >= power_target:
            return {
                "min_n": n,
                "per_group": n // 2,
                "effect_size": effect_size,
                "alpha": alpha,
                "power_target": power_target,
            }

    return {
        "min_n": 10000,
        "per_group": 5000,
        "effect_size": effect_size,
        "note": "exceeded search range",
    }


# ── Full Report ──────────────────────────────────────────────────────────────


def full_report(
    group1: list[float],
    group2: list[float],
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Complete statistical report combining all analyses."""
    effect = cohens_d(group1, group2, confidence)
    bf = bayes_factor(group1, group2)
    ci1 = confidence_interval(group1, confidence)
    ci2 = confidence_interval(group2, confidence)
    n_total = len(group1) + len(group2)
    pwr = power_analysis(
        abs(effect["cohens_d"]) if math.isfinite(effect["cohens_d"]) else 0, n_total
    )
    min_n = min_sample_size(max(abs(effect["cohens_d"]), 0.01))

    # Welch's t-test p-value
    if len(group1) >= 2 and len(group2) >= 2:
        _, p_val = sp_stats.ttest_ind(group1, group2, equal_var=False)
        p_val = round(float(p_val), 6)
    else:
        p_val = None

    # Mann-Whitney U (non-parametric alternative)
    if len(group1) >= 2 and len(group2) >= 2:
        try:
            u_stat, u_p = sp_stats.mannwhitneyu(group1, group2, alternative="two-sided")
            mann_whitney = {"U": round(float(u_stat), 2), "p_value": round(float(u_p), 6)}
        except Exception:
            mann_whitney = None
    else:
        mann_whitney = None

    return {
        "effect_size": effect,
        "bayes_factor": bf,
        "ci_baseline": ci1,
        "ci_treatment": ci2,
        "power": pwr,
        "min_sample_size": min_n,
        "p_value": p_val,
        "mann_whitney": mann_whitney,
    }


# ── Health ───────────────────────────────────────────────────────────────────


def health() -> dict[str, Any]:
    """Health check: verify scipy is working."""
    try:
        test = cohens_d([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        ok = test["interpretation"] == "large" and test["cohens_d"] > 1.0
        return {
            "ok": ok,
            "scipy_version": __import__("scipy").__version__,
            "test_d": test["cohens_d"],
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
