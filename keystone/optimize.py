"""Fence policy simulation, package optimization, and hotel-level rules shelf."""

from __future__ import annotations

import pandas as pd

from keystone.config import (
    FENCE_ORDER,
    FENCES,
    PAYMENT_COST_RATE,
)
from keystone.economics import effective_promo_rate, perceived_benefit_rate


def build_recommendations(sessions: pd.DataFrame, ab_readout: dict) -> pd.DataFrame:
    """Simulate the weekly price-fence package on observed 90-day sessions."""
    rows = []
    for fence_id in FENCE_ORDER:
        policy = FENCES[fence_id]
        part = sessions[sessions["fence_id"] == fence_id]
        n_sess = int(len(part))
        bookings_now = int(part["converted"].sum())
        cvr_now = bookings_now / n_sess
        gbv_now = float(part["gbv"].sum())
        net_rev_now = float(part["net_revenue_before_promo"].sum())
        promo_now = float(part["promo_cost"].sum())
        cannib_cost_now = float(part["cannibalized_promo_cost"].sum())
        contrib_now = float(part["contribution"].sum())
        booked = part[part["converted"] == 1]
        cannib_share = float(booked["cannibalized"].mean()) if bookings_now else 0.0
        win_cug = float((part["cug_price_index"] <= 1.01).mean())

        eff_now = float(part["effective_promo_rate"].mean())
        perc_now = float(
            part.apply(lambda r: perceived_benefit_rate(str(r["mechanic"]), float(r["nominal_rate"])), axis=1).mean()
        )
        eff_new = effective_promo_rate(policy.proposed_mechanic, policy.proposed_nominal_rate)
        perc_new = perceived_benefit_rate(policy.proposed_mechanic, policy.proposed_nominal_rate)

        if fence_id == "public_parity":
            cvr_ratio = 1.0
            eff_new = 0.0
        elif fence_id == "member_web":
            # In the 90-day book, half of member_web was already in Group B; moving 100% to points
            # brings the remaining cash half to Group B economics with a conservative 0.0% CVR change
            # (since the +0.3 pp A/B difference has p = 0.062 and sits inside the 0.5 pp MDE).
            cvr_ratio = 1.0
        elif fence_id == "app_only":
            # Differentiating discount (-4% on 0-3d, -7% on 8+d) captures elastic long-lead demand
            cvr_ratio = 1.0 + 0.042
        elif fence_id == "cart_recovery":
            # Minimum basket >= EUR 180 + 7.5% points trims low-value redemptions, raises net contribution
            cvr_ratio = 1.0 - 0.018
        else:
            # Retiring the -8% public banner coupon and gating to 5% welcome points
            cvr_ratio = 1.0 - 0.048

        bookings_new = bookings_now * cvr_ratio
        cvr_new = bookings_new / n_sess
        gbv_new = gbv_now * cvr_ratio
        net_rev_new = net_rev_now * cvr_ratio
        retained_gbv_ratio = (net_rev_now / (gbv_now * (0.12 / 1.12))) if gbv_now else 0.90
        promo_new = gbv_new * eff_new * retained_gbv_ratio
        payment_new = gbv_new * PAYMENT_COST_RATE * retained_gbv_ratio
        session_cost_total = float(part["session_cost"].sum())
        contrib_new = net_rev_new - promo_new - payment_new - session_cost_total

        rows.append(
            {
                "fence_id": fence_id,
                "sessions": n_sess,
                "bookings_now": bookings_now,
                "conversion_now": cvr_now,
                "conversion_new": cvr_new,
                "gbv_now": gbv_now,
                "gbv_new": gbv_new,
                "net_revenue_now": net_rev_now,
                "net_revenue_new": net_rev_new,
                "promo_cost_now": promo_now,
                "promo_cost_new": promo_new,
                "cannibalized_cost_now": cannib_cost_now,
                "cannibalization_share": cannib_share,
                "contribution_now": contrib_now,
                "contribution_new": contrib_new,
                "cps_now": contrib_now / n_sess,
                "cps_new": contrib_new / n_sess,
                "margin_now": contrib_now / gbv_now if gbv_now else 0.0,
                "margin_new": contrib_new / gbv_new if gbv_new else 0.0,
                "cug_win_rate": win_cug,
                "mechanic_now": policy.mechanic_now,
                "nominal_now": policy.nominal_rate_now,
                "effective_now": eff_now,
                "mechanic_new": policy.proposed_mechanic,
                "nominal_new": policy.proposed_nominal_rate,
                "effective_new": eff_new,
                "rule_code": policy.proposed_rule_code,
                "delta_contribution": contrib_new - contrib_now,
                "delta_promo_cost": promo_new - promo_now,
                "delta_gbv": gbv_new - gbv_now,
                "delta_conversion": cvr_new - cvr_now,
            }
        )
    return pd.DataFrame(rows)


def build_fence_shelf(hotels: pd.DataFrame, recommendations: pd.DataFrame) -> pd.DataFrame:
    """Generate the operational per-hotel × fence rule table (`output/fence_rules_shelf.csv`)."""
    rec_map = recommendations.set_index("fence_id")
    rows = []
    for hotel in hotels.itertuples(index=False):
        public_price = round(float(hotel.base_net) * 1.12, 2)
        for fence_id in FENCE_ORDER:
            r = rec_map.loc[fence_id]
            mech = str(r["mechanic_new"])
            nom = float(r["nominal_new"])
            eff = float(r["effective_new"])
            if mech == "cash":
                shown_price = round(public_price * (1.0 - nom), 2)
                points_eur = 0.0
            elif mech == "points":
                shown_price = public_price
                points_eur = round(public_price * nom, 2)
            else:
                shown_price = public_price
                points_eur = 0.0
            unit_margin = (shown_price - float(hotel.base_net) - public_price * eff - shown_price * PAYMENT_COST_RATE) / public_price
            rows.append(
                {
                    "hotel_id": int(hotel.hotel_id),
                    "hotel_name": str(hotel.hotel_name),
                    "city": str(hotel.city),
                    "stars": int(hotel.stars),
                    "fence_id": fence_id,
                    "hotel_net_1n": float(hotel.base_net),
                    "public_parity_price": public_price,
                    "mechanic_new": mech,
                    "nominal_benefit_pct": round(nom, 4),
                    "effective_cost_pct": round(eff, 4),
                    "customer_pay_price": shown_price,
                    "loyalty_points_eur": points_eur,
                    "unit_margin_pct": round(unit_margin, 4),
                    "parity_compliant": int(fence_id != "public_parity" or shown_price >= public_price),
                    "rule_code": str(r["rule_code"]),
                }
            )
    return pd.DataFrame(rows)
