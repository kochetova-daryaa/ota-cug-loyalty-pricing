"""Synthetic 90-day session book with 5 price fences and a 50/50 A/B test on member_web."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from keystone.config import (
    AB_CONTROL_CASH_RATE,
    AB_FENCE,
    AB_TREATMENT_POINTS,
    BASE_MARKUP,
    CANCEL_KEEP,
    CITIES,
    FENCE_ORDER,
    FENCES,
    HOTEL_NAMES,
    N_SESSIONS,
    PAYMENT_COST_RATE,
    SAMPLE_END,
    SAMPLE_START,
    SEED,
)
from keystone.economics import effective_promo_rate, perceived_benefit_rate


@dataclass
class Book:
    sessions: pd.DataFrame
    hotels: pd.DataFrame
    fences: pd.DataFrame
    meta: pd.DataFrame


def build_hotels() -> pd.DataFrame:
    rows = []
    hotel_id = 1
    for city, base_net, demand_mult in CITIES:
        for idx, name in enumerate(HOTEL_NAMES[city]):
            stars = 3 + (idx % 3)
            star_mult = 0.86 if stars == 3 else 1.00 if stars == 4 else 1.24
            rows.append(
                {
                    "hotel_id": hotel_id,
                    "hotel_name": name,
                    "city": city,
                    "stars": stars,
                    "base_net": round(base_net * star_mult, 2),
                    "demand_mult": demand_mult,
                }
            )
            hotel_id += 1
    return pd.DataFrame(rows)


def build_fences() -> pd.DataFrame:
    rows = []
    for fence_id in FENCE_ORDER:
        p = FENCES[fence_id]
        rows.append(
            {
                "fence_id": p.fence_id,
                "share": p.share,
                "base_cvr": p.base_cvr,
                "session_cost": p.session_cost,
                "mechanic_now": p.mechanic_now,
                "nominal_rate_now": p.nominal_rate_now,
                "effective_rate_now": effective_promo_rate(p.mechanic_now, p.nominal_rate_now),
                "organic_share_prior": p.organic_share_prior,
                "uplift_elasticity": p.uplift_elasticity,
                "min_margin_floor": p.min_margin_floor,
                "proposed_mechanic": p.proposed_mechanic,
                "proposed_nominal_rate": p.proposed_nominal_rate,
                "proposed_rule_code": p.proposed_rule_code,
            }
        )
    return pd.DataFrame(rows)


def generate(
    n_sessions: int = N_SESSIONS,
    seed: int = SEED,
    sample_start: str = SAMPLE_START,
    sample_end: str = SAMPLE_END,
) -> Book:
    rng = np.random.default_rng(seed)
    hotels = build_hotels()
    fences = build_fences()

    dates = pd.date_range(sample_start, sample_end, freq="D")
    day_weights = np.linspace(1.12, 0.90, len(dates))
    day_weights = day_weights / day_weights.sum()
    chosen_days = rng.choice(dates, size=n_sessions, p=day_weights)
    session_dates = pd.to_datetime(chosen_days)
    weeks = pd.Series(session_dates).dt.strftime("%G-W%V").to_numpy()

    hotel_idx = rng.integers(0, len(hotels), size=n_sessions)
    hotel_ids = hotels["hotel_id"].to_numpy()[hotel_idx]
    cities = hotels["city"].to_numpy()[hotel_idx]
    base_nets = hotels["base_net"].to_numpy()[hotel_idx]
    demand_mults = hotels["demand_mult"].to_numpy()[hotel_idx]

    fence_probs = np.array([FENCES[f].share for f in FENCE_ORDER])
    fence_probs = fence_probs / fence_probs.sum()
    fence_idx = rng.choice(len(FENCE_ORDER), size=n_sessions, p=fence_probs)
    fence_ids = np.array(FENCE_ORDER)[fence_idx]

    lead_days = rng.choice(
        [1, 2, 5, 10, 16, 28, 45],
        size=n_sessions,
        p=[0.14, 0.14, 0.22, 0.20, 0.14, 0.10, 0.06],
    )
    lead_bucket = np.where(
        lead_days <= 3,
        "0-3",
        np.where(lead_days <= 7, "4-7", np.where(lead_days <= 21, "8-21", "22+")),
    )
    nights = rng.choice([1, 2, 3, 4, 5], size=n_sessions, p=[0.24, 0.34, 0.22, 0.12, 0.08])

    season_mult = np.where(session_dates.month == 8, 1.09, np.where(session_dates.month == 9, 1.01, 0.93))
    hotel_net = np.round(base_nets * nights * season_mult * rng.uniform(0.94, 1.06, size=n_sessions), 2)
    public_sell = np.round(hotel_net * (1.0 + BASE_MARKUP), 2)

    # Competitor public price is at parity (~1.00), but competitors offer ~4.5% closed-group discounts
    comp_public_price = np.round(public_sell * rng.normal(1.00, 0.015, size=n_sessions), 2)
    comp_cug_price = np.round(public_sell * rng.normal(0.955, 0.018, size=n_sessions), 2)

    variant = np.full(n_sessions, "none", dtype=object)
    is_ab = fence_ids == AB_FENCE
    ab_draw = rng.random(n_sessions) < 0.50
    variant = np.where(is_ab & ab_draw, "control_cash", np.where(is_ab & (~ab_draw), "treatment_points", "none"))

    mechanic = np.array([FENCES[f].mechanic_now for f in fence_ids], dtype=object)
    nominal_rate = np.array([FENCES[f].nominal_rate_now for f in fence_ids], dtype=float)

    # Apply Group B treatment on member_web
    treat_mask = variant == "treatment_points"
    mechanic = np.where(treat_mask, "points", mechanic)
    nominal_rate = np.where(treat_mask, AB_TREATMENT_POINTS, nominal_rate)
    ctrl_mask = variant == "control_cash"
    mechanic = np.where(ctrl_mask, "cash", mechanic)
    nominal_rate = np.where(ctrl_mask, AB_CONTROL_CASH_RATE, nominal_rate)

    eff_rate = np.array([effective_promo_rate(m, r) for m, r in zip(mechanic, nominal_rate)])
    perceived = np.array([perceived_benefit_rate(m, r) for m, r in zip(mechanic, nominal_rate)])

    base_cvr = np.array([FENCES[f].base_cvr for f in fence_ids])
    uplift_elas = np.array([FENCES[f].uplift_elasticity for f in fence_ids])
    lead_elas_boost = np.where(lead_days <= 3, 0.72, np.where(lead_days <= 7, 0.95, 1.18))

    # Conversion probability decomposes into organic baseline + promo-induced uplift
    organic_prior = np.array([FENCES[f].organic_share_prior for f in fence_ids])
    lead_org_shift = np.where(
        fence_ids == "app_only",
        np.where(lead_days <= 3, 0.18, np.where(lead_days >= 8, -0.1056, 0.0)),
        0.0,
    )
    organic_prior_eff = np.clip(organic_prior + lead_org_shift, 0.10, 0.95)
    cvr_organic_base = base_cvr * organic_prior * demand_mults
    cvr_organic = base_cvr * organic_prior_eff * demand_mults
    # Make Group B conversion nearly identical to Group A (~4.5% vs ~4.4%, within noise)
    perceived_adj = np.where(treat_mask, AB_CONTROL_CASH_RATE * 0.96, perceived)
    cvr_uplift = base_cvr * (1.0 - organic_prior) + base_cvr * uplift_elas * lead_elas_boost * perceived_adj * 0.55
    cvr_uplift = np.where(mechanic == "none", 0.0, cvr_uplift)
    cvr_total = np.clip(cvr_organic_base + cvr_uplift, 0.005, 0.25)

    u_conv = rng.random(n_sessions)
    converted = (u_conv < cvr_total).astype(int)
    # A booking is "cannibalized" if the user would have converted under cvr_organic alone
    cannibalized = ((u_conv < cvr_organic) & (mechanic != "none") & (converted == 1)).astype(int)
    incremental = ((converted == 1) & (cannibalized == 0)).astype(int)

    cancel_prob = np.array([FENCES[f].cancel_base for f in fence_ids]) + np.where(lead_days > 21, 0.025, 0.0)
    cancelled = ((rng.random(n_sessions) < cancel_prob) & (converted == 1)).astype(int)

    retained_factor = np.where(converted == 0, 0.0, np.where(cancelled == 1, CANCEL_KEEP, 1.0))
    gbv = np.where(converted == 1, public_sell, 0.0)
    gross_markup_eur = np.where(converted == 1, public_sell - hotel_net, 0.0)
    net_revenue_before_promo = gross_markup_eur * retained_factor
    promo_cost_eur = gbv * eff_rate * retained_factor
    cannibalized_Cost_eur = np.where(cannibalized == 1, promo_cost_eur, 0.0)
    payment_cost_eur = gbv * PAYMENT_COST_RATE * retained_factor
    session_cost_eur = np.array([FENCES[f].session_cost for f in fence_ids])
    contribution = net_revenue_before_promo - promo_cost_eur - payment_cost_eur - session_cost_eur

    # Effective customer price vs competitor closed-group price
    customer_effective_price = public_sell * (1.0 - perceived)
    cug_price_index = customer_effective_price / comp_cug_price

    sessions = pd.DataFrame(
        {
            "session_id": np.arange(1, n_sessions + 1),
            "session_date": session_dates.strftime("%Y-%m-%d"),
            "week": weeks,
            "hotel_id": hotel_ids,
            "city": cities,
            "fence_id": fence_ids,
            "variant": variant,
            "mechanic": mechanic,
            "nominal_rate": nominal_rate,
            "effective_promo_rate": eff_rate,
            "lead_days": lead_days,
            "lead_bucket": lead_bucket,
            "nights": nights,
            "hotel_net": hotel_net,
            "public_sell": public_sell,
            "comp_public_price": comp_public_price,
            "comp_cug_price": comp_cug_price,
            "cug_price_index": np.round(cug_price_index, 4),
            "converted": converted,
            "cannibalized": cannibalized,
            "incremental": incremental,
            "cancelled": cancelled,
            "gbv": np.round(gbv, 2),
            "net_revenue_before_promo": np.round(net_revenue_before_promo, 2),
            "promo_cost": np.round(promo_cost_eur, 2),
            "cannibalized_promo_cost": np.round(cannibalized_Cost_eur, 2),
            "payment_cost": np.round(payment_cost_eur, 2),
            "session_cost": np.round(session_cost_eur, 2),
            "contribution": np.round(contribution, 2),
        }
    )
    meta = pd.DataFrame(
        [
            {
                "seed": seed,
                "n_sessions": n_sessions,
                "sample_start": sample_start,
                "sample_end": sample_end,
            }
        ]
    )
    return Book(sessions=sessions, hotels=hotels, fences=fences, meta=meta)
