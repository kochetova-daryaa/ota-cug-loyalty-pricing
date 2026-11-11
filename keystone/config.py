"""Configuration, fence policies, and loyalty economics parameters."""

from __future__ import annotations

from dataclasses import dataclass

SEED = 42
N_SESSIONS = 250_000
SAMPLE_START = "2026-08-03"
SAMPLE_END = "2026-10-31"

BASE_MARKUP = 0.120          # 12.0% public rate-parity markup over hotel net rate
CANCEL_KEEP = 0.25           # retained share of markup/charge on cancelled bookings
PAYMENT_COST_RATE = 0.014    # 1.4% payment processing on gross booking value
POINTS_BREAKAGE = 0.36       # 36% of issued loyalty points expire unredeemed
REPEAT_AD_SAVING = 0.25      # 25% of redeemed points replace paid re-acquisition cost
CONVERSION_GUARDRAIL = 0.025 # max allowed relative conversion drop per fence (2.5%)

AB_FENCE = "member_web"
AB_CONTROL_CASH_RATE = 0.060   # Group A: 6.0% instant cash discount
AB_TREATMENT_POINTS = 0.090    # Group B: 9.0% loyalty cashback points (4.32% effective cost)


@dataclass(frozen=True)
class FencePolicy:
    fence_id: str
    share: float
    base_cvr: float
    session_cost: float
    mechanic_now: str          # "none", "cash", "points"
    nominal_rate_now: float    # face-value discount or points rate
    organic_share_prior: float # expected share of buyers who would buy without promo (cannibalization)
    uplift_elasticity: float   # conversion sensitivity to perceived benefit
    cancel_base: float
    min_margin_floor: float
    proposed_mechanic: str
    proposed_nominal_rate: float
    proposed_rule_code: str


FENCES: dict[str, FencePolicy] = {
    "public_parity": FencePolicy(
        fence_id="public_parity",
        share=0.34,
        base_cvr=0.038,
        session_cost=0.19,
        mechanic_now="none",
        nominal_rate_now=0.000,
        organic_share_prior=1.00,
        uplift_elasticity=1.40,
        cancel_base=0.105,
        min_margin_floor=0.045,
        proposed_mechanic="none",
        proposed_nominal_rate=0.000,
        proposed_rule_code="keep_parity_lock",
    ),
    "member_web": FencePolicy(
        fence_id="member_web",
        share=0.24,
        base_cvr=0.045,
        session_cost=0.11,
        mechanic_now="cash",
        nominal_rate_now=0.060,
        organic_share_prior=0.64,
        uplift_elasticity=1.85,
        cancel_base=0.092,
        min_margin_floor=0.040,
        proposed_mechanic="points",
        proposed_nominal_rate=0.090,
        proposed_rule_code="switch_cash_to_points_ab",
    ),
    "app_only": FencePolicy(
        fence_id="app_only",
        share=0.20,
        base_cvr=0.062,
        session_cost=0.05,
        mechanic_now="cash",
        nominal_rate_now=0.050,
        organic_share_prior=0.52,
        uplift_elasticity=2.25,
        cancel_base=0.078,
        min_margin_floor=0.038,
        proposed_mechanic="cash",
        proposed_nominal_rate=0.044,
        proposed_rule_code="lead_time_tiered_app",
    ),
    "cart_recovery": FencePolicy(
        fence_id="cart_recovery",
        share=0.10,
        base_cvr=0.054,
        session_cost=0.06,
        mechanic_now="cash",
        nominal_rate_now=0.050,
        organic_share_prior=0.58,
        uplift_elasticity=2.05,
        cancel_base=0.088,
        min_margin_floor=0.042,
        proposed_mechanic="points",
        proposed_nominal_rate=0.075,
        proposed_rule_code="basket_floor_180_points",
    ),
    "blanket_promo": FencePolicy(
        fence_id="blanket_promo",
        share=0.12,
        base_cvr=0.049,
        session_cost=0.22,
        mechanic_now="cash",
        nominal_rate_now=0.080,
        organic_share_prior=0.74,
        uplift_elasticity=1.35,
        cancel_base=0.128,
        min_margin_floor=0.040,
        proposed_mechanic="points",
        proposed_nominal_rate=0.050,
        proposed_rule_code="retire_blanket_coupon",
    ),
}

FENCE_ORDER = list(FENCES)

LABELS = {
    "en": {
        "public_parity": "0. Public storefront (parity)",
        "member_web": "1. Logged-in club (web)",
        "app_only": "2. Mobile app closed rate",
        "cart_recovery": "3. Abandoned-cart trigger",
        "blanket_promo": "4. Public banner coupon",
        "none": "0% (rate parity)",
        "cash": "Instant discount",
        "points": "Loyalty points",
    },
    "ru": {
        "public_parity": "0. Открытая витрина (паритет)",
        "member_web": "1. Клубный тариф (веб после входа)",
        "app_only": "2. Закрытый тариф в приложении",
        "cart_recovery": "3. Триггер брошенной корзины",
        "blanket_promo": "4. Массовый промокод в баннерах",
        "none": "0% (паритет цен)",
        "cash": "Прямая скидка",
        "points": "Кешбэк баллами",
    },
}

CITIES = (
    ("Rome", 195.0, 1.05),
    ("Barcelona", 210.0, 1.08),
    ("Istanbul", 148.0, 0.96),
    ("Dubai", 265.0, 0.94),
    ("Lisbon", 182.0, 1.03),
    ("Prague", 154.0, 1.01),
    ("Vienna", 188.0, 0.99),
    ("Athens", 162.0, 1.00),
)

HOTEL_NAMES = {
    "Rome": ("Aurelia Palace", "TrastevereSuites", "Cavalli Grand"),
    "Barcelona": ("Eixample Corner", "Mar Bella Hotel", "Gothic Quarter Inn"),
    "Istanbul": ("Bosphorus Crest", "Galata Port Suites", "Nisantasi House"),
    "Dubai": ("Marina Bay Tower", "Creekside Residences", "Downtown Pearl"),
    "Lisbon": ("Chiado Terrace", "Avenida Park Hotel", "Tagus View Inn"),
    "Prague": ("Old Town Lantern", "Vltava Grand", "Vinohrady Court"),
    "Vienna": ("Ringstrasse Hof", "Belvedere Suites", "Leopold Boutique"),
    "Athens": ("Syntagma Square Inn", "Plaka Heritage", "Koukaki Rooms"),
}

LEAD_BUCKETS = (
    (0, 3, "0-3"),
    (4, 7, "4-7"),
    (8, 21, "8-21"),
    (22, 90, "22+"),
)
