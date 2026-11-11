"""End-to-end Keystone pipeline: generate -> SQL warehouse -> stats -> optimizer -> Excel, HTML, and briefs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from keystone.config import N_SESSIONS, SAMPLE_END, SAMPLE_START, SEED
from keystone.dashboard import write_dashboard
from keystone.excel_export import write_workbook
from keystone.generate import generate
from keystone.narrative import build_context, render_brief
from keystone.optimize import build_fence_shelf, build_recommendations
from keystone.stats import ab_test_readout, lead_time_summary, small_basket_diagnostic
from keystone.warehouse import load


def run_pipeline(
    n_sessions: int = N_SESSIONS,
    seed: int = SEED,
    root: Path | None = None,
    sample_start: str = SAMPLE_START,
    sample_end: str = SAMPLE_END,
) -> dict:
    source = Path(__file__).resolve().parents[1]
    root = Path(root) if root is not None else source
    output = root / "output"
    reports = root / "reports"
    extract = output / "bi_extract"
    output.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    extract.mkdir(parents=True, exist_ok=True)
    (root / "data").mkdir(parents=True, exist_ok=True)

    book = generate(n_sessions=n_sessions, seed=seed, sample_start=sample_start, sample_end=sample_end)
    views = load(book, output / "keystone.db", source / "sql")
    sql_bookings = int(views["vw_fence_scorecard"]["bookings"].sum())
    py_bookings = int(book.sessions["converted"].sum())
    if sql_bookings != py_bookings:
        raise RuntimeError(f"SQL bookings {sql_bookings} != Python bookings {py_bookings}")

    ab_test = ab_test_readout(book.sessions)
    lead_info = lead_time_summary(book.sessions)
    basket_info = small_basket_diagnostic(book.sessions)
    recommendations = build_recommendations(book.sessions, ab_test)
    shelf = build_fence_shelf(book.hotels, recommendations)
    weekly = _weekly(book.sessions)
    daily = _daily(book.sessions)

    for name, frame in views.items():
        frame.to_csv(extract / f"{name}.csv", index=False)
    recommendations.to_csv(extract / "recommendations.csv", index=False)
    shelf.to_csv(output / "fence_rules_shelf.csv", index=False)
    book.sessions.head(200).to_csv(root / "data" / "sample_sessions.csv", index=False)

    ctx = build_context(
        book.sessions,
        recommendations,
        ab_test,
        lead_info,
        basket_info,
        weekly,
        book.meta.iloc[0],
    )
    (reports / "monday_brief.ru.md").write_text(render_brief("ru", ctx), encoding="utf-8")
    (reports / "monday_brief.en.md").write_text(render_brief("en", ctx), encoding="utf-8")
    write_dashboard(output / "pricing_cockpit.html", ctx)
    write_dashboard(root / "index.html", ctx)
    write_workbook(output / "keystone_pricing_cockpit.xlsx", daily, weekly, recommendations, ab_test)

    summary = {
        "sessions": ctx["total"]["sessions"],
        "bookings": ctx["total"]["bookings"],
        "sql_bookings": sql_bookings,
        "contribution": round(ctx["total"]["contribution"], 2),
        "promo_cost": round(ctx["total"]["promo_cost"], 2),
        "cannibalized_cost": round(ctx["total"]["cannibalized_cost"], 2),
        "delta_contribution": round(ctx["package"]["delta_contribution"], 2),
        "delta_promo_cost": round(ctx["package"]["delta_promo_cost"], 2),
        "ab_status": ab_test["status"],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _weekly(sessions: pd.DataFrame) -> pd.DataFrame:
    frame = sessions.groupby("week", as_index=False).agg(
        sessions=("session_id", "size"),
        bookings=("converted", "sum"),
        net_revenue=("net_revenue_before_promo", "sum"),
        promo_cost=("promo_cost", "sum"),
        contribution=("contribution", "sum"),
    )
    frame["cvr"] = frame["bookings"] / frame["sessions"]
    frame["promo_share"] = frame["promo_cost"] / frame["net_revenue"]
    return frame.sort_values("week")


def _daily(sessions: pd.DataFrame) -> pd.DataFrame:
    frame = sessions.groupby(["session_date", "fence_id", "city"], as_index=False).agg(
        sessions=("session_id", "size"),
        bookings=("converted", "sum"),
        gbv=("gbv", "sum"),
        net_revenue=("net_revenue_before_promo", "sum"),
        promo_cost=("promo_cost", "sum"),
        cannibalized_cost=("cannibalized_promo_cost", "sum"),
        contribution=("contribution", "sum"),
    )
    return frame.sort_values(["session_date", "fence_id", "city"])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Keystone pricing pipeline")
    parser.add_argument("command", nargs="?", default="run", choices=["run"])
    parser.add_argument("--sessions", type=int, default=N_SESSIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    summary = run_pipeline(n_sessions=args.sessions, seed=args.seed, root=args.root)
    print(
        "Keystone pipeline complete\n"
        f"sessions {summary['sessions']:,}  bookings {summary['bookings']:,}\n"
        f"net contribution EUR {summary['contribution']:,.0f}  promo spend EUR {summary['promo_cost']:,.0f}\n"
        f"A/B test status {summary['ab_status']}\n"
        f"package delta contribution EUR {summary['delta_contribution']:,.0f}\n"
        "RU  reports/monday_brief.ru.md\n"
        "EN  reports/monday_brief.en.md\n"
        "HTML output/pricing_cockpit.html"
    )
