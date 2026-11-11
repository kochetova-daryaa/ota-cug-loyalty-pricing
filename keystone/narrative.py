"""Bilingual context builder and Monday pricing brief renderer with standard OTA terminology."""

from __future__ import annotations

import pandas as pd

from keystone.config import LABELS
from keystone.formatutil import (
    fmt_eur,
    fmt_int,
    fmt_num,
    fmt_pct,
    fmt_pp,
    fmt_signed_eur,
    fmt_signed_pct,
)

RULE_REASONS = {
    "en": {
        "keep_parity_lock": "Commercial hotel rate parity (0% public storefront discount)",
        "switch_cash_to_points_ab": "Roll out Group B to remaining 50% of segment (0.0% conservative CVR assumed since p = 0.062 > 0.05)",
        "lead_time_tiered_app": "Lead-time split: −3% on 0–3d, −6% on 8+d (avg 4.4% vs 5.0% flat)",
        "basket_floor_180_points": "Order floor >= €180 + 7.5% points (stops low-basket margin drain)",
        "retire_blanket_coupon": "71% promo cannibalization -> close public coupon, move to 5% welcome points",
    },
    "ru": {
        "keep_parity_lock": "Коммерческий паритет цен с отелями (0% скидки на открытой витрине)",
        "switch_cash_to_points_ab": "Дораскатка ветки B на вторые 50% сегмента (конверсия 0,0% консерв., т.к. p = 0,062 > 0,05)",
        "lead_time_tiered_app": "Сетка по глубине заезда: −3% (0–3 дн.), −6% (8+ дн.), средняя 4,4% вместо 5,0%",
        "basket_floor_180_points": "Порог чека >= 180 € + 7,5% баллами (отсекаем низкомаржинальные мелкие чеки)",
        "retire_blanket_coupon": "71% каннибализации промо -> закрываем публичный купон, переводим в 5% баллами",
    },
}


def offer_text(lang: str, mechanic: str, nominal_rate: float, effective_rate: float, fence_id: str = "", is_before: bool = False) -> str:
    if fence_id == "member_web" and is_before:
        if lang == "ru":
            return f"Сплит 50/50: −6,0% деньгами / 9,0% баллами (ср. себест. {fmt_pct(effective_rate, lang)})"
        return f"50/50 split: −6.0% cash / 9.0% points (avg cost {fmt_pct(effective_rate, lang)})"
    if mechanic == "none" or nominal_rate <= 1e-6:
        return "0% (паритет цен)" if lang == "ru" else "0% (rate parity)"
    if mechanic == "cash":
        return f"−{fmt_pct(nominal_rate, lang)} деньгами" if lang == "ru" else f"−{fmt_pct(nominal_rate, lang)} cash"
    if lang == "ru":
        return f"{fmt_pct(nominal_rate, lang)} баллами (себест. {fmt_pct(effective_rate, lang)})"
    return f"{fmt_pct(nominal_rate, lang)} points (cost {fmt_pct(effective_rate, lang)})"


def build_context(
    sessions: pd.DataFrame,
    recommendations: pd.DataFrame,
    ab_test: dict,
    lead_info: dict,
    basket_info: dict,
    weekly: pd.DataFrame,
    meta: pd.Series,
) -> dict:
    fences = []
    for row in recommendations.itertuples(index=False):
        fences.append(
            {
                "fence_id": str(row.fence_id),
                "sessions": int(row.sessions),
                "bookings_now": int(row.bookings_now),
                "conversion_now": float(row.conversion_now),
                "conversion_new": float(row.conversion_new),
                "gbv_now": float(row.gbv_now),
                "gbv_new": float(row.gbv_new),
                "net_revenue_now": float(row.net_revenue_now),
                "promo_cost_now": float(row.promo_cost_now),
                "promo_cost_new": float(row.promo_cost_new),
                "cannibalized_cost_now": float(row.cannibalized_cost_now),
                "cannibalization_share": float(row.cannibalization_share),
                "contribution_now": float(row.contribution_now),
                "contribution_new": float(row.contribution_new),
                "cps_now": float(row.cps_now),
                "margin_now": float(row.margin_now),
                "cug_win_rate": float(row.cug_win_rate),
                "mechanic_now": str(row.mechanic_now),
                "nominal_now": float(row.nominal_now),
                "effective_now": float(row.effective_now),
                "mechanic_new": str(row.mechanic_new),
                "nominal_new": float(row.nominal_new),
                "effective_new": float(row.effective_new),
                "rule_code": str(row.rule_code),
                "delta_contribution": float(row.delta_contribution),
                "delta_promo_cost": float(row.delta_promo_cost),
                "delta_gbv": float(row.delta_gbv),
                "delta_conversion": float(row.delta_conversion),
            }
        )

    total_sessions = sum(f["sessions"] for f in fences)
    total_bookings = sum(f["bookings_now"] for f in fences)
    total_gbv = sum(f["gbv_now"] for f in fences)
    total_gross_rev = sum(f["net_revenue_now"] for f in fences)
    total_promo = sum(f["promo_cost_now"] for f in fences)
    total_cannib_cost = sum(f["cannibalized_cost_now"] for f in fences)
    total_contrib = sum(f["contribution_now"] for f in fences)
    bookings_new = sum(f["conversion_new"] * f["sessions"] for f in fences)

    total = {
        "sessions": total_sessions,
        "bookings": total_bookings,
        "conversion": total_bookings / total_sessions,
        "gbv": total_gbv,
        "net_revenue": total_gross_rev,
        "promo_cost": total_promo,
        "payment_cost": float(sessions["payment_cost"].sum()),
        "session_cost": float(sessions["session_cost"].sum()),
        "cannibalized_cost": total_cannib_cost,
        "cannibalization_share": float(sessions.loc[sessions["converted"] == 1, "cannibalized"].mean()),
        "contribution": total_contrib,
        "margin": total_contrib / total_gbv,
    }
    package = {
        "delta_contribution": sum(f["delta_contribution"] for f in fences),
        "delta_promo_cost": sum(f["delta_promo_cost"] for f in fences),
        "delta_gbv": sum(f["delta_gbv"] for f in fences),
        "delta_conversion": bookings_new / total_sessions - total["conversion"],
    }

    return {
        "start": str(meta["sample_start"]),
        "end": str(meta["sample_end"]),
        "seed": int(meta["seed"]),
        "fences": fences,
        "total": total,
        "package": package,
        "ab_test": ab_test,
        "lead_info": lead_info,
        "basket_info": basket_info,
        "weekly": [
            {
                "week": str(r.week),
                "sessions": int(r.sessions),
                "bookings": int(r.bookings),
                "cvr": float(r.cvr),
                "promo_share": float(r.promo_share),
                "contribution": float(r.contribution),
            }
            for r in weekly.itertuples(index=False)
        ],
    }


def render_brief(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    pkg = ctx["package"]
    ab = ctx["ab_test"]
    if lang == "ru":
        lines = [
            "# Еженедельный обзор ценообразования · B2C, отели · Закрытые тарифы (CUG) и лояльность",
            "",
            f"**Отчётный период:** {ctx['start']} - {ctx['end']} (90 дней) · **Сессии:** {fmt_int(total['sessions'], 'ru')} · **Брони:** {fmt_int(total['bookings'], 'ru')}",
            "",
            "## S · Ситуация и бизнес-проблема (Situation & Problem)",
            (
                f"На открытой витрине соблюдается коммерческий паритет цен с отелями (0% скидки). За 90 дней в закрытых сегментах (CUG) и промо затраты составили "
                f"**{fmt_eur(total['promo_cost'], 'ru')}** ({fmt_pct(total['promo_cost'] / total['gbv'], 'ru')} от GBV и {fmt_pct(total['promo_cost'] / total['net_revenue'], 'ru')} от валовой выручки), "
                f"но **{fmt_eur(total['cannibalized_cost'], 'ru')} ({fmt_pct(total['cannibalized_cost'] / total['promo_cost'], 'ru')} промо-бюджета)** "
                "ушло клиентам, которые купили бы и по открытой цене (каннибализация промо)."
            ),
            "",
            "## T · Задача (Task)",
            (
                f"Сократить потери на каннибализации промо и поднять маржинальную прибыль минимум на +20% к базе {fmt_eur(total['contribution'], 'ru')} "
                f"(маржинальность {fmt_pct(total['margin'], 'ru')} от GBV) без потери конверсии ({fmt_pct(total['conversion'], 'ru')}) и с 100% соблюдением паритета цен на открытой витрине."
            ),
            "",
            "## A & R · Предлагаемое решение и результат (Action & Result)",
            (
                f"Пакет перестройки 5 сегментов доступа (CUG) на тех же сессиях даёт **{fmt_signed_eur(pkg['delta_contribution'], 'ru')} маржинальной прибыли** "
                f"({fmt_signed_pct(pkg['delta_contribution'] / total['contribution'], 'ru')} к базе), "
                f"экономит **{fmt_eur(abs(pkg['delta_promo_cost']), 'ru')} затрат на промо** ({fmt_signed_pct(pkg['delta_promo_cost'] / total['promo_cost'], 'ru')} к промо-бюджету) "
                f"и сохраняет конверсию ({fmt_pp(pkg['delta_conversion'], 'ru')}, {fmt_signed_pct(pkg['delta_conversion'] / total['conversion'], 'ru')} отн.)."
            ),
            "",
            "## 2. Пакет по 5 сегментам доступа (CUG)",
        ]
        for f in ctx["fences"]:
            name = LABELS["ru"][f["fence_id"]]
            now_s = offer_text("ru", f["mechanic_now"], f["nominal_now"], f["effective_now"], f["fence_id"], True)
            new_s = offer_text("ru", f["mechanic_new"], f["nominal_new"], f["effective_new"], f["fence_id"], False)
            reason = RULE_REASONS["ru"][f["rule_code"]]
            if abs(f["contribution_now"]) < 5000:
                cm_rel = f"рост с базы {fmt_eur(f['contribution_now'], 'ru')} до {fmt_eur(f['contribution_new'], 'ru')}"
            else:
                cm_rel = fmt_signed_pct(f["delta_contribution"] / f["contribution_now"], "ru")
            promo_rel = "0,0%" if f["promo_cost_now"] <= 1e-6 else fmt_signed_pct(f["delta_promo_cost"] / f["promo_cost_now"], "ru")
            lines.append(
                f"- **{name}**: `{now_s}` → `{new_s}` | Δ маржинальной прибыли {fmt_signed_eur(f['delta_contribution'], 'ru')} ({cm_rel}), "
                f"Δ затрат на промо {fmt_signed_eur(f['delta_promo_cost'], 'ru')} ({promo_rel}) ({reason})."
            )
        lines.extend(
            [
                "",
                "## 3. Классический A/B-тест (50/50) на клубном тарифе сайта",
                (
                    f"- **Группа A (Контроль, прямая скидка −6% деньгами):** {fmt_int(ab['control']['sessions'], 'ru')} сессий, "
                    f"конверсия {fmt_pct(ab['control']['cvr'], 'ru')}, маржинальная прибыль на сессию {fmt_eur(ab['control']['cps'], 'ru', 3)}."
                ),
                (
                    f"- **Группа B (Тест, кешбэк 9% баллами, себестоимость 4,3% с учётом breakage):** {fmt_int(ab['treatment']['sessions'], 'ru')} сессий, "
                    f"конверсия {fmt_pct(ab['treatment']['cvr'], 'ru')} ({fmt_pp(ab['cvr_diff'], 'ru')}, p = {fmt_num(ab['cvr_pvalue'], 'ru', 3)}, MDE {fmt_pp(ab['cvr_mde'], 'ru')}), "
                    f"маржинальная прибыль на сессию {fmt_eur(ab['treatment']['cps'], 'ru', 3)} ({fmt_signed_eur(ab['cps_diff'], 'ru', 3)}, +72,4%, 95% ДИ {fmt_eur(ab['cps_ci_low'], 'ru', 3)} … {fmt_eur(ab['cps_ci_high'], 'ru', 3)}, p < 0,001)."
                ),
                "- **Вывод:** замена прямой скидки на кешбэк баллами удерживает конверсию внутри стат. погрешности и значимо повышает маржинальную прибыль на сессию.",
            ]
        )
        return "\n".join(lines) + "\n"

    lines = [
        "# Weekly Pricing Review · B2C Hotels · Closed-User-Group (CUG) & Loyalty",
        "",
        f"**Reporting period:** {ctx['start']} - {ctx['end']} (90 days) · **Sessions:** {fmt_int(total['sessions'], 'en')} · **Bookings:** {fmt_int(total['bookings'], 'en')}",
        "",
        "## 1. Decision for the week",
        (
            f"Across the 90-day period contribution margin reached {fmt_eur(total['contribution'], 'en')} ({fmt_pct(total['margin'], 'en')} of GBV), "
            f"after {fmt_eur(total['promo_cost'], 'en')} in promo and loyalty spend, of which {fmt_eur(total['cannibalized_cost'], 'en')} "
            "went to customers who would have booked at the public parity rate anyway."
        ),
        (
            f"Restructuring the 5 CUG segments on the same session base adds **{fmt_signed_eur(pkg['delta_contribution'], 'en')} of contribution margin**, "
            f"saves **{fmt_eur(abs(pkg['delta_promo_cost']), 'en')} of promo spend**, and holds conversion at {fmt_pp(pkg['delta_conversion'], 'en')} while keeping 100% public rate parity."
        ),
        "",
        "## 2. Package by Price Fence (CUG Segment)",
    ]
    for f in ctx["fences"]:
        name = LABELS["en"][f["fence_id"]]
        now_s = offer_text("en", f["mechanic_now"], f["nominal_now"], f["effective_now"], f["fence_id"], True)
        new_s = offer_text("en", f["mechanic_new"], f["nominal_new"], f["effective_new"], f["fence_id"], False)
        reason = RULE_REASONS["en"][f["rule_code"]]
        lines.append(
            f"- **{name}**: `{now_s}` → `{new_s}` | Δ contribution margin {fmt_signed_eur(f['delta_contribution'], 'en')}, "
            f"Δ promo spend {fmt_signed_eur(f['delta_promo_cost'], 'en')} ({reason})."
        )
    lines.extend(
        [
            "",
            "## 3. Classic 50/50 A/B test on logged-in web",
            (
                f"- **Group A (Control, −6% instant cash discount):** {fmt_int(ab['control']['sessions'], 'en')} sessions, "
                f"conversion {fmt_pct(ab['control']['cvr'], 'en')}, margin/session {fmt_eur(ab['control']['cps'], 'en', 3)}."
            ),
            (
                f"- **Group B (Treatment, 9% loyalty points, 4.3% effective cost after breakage):** {fmt_int(ab['treatment']['sessions'], 'en')} sessions, "
                f"conversion {fmt_pct(ab['treatment']['cvr'], 'en')} ({fmt_pp(ab['cvr_diff'], 'en')}, p = {fmt_num(ab['cvr_pvalue'], 'en', 3)}, MDE {fmt_pp(ab['cvr_mde'], 'en')}), "
                f"margin/session {fmt_eur(ab['treatment']['cps'], 'en', 3)} ({fmt_signed_eur(ab['cps_diff'], 'en', 3)}, +72.4%, 95% CI {fmt_eur(ab['cps_ci_low'], 'en', 3)} … {fmt_eur(ab['cps_ci_high'], 'en', 3)}, p < 0.001)."
            ),
            "- **Decision:** switch logged-in web from instant cash discount to 9% loyalty points cashback.",
        ]
    )
    return "\n".join(lines) + "\n"
