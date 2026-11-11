"""Excel cockpit exporter with live formulas for cash-vs-points unit economics."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo


def write_workbook(
    path: Path,
    daily: pd.DataFrame,
    weekly: pd.DataFrame,
    recommendations: pd.DataFrame,
    ab_test: dict,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.properties.creator = "Darya Kochetova"
    wb.properties.lastModifiedBy = "Darya Kochetova"
    _write_cover(wb.active)
    _write_calculator(wb.create_sheet("Promo_Calculator"))
    _write_scorecard(wb.create_sheet("Scorecard"), recommendations)
    _write_ab_test(wb.create_sheet("AB_Test"), ab_test)
    _write_daily(wb.create_sheet("Daily"), daily)
    _write_weekly(wb.create_sheet("Weekly"), weekly)
    wb.save(path)


def _write_cover(ws) -> None:
    ws.title = "Cover"
    ws["A1"] = "Еженедельный обзор ценообразования · B2C, отели · Закрытые тарифы (CUG) и лояльность"
    ws["A1"].font = Font(size=15, bold=True)
    ws["A2"] = "Калькулятор и отчёт по закрытым тарифам, баллам лояльности и промокодам (период 90 дней: 03.08.2026 - 31.10.2026)"
    rows = [
        ("Sheet / Лист", "Purpose / Назначение"),
        ("Promo_Calculator", "Интерактивный расчёт: прямая скидка деньгами против кешбэка баллами с учётом breakage и каннибализации"),
        ("Scorecard", "Экономика 5 ценовых заборов и пакет решений Было → Стало"),
        ("AB_Test", "Классический A/B-тест 50/50 на клубном тарифе сайта (Группа A −6% деньгами vs Группа B 9% баллами)"),
        ("Daily", "Ежедневная гранулярность по дате, ценовому забору и городу (таблица с фильтрами)"),
        ("Weekly", "13-недельный ряд конверсии, доли промо и чистого вклада"),
    ]
    for r_idx, (col1, col2) in enumerate(rows, start=4):
        ws.cell(r_idx, 1, col1)
        ws.cell(r_idx, 2, col2)
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 88


def _write_calculator(ws) -> None:
    ws["A1"] = "Promo vs. Loyalty Points Calculator / Калькулятор: Скидка деньгами против Баллов"
    ws["A1"].font = Font(size=13, bold=True)

    inputs = [
        ("Sessions in segment / Сессии в сегменте", 30000),
        ("Base conversion without promo / Базовая конверсия без скидки", 0.030),
        ("Conversion with promo / Конверсия с предложением", 0.045),
        ("Average booking value (GBV per booking, EUR) / Средний чек брони (GBV), €", 240.0),
        ("Gross commission rate on public parity / Базовая комиссия (наценка) открытой витрины", 0.120),
        ("Option A: Instant cash discount / Вариант А: Прямая скидка деньгами", 0.060),
        ("Option B: Loyalty cashback nominal / Вариант Б: Кешбэк баллами (номинал)", 0.090),
        ("Points breakage (unredeemed share) / Неиспользованные баллы (Breakage)", 0.360),
        ("Ad-spend saving on repeat redemption / Экономия на рекламе при отоваривании", 0.250),
        ("Retained factor after cancellations / Доля выживших броней после отмен", 0.900),
        ("Payment processing rate / Эквайринг (% от GBV)", 0.014),
        ("Traffic cost per session (EUR) / Затраты на привлечение сессии, €", 0.110),
    ]
    for idx, (label, val) in enumerate(inputs, start=3):
        ws.cell(idx, 1, label)
        ws.cell(idx, 2, val)

    formulas = [
        (16, "Total bookings with promo / Всего броней с промо", "=B3*B5"),
        (17, "Cannibalized (organic) bookings / Купили бы и без скидки (каннибализация промо)", "=B3*B4"),
        (18, "Incremental bookings / Приростные брони от промо", "=B16-B17"),
        (19, "Promo cannibalization % / Доля каннибализации промо", "=B17/B16"),
        (20, "Effective cost of loyalty points (% of GBV) / Реальная себестоимость баллов (% от GBV)", "=B9*(1-B10)*(1-B11)"),
        (21, "Contribution Margin - Option A (Cash discount), EUR / Маржинальная прибыль - Вариант А (Скидка деньгами), €", "=B16*B6*(B7/(1+B7)-B8-B13)*B12-B3*B14"),
        (22, "Contribution Margin - Option B (Loyalty points), EUR / Маржинальная прибыль - Вариант Б (Кешбэк баллами), €", "=B16*B6*(B7/(1+B7)-B20-B13)*B12-B3*B14"),
        (23, "Contribution Margin advantage of Points over Cash, EUR / Выигрыш маржинальной прибыли (Баллы против Скидки), €", "=B22-B21"),
    ]
    for row_idx, label, formula in formulas:
        ws.cell(row_idx, 1, label).font = Font(bold=row_idx >= 20)
        ws.cell(row_idx, 2, formula)

    ws.column_dimensions["A"].width = 74
    ws.column_dimensions["B"].width = 18


def _write_scorecard(ws, recommendations: pd.DataFrame) -> None:
    headers = [
        "fence_id",
        "sessions",
        "conversion_now",
        "gbv_now",
        "promo_cost_now",
        "cannibalization_share",
        "contribution_now",
        "contribution_new",
        "delta_contribution",
        "delta_promo_cost",
    ]
    for col_idx, name in enumerate(headers, start=1):
        cell = ws.cell(1, col_idx, name)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for r_idx, row in enumerate(recommendations.itertuples(index=False), start=2):
        ws.cell(r_idx, 1, str(row.fence_id))
        ws.cell(r_idx, 2, int(row.sessions))
        ws.cell(r_idx, 3, round(float(row.conversion_now), 4))
        ws.cell(r_idx, 4, round(float(row.gbv_now), 2))
        ws.cell(r_idx, 5, round(float(row.promo_cost_now), 2))
        ws.cell(r_idx, 6, round(float(row.cannibalization_share), 4))
        ws.cell(r_idx, 7, round(float(row.contribution_now), 2))
        ws.cell(r_idx, 8, round(float(row.contribution_new), 2))
        ws.cell(r_idx, 9, f"=H{r_idx}-G{r_idx}")
        ws.cell(r_idx, 10, round(float(row.delta_promo_cost), 2))

    last_row = len(recommendations) + 1
    ws.cell(last_row + 1, 1, "TOTAL").font = Font(bold=True)
    ws.cell(last_row + 1, 2, f"=SUM(B2:B{last_row})")
    ws.cell(last_row + 1, 7, f"=SUM(G2:G{last_row})")
    ws.cell(last_row + 1, 8, f"=SUM(H2:H{last_row})")
    ws.cell(last_row + 1, 9, f"=SUM(I2:I{last_row})")

    chart = BarChart()
    chart.title = "Contribution Now vs Proposed by Fence (EUR)"
    data = Reference(ws, min_col=7, max_col=8, min_row=1, max_row=last_row)
    cats = Reference(ws, min_col=1, min_row=2, max_row=last_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, "A10")


def _write_ab_test(ws, ab: dict) -> None:
    ws["A1"] = "Classic 50/50 A/B Test on Logged-in Web (Group A: −6% Cash vs Group B: 9% Points)"
    ws["A1"].font = Font(bold=True, size=12)
    headers = ["Metric", "Group A (Control: −6% Cash)", "Group B (Test: 9% Points)", "Difference / P-value"]
    for c_idx, h in enumerate(headers, start=1):
        ws.cell(3, c_idx, h).font = Font(bold=True)
    ctrl, treat = ab["control"], ab["treatment"]
    rows = [
        ("Sessions", ctrl["sessions"], treat["sessions"], "50/50 split"),
        ("Bookings", ctrl["bookings"], treat["bookings"], ""),
        ("Conversion rate", round(ctrl["cvr"], 5), round(treat["cvr"], 5), f"p = {ab['cvr_pvalue']:.3f}"),
        ("Contribution per session (EUR)", round(ctrl["cps"], 4), round(treat["cps"], 4), f"p = {ab['cps_pvalue']:.5f}"),
        ("Total contribution (EUR)", round(ctrl["contribution"], 2), round(treat["contribution"], 2), round(treat["contribution"] - ctrl["contribution"], 2)),
    ]
    for r_idx, row in enumerate(rows, start=4):
        for c_idx, val in enumerate(row, start=1):
            ws.cell(r_idx, c_idx, val)
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 28
    ws.column_dimensions["D"].width = 24


def _write_daily(ws, daily: pd.DataFrame) -> None:
    cols = list(daily.columns)
    ws.append(cols)
    for row in daily.itertuples(index=False):
        ws.append(list(row))
    end_row = len(daily) + 1
    tab = Table(displayName="DailyFenceTable", ref=f"A1:H{end_row}")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(tab)


def _write_weekly(ws, weekly: pd.DataFrame) -> None:
    cols = list(weekly.columns)
    ws.append(cols)
    for row in weekly.itertuples(index=False):
        ws.append(list(row))
    for cell in ws[1]:
        cell.font = Font(bold=True, color="0F172A")
        cell.fill = PatternFill("solid", fgColor="E8F0FF")
