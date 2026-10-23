from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

from tools.daily_quote import QUOTES, Quote, main, quote_for_date, render_quote_svg
from tools.profile_assets import LIGHT_THEME


def test_quote_changes_each_day_and_cycles_deterministically() -> None:
    first = quote_for_date(date(2026, 1, 1))
    second = quote_for_date(date(2026, 1, 2))

    assert first == QUOTES[0]
    assert second == QUOTES[1]
    assert first != second
    assert quote_for_date(date(2026, 1, 1)) == first
    year = [
        quote_for_date(date(2026, 1, 1) + timedelta(days=offset))
        for offset in range(365)
    ]
    adjacent = zip(year, year[1:], strict=False)
    assert all(current != following for current, following in adjacent)


def test_quote_svg_is_accessible_and_escapes_text() -> None:
    quote = Quote('Build < observe & learn "daily"', "A > B")
    svg = render_quote_svg(quote, LIGHT_THEME)
    root = ET.fromstring(svg)

    assert root.attrib["role"] == "img"
    assert "Build &lt; observe &amp; learn &quot;daily&quot;" in svg
    assert "A &gt; B" in svg
    child_names = {element.tag.rsplit("}", 1)[-1] for element in root}
    assert {"title", "desc"} <= child_names


def test_cli_writes_light_and_dark_quote_cards(tmp_path: Path) -> None:
    exit_code = main(["--output-dir", str(tmp_path), "--date", "2026-10-23"])

    assert exit_code == 0
    for name in ("quote.svg", "quote-dark.svg"):
        output = tmp_path / name
        assert output.exists()
        ET.parse(output)
