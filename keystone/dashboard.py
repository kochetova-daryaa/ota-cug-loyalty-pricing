"""Self-contained bilingual HTML cockpit for Keystone using real OTA industry terminology."""

from __future__ import annotations

import math
from datetime import date
from html import escape
from pathlib import Path

from keystone.config import LABELS, POINTS_BREAKAGE, REPEAT_AD_SAVING
from keystone.formatutil import (
    fmt_eur,
    fmt_int,
    fmt_num,
    fmt_pct,
    fmt_pp,
    fmt_signed_eur,
    fmt_signed_pct,
)
from keystone.narrative import RULE_REASONS, offer_text


def write_dashboard(path: Path, ctx: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_page(ctx), encoding="utf-8")


def _page(ctx: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="B2C Hotel OTA Pricing Review: Closed-User-Group (CUG) rates, loyalty points unit economics, 50/50 A/B test, and SQL/Excel analytics (synthetic dataset, seed 42).">
<meta property="og:title" content="Еженедельный обзор ценообразования · B2C, отели · Закрытые тарифы (CUG) и лояльность">
<meta property="og:description" content="Аналитический кейс по управлению ценообразованием, закрытыми тарифами (CUG) и программой лояльности в B2C OTA (синтетические данные, seed 42).">
<title>Еженедельный обзор ценообразования · B2C, отели · Закрытые тарифы (CUG) и лояльность</title>
<style>
  :root {{
    --paper: #f4f6fb;
    --card: #ffffff;
    --ink: #0f172a;
    --muted: #5b677d;
    --line: #e4e9f2;
    --copper: #005bff;
    --accent-warm: #ff5a26;
    --navy: #005bff;
    --good: #0d8a52;
    --bad: #d92d20;
    --track: #e9eef7;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: Inter, "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    font-size: 15px;
    line-height: 1.5;
  }}
  .lang-en {{ display: none !important; }}
  body[data-lang="en"] .lang-en {{ display: block !important; }}
  body[data-lang="en"] h1.kicker.lang-en {{ display: inline-block !important; }}
  body[data-lang="ru"] h1.kicker.lang-ru {{ display: inline-block !important; }}
  body[data-lang="en"] .lang-ru {{ display: none !important; }}
  header {{
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    max-width: 1180px;
    margin: 0 auto;
    padding: 34px 24px 28px;
    text-align: center;
  }}
  .kicker {{
    display: inline-block;
    margin: 0;
    padding: 12px 28px;
    border-radius: 20px;
    background: #e8f0ff;
    border: 1px solid #cfe0ff;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-size: 16px;
    font-weight: 800;
    line-height: 1.45;
    color: var(--copper);
    text-align: center;
  }}
  .kicker small {{
    display: block;
    margin-top: 2px;
    font-size: 13px;
    font-weight: 700;
    opacity: 0.9;
  }}
  h1 {{
    margin: 0;
    font-family: Inter, "Segoe UI", sans-serif;
  }}
  h2 {{
    margin: 0 0 10px;
    font-family: Inter, "Segoe UI", sans-serif;
    font-size: 20px;
    font-weight: 750;
    letter-spacing: -0.015em;
    color: var(--ink);
  }}
  h3 {{
    margin: 16px 0 8px;
    font-size: 14px;
    font-weight: 700;
    color: var(--ink);
  }}
  .toggle {{
    position: absolute;
    right: 24px;
    top: 34px;
    display: inline-flex;
    background: #e6ebf5;
    padding: 3px;
    border-radius: 999px;
    gap: 2px;
  }}
  .toggle button {{
    border: none;
    border-radius: 999px;
    background: transparent;
    color: var(--muted);
    font: inherit;
    font-size: 13px;
    font-weight: 700;
    padding: 6px 14px;
    cursor: pointer;
  }}
  body[data-lang="en"] #btn-en,
  body[data-lang="ru"] #btn-ru {{
    background: var(--navy);
    color: white;
    box-shadow: 0 2px 6px rgba(0, 91, 255, 0.28);
  }}
  main {{ max-width: 1180px; margin: 0 auto; padding: 8px 24px 48px; }}
  .period {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 10px 0 16px;
  }}
  .period div, .kpi, .card, .ask {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
  }}
  .period div {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 14px 12px;
    text-align: center;
    background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
  }}
  .period span, .kpi span {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 28px;
    text-align: center;
    color: var(--muted);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}
  .period strong {{
    display: block;
    width: 100%;
    text-align: center;
    margin-top: 4px;
    font-size: 16px;
    font-weight: 750;
    color: var(--ink);
  }}
  .lead {{
    margin: 0 0 16px;
    padding: 14px 18px;
    background: #eef4ff;
    border: 1px solid #d4e2ff;
    border-radius: 14px;
    font-size: 15px;
    color: var(--ink);
  }}
  .kpis {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 14px;
    margin: 0 0 12px;
  }}
  .kpi {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 16px 10px 14px;
    text-align: center;
    border: 2px solid var(--copper);
    background: linear-gradient(180deg, #f2f7ff 0%, #ffffff 100%);
  }}
  .kpi.target {{
    border: 2px solid var(--copper);
    background: linear-gradient(180deg, #e8f1ff 0%, #ffffff 100%);
  }}
  .kpi strong {{
    display: block;
    width: 100%;
    margin-top: 6px;
    font-family: Inter, "Segoe UI", sans-serif;
    font-variant-numeric: tabular-nums;
    font-size: 20px;
    font-weight: 800;
    text-align: center;
    color: var(--ink);
  }}
  .kpi.target strong {{ color: var(--copper); }}
  .kpi em {{
    display: block;
    width: 100%;
    margin-top: 6px;
    color: var(--muted);
    font-style: normal;
    font-size: 11px;
    text-align: center;
  }}
  .card {{ padding: 20px 20px 18px; margin: 18px 0; }}
  .insight {{ margin: 0 0 14px; color: #273248; }}
  .note {{ margin: 10px 0 0; color: var(--muted); font-size: 13px; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{
    text-align: center;
    font-weight: 700;
    font-size: 12px;
    color: var(--muted);
    background: #f8faff;
    border-bottom: 1px solid var(--line);
    padding: 10px 8px;
    vertical-align: bottom;
  }}
  td {{
    text-align: right;
    padding: 9px 8px;
    border-bottom: 1px solid #eef2f8;
    font-variant-numeric: tabular-nums;
    font-family: Inter, "Segoe UI", sans-serif;
    font-size: 13px;
  }}
  td:first-child {{
    font-weight: 600;
    font-size: 13px;
    text-align: left;
  }}
  td.offer {{
    font-size: 12px;
    text-align: left;
  }}
  td.reason {{
    font-size: 12px;
    text-align: left;
    color: var(--muted);
  }}
  tfoot td {{
    border-top: 2px solid var(--ink);
    border-bottom: none;
    background: #f8faff;
    font-weight: 750;
    padding-top: 10px;
  }}
  .cell-bar {{
    display: block;
    height: 5px;
    border-radius: 999px;
    background: var(--track);
    margin-top: 5px;
    overflow: hidden;
  }}
  .cell-bar i {{
    display: block;
    height: 5px;
    border-radius: 999px;
    background: var(--copper);
  }}
  .sub-pct {{
    display: block;
    margin-top: 2px;
    font-size: 11px;
    font-weight: 500;
    color: var(--muted);
  }}
  .good {{ color: var(--good); font-weight: 700; }}
  .bad {{ color: var(--bad); font-weight: 700; }}
  .status {{
    display: inline-block;
    border-radius: 999px;
    background: #e8f8f0;
    border: 1px solid #a9e5c7;
    color: var(--good);
    padding: 4px 12px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 11px;
    font-weight: 700;
  }}
  .callout {{
    border-left: 4px solid var(--copper);
    border-radius: 10px;
    background: #eef4ff;
    padding: 12px 14px;
    margin: 14px 0;
  }}
  .callout p {{ margin: 0; }}
  .scale-head {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    font-weight: 600;
    color: var(--muted);
    margin: 10px 0 6px;
  }}
  .ruler {{
    position: relative;
    height: 16px;
    border-radius: 999px;
    background: var(--track);
    margin: 4px 0 8px;
  }}
  .ruler .obs {{
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    border-radius: 999px;
    background: var(--copper);
  }}
  .ruler .mde {{
    position: absolute;
    top: -5px;
    bottom: -5px;
    width: 3px;
    border-radius: 2px;
    background: var(--accent-warm);
  }}
  .asks {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .problem-hero {{
    background: linear-gradient(180deg, #fff5f4 0%, #ffffff 100%);
    border: 2px solid #f2b8b2;
    border-radius: 18px;
    padding: 20px 22px;
    margin: 22px 0 20px;
    box-shadow: 0 6px 22px rgba(217, 45, 32, 0.06);
    text-align: center;
  }}
  .problem-tag {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    background: #feeceb;
    color: var(--bad);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .problem-hero h2 {{
    margin: 0 0 8px;
    font-size: 21px;
    font-weight: 800;
    color: var(--ink);
    text-align: center;
  }}
  .problem-hero p {{
    margin: 0;
    font-size: 14px;
    color: #273248;
    text-align: left;
  }}
  .scqa-bar {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin: 14px 0 0;
    text-align: left;
  }}
  .scqa-item {{
    background: #ffffff;
    border: 1px solid #f2d5d2;
    border-radius: 14px;
    padding: 12px 14px;
    font-size: 13px;
    color: #273248;
  }}
  .scqa-item b {{
    display: block;
    text-align: center;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--copper);
    margin-bottom: 6px;
  }}
  .apex {{
    background: linear-gradient(180deg, #eef4ff 0%, #ffffff 100%);
    border: 2px solid var(--copper);
    border-radius: 18px;
    padding: 20px 22px;
    margin: 0 0 16px;
    box-shadow: 0 6px 22px rgba(0, 91, 255, 0.08);
    text-align: center;
  }}
  .apex-tag {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    background: var(--copper);
    color: #ffffff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .apex h2 {{
    margin: 0 0 6px;
    font-size: 21px;
    font-weight: 800;
    color: var(--ink);
    text-align: center;
  }}
  .apex p {{
    margin: 0;
    font-size: 14px;
    color: #273248;
    text-align: left;
  }}
  .pillars {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 0 0 22px;
  }}
  .pillar {{
    background: var(--card);
    border: 1px solid var(--line);
    border-top: 4px solid var(--copper);
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
  }}
  .pillar-head {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    gap: 4px;
    margin-bottom: 8px;
  }}
  .pillar-tag {{
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--copper);
    text-align: center;
  }}
  .pillar-share {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    background: #e8f8f0;
    color: var(--good);
    font-size: 11px;
    font-weight: 800;
  }}
  .pillar h3 {{
    margin: 0 0 6px;
    font-size: 15px;
    font-weight: 800;
    color: var(--ink);
    text-align: center;
  }}
  .pillar p {{
    margin: 0;
    font-size: 13px;
    color: #273248;
  }}
  .section-tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    background: #e8f0ff;
    color: var(--copper);
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 6px;
  }}
  .ask {{ padding: 14px 16px; border-radius: 14px; background: #fbfcff; }}
  .ask h3 {{
    display: inline-block;
    margin: 0 0 8px;
    padding: 3px 10px;
    border-radius: 999px;
    background: #e8f0ff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--copper);
  }}
  .ask p {{ margin: 0 0 6px; }}
  .ask p:last-child {{ margin: 0; color: var(--muted); font-size: 13px; }}
  details {{ margin-top: 12px; }}
  summary {{ cursor: pointer; color: var(--copper); font-weight: 600; font-size: 13px; }}
  li.rule-on {{ font-weight: 700; color: var(--copper); }}
  svg text {{ fill: var(--ink); font-family: Inter, "Segoe UI", sans-serif; font-weight: 600; }}
  .about-box {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px 20px;
    margin: 0 0 14px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
    font-size: 13px;
    color: #273248;
    text-align: left;
  }}
  .about-box p {{ margin: 0 0 6px; text-align: left; }}
  .about-box p:last-of-type {{ margin: 0; }}
  .synth-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    background: #eef4ff;
    color: var(--copper);
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 8px;
  }}
  .glossary-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--line);
    font-size: 12px;
  }}
  .glossary-grid div {{
    background: #f8faff;
    border: 1px solid #e6ecf7;
    border-radius: 10px;
    padding: 8px 10px;
  }}
  .glossary-grid b {{ color: var(--ink); display: block; margin-bottom: 2px; }}
  footer.doc-footer {{
    margin-top: 28px;
    padding: 16px 20px;
    border-radius: 16px;
    background: var(--card);
    border: 1px solid var(--line);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 13px;
    color: var(--muted);
  }}
  footer.doc-footer a {{
    color: var(--copper);
    text-decoration: none;
    font-weight: 600;
  }}
  footer.doc-footer a:hover {{ text-decoration: underline; }}
  .sens-box {{
    background: #f8faff;
    border: 1px solid #d4e2ff;
    border-radius: 14px;
    padding: 14px 16px;
    margin: 12px 0;
  }}
  .sens-box h4 {{
    margin: 0 0 8px;
    font-size: 13px;
    font-weight: 750;
    color: var(--ink);
  }}
  .sens-controls {{
    display: grid;
    grid-template-columns: 1fr 1fr 1.2fr;
    gap: 14px;
    align-items: center;
    font-size: 13px;
  }}
  .sens-controls label {{
    display: block;
    font-weight: 600;
    color: #273248;
  }}
  .sens-controls input[type="range"] {{
    width: 100%;
    margin-top: 6px;
    accent-color: var(--copper);
  }}
  .sens-out {{
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 10px 12px;
    font-variant-numeric: tabular-nums;
    font-size: 13px;
  }}
  @media (max-width: 900px) {{
    .period, .kpis, .asks, .scqa-bar, .pillars, .glossary-grid, .sens-controls {{ grid-template-columns: 1fr; }}
    h1 {{ font-size: 34px; }}
    .scale-head {{ flex-direction: column; gap: 2px; }}
  }}
</style>
</head>
<body data-lang="ru">
<header>
  <div>
    <h1 class="kicker lang-ru">Еженедельный обзор ценообразования<small>B2C, отели · Закрытые тарифы (CUG) и лояльность</small></h1>
    <h1 class="kicker lang-en">Weekly Pricing Review<small>B2C Hotels · Closed-User-Group (CUG) &amp; Loyalty</small></h1>
  </div>
  <div class="toggle">
    <button id="btn-ru" type="button">RU</button>
    <button id="btn-en" type="button">EN</button>
  </div>
</header>
<main>
  <section class="lang-ru">{_body("ru", ctx)}</section>
  <section class="lang-en">{_body("en", ctx)}</section>
</main>
<script>
  function setLang(lang) {{
    document.body.dataset.lang = lang;
    document.documentElement.lang = lang;
    try {{ localStorage.setItem("keystone-lang", lang); }} catch (err) {{}}
  }}
  document.getElementById("btn-en").addEventListener("click", function () {{ setLang("en"); }});
  document.getElementById("btn-ru").addEventListener("click", function () {{ setLang("ru"); }});
  function fmtNum(x, digits, lang) {{
    var parts = Math.abs(x).toFixed(digits).split(".");
    var sep = lang === "ru" ? " " : ",";
    var intPart = parts[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, sep);
    return parts.length > 1 ? intPart + (lang === "ru" ? "," : ".") + parts[1] : intPart;
  }}
  function fmtEur(x, digits, lang, signed) {{
    var sign = x < 0 ? "−" : (signed && x > 0 ? "+" : "");
    var body = fmtNum(x, digits, lang);
    return lang === "ru" ? sign + body + " €" : sign + "€" + body;
  }}
  function updateSens(lang) {{
    var out = document.getElementById("sens-res-" + lang);
    var d = out.dataset;
    var brk = parseFloat(document.getElementById("brk-" + lang).value) / 100.0;
    var adv = parseFloat(document.getElementById("adv-" + lang).value) / 100.0;
    document.getElementById("brk-val-" + lang).textContent = Math.round(brk * 100) + "%";
    document.getElementById("adv-val-" + lang).textContent = Math.round(adv * 100) + "%";
    var nominal = parseFloat(d.nominal);
    var baseEff = parseFloat(d.baseEff);
    var eff = nominal * (1.0 - brk) * (1.0 - adv);
    var scale = eff / baseEff - 1.0;
    var cpsB = parseFloat(d.cpsB) - parseFloat(d.promoBPs) * scale;
    var diff = cpsB - parseFloat(d.cpsA);
    var totalDiff = parseFloat(d.armGap) - parseFloat(d.promoB) * scale;
    var nomStr = Math.round(nominal * 100) + "%";
    var effStr = fmtNum(eff * 100, 2, lang) + "%";
    if (lang === "ru") {{
      out.innerHTML =
        "Ставка резерва под " + nomStr + " баллов: <strong>" + effStr + " от GBV</strong><br>" +
        "Маржа Группы B: <strong>" + fmtEur(cpsB, 3, lang, false) + "/сессия</strong> (" + fmtEur(diff, 3, lang, true) + " к A, или <strong>" + fmtEur(totalDiff, 0, lang, true) + "</strong> на ветке B)";
    }} else {{
      out.innerHTML =
        "Accrued cost of " + nomStr + " points: <strong>" + effStr + " of GBV</strong><br>" +
        "Group B margin: <strong>" + fmtEur(cpsB, 3, lang, false) + "/session</strong> (" + fmtEur(diff, 3, lang, true) + " vs A, or <strong>" + fmtEur(totalDiff, 0, lang, true) + "</strong> on Arm B)";
    }}
  }}
  ["ru", "en"].forEach(function (l) {{
    var b = document.getElementById("brk-" + l);
    var a = document.getElementById("adv-" + l);
    if (b && a) {{
      b.addEventListener("input", function () {{ updateSens(l); }});
      a.addEventListener("input", function () {{ updateSens(l); }});
    }}
  }});
  try {{
    var saved = localStorage.getItem("keystone-lang");
    if (saved === "ru" || saved === "en") setLang(saved);
  }} catch (err) {{}}
</script>
</body>
</html>
"""


def _t(lang: str, en: str, ru: str) -> str:
    return ru if lang == "ru" else en


def _period(ctx: dict) -> tuple[date, date, int]:
    start = date.fromisoformat(str(ctx["start"])[:10])
    end = date.fromisoformat(str(ctx["end"])[:10])
    return start, end, (end - start).days + 1


def _dmy(value: date, lang: str = "ru") -> str:
    if lang == "en":
        return value.isoformat()
    return f"{value.day:02d}.{value.month:02d}.{value.year}"


def _week_tick(week: str, lang: str = "ru") -> str:
    text = str(week)
    if "-W" not in text:
        return text
    year_s, week_s = text.split("-W", 1)
    monday = date.fromisocalendar(int(year_s), int(week_s), 1)
    if lang == "en":
        months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        return f"{months[monday.month - 1]} {monday.day:02d}"
    return f"{monday.day:02d}.{monday.month:02d}"


def _body(lang: str, ctx: dict) -> str:
    return f"""
    {_about_and_glossary(lang, ctx)}
    {_period_band(lang, ctx)}
    <div class="kpis">{_kpis(lang, ctx)}</div>
    <p class="note">{escape(_kpi_note(lang, ctx))}</p>
    {_minto_pyramid(lang, ctx)}
    <div class="card">
      <span class="section-tag">{escape(_t(lang, "Decision Matrix · By Segment", "Детализация решения · По сегментам"))}</span>
      <h2>{escape(_t(lang, "1. Decision Matrix Across the 5 CUG Segments (Before → After)", "1. Матрица решений по 5 сегментам доступа (CUG) и промо (Было → Стало)"))}</h2>
      <p class="insight">{escape(_package_insight(lang, ctx))}</p>
      <div class="table-wrap">{_move_table(lang, ctx)}</div>
    </div>
    <div class="card">
      <span class="section-tag">{escape(_t(lang, "Analytical Evidence · Segment Unit Economics", "Аналитическое обоснование · Юнит-экономика сегментов CUG"))}</span>
      <h2>{escape(_t(lang, "2. 90-Day Audit of the 5 CUG Segments & Promo Cannibalization", "2. Диагностика 5 сегментов доступа (CUG) и потерь на каннибализации промо за 90 дней"))}</h2>
      <p class="insight">{escape(_fence_insight(lang, ctx))}</p>
      <div class="table-wrap">{_score_table(lang, ctx)}</div>
      <p class="note">{escape(_t(lang, _SCORE_NOTE_EN, _SCORE_NOTE_RU))}</p>
    </div>
    <div class="card">
      <span class="section-tag">{escape(_t(lang, "Analytical Evidence · 50/50 A/B Experiment", "Аналитическое обоснование · Эксперимент A/B 50/50"))}</span>
      <h2>{escape(_t(lang, "3. Classic 50/50 A/B Test on Logged-in Web: −6% Cash vs. 9% Loyalty Points", "3. Классический A/B-тест (50/50) на клубном тарифе сайта: скидка −6% деньгами против 9% баллами"))}</h2>
      {_ab_section(lang, ctx)}
    </div>
    <div class="card">
      <span class="section-tag">{escape(_t(lang, "Analytical Evidence · 13-Week Time-Series", "Аналитическое обоснование · Сезонность и промо-нагрузка (13 недель)"))}</span>
      <h2>{escape(_t(lang, "4. Weekly Conversion and Promo Spend Share (13 Weeks)", "4. Недельный ряд: конверсия и доля затрат на промо в валовой выручке (13 недель)"))}</h2>
      <p class="insight">{escape(_weekly_insight(lang, ctx))}</p>
      {_lines(lang, ctx)}
      <details>
        <summary>{escape(_t(lang, "Show weekly table (13 weeks)", "Показать таблицу по неделям (13 недель)"))}</summary>
        <div class="table-wrap">{_weekly_table(lang, ctx)}</div>
      </details>
    </div>
    <div class="card">
      <span class="section-tag">{escape(_t(lang, "Rollout Plan · Partner Teams", "План внедрения · Смежные подразделения"))}</span>
      <h2>{escape(_t(lang, "5. Recommendations to Partner Teams for the Coming Week", "5. Рекомендации смежным подразделениям на ближайшую неделю"))}</h2>
      <p class="insight">{escape(_t(lang, _ASK_INTRO_EN, _ASK_INTRO_RU))}</p>
      <div class="asks">{_ask_cards(lang, ctx)}</div>
    </div>
    {_footer(lang, ctx)}
    """


_SCORE_NOTE_EN = (
    "Promo cannibalization % is the share of discounted/CUG bookings made by customers who would have booked at the public parity rate anyway (in production measured via a 5–10% Holdout group). "
    "The 4.3% effective cost for 9% loyalty points is a model assumption (0.09 * (1 - 0.36) * (1 - 0.25) = 4.32%) calibrated on points-expiry cohorts (36% breakage) and repeat direct-booking attribution (25% ad-spend saving; 5.76% without ad-spend credit)."
)
_SCORE_NOTE_RU = (
    "Доля каннибализации промо - процент броней со скидкой, которые совершили клиенты, готовые купить и по открытой цене витрины (на реальных данных измеряется через 5–10% Holdout-группу). "
    "Себестоимость 4,3% от GBV для 9% баллами - модельное допущение (0,09 * (1 - 0,36) * (1 - 0,25) = 4,32%), калибруемое на собственных когортах неиспользованных баллов (breakage 36%) и экономии на повторном платном трафике (25%; без зачёта рекламы - 5,76% от GBV)."
)
_ASK_INTRO_EN = (
    "Section 1 sets the CUG and loyalty pricing rules. "
    "The four cards below specify the partner-team actions required this week."
)
_ASK_INTRO_RU = (
    "Раздел 1 задаёт правила закрытых тарифов и баллов лояльности. "
    "Ниже - конкретные задачи смежным подразделениям на ближайшую неделю."
)


def _about_and_glossary(lang: str, ctx: dict) -> str:
    seed = ctx["seed"]
    if lang == "ru":
        return (
            "<div class='about-box'>"
            f"<div><span class='synth-badge'>О проекте · Синтетические данные (seed {seed})</span></div>"
            "<p><strong>О проекте:</strong> аналитический кейс по управлению ценообразованием, закрытыми тарифами и программой лояльности в B2C-сервисе бронирования отелей. Все цифры сгенерированы программно и иллюстративны.</p>"
            "<p><strong>Задача кейса:</strong> показать, как расти в маржинальной прибыли в условиях жёсткого паритета цен с отелями - за счёт настройки закрытых сегментов (CUG), перевода прямых скидок в баллы лояльности и отключения каннибализирующих купонов.</p>"
            "<details><summary>Мини-глоссарий терминов отчёта (CUG, GBV, Breakage, Каннибализация, MDE)</summary>"
            "<div class='glossary-grid'>"
            "<div><b>CUG (Closed User Group)</b>Закрытый сегмент пользователей (после логина, в приложении или по триггеру корзины), где скидки не нарушают публичный паритет цен с отелями.</div>"
            "<div><b>GBV (Gross Booking Value)</b>Валовая стоимость всех бронирований в ценах открытой витрины до вычета скидок и комиссии отеля.</div>"
            "<div><b>Валовая выручка (Take Rate)</b>Удержанная комиссия OTA (наценка 12% к нетто-тарифу отеля за вычетом отмен) до вычета затрат на промо и баллы.</div>"
            "<div><b>Breakage (Неиспользованные баллы)</b>Доля начисленных баллов лояльности (36%), которые сгорают или не списываются клиентами, снижая реальную себестоимость кешбэка.</div>"
            "<div><b>Каннибализация промо</b>Доля скидок, которую забирают клиенты, готовые купить отель и по полной открытой цене (на реальных данных измеряется через Holdout-группу).</div>"
            "<div><b>MDE (Min. Detectable Effect)</b>Минимальный сдвиг конверсии (0,5 п.п.), который A/B-тест данного объёма выборки способен отличить от случайного шума при мощности 80%.</div>"
            "</div></details></div>"
        )
    return (
        "<div class='about-box'>"
        f"<div><span class='synth-badge'>About · Synthetic Data (seed {seed})</span></div>"
        "<p><strong>About the project:</strong> analytical case study on pricing, closed-user-group rates, and loyalty optimization for a B2C hotel OTA. All figures are synthetic and illustrative.</p>"
        "<p><strong>Case objective:</strong> demonstrate how to grow contribution margin under strict hotel rate parity by optimizing Closed-User-Group (CUG) fences, shifting from instant cash discounts to loyalty points, and retiring cannibalizing coupons.</p>"
        "<details><summary>Mini-glossary of terms (CUG, GBV, Breakage, Cannibalization, MDE)</summary>"
        "<div class='glossary-grid'>"
        "<div><b>CUG (Closed User Group)</b>Gated customer segment (logged-in web, mobile app, abandoned cart) where discounts do not violate public hotel rate parity.</div>"
        "<div><b>GBV (Gross Booking Value)</b>Total booking value at public parity prices before discounts and supplier payouts.</div>"
        "<div><b>Gross Revenue (Take Rate)</b>Retained OTA commission (12% markup over hotel net rate after cancellations) before promo and loyalty spend.</div>"
        "<div><b>Points Breakage</b>Share of issued loyalty points (36%) that expire unredeemed, lowering the real unit cost of cashback points.</div>"
        "<div><b>Promo Cannibalization</b>Share of discounts claimed by customers who would have booked at full price anyway (measured in production via Holdout groups).</div>"
        "<div><b>MDE (Min. Detectable Effect)</b>Smallest conversion change (0.5 pp) the 50/50 A/B sample can reliably detect at 80% statistical power.</div>"
        "</div></details></div>"
    )


def _footer(lang: str, ctx: dict) -> str:
    seed = ctx["seed"]
    if lang == "ru":
        return (
            "<footer class='doc-footer'>"
            f"<span>Синтетические данные (seed {seed}), цифры иллюстративны и не содержат коммерческой тайны.</span>"
            "<span>Автор: <strong>Дарья Кочетова</strong> · "
            "<a href='https://github.com/kochetova-daryaa/ota-cug-loyalty-pricing' target='_blank' rel='noopener'>GitHub-репозиторий</a> · "
            "<a href='https://github.com/kochetova-daryaa/ota-cug-loyalty-pricing/blob/main/README.ru.md' target='_blank' rel='noopener'>Описание и методология (RU)</a></span>"
            "</footer>"
        )
    return (
        "<footer class='doc-footer'>"
        f"<span>Synthetic data (seed {seed}); figures are illustrative and contain no proprietary OTA data.</span>"
        "<span>Author: <strong>Darya Kochetova</strong> · "
        "<a href='https://github.com/kochetova-daryaa/ota-cug-loyalty-pricing' target='_blank' rel='noopener'>GitHub Repository</a> · "
        "<a href='https://github.com/kochetova-daryaa/ota-cug-loyalty-pricing/blob/main/README.md' target='_blank' rel='noopener'>Documentation &amp; Assumptions (EN)</a></span>"
        "</footer>"
    )


def _period_band(lang: str, ctx: dict) -> str:
    start, end, days = _period(ctx)
    total = ctx["total"]
    cells = [
        (_t(lang, "Reporting period", "Отчётный период"), _t(lang, f"{days} days", f"{days} дней")),
        (_t(lang, "Dates, inclusive", "Даты, включительно"), f"{_dmy(start, lang)} - {_dmy(end, lang)}"),
        (
            _t(lang, "Volume in period", "Объём периода"),
            _t(
                lang,
                f"{fmt_int(total['sessions'], lang)} sessions · {fmt_int(total['bookings'], lang)} bookings",
                f"{fmt_int(total['sessions'], lang)} сессий · {fmt_int(total['bookings'], lang)} броней",
            ),
        ),
        (
            _t(lang, "Target metric", "Целевая метрика"),
            _t(lang, "Contribution Margin, EUR", "Маржинальная прибыль, €"),
        ),
    ]
    body = "".join(f"<div><span>{escape(label)}</span><strong>{escape(value)}</strong></div>" for label, value in cells)
    return f'<div class="period">{body}</div>'


def _minto_pyramid(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    pkg = ctx["package"]
    fmap = {f["fence_id"]: f for f in ctx["fences"]}
    blanket = fmap["blanket_promo"]
    member = fmap["member_web"]
    cart = fmap["cart_recovery"]
    app = fmap["app_only"]

    promo_of_gross = total["promo_cost"] / total["net_revenue"]
    cannib_of_promo = total["cannibalized_cost"] / total["promo_cost"]
    rel_cm = pkg["delta_contribution"] / total["contribution"]
    rel_promo = pkg["delta_promo_cost"] / total["promo_cost"]
    new_margin = (total["contribution"] + pkg["delta_contribution"]) / (total["gbv"] + pkg["delta_gbv"])

    p1_eur = blanket["delta_contribution"]
    p2_eur = member["delta_contribution"] + cart["delta_contribution"]
    p3_eur = app["delta_contribution"]
    tot_delta = pkg["delta_contribution"]
    p1_sh = p1_eur / tot_delta
    p2_sh = p2_eur / tot_delta
    p3_sh = p3_eur / tot_delta

    if lang == "ru":
        problem_tag = "Текущая бизнес-проблема · Утечка маржи"
        problem_title = (
            f"Мы теряем {fmt_eur(total['cannibalized_cost'], 'ru')} ({fmt_pct(cannib_of_promo, 'ru')} всего промо-бюджета) "
            f"на каннибализации скидок - клиентам, готовым покупать и по полной цене"
        )
        problem_sub = (
            f"За 90 дней на скидки и баллы потрачено {fmt_eur(total['promo_cost'], 'ru')} ({fmt_pct(total['promo_cost'] / total['gbv'], 'ru')} от GBV и {fmt_pct(promo_of_gross, 'ru')} валовой выручки), "
            f"но более половины этих денег субсидирует органический спрос. Главный источник потерь - массовый купон −8% в баннерах (каннибализация {fmt_pct(blanket['cannibalization_share'], 'ru', 0)}, потеряно {fmt_eur(blanket['cannibalized_cost_now'], 'ru')})."
        )
        scqa = [
            (
                "scqa-item",
                "Рыночный контекст",
                "На открытой витрине (34,0% трафика) мы держим 0% скидки, чтобы сохранять коммерческий паритет с отелями и не терять ранжирование в метапоиске; поэтому ценовая конкуренция идёт внутри закрытых сегментов (CUG).",
            ),
            (
                "scqa-item",
                "Целевая задача",
                f"Остановить сжигание маржи на каннибализации без размытия открытой витрины и без потери конверсии сервиса ({fmt_pct(total['conversion'], 'ru')}).",
            ),
        ]
        apex_tag = "Предлагаемое решение на утверждение"
        apex_title = (
            f"Перестроить матрицу закрытых тарифов (CUG) и баллов лояльности: "
            f"{fmt_signed_eur(tot_delta, 'ru')} ({fmt_signed_pct(rel_cm, 'ru')}) к маржинальной прибыли "
            f"и {fmt_signed_eur(pkg['delta_promo_cost'], 'ru')} ({fmt_signed_pct(rel_promo, 'ru')}) затрат на промо"
        )
        apex_sub = (
            f"На базе тех же 250 000 сессий маржинальная прибыль вырастет с {fmt_eur(total['contribution'], 'ru')} до {fmt_eur(total['contribution'] + tot_delta, 'ru')} "
            f"(маржинальность с {fmt_pct(total['margin'], 'ru')} до {fmt_pct(new_margin, 'ru')} от GBV) при сохранении конверсии ({fmt_pp(pkg['delta_conversion'], 'ru')}) и 100% паритете на витрине. "
            "Результат складывается из трёх рычагов:"
        )
        pillars = [
            (
                "Рычаг 1 · Отключение неэффективного купона",
                f"{fmt_pct(p1_sh, 'ru')} эффекта",
                f"{fmt_signed_eur(p1_eur, 'ru')} маржинальной прибыли",
                f"Закрываем публичный купон −8% в баннерах (71% каннибализации) и переводим в закрытый бонус 5% баллами (резерв 2,4% от GBV). Экономия промо-бюджета: {fmt_signed_eur(blanket['delta_promo_cost'], 'ru')} (−71,4%).",
            ),
            (
                "Рычаг 2 · Перевод скидок в баллы (Веб + Корзина)",
                f"{fmt_pct(p2_sh, 'ru')} эффекта",
                f"{fmt_signed_eur(p2_eur, 'ru')} маржинальной прибыли",
                f"Дораскатываем кешбэк 9% баллами на вторые 50% клубного веба ({fmt_signed_eur(member['delta_contribution'], 'ru')}) и вводим в корзине порог чека >= 180 € с 7,5% баллами ({fmt_signed_eur(cart['delta_contribution'], 'ru')}). При когортном breakage 36% резерв под баллы составляет 3,6–4,3% вместо 5–6% деньгами.",
            ),
            (
                "Рычаг 3 · Таргетинг по глубине в Приложении",
                f"{fmt_pct(p3_sh, 'ru')} эффекта",
                f"{fmt_signed_eur(p3_eur, 'ru')} маржинальной прибыли",
                "В мобильном приложении заменяем плоскую скидку −5% на сетку по глубине заезда: −3% на неэластичном окне 0–3 дня (где каннибализация 69%) и −6% на эластичном окне 8+ дней (где каннибализация 39% и выше ценовой отклик), поднимая конверсию сегмента на +0,3 п.п.",
            ),
        ]
    else:
        problem_tag = "Current Business Problem · Margin Leakage"
        problem_title = (
            f"We are losing {fmt_eur(total['cannibalized_cost'], 'en')} ({fmt_pct(cannib_of_promo, 'en')} of total promo spend) "
            f"to promo cannibalization - subsidizing customers who would book at full price anyway"
        )
        problem_sub = (
            f"Over 90 days {fmt_eur(total['promo_cost'], 'en')} ({fmt_pct(total['promo_cost'] / total['gbv'], 'en')} of GBV and {fmt_pct(promo_of_gross, 'en')} of Gross Revenue) was spent on discounts and points, "
            f"with more than half going to organic buyers. The primary leak is the −8% public banner coupon ({fmt_pct(blanket['cannibalization_share'], 'en', 0)} cannibalization, {fmt_eur(blanket['cannibalized_cost_now'], 'en')} lost)."
        )
        scqa = [
            (
                "scqa-item",
                "Market Context",
                "On the public storefront (34.0% of traffic) we maintain 0% discount to preserve commercial parity with hotel partners and metasearch ranking, so price competition happens inside closed CUG segments.",
            ),
            (
                "scqa-item",
                "Objective",
                f"Stop margin drain from promo cannibalization without undercutting the public storefront or dropping conversion ({fmt_pct(total['conversion'], 'en')}).",
            ),
        ]
        apex_tag = "Proposed Solution for Approval"
        apex_title = (
            f"Restructure the CUG & Loyalty Matrix: "
            f"{fmt_signed_eur(tot_delta, 'en')} ({fmt_signed_pct(rel_cm, 'en')}) in Contribution Margin "
            f"and {fmt_signed_eur(pkg['delta_promo_cost'], 'en')} ({fmt_signed_pct(rel_promo, 'en')}) in Promo Spend"
        )
        apex_sub = (
            f"On the same 250,000 sessions, contribution margin rises from {fmt_eur(total['contribution'], 'en')} to {fmt_eur(total['contribution'] + tot_delta, 'en')} "
            f"(margin from {fmt_pct(total['margin'], 'en')} to {fmt_pct(new_margin, 'en')} of GBV) while holding conversion ({fmt_pp(pkg['delta_conversion'], 'en')}) and 100% rate parity. "
            "Delivered through three levers:"
        )
        pillars = [
            (
                "Lever 1 · Retire Low-Efficiency Banner Coupon",
                f"{fmt_pct(p1_sh, 'en')} of impact",
                f"{fmt_signed_eur(p1_eur, 'en')} contribution margin",
                f"Close the −8% public banner coupon (71% cannibalization) and gate into 5% welcome points (2.4% of GBV accrued cost), saving {fmt_signed_eur(blanket['delta_promo_cost'], 'en')} (−71.4%) in promo spend.",
            ),
            (
                "Lever 2 · Cash-to-Points Shift (Web + Cart)",
                f"{fmt_pct(p2_sh, 'en')} of impact",
                f"{fmt_signed_eur(p2_eur, 'en')} contribution margin",
                f"Roll 9% points out to the remaining 50% of logged-in web ({fmt_signed_eur(member['delta_contribution'], 'en')}) and set a €180 floor on abandoned cart with 7.5% points ({fmt_signed_eur(cart['delta_contribution'], 'en')}), accruing points at 3.6–4.3% vs 5–6% cash.",
            ),
            (
                "Lever 3 · Lead-Time Tiering in Mobile App",
                f"{fmt_pct(p3_sh, 'en')} of impact",
                f"{fmt_signed_eur(p3_eur, 'en')} contribution margin",
                "Replace the flat −5% app discount with a lead-time grid: −3% on inelastic 0–3d stays (69% cannibalization) and −6% on elastic 8+d stays (39% cannibalization, higher price response), lifting app conversion by +0.3 pp.",
            ),
        ]

    scqa_html = "".join(
        f"<div class='{cls}'><b>{escape(tag)}</b>{escape(text)}</div>"
        for cls, tag, text in scqa
    )
    pillar_html = "".join(
        "<article class='pillar'>"
        f"<div class='pillar-head'><span class='pillar-tag'>{escape(tag)}</span><span class='pillar-share'>{escape(share)}</span></div>"
        f"<h3>{escape(headline)}</h3>"
        f"<p>{escape(desc)}</p>"
        "</article>"
        for tag, share, headline, desc in pillars
    )
    return (
        f"<div class='problem-hero'><span class='problem-tag'>{escape(problem_tag)}</span><h2>{escape(problem_title)}</h2><p>{escape(problem_sub)}</p><div class='scqa-bar'>{scqa_html}</div></div>"
        f"<div class='apex'><span class='apex-tag'>{escape(apex_tag)}</span><h2>{escape(apex_title)}</h2><p>{escape(apex_sub)}</p></div>"
        f"<div class='pillars'>{pillar_html}</div>"
    )


def _kpi_note(lang: str, ctx: dict) -> str:
    _, _, days = _period(ctx)
    total = ctx["total"]
    pay = total["payment_cost"]
    sess_c = total["session_cost"]
    if lang == "ru":
        return (
            f"Формула каскада P&L за {days} дней: наценка 12% к нетто отеля даёт 10,71% от GBV до отмен; после вычета ~10% отмен (с удержанием 25% сбора) "
            f"Валовая выручка составляет {fmt_eur(total['net_revenue'], 'ru')} (9,9% от GBV). "
            f"Маржинальная прибыль ({fmt_eur(total['contribution'], 'ru')}) = Валовая выручка ({fmt_eur(total['net_revenue'], 'ru')}) "
            f"− Затраты на промо и баллы ({fmt_eur(total['promo_cost'], 'ru')}) − Эквайринг 1,4% ({fmt_eur(pay, 'ru')}) − Затраты на привлечение трафика ({fmt_eur(sess_c, 'ru')})."
        )
    return (
        f"P&L bridge across {days} days: a 12% markup over hotel net equals 10.71% of GBV before cancellations; after ~10% cancellations (with 25% fee retention) "
        f"Gross Revenue is {fmt_eur(total['net_revenue'], 'en')} (9.9% of GBV Take Rate). "
        f"Contribution Margin ({fmt_eur(total['contribution'], 'en')}) = Gross Revenue ({fmt_eur(total['net_revenue'], 'en')}) "
        f"− Promo & Loyalty Spend ({fmt_eur(total['promo_cost'], 'en')}) − Payment Processing 1.4% ({fmt_eur(pay, 'en')}) − Traffic Acquisition Cost ({fmt_eur(sess_c, 'en')})."
    )


def _kpis(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    aov = total["gbv"] / total["bookings"]
    take_rate = total["net_revenue"] / total["gbv"]
    promo_gbv = total["promo_cost"] / total["gbv"]
    promo_gross = total["promo_cost"] / total["net_revenue"]
    cm_gbv = total["margin"]
    cm_gross = total["contribution"] / total["net_revenue"]
    rows = [
        (
            "Sessions",
            "Сессии",
            fmt_int(total["sessions"], lang),
            f"visits in 90 days · {fmt_int(total['bookings'], 'en')} bookings",
            f"визиты за 90 дней · {fmt_int(total['bookings'], 'ru')} броней",
            False,
        ),
        (
            "Conversion",
            "Конверсия",
            fmt_pct(total["conversion"], lang),
            f"{fmt_int(total['bookings'], 'en')} of {fmt_int(total['sessions'], 'en')} sessions",
            f"{fmt_int(total['bookings'], 'ru')} из {fmt_int(total['sessions'], 'ru')} сессий",
            False,
        ),
        (
            "GBV, EUR",
            "Валовая стоимость (GBV)",
            fmt_eur(total["gbv"], lang),
            f"avg booking value {fmt_eur(aov, 'en')}",
            f"средний чек брони {fmt_eur(aov, 'ru')}",
            False,
        ),
        (
            "Gross Revenue",
            "Валовая выручка",
            fmt_eur(total["net_revenue"], lang),
            f"{fmt_pct(take_rate, 'en')} of GBV (Take Rate)",
            f"{fmt_pct(take_rate, 'ru')} от GBV (Take Rate)",
            False,
        ),
        (
            "Promo & Loyalty Spend",
            "Затраты на промо и баллы",
            fmt_eur(total["promo_cost"], lang),
            f"{fmt_pct(promo_gbv, 'en')} of GBV · {fmt_pct(promo_gross, 'en')} of Gross Rev",
            f"{fmt_pct(promo_gbv, 'ru')} от GBV · {fmt_pct(promo_gross, 'ru')} вал. выручки",
            False,
        ),
        (
            "Contribution Margin",
            "Маржинальная прибыль",
            fmt_eur(total["contribution"], lang),
            f"{fmt_pct(cm_gbv, 'en')} of GBV · {fmt_pct(cm_gross, 'en')} of Gross Rev",
            f"{fmt_pct(cm_gbv, 'ru')} от GBV · {fmt_pct(cm_gross, 'ru')} вал. выручки",
            True,
        ),
    ]
    cards = []
    for en, ru, value, hint_en, hint_ru, target in rows:
        cls = "kpi target" if target else "kpi"
        cards.append(
            f"<div class='{cls}'>"
            f"<span>{escape(_t(lang, en, ru))}</span>"
            f"<strong>{escape(value)}</strong>"
            f"<em>{escape(_t(lang, hint_en, hint_ru))}</em>"
            "</div>"
        )
    return "".join(cards)


def _package_insight(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    pkg = ctx["package"]
    rel_promo = abs(pkg["delta_promo_cost"]) / total["promo_cost"]
    rel_cm = pkg["delta_contribution"] / total["contribution"]
    new_margin = (total["contribution"] + pkg["delta_contribution"]) / (total["gbv"] + pkg["delta_gbv"])
    if lang == "ru":
        return (
            f"Пакет не затрагивает открытую витрину (0% скидки, 100% соблюдение паритета цен перед отелями), "
            f"сокращает затраты на промо и лояльность на {fmt_eur(abs(pkg['delta_promo_cost']), lang)} ({fmt_signed_pct(-rel_promo, lang)} к текущему промо-бюджету) "
            f"и приносит {fmt_signed_eur(pkg['delta_contribution'], lang)} маржинальной прибыли ({fmt_signed_pct(rel_cm, lang)} к базе, рост маржинальности с {fmt_pct(total['margin'], lang)} до {fmt_pct(new_margin, lang)} от GBV)."
        )
    return (
        f"The package leaves the public storefront untouched (0% discount, 100% hotel rate parity), "
        f"cuts promo & loyalty spend by {fmt_eur(abs(pkg['delta_promo_cost']), lang)} ({fmt_signed_pct(-rel_promo, lang)} vs current promo budget), "
        f"and adds {fmt_signed_eur(pkg['delta_contribution'], lang)} in contribution margin ({fmt_signed_pct(rel_cm, lang)} vs base, lifting margin from {fmt_pct(total['margin'], lang)} to {fmt_pct(new_margin, lang)} of GBV)."
    )


def _fence_insight(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    blanket = next(f for f in ctx["fences"] if f["fence_id"] == "blanket_promo")
    public = next(f for f in ctx["fences"] if f["fence_id"] == "public_parity")
    app = next(f for f in ctx["fences"] if f["fence_id"] == "app_only")
    b_cm_share = blanket["contribution_now"] / total["contribution"]
    b_promo_share = blanket["promo_cost_now"] / total["promo_cost"]
    app_cm_share = app["contribution_now"] / total["contribution"]
    pub_cm_share = public["contribution_now"] / total["contribution"]
    if lang == "ru":
        return (
            f"Главная потеря маржинальности - «{LABELS['ru']['blanket_promo']}»: сегмент потребляет {fmt_eur(blanket['promo_cost_now'], lang)} ({fmt_pct(b_promo_share, lang)} всего промо-бюджета), "
            f"но {fmt_pct(blanket['cannibalization_share'], lang, 0)} купонов уходит органическим покупателям, поэтому маржинальная прибыль составляет лишь {fmt_eur(blanket['contribution_now'], lang)} "
            f"({fmt_pct(b_cm_share, lang)} от общей маржи сервиса, {fmt_pct(blanket['margin_now'], lang)} от GBV). "
            f"Основную массу маржинальной прибыли формируют «{LABELS['ru']['public_parity']}» - {fmt_eur(public['contribution_now'], lang)} ({fmt_pct(pub_cm_share, lang)} итога) "
            f"и «{LABELS['ru']['app_only']}» - {fmt_eur(app['contribution_now'], lang)} ({fmt_pct(app_cm_share, lang)} итога, маржинальность {fmt_pct(app['margin_now'], lang)} от GBV)."
        )
    return (
        f"The main margin leak is '{LABELS['en']['blanket_promo']}': it consumes {fmt_eur(blanket['promo_cost_now'], lang)} ({fmt_pct(b_promo_share, lang)} of total promo spend), "
        f"yet {fmt_pct(blanket['cannibalization_share'], lang, 0)} of coupons go to organic buyers, leaving {fmt_eur(blanket['contribution_now'], lang)} "
        f"({fmt_pct(b_cm_share, lang)} of total margin, {fmt_pct(blanket['margin_now'], lang)} of GBV). "
        f"Total margin is anchored by '{LABELS['en']['public_parity']}' at {fmt_eur(public['contribution_now'], lang)} ({fmt_pct(pub_cm_share, lang)} of total) "
        f"and '{LABELS['en']['app_only']}' at {fmt_eur(app['contribution_now'], lang)} ({fmt_pct(app_cm_share, lang)} of total, {fmt_pct(app['margin_now'], lang)} of GBV)."
    )


def _tone(value: float) -> str:
    if value > 1e-9:
        return "good"
    if value < -1e-9:
        return "bad"
    return ""


def _move_table(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    pkg = ctx["package"]
    if lang == "ru":
        head = (
            "<tr><th>Сегмент доступа (CUG)</th><th>Было (механика и % от GBV)</th><th>Стало (решение недели)</th>"
            "<th>Δ затрат на промо (% к базе)</th><th>Δ маржинальной прибыли (% к базе)</th><th>Δ конверсии (% отн.)</th><th>Основание и ограничение</th></tr>"
        )
        total_label = "Итого по пакету"
    else:
        head = (
            "<tr><th>Price Fence (CUG Segment)</th><th>Before (mechanic &amp; % of GBV)</th><th>Proposed (weekly decision)</th>"
            "<th>Δ promo spend (% vs base)</th><th>Δ contribution margin (% vs base)</th><th>Δ conversion (% rel.)</th><th>Rationale &amp; constraint</th></tr>"
        )
        total_label = "Package total"

    rows = []
    for f in ctx["fences"]:
        now_s = offer_text(lang, f["mechanic_now"], f["nominal_now"], f["effective_now"], f["fence_id"], True)
        new_s = offer_text(lang, f["mechanic_new"], f["nominal_new"], f["effective_new"], f["fence_id"], False)
        reason = RULE_REASONS[lang][f["rule_code"]]
        promo_pct = (
            "-"
            if f["promo_cost_now"] <= 1e-6
            else fmt_signed_pct(f["delta_promo_cost"] / f["promo_cost_now"], lang)
        )
        if abs(f["contribution_now"]) < 5000:
            cm_pct = (
                f"база {fmt_eur(f['contribution_now'], 'ru')} → {fmt_eur(f['contribution_new'], 'ru')}"
                if lang == "ru"
                else f"base {fmt_eur(f['contribution_now'], 'en')} → {fmt_eur(f['contribution_new'], 'en')}"
            )
        else:
            cm_pct = fmt_signed_pct(f["delta_contribution"] / f["contribution_now"], lang)
        cvr_pct = fmt_signed_pct(f["delta_conversion"] / f["conversion_now"], lang)
        rows.append(
            "<tr>"
            f"<td>{escape(LABELS[lang][f['fence_id']])}</td>"
            f"<td class='offer'>{escape(now_s)}</td>"
            f"<td class='offer'><strong>{escape(new_s)}</strong></td>"
            f"<td class='{_tone(-f['delta_promo_cost'])}'>{escape(fmt_signed_eur(f['delta_promo_cost'], lang))}"
            f"<span class='sub-pct'>{escape(promo_pct)}</span></td>"
            f"<td class='{_tone(f['delta_contribution'])}'>{escape(fmt_signed_eur(f['delta_contribution'], lang))}"
            f"<span class='sub-pct'>{escape(cm_pct)}</span></td>"
            f"<td class='{_tone(f['delta_conversion'])}'>{escape(fmt_pp(f['delta_conversion'], lang))}"
            f"<span class='sub-pct'>{escape(cvr_pct)}</span></td>"
            f"<td class='reason'>{escape(reason)}</td>"
            "</tr>"
        )
    tot_promo_pct = fmt_signed_pct(pkg["delta_promo_cost"] / total["promo_cost"], lang)
    tot_cm_pct = fmt_signed_pct(pkg["delta_contribution"] / total["contribution"], lang)
    tot_cvr_pct = fmt_signed_pct(pkg["delta_conversion"] / total["conversion"], lang)
    foot = (
        "<tfoot><tr>"
        f"<td>{escape(total_label)}</td>"
        "<td>-</td><td>-</td>"
        f"<td class='{_tone(-pkg['delta_promo_cost'])}'>{escape(fmt_signed_eur(pkg['delta_promo_cost'], lang))}"
        f"<span class='sub-pct'>{escape(tot_promo_pct)}</span></td>"
        f"<td class='{_tone(pkg['delta_contribution'])}'>{escape(fmt_signed_eur(pkg['delta_contribution'], lang))}"
        f"<span class='sub-pct'>{escape(tot_cm_pct)}</span></td>"
        f"<td class='{_tone(pkg['delta_conversion'])}'>{escape(fmt_pp(pkg['delta_conversion'], lang))}"
        f"<span class='sub-pct'>{escape(tot_cvr_pct)}</span></td>"
        "<td></td>"
        "</tr></tfoot>"
    )
    return f"<table><thead>{head}</thead><tbody>{''.join(rows)}</tbody>{foot}</table>"


def _score_table(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    hi = max(abs(f["contribution_now"]) for f in ctx["fences"]) or 1.0
    if lang == "ru":
        head = (
            "<tr><th>Сегмент доступа (CUG)</th><th>Сессии (% трафика)</th><th>Конверсия (брони)</th><th>Валовая выручка (% от GBV)</th>"
            "<th>Затраты на промо (% вал. выручки)</th><th>Каннибализация промо (€ и % промо)</th><th>Маржинальная прибыль (% итога)</th><th>Маржа / сессия (% к ср.)</th><th>Маржинальность (% от GBV)</th></tr>"
        )
        total_label = "Итого / среднее"
        of_gbv = "от GBV"
        of_gross = "вал. выр."
        of_total = "итога"
        of_avg = "к средн."
    else:
        head = (
            "<tr><th>Price Fence (CUG Segment)</th><th>Sessions (% traffic)</th><th>Conversion (bookings)</th><th>Gross Revenue (% of GBV)</th>"
            "<th>Promo Spend (% Gross Rev)</th><th>Promo Cannibalization (€ &amp; %)</th><th>Contribution Margin (% total)</th><th>Margin / session (% vs avg)</th><th>Margin (% of GBV)</th></tr>"
        )
        total_label = "Total / average"
        of_gbv = "of GBV"
        of_gross = "Gross Rev"
        of_total = "of total"
        of_avg = "vs avg"

    avg_cps = total["contribution"] / total["sessions"]
    rows = []
    for f in ctx["fences"]:
        width = max(abs(f["contribution_now"]) / hi * 100.0, 2.0)
        sess_share = f["sessions"] / total["sessions"]
        take_rate = f["net_revenue_now"] / f["gbv_now"] if f["gbv_now"] else 0.0
        promo_of_gross = f["promo_cost_now"] / f["net_revenue_now"] if f["net_revenue_now"] else 0.0
        cm_share = f["contribution_now"] / total["contribution"]
        cps_rel = f["cps_now"] / avg_cps
        if f["mechanic_now"] == "none":
            cannib_cell = "-<span class='sub-pct'>0%</span>"
        else:
            cannib_cell = (
                f"{escape(fmt_eur(f['cannibalized_cost_now'], lang))}"
                f"<span class='sub-pct'>{escape(fmt_pct(f['cannibalization_share'], lang, 0))}</span>"
            )
        rows.append(
            "<tr>"
            f"<td>{escape(LABELS[lang][f['fence_id']])}</td>"
            f"<td>{escape(fmt_int(f['sessions'], lang))}<span class='sub-pct'>{escape(fmt_pct(sess_share, lang))}</span></td>"
            f"<td>{escape(fmt_pct(f['conversion_now'], lang))}<span class='sub-pct'>{escape(fmt_int(f['bookings_now'], lang))}</span></td>"
            f"<td>{escape(fmt_eur(f['net_revenue_now'], lang))}<span class='sub-pct'>{escape(fmt_pct(take_rate, lang))} {escape(of_gbv)}</span></td>"
            f"<td>{escape(fmt_eur(f['promo_cost_now'], lang))}<span class='sub-pct'>{escape(fmt_pct(promo_of_gross, lang))} {escape(of_gross)}</span></td>"
            f"<td>{cannib_cell}</td>"
            f"<td>{escape(fmt_eur(f['contribution_now'], lang))}<span class='sub-pct'>{escape(fmt_pct(cm_share, lang))} {escape(of_total)}</span>"
            f"<span class='cell-bar'><i style='width:{width:.1f}%'></i></span></td>"
            f"<td>{escape(fmt_eur(f['cps_now'], lang, 2))}<span class='sub-pct'>{escape(fmt_pct(cps_rel, lang, 0))} {escape(of_avg)}</span></td>"
            f"<td>{escape(fmt_pct(f['margin_now'], lang))}</td>"
            "</tr>"
        )
    tot_take = total["net_revenue"] / total["gbv"]
    tot_promo_gross = total["promo_cost"] / total["net_revenue"]
    tot_cannib_promo = total["cannibalized_cost"] / total["promo_cost"]
    foot = (
        "<tfoot><tr>"
        f"<td>{escape(total_label)}</td>"
        f"<td>{escape(fmt_int(total['sessions'], lang))}<span class='sub-pct'>{escape(fmt_pct(1.0, lang))}</span></td>"
        f"<td>{escape(fmt_pct(total['conversion'], lang))}<span class='sub-pct'>{escape(fmt_int(total['bookings'], lang))}</span></td>"
        f"<td>{escape(fmt_eur(total['net_revenue'], lang))}<span class='sub-pct'>{escape(fmt_pct(tot_take, lang))} {escape(of_gbv)}</span></td>"
        f"<td>{escape(fmt_eur(total['promo_cost'], lang))}<span class='sub-pct'>{escape(fmt_pct(tot_promo_gross, lang))} {escape(of_gross)}</span></td>"
        f"<td>{escape(fmt_eur(total['cannibalized_cost'], lang))}<span class='sub-pct'>{escape(fmt_pct(tot_cannib_promo, lang))}</span></td>"
        f"<td>{escape(fmt_eur(total['contribution'], lang))}<span class='sub-pct'>{escape(fmt_pct(1.0, lang))}</span></td>"
        f"<td>{escape(fmt_eur(avg_cps, lang, 2))}<span class='sub-pct'>100%</span></td>"
        f"<td>{escape(fmt_pct(total['margin'], lang))}</td>"
        "</tr></tfoot>"
    )
    return f"<table><thead>{head}</thead><tbody>{''.join(rows)}</tbody>{foot}</table>"


def _pp_mag(value: float, lang: str) -> str:
    unit = " п.п." if lang == "ru" else " pp"
    return fmt_num(abs(value) * 100, lang, 1) + unit


def _ab_section(lang: str, ctx: dict) -> str:
    ab = ctx["ab_test"]
    _, _, days = _period(ctx)
    ctrl, treat = ab["control"], ab["treatment"]
    tot_ab_sess = ctrl["sessions"] + treat["sessions"]
    ctrl_share = ctrl["sessions"] / tot_ab_sess
    treat_share = treat["sessions"] / tot_ab_sess
    rate_rel = (ab["treatment_effective_rate"] - ab["control_rate"]) / ab["control_rate"]
    cps_rel = ab["cps_diff"] / ctrl["cps"]
    cancel_diff = treat["cancel_rate"] - ctrl["cancel_rate"]
    cancel_rel = cancel_diff / ctrl["cancel_rate"]
    ci = f"{fmt_eur(ab['cps_ci_low'], lang, 3)} … {fmt_eur(ab['cps_ci_high'], lang, 3)}"
    ab_base_total = ctrl["contribution"] + treat["contribution"]
    arm_gap = treat["contribution"] - ctrl["contribution"]
    rollout_delta = next(f["delta_contribution"] for f in ctx["fences"] if f["fence_id"] == ab["fence_id"])
    eff_rate = ab["treatment_effective_rate"]
    sens_data = (
        f"data-nominal='{ab['treatment_points_rate']:.6f}' data-base-eff='{eff_rate:.6f}' "
        f"data-cps-a='{ctrl['cps']:.6f}' data-cps-b='{treat['cps']:.6f}' "
        f"data-promo-b-ps='{treat['promo_cost'] / treat['sessions']:.6f}' "
        f"data-promo-b='{treat['promo_cost']:.2f}' data-arm-gap='{arm_gap:.2f}'"
    )
    brk_pct = round(POINTS_BREAKAGE * 100)
    adv_pct = round(REPEAT_AD_SAVING * 100)
    if lang == "ru":
        badge = "Победила Группа B · Переводим на баллы"
        setup = (
            f"Сегмент «{LABELS['ru'][ab['fence_id']]}», честный сплит 50/50 на все {days} дней периода ({fmt_int(tot_ab_sess, 'ru')} сессий, 100% сегмента). "
            "Проверяем: можно ли заменить прямую скидку −6% деньгами (Группа A) на кешбэк 9% баллами лояльности (Группа B, реальная себестоимость 4,3% от GBV с учётом breakage), "
            "чтобы не потерять конверсию, но повысить маржинальную прибыль на каждом заказе."
        )
        head = "<tr><th>Показатель</th><th>Группа A (Контроль: −6% деньгами)</th><th>Группа B (Тест: 9% баллами)</th><th>Разница B − A (абс. и % к A)</th><th>Стат. значимость и вывод</th></tr>"
        rows = [
            (
                "Сессии и брони (% выборки)",
                f"{fmt_int(ctrl['sessions'], lang)} ({fmt_pct(ctrl_share, lang)}) · {fmt_int(ctrl['bookings'], lang)} бр.",
                f"{fmt_int(treat['sessions'], lang)} ({fmt_pct(treat_share, lang)}) · {fmt_int(treat['bookings'], lang)} бр.",
                f"+{fmt_int(treat['bookings'] - ctrl['bookings'], lang)} бр. ({fmt_signed_pct((treat['bookings'] - ctrl['bookings']) / ctrl['bookings'], lang)})",
                "равный сплит 50/50",
            ),
            (
                "Реальные затраты на промо (% от GBV)",
                fmt_pct(ab["control_rate"], lang),
                fmt_pct(ab["treatment_effective_rate"], lang),
                f"{fmt_pp(ab['treatment_effective_rate'] - ab['control_rate'], lang)} ({fmt_signed_pct(rate_rel, lang)} к A)",
                "учтены 36% неиспользованных баллов (breakage) и 25% экономии на рекламе",
            ),
            (
                "Конверсия в бронь",
                fmt_pct(ctrl["cvr"], lang),
                fmt_pct(treat["cvr"], lang),
                f"{fmt_pp(ab['cvr_diff'], lang)} ({fmt_signed_pct(ab['relative_cvr'], lang)} к A)",
                f"p = {fmt_num(ab['cvr_pvalue'], lang, 3)} · не значимо (внутри MDE {_pp_mag(ab['cvr_mde'], lang)})",
            ),
            (
                "Маржинальная прибыль на сессию",
                fmt_eur(ctrl["cps"], lang, 3),
                fmt_eur(treat["cps"], lang, 3),
                f"{fmt_signed_eur(ab['cps_diff'], lang, 3)} ({fmt_signed_pct(cps_rel, lang)} к A)",
                f"p < 0,001 · стат. значимо · 95% ДИ {ci}",
            ),
            (
                "Маржинальная прибыль группы, €",
                fmt_eur(ctrl["contribution"], lang),
                fmt_eur(treat["contribution"], lang),
                f"{fmt_signed_eur(treat['contribution'] - ctrl['contribution'], lang)} ({fmt_signed_pct((treat['contribution'] - ctrl['contribution']) / ctrl['contribution'], lang)} к A)",
                "суммарная маржинальная прибыль ветки за 90 дней",
            ),
            (
                "Доля отмен (Cancellation Rate)",
                fmt_pct(ctrl["cancel_rate"], lang),
                fmt_pct(treat["cancel_rate"], lang),
                f"{fmt_pp(cancel_diff, lang)} ({fmt_signed_pct(cancel_rel, lang)} к A)",
                "качество броней не ухудшилось",
            ),
        ]
        left_lbl = f"Фактическое отличие конверсии B от A: {_pp_mag(ab['cvr_diff'], lang)} ({fmt_signed_pct(ab['relative_cvr'], lang)} к контролю A)"
        right_lbl = f"Оранжевая риска - минимальный детектируемый эффект (MDE, мощность 80%): {_pp_mag(ab['cvr_mde'], lang)} ({fmt_pct(ab['cvr_mde'] / ctrl['cvr'], lang)} к A)"
        decision = (
            f"Вывод по A/B-тесту и модели резервирования: в самом эксперименте напрямую измерены конверсия ({fmt_pp(ab['cvr_diff'], lang)}, p = {fmt_num(ab['cvr_pvalue'], lang, 3)} - ухудшения конверсии в пределах MDE нет) "
            f"и доля отмен ({fmt_pp(cancel_diff, lang)}). Поскольку срок жизни баллов составляет 12 месяцев, ставка затрат на промо {fmt_pct(eff_rate, lang)} от GBV (против {fmt_pct(ab['control_rate'], lang)} деньгами) "
            f"рассчитана по когортной модели резервирования обязательств (accrual model: breakage {brk_pct}%, экономия на повторной рекламе {adv_pct}%), что даёт {fmt_signed_eur(ab['cps_diff'], lang, 3)} ({fmt_signed_pct(cps_rel, lang)}, p < 0,001) ожидаемой маржинальной прибыли на сессию. "
            f"В базе 90 дней ({fmt_eur(ab_base_total, 'ru')}) уже сидит сплит 50/50 ({fmt_eur(ctrl['contribution'], 'ru')} в A + {fmt_eur(treat['contribution'], 'ru')} в B); перевод оставшейся половины трафика A на баллы при консервативном допущении 0,0% по конверсии даёт {fmt_signed_eur(rollout_delta, 'ru')} в Разделе 1."
        )
        sens_html = (
            "<div class='sens-box'>"
            "<h4>Интерактивная проверка чувствительности резерва под баллы (Группа B против Группы A)</h4>"
            "<div class='sens-controls'>"
            f"<div><label>Доля неиспользованных баллов (Breakage): <span id='brk-val-ru'>{brk_pct}%</span></label>"
            f"<input id='brk-ru' type='range' min='0' max='60' step='1' value='{brk_pct}'></div>"
            f"<div><label>Зачёт экономии на повторной рекламе: <span id='adv-val-ru'>{adv_pct}%</span> (0% = строгий резерв)</label>"
            f"<input id='adv-ru' type='range' min='0' max='40' step='5' value='{adv_pct}'></div>"
            f"<div id='sens-res-ru' class='sens-out' {sens_data}>"
            f"Ставка резерва под {fmt_pct(ab['treatment_points_rate'], lang, 0)} баллов: <strong>{fmt_pct(eff_rate, lang, 2)} от GBV</strong><br>"
            f"Маржа Группы B: <strong>{fmt_eur(treat['cps'], lang, 3)}/сессия</strong> ({fmt_signed_eur(ab['cps_diff'], lang, 3)} к A, или <strong>{fmt_signed_eur(arm_gap, lang)}</strong> на ветке B)"
            "</div></div></div>"
        )
        rules_title = "Правила принятия решения по A/B-тесту (выделено сработавшее)"
        rules = [
            ("keep_cash", "Если маржинальная прибыль на сессию в Группе B значимо ниже Группы A - оставляем прямую скидку."),
            ("ship_points", "Если маржинальная прибыль на сессию в Группе B значимо выше (p < 0,05), а потеря конверсии не превышает защитный порог 2,5% (non-inferiority guardrail) - переводим сегмент на баллы."),
            ("extend", "Иначе продлеваем тест до набора мощности."),
        ]
    else:
        badge = "Group B Wins · Roll Out 9% Points"
        setup = (
            f"Segment '{LABELS['en'][ab['fence_id']]}', 50/50 split across all {days} days ({fmt_int(tot_ab_sess, 'en')} sessions, 100% of segment). "
            "Hypothesis: can we replace the −6% instant cash discount (Group A) with 9% loyalty points cashback (Group B, 4.3% accrued cost after breakage) "
            "without conversion loss beyond the guardrail while improving expected unit margin?"
        )
        head = "<tr><th>Measure</th><th>Group A (Control: −6% Cash)</th><th>Group B (Test: 9% Points)</th><th>Difference B − A (abs &amp; % vs A)</th><th>Significance &amp; Interpretation</th></tr>"
        rows = [
            (
                "Sessions & bookings (% of test)",
                f"{fmt_int(ctrl['sessions'], lang)} ({fmt_pct(ctrl_share, lang)}) · {fmt_int(ctrl['bookings'], lang)} bk.",
                f"{fmt_int(treat['sessions'], lang)} ({fmt_pct(treat_share, lang)}) · {fmt_int(treat['bookings'], lang)} bk.",
                f"+{fmt_int(treat['bookings'] - ctrl['bookings'], lang)} bk. ({fmt_signed_pct((treat['bookings'] - ctrl['bookings']) / ctrl['bookings'], lang)})",
                "50/50 traffic split",
            ),
            (
                "Accrued promo cost (% of GBV)",
                fmt_pct(ab["control_rate"], lang),
                fmt_pct(ab["treatment_effective_rate"], lang),
                f"{fmt_pp(ab['treatment_effective_rate'] - ab['control_rate'], lang)} ({fmt_signed_pct(rate_rel, lang)} vs A)",
                "accrual model: 36% breakage & 25% repeat ad saving",
            ),
            (
                "Conversion rate",
                fmt_pct(ctrl["cvr"], lang),
                fmt_pct(treat["cvr"], lang),
                f"{fmt_pp(ab['cvr_diff'], lang)} ({fmt_signed_pct(ab['relative_cvr'], lang)} vs A)",
                f"p = {fmt_num(ab['cvr_pvalue'], lang, 3)} · not significant (inside MDE {_pp_mag(ab['cvr_mde'], lang)})",
            ),
            (
                "Contribution margin / session",
                fmt_eur(ctrl["cps"], lang, 3),
                fmt_eur(treat["cps"], lang, 3),
                f"{fmt_signed_eur(ab['cps_diff'], lang, 3)} ({fmt_signed_pct(cps_rel, lang)} vs A)",
                f"p < 0.001 · significant · 95% CI {ci}",
            ),
            (
                "Total arm contribution margin, EUR",
                fmt_eur(ctrl["contribution"], lang),
                fmt_eur(treat["contribution"], lang),
                f"{fmt_signed_eur(treat['contribution'] - ctrl['contribution'], lang)} ({fmt_signed_pct((treat['contribution'] - ctrl['contribution']) / ctrl['contribution'], lang)} vs A)",
                "90-day arm total",
            ),
            (
                "Cancellation Rate",
                fmt_pct(ctrl["cancel_rate"], lang),
                fmt_pct(treat["cancel_rate"], lang),
                f"{fmt_pp(cancel_diff, lang)} ({fmt_signed_pct(cancel_rel, lang)} vs A)",
                "booking quality unchanged",
            ),
        ]
        left_lbl = f"Observed conversion gap (B vs A): {_pp_mag(ab['cvr_diff'], lang)} ({fmt_signed_pct(ab['relative_cvr'], lang)} vs control A)"
        right_lbl = f"Orange mark - Minimum Detectable Effect (MDE at 80% power): {_pp_mag(ab['cvr_mde'], lang)} ({fmt_pct(ab['cvr_mde'] / ctrl['cvr'], lang)} vs A)"
        decision = (
            f"A/B test & accrual model readout: the experiment directly measured conversion ({fmt_pp(ab['cvr_diff'], lang)}, p = {fmt_num(ab['cvr_pvalue'], lang, 3)} - no conversion degradation within the MDE guardrail) "
            f"and cancellations ({fmt_pp(cancel_diff, lang)}). Because loyalty points carry a 12-month expiry, the {fmt_pct(eff_rate, lang)} of GBV promo cost (vs {fmt_pct(ab['control_rate'], lang)} cash) "
            f"is an accrual-model estimate ({brk_pct}% breakage, {adv_pct}% repeat ad saving), yielding {fmt_signed_eur(ab['cps_diff'], lang, 3)} ({fmt_signed_pct(cps_rel, lang)}, p < 0.001) in expected contribution margin per session. "
            f"Because the 90-day baseline ({fmt_eur(ab_base_total, 'en')}) already reflects the 50/50 split ({fmt_eur(ctrl['contribution'], 'en')} in A + {fmt_eur(treat['contribution'], 'en')} in B), rolling Group B out to the remaining 50% of traffic under a conservative 0.0% conversion change adds {fmt_signed_eur(rollout_delta, 'en')} in Section 1."
        )
        sens_html = (
            "<div class='sens-box'>"
            "<h4>Interactive Sensitivity Check: Points Accrual Assumptions (Group B vs. Group A)</h4>"
            "<div class='sens-controls'>"
            f"<div><label>Unredeemed points (Breakage): <span id='brk-val-en'>{brk_pct}%</span></label>"
            f"<input id='brk-en' type='range' min='0' max='60' step='1' value='{brk_pct}'></div>"
            f"<div><label>Repeat ad-spend credit: <span id='adv-val-en'>{adv_pct}%</span> (0% = strict liability)</label>"
            f"<input id='adv-en' type='range' min='0' max='40' step='5' value='{adv_pct}'></div>"
            f"<div id='sens-res-en' class='sens-out' {sens_data}>"
            f"Accrued cost of {fmt_pct(ab['treatment_points_rate'], lang, 0)} points: <strong>{fmt_pct(eff_rate, lang, 2)} of GBV</strong><br>"
            f"Group B margin: <strong>{fmt_eur(treat['cps'], lang, 3)}/session</strong> ({fmt_signed_eur(ab['cps_diff'], lang, 3)} vs A, or <strong>{fmt_signed_eur(arm_gap, lang)}</strong> on Arm B)"
            "</div></div></div>"
        )
        rules_title = "A/B decision rules (active rule highlighted)"
        rules = [
            ("keep_cash", "If Group B contribution margin per session is significantly below Group A - keep the instant cash discount."),
            ("ship_points", "If Group B contribution margin per session is significantly higher (p < 0.05) and conversion stays within the 2.5% non-inferiority guardrail - ship loyalty points."),
            ("extend", "Otherwise extend the experiment."),
        ]

    tbody = "".join(
        "<tr>"
        + f"<td>{escape(name)}</td>"
        + "".join(f"<td class='reason'>{escape(c)}</td>" if i == 3 else f"<td>{escape(c)}</td>" for i, c in enumerate(cells))
        + "</tr>"
        for name, *cells in rows
    )
    observed = abs(ab["cvr_diff"])
    mde = ab["cvr_mde"]
    ceiling = max(observed, mde if not math.isnan(mde) else 0.0, 1e-6) * 1.18
    obs_w = observed / ceiling * 100.0
    mde_x = mde / ceiling * 100.0
    rule_items = "".join(
        f"<li class='rule-on'>{escape(txt)}</li>" if key == ab["status"] else f"<li>{escape(txt)}</li>"
        for key, txt in rules
    )
    return (
        f"<p><span class='status'>{escape(badge)}</span></p>"
        f"<p class='insight'>{escape(setup)}</p>"
        f"<div class='table-wrap'><table><thead>{head}</thead><tbody>{tbody}</tbody></table></div>"
        f"<div class='scale-head'><span>{escape(left_lbl)}</span><span>{escape(right_lbl)}</span></div>"
        f"<div class='ruler'><i class='obs' style='width:{obs_w:.1f}%'></i><i class='mde' style='left:{mde_x:.1f}%'></i></div>"
        f"{sens_html}"
        f"<div class='callout'><p>{escape(decision)}</p></div>"
        f"<details><summary>{escape(rules_title)}</summary><ol>{rule_items}</ol></details>"
    )


def _weekly_insight(lang: str, ctx: dict) -> str:
    weekly = ctx["weekly"]
    full_weeks = weekly[:-1] if len(weekly) > 2 else weekly
    cvrs = [w["cvr"] for w in full_weeks]
    pshares = [w["promo_share"] for w in weekly]
    low = min(full_weeks, key=lambda w: w["cvr"])
    high = max(full_weeks, key=lambda w: w["cvr"])
    last_w = weekly[-1]
    if lang == "ru":
        return (
            f"Наблюдение по 12 полным неделям (плюс 6 дней недели с {_week_tick(last_w['week'], lang)}, конверсия {fmt_pct(last_w['cvr'], lang)}): "
            f"конверсия полных недель шла от {fmt_pct(min(cvrs), lang)} (неделя с {_week_tick(low['week'], lang)}) "
            f"до {fmt_pct(max(cvrs), lang)} (неделя с {_week_tick(high['week'], lang)}) вслед за сезонным трендом, при этом доля затрат на промо в валовой выручке оставалась стабильной "
            f"({fmt_pct(min(pshares), lang)}–{fmt_pct(max(pshares), lang)}). При неизменной промо-механике почти 38% валовой выручки еженедельно уходило в скидки с высокой долей каннибализации."
        )
    return (
        f"Observation across the 12 full weeks (plus the 6-day partial week of {_week_tick(last_w['week'], lang)} at {fmt_pct(last_w['cvr'], lang)} conversion): "
        f"full-week conversion moved from {fmt_pct(min(cvrs), lang)} (week of {_week_tick(low['week'], lang)}) "
        f"to {fmt_pct(max(cvrs), lang)} (week of {_week_tick(high['week'], lang)}) with seasonality, while promo spend remained steady at "
        f"{fmt_pct(min(pshares), lang)}–{fmt_pct(max(pshares), lang)} of Gross Revenue. Under a static discount policy, ~38% of Gross Revenue was consumed each week with high cannibalization."
    )


def _weekly_table(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    if lang == "ru":
        head = "<tr><th>Неделя с</th><th>Сессии (% периода)</th><th>Брони (% периода)</th><th>Конверсия</th><th>Промо / Валовая выручка</th><th>Маржинальная прибыль (% периода)</th></tr>"
    else:
        head = "<tr><th>Week of</th><th>Sessions (% period)</th><th>Bookings (% period)</th><th>Conversion</th><th>Promo / Gross Revenue</th><th>Contribution Margin (% period)</th></tr>"
    rows = []
    for idx, w in enumerate(ctx["weekly"]):
        s_sh = w["sessions"] / total["sessions"]
        b_sh = w["bookings"] / total["bookings"]
        c_sh = w["contribution"] / total["contribution"]
        w_label = _week_tick(w["week"], lang)
        if idx == len(ctx["weekly"]) - 1:
            w_label += " (6 дн.)" if lang == "ru" else " (6d)"
        rows.append(
            "<tr>"
            f"<td>{escape(w_label)}</td>"
            f"<td>{escape(fmt_int(w['sessions'], lang))}<span class='sub-pct'>{escape(fmt_pct(s_sh, lang))}</span></td>"
            f"<td>{escape(fmt_int(w['bookings'], lang))}<span class='sub-pct'>{escape(fmt_pct(b_sh, lang))}</span></td>"
            f"<td>{escape(fmt_pct(w['cvr'], lang))}</td>"
            f"<td>{escape(fmt_pct(w['promo_share'], lang))}</td>"
            f"<td>{escape(fmt_eur(w['contribution'], lang))}<span class='sub-pct'>{escape(fmt_pct(c_sh, lang))}</span></td>"
            "</tr>"
        )
    return f"<table><thead>{head}</thead><tbody>{''.join(rows)}</tbody></table>"


def _lines(lang: str, ctx: dict) -> str:
    weekly = ctx["weekly"]
    cvr_title = _t(lang, "Conversion by week", "Конверсия по неделям")
    promo_title = _t(
        lang,
        "Promo & loyalty spend as % of Gross Revenue",
        "Затраты на промо и лояльность как % от валовой выручки",
    )
    cvr_svg = _series_chart(weekly, [w["cvr"] for w in weekly], "#005bff", lambda v: fmt_pct(v, lang), lang)
    promo_svg = _series_chart(weekly, [w["promo_share"] for w in weekly], "#ff5a26", lambda v: fmt_pct(v, lang), lang)
    return f"<h3>{escape(cvr_title)}</h3>{cvr_svg}<h3>{escape(promo_title)}</h3>{promo_svg}"


def _series_chart(weekly: list[dict], values: list[float], color: str, label_of, lang: str = "ru") -> str:
    width, height = 1080, 236
    left, right, top, bottom = 52, 28, 28, 34
    plot_w = width - left - right
    plot_h = height - top - bottom
    lo, hi = min(values), max(values)
    pad = (hi - lo) * 0.22 or 0.005
    lo -= pad
    hi += pad
    span = hi - lo or 1.0

    def px(i: int) -> float:
        return left + plot_w * i / (len(values) - 1)

    def py(val: float) -> float:
        return top + plot_h * (1.0 - (val - lo) / span)

    pts = " ".join(f"{px(i):.1f},{py(values[i]):.1f}" for i in range(len(values)))
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" role="img">',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height - bottom}" stroke="#d8e0ef"></line>',
    ]
    for tick in (lo + pad, (lo + hi) / 2.0, hi - pad):
        y = py(tick)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="#edf1f8"></line>')
    parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{pts}"></polyline>')
    for i, val in enumerate(values):
        x, y = px(i), py(val)
        anchor = "start" if i == 0 else "end" if i == len(values) - 1 else "middle"
        lx = x + 6 if i == 0 else x - 6 if i == len(values) - 1 else x
        ly = y - 12 if y >= top + 16 else y + 16
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"></circle>')
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="10" text-anchor="{anchor}">{escape(label_of(val))}</text>')
        parts.append(
            f'<text x="{x:.1f}" y="{height - 10}" font-size="10" text-anchor="middle">{escape(_week_tick(weekly[i]["week"], lang))}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def _ask_cards(lang: str, ctx: dict) -> str:
    total = ctx["total"]
    ab = ctx["ab_test"]
    lead = ctx["lead_info"]
    basket = ctx["basket_info"]
    pkg = ctx["package"]
    blanket = next(f for f in ctx["fences"] if f["fence_id"] == "blanket_promo")
    cps_rel = ab["cps_diff"] / ab["control"]["cps"]
    b_waste_pct = blanket["cannibalized_cost_now"] / blanket["promo_cost_now"]
    basket_ratio = basket["large_cps"] / basket["small_cps"] if basket["small_cps"] else 0.0
    rel_cm = pkg["delta_contribution"] / total["contribution"]
    rel_promo = pkg["delta_promo_cost"] / total["promo_cost"]
    if lang == "ru":
        items = [
            (
                "Продукт",
                "Переключить клубный тариф на вебе со скидки −6% деньгами на бейдж «9% баллами» и развести скидку в приложении по глубине заезда (−3% на 0–3 дня, −6% на 8+ дней).",
                f"Основание: в A/B-тесте 9% баллами дали {fmt_signed_eur(ab['cps_diff'], 'ru', 3)} ожидаемой маржинальной прибыли на сессию ({fmt_signed_pct(cps_rel, 'ru')} к контролю, p < 0,001); в приложении на окне 0–3 дня доля каннибализации промо {fmt_pct(lead['short_cannibalized'], 'ru', 0)} против {fmt_pct(lead['long_cannibalized'], 'ru', 0)} на длинном окне 8+ дней.",
            ),
            (
                "CRM и маркетинг",
                "Отключить публичный промокод −8% в баннерах и поставить в триггер брошенной корзины порог чека от 180 € с начислением 7,5% баллами.",
                f"Основание: у массового купона {fmt_pct(blanket['cannibalization_share'], 'ru', 0)} каннибализации промо ({fmt_eur(blanket['cannibalized_cost_now'], 'ru')}, или {fmt_pct(b_waste_pct, 'ru')} промо-бюджета сегмента), а чеки до 180 € ({fmt_pct(basket['small_share'], 'ru', 0)} трафика корзины) дают лишь {fmt_eur(basket['small_cps'], 'ru', 2)} маржи на сессию против {fmt_eur(basket['large_cps'], 'ru', 2)} (в {fmt_num(basket_ratio, 'ru', 1)} раза выше) на чеках от 180 €.",
            ),
            (
                "Коммерция и отели",
                "Сохранять 0% скидки на открытой витрине (34,0% трафика и 46,3% маржинальной прибыли сервиса) и выгрузить поотельную тарифную сетку закрытых правил (output/fence_rules_shelf.csv).",
                "Основание: соблюдение коммерческого паритета на открытой витрине и защита ранжирования в метапоиске (120 из 120 правил в сетке) при сохранении конкурентной цены внутри приложения и клуба.",
            ),
            (
                "Финансы",
                "Отразить в бюджете месяца эффект пакета на базе сессий последних 90 дней и ставку резервирования баллов 4,3% от GBV (при номинале 9% и когортном breakage 36%).",
                f"Основание: {fmt_signed_eur(pkg['delta_contribution'], 'ru')} маржинальной прибыли ({fmt_signed_pct(rel_cm, 'ru')} к базе), {fmt_signed_eur(pkg['delta_promo_cost'], 'ru')} затрат на промо ({fmt_signed_pct(rel_promo, 'ru')} к промо-бюджету), {fmt_pp(pkg['delta_conversion'], 'ru')} конверсии.",
            ),
        ]
    else:
        items = [
            (
                "Product",
                "Switch logged-in web from −6% instant cash to the '9% loyalty points' badge and tier the mobile-app discount by lead time (−3% on 0–3d, −6% on 8+d).",
                f"Evidence: Group B delivered {fmt_signed_eur(ab['cps_diff'], 'en', 3)} expected contribution margin/session ({fmt_signed_pct(cps_rel, 'en')} vs control, p < 0.001); app promo cannibalization is {fmt_pct(lead['short_cannibalized'], 'en', 0)} on 0–3d vs {fmt_pct(lead['long_cannibalized'], 'en', 0)} on 8+d.",
            ),
            (
                "CRM & Marketing",
                "Retire the −8% public banner coupon and enforce a €180 minimum basket on abandoned-cart triggers with 7.5% loyalty points.",
                f"Evidence: the banner coupon suffers {fmt_pct(blanket['cannibalization_share'], 'en', 0)} promo cannibalization ({fmt_eur(blanket['cannibalized_cost_now'], 'en')}, or {fmt_pct(b_waste_pct, 'en')} of segment promo spend), and carts below €180 ({fmt_pct(basket['small_share'], 'en', 0)} of cart traffic) yield {fmt_eur(basket['small_cps'], 'en', 2)} margin/session vs {fmt_eur(basket['large_cps'], 'en', 2)} ({fmt_num(basket_ratio, 'en', 1)}x) above €180.",
            ),
            (
                "Commercial & Supply",
                "Maintain 0% discount on the public storefront (34.0% of traffic and 46.3% of total margin) and publish the hotel-level CUG rate card (output/fence_rules_shelf.csv).",
                "Evidence: commercial rate-parity alignment with hotel partners and metasearch ranking protection (120 of 120 shelf rules) while keeping closed-group rates competitive.",
            ),
            (
                "Finance",
                "Book the weekly package on the observed 90-day session base and accrue 9% nominal points at 4.3% of GBV (36% breakage, 25% repeat-ad saving).",
                f"Evidence: {fmt_signed_eur(pkg['delta_contribution'], 'en')} contribution margin ({fmt_signed_pct(rel_cm, 'en')} vs base), {fmt_signed_eur(pkg['delta_promo_cost'], 'en')} promo spend ({fmt_signed_pct(rel_promo, 'en')} vs promo budget), {fmt_pp(pkg['delta_conversion'], 'en')} conversion.",
            ),
        ]
    return "".join(
        f"<article class='ask'><h3>{escape(owner)}</h3><p><strong>{escape(action)}</strong></p><p>{escape(evidence)}</p></article>"
        for owner, action, evidence in items
    )
