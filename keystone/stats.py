"""Statistical inference: classic 50/50 A/B test, MDE, cannibalization, and lead-time response."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from keystone.config import AB_CONTROL_CASH_RATE, AB_FENCE, AB_TREATMENT_POINTS, CONVERSION_GUARDRAIL
from keystone.economics import effective_promo_rate


def minimum_detectable_effect(baseline: float, n_per_arm: int, alpha: float = 0.05, power: float = 0.80) -> float:
    """Absolute MDE for a two-sided two-proportion z-test."""
    if n_per_arm < 2 or not 0 < baseline < 1:
        return float("nan")
    z = stats.norm.ppf(1.0 - alpha / 2.0) + stats.norm.ppf(power)
    return float(z * math.sqrt(2.0 * baseline * (1.0 - baseline) / n_per_arm))


def two_proportion_z(success_a: int, n_a: int, success_b: int, n_b: int) -> tuple[float, float]:
    """Return (difference a - b, two-sided p-value)."""
    p1 = success_a / n_a
    p2 = success_b / n_b
    pooled = (success_a + success_b) / (n_a + n_b)
    se = math.sqrt(pooled * (1.0 - pooled) * (1.0 / n_a + 1.0 / n_b))
    if se == 0:
        return p1 - p2, 1.0
    z = (p1 - p2) / se
    return float(p1 - p2), float(2.0 * stats.norm.sf(abs(z)))


def ab_test_readout(sessions: pd.DataFrame, fence_id: str = AB_FENCE) -> dict:
    """Evaluate the 50/50 A/B test on member_web: Group A (-6% cash) vs Group B (9% points)."""
    sub = sessions[(sessions["fence_id"] == fence_id) & (sessions["variant"].isin(["control_cash", "treatment_points"]))]
    arms: dict[str, dict] = {}
    for arm_name, df in sub.groupby("variant"):
        n = int(len(df))
        bookings = int(df["converted"].sum())
        booked = df[df["converted"] == 1]
        arms[str(arm_name)] = {
            "sessions": n,
            "bookings": bookings,
            "cvr": bookings / n,
            "gbv": float(df["gbv"].sum()),
            "promo_cost": float(df["promo_cost"].sum()),
            "contribution": float(df["contribution"].sum()),
            "cps": float(df["contribution"].mean()),
            "cps_std": float(df["contribution"].std(ddof=1)),
            "cancel_rate": float(booked["cancelled"].mean()) if bookings else 0.0,
            "cannibalization_share": float(booked["cannibalized"].mean()) if bookings else 0.0,
        }

    control = arms["control_cash"]
    treatment = arms["treatment_points"]

    cvr_diff, cvr_p = two_proportion_z(
        treatment["bookings"], treatment["sessions"], control["bookings"], control["sessions"]
    )
    welch = stats.ttest_ind_from_stats(
        treatment["cps"],
        treatment["cps_std"],
        treatment["sessions"],
        control["cps"],
        control["cps_std"],
        control["sessions"],
        equal_var=False,
        alternative="two-sided",
    )
    cps_diff = treatment["cps"] - control["cps"]
    se = math.sqrt(
        treatment["cps_std"] ** 2 / treatment["sessions"] + control["cps_std"] ** 2 / control["sessions"]
    )
    z95 = float(stats.norm.ppf(0.975))
    mde = minimum_detectable_effect(control["cvr"], min(control["sessions"], treatment["sessions"]))
    rel_cvr = treatment["cvr"] / control["cvr"] - 1.0

    cvr_breach = cvr_p < 0.05 and rel_cvr < -CONVERSION_GUARDRAIL
    if welch.pvalue < 0.05 and cps_diff > 0 and not cvr_breach:
        status = "ship_points"
    elif welch.pvalue < 0.05 and cps_diff < 0:
        status = "keep_cash"
    else:
        status = "extend"

    return {
        "fence_id": fence_id,
        "control_rate": AB_CONTROL_CASH_RATE,
        "treatment_points_rate": AB_TREATMENT_POINTS,
        "treatment_effective_rate": effective_promo_rate("points", AB_TREATMENT_POINTS),
        "control": control,
        "treatment": treatment,
        "cvr_diff": float(cvr_diff),
        "cvr_pvalue": float(cvr_p),
        "cvr_mde": float(mde),
        "relative_cvr": float(rel_cvr),
        "cps_diff": float(cps_diff),
        "cps_pvalue": float(welch.pvalue),
        "cps_ci_low": float(cps_diff - z95 * se),
        "cps_ci_high": float(cps_diff + z95 * se),
        "status": status,
    }


def lead_time_summary(sessions: pd.DataFrame) -> dict:
    """Compare short lead (0-3 days) vs medium/long lead (8+ days) inside app_only."""
    app = sessions[sessions["fence_id"] == "app_only"]
    short = app[app["lead_bucket"] == "0-3"]
    long_b = app[app["lead_bucket"].isin(["8-21", "22+"])]
    short_b = short[short["converted"] == 1]
    long_booked = long_b[long_b["converted"] == 1]
    return {
        "short_cvr": float(short["converted"].mean()),
        "short_cannibalized": float(short_b["cannibalized"].mean()) if len(short_b) else 0.0,
        "long_cvr": float(long_b["converted"].mean()),
        "long_cannibalized": float(long_booked["cannibalized"].mean()) if len(long_booked) else 0.0,
    }


def small_basket_diagnostic(sessions: pd.DataFrame, threshold: float = 180.0) -> dict:
    """Diagnose low-basket orders in cart_recovery."""
    cart = sessions[sessions["fence_id"] == "cart_recovery"]
    small = cart[cart["public_sell"] < threshold]
    large = cart[cart["public_sell"] >= threshold]
    return {
        "threshold": threshold,
        "small_share": float(len(small) / len(cart)) if len(cart) else 0.0,
        "small_cps": float(small["contribution"].mean()) if len(small) else 0.0,
        "large_cps": float(large["contribution"].mean()) if len(large) else 0.0,
    }
