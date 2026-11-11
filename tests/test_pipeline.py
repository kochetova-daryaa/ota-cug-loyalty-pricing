from openpyxl import load_workbook

from keystone.pipeline import run_pipeline


def test_keystone_pipeline_builds_all_artifacts(tmp_path):
    summary = run_pipeline(n_sessions=12_000, seed=42, root=tmp_path)
    assert summary["sql_bookings"] == summary["bookings"]
    assert summary["sessions"] == 12_000
    assert summary["delta_contribution"] > 0

    ru_brief = (tmp_path / "reports" / "monday_brief.ru.md").read_text(encoding="utf-8")
    en_brief = (tmp_path / "reports" / "monday_brief.en.md").read_text(encoding="utf-8")
    assert "Еженедельный обзор ценообразования" in ru_brief
    assert "Группа B" in ru_brief
    assert "Group B" in en_brief

    html = (tmp_path / "output" / "pricing_cockpit.html").read_text(encoding="utf-8")
    assert "Отчётный период" in html
    assert "90 дней" in html
    assert "Текущая бизнес-проблема" in html
    assert "Предлагаемое решение на утверждение" in html
    assert "1. Матрица решений по 5 сегментам доступа (CUG) и промо (Было → Стало)" in html
    assert "Маржинальная прибыль" in html
    assert "sub-pct" in html
    assert "3. Классический A/B-тест (50/50)" in html
    assert "5. Рекомендации смежным подразделениям на ближайшую неделю" in html

    wb = load_workbook(tmp_path / "output" / "keystone_pricing_cockpit.xlsx")
    assert wb["Promo_Calculator"]["B20"].value.startswith("=")
    assert wb["Promo_Calculator"]["B23"].value.startswith("=")
    assert "AB_Test" in wb.sheetnames
