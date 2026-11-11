"""Unit economics of instant cash discounts versus loyalty cashback points."""

from __future__ import annotations

from dataclasses import dataclass

from keystone.config import (
    BASE_MARKUP,
    CANCEL_KEEP,
    PAYMENT_COST_RATE,
    POINTS_BREAKAGE,
    REPEAT_AD_SAVING,
)


def effective_promo_rate(
    mechanic: str,
    nominal_rate: float,
    breakage: float = POINTS_BREAKAGE,
    repeat_ad_saving: float = REPEAT_AD_SAVING,
) -> float:
    """Convert nominal customer-facing benefit into real unit cost as % of gross sell price.

    - "none": 0.0
    - "cash": 100% of nominal discount is surrendered immediately
    - "points": only the non-expired share `(1 - breakage)` is redeemed, and
      redeemed points save `repeat_ad_saving` in paid re-acquisition cost.
    """
    if mechanic == "none" or nominal_rate <= 0:
        return 0.0
    if mechanic == "cash":
        return float(nominal_rate)
    if mechanic == "points":
        return float(nominal_rate * (1.0 - breakage) * (1.0 - repeat_ad_saving))
    raise ValueError(f"Unknown promo mechanic: {mechanic}")


def perceived_benefit_rate(mechanic: str, nominal_rate: float) -> float:
    """Customer-perceived value used in demand response.

    A 9% points badge is discounted slightly by customers relative to immediate cash
    (factor 0.72), so 9.0% points has ~6.48% cash-equivalent appeal while costing 4.32%.
    """
    if mechanic == "none" or nominal_rate <= 0:
        return 0.0
    if mechanic == "cash":
        return float(nominal_rate)
    if mechanic == "points":
        return float(nominal_rate * 0.72)
    raise ValueError(f"Unknown promo mechanic: {mechanic}")


@dataclass(frozen=True)
class BookingEconomics:
    gross_sell: float
    hotel_net: float
    gross_markup: float
    promo_cost: float
    payment_cost: float
    retained_factor: float
    net_revenue_before_promo: float
    retained_promo_cost: float
    net_contribution_before_ads: float


def booking_unit_economics(
    hotel_net: float,
    mechanic: str,
    nominal_rate: float,
    cancelled: bool,
    base_markup: float = BASE_MARKUP,
    cancel_keep: float = CANCEL_KEEP,
    payment_cost_rate: float = PAYMENT_COST_RATE,
) -> BookingEconomics:
    """Compute realized unit economics for one booking."""
    gross_sell = round(hotel_net * (1.0 + base_markup), 2)
    gross_markup = gross_sell - hotel_net
    eff_rate = effective_promo_rate(mechanic, nominal_rate)
    promo_cost = gross_sell * eff_rate
    retained_factor = cancel_keep if cancelled else 1.0
    net_rev_before_promo = gross_markup * retained_factor
    retained_promo = promo_cost * retained_factor
    payment_cost = gross_sell * payment_cost_rate * retained_factor
    net_contrib = net_rev_before_promo - retained_promo - payment_cost
    return BookingEconomics(
        gross_sell=gross_sell,
        hotel_net=hotel_net,
        gross_markup=gross_markup,
        promo_cost=promo_cost,
        payment_cost=payment_cost,
        retained_factor=retained_factor,
        net_revenue_before_promo=net_rev_before_promo,
        retained_promo_cost=retained_promo,
        net_contribution_before_ads=net_contrib,
    )
