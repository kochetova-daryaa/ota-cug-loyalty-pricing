"""Locale-aware formatting for Russian and English outputs."""

from __future__ import annotations


def _group(n: float, digits: int, lang: str) -> str:
    if digits == 0:
        text = f"{int(round(n)):,}"
    else:
        text = f"{n:,.{digits}f}"
    if lang == "ru":
        return text.replace(",", " ").replace(".", ",")
    return text


def fmt_int(n: float, lang: str) -> str:
    return _group(abs(n), 0, lang) if n >= 0 else "−" + _group(abs(n), 0, lang)


def fmt_eur(n: float, lang: str, digits: int = 0) -> str:
    body = _group(abs(n), digits, lang)
    sign = "−" if n < 0 else ""
    if lang == "ru":
        return f"{sign}{body} €"
    return f"{sign}€{body}"


def fmt_pct(x: float, lang: str, digits: int = 1) -> str:
    sign = "−" if x < 0 else ""
    return sign + _group(abs(x) * 100, digits, lang) + "%"


def fmt_signed_pct(x: float, lang: str, digits: int = 1) -> str:
    if x > 1e-12:
        return "+" + fmt_pct(x, lang, digits)
    return fmt_pct(x, lang, digits)


def fmt_pp(x: float, lang: str, digits: int = 1) -> str:
    sign = "+" if x > 1e-12 else "−" if x < -1e-12 else ""
    unit = " п.п." if lang == "ru" else " pp"
    return sign + _group(abs(x) * 100, digits, lang) + unit


def fmt_num(x: float, lang: str, digits: int = 2) -> str:
    sign = "−" if x < 0 else ""
    return sign + _group(abs(x), digits, lang)


def fmt_signed_eur(n: float, lang: str, digits: int = 0) -> str:
    if n > 0:
        return "+" + fmt_eur(n, lang, digits)
    return fmt_eur(n, lang, digits)
