"""Render the deterministic quote of the day for the profile output branch."""

from __future__ import annotations

import argparse
import html
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tools.profile_assets import DARK_THEME, LIGHT_THEME, Theme


@dataclass(frozen=True, slots=True)
class Quote:
    text: str
    author: str


QUOTES = (
    Quote("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    Quote("The purpose of computing is insight, not numbers.", "Richard Hamming"),
    Quote(
        "The competent programmer is fully aware of the limited size of his own skull.",
        "Edsger W. Dijkstra",
    ),
    Quote("Premature optimization is the root of all evil.", "Donald Knuth"),
    Quote(
        "Walking on water and developing software from a specification are easy "
        "if both are frozen.",
        "Edward V. Berard",
    ),
    Quote(
        "It is practically impossible to teach good programming to students that "
        "have had a prior exposure to BASIC.",
        "Edsger W. Dijkstra",
    ),
    Quote(
        "Controlling complexity is the essence of computer programming.",
        "Brian Kernighan",
    ),
    Quote("Make it work, make it right, make it fast.", "Kent Beck"),
    Quote(
        "Programs must be written for people to read, and only incidentally for "
        "machines to execute.",
        "Harold Abelson",
    ),
    Quote(
        "Any fool can write code that a computer can understand. Good programmers "
        "write code that humans can understand.",
        "Martin Fowler",
    ),
    Quote(
        "A ship in port is safe, but that's not what ships are built for.",
        "Grace Hopper",
    ),
    Quote("The database is not the enemy. Ignoring it is.", "Astoris"),
)


def quote_for_date(day: date) -> Quote:
    """Select a stable quote by calendar day, including leap years."""

    return QUOTES[(day.timetuple().tm_yday - 1) % len(QUOTES)]


def render_quote_svg(quote: Quote, theme: Theme) -> str:
    """Render an accessible quote card in the profile's notebook style."""

    lines = textwrap.wrap(quote.text, width=70) or [quote.text]
    quote_lines = []
    for index, line in enumerate(lines[:3]):
        quote_lines.append(
            f'<text x="36" y="{88 + index * 30}" class="quote" '
            f'fill="{theme.foreground}">{html.escape(line, quote=True)}</text>'
        )
    author_y = 108 + len(quote_lines) * 30
    description = html.escape(f"{quote.text} - {quote.author}", quote=True)
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="220" '
            'viewBox="0 0 760 220" role="img" '
            'aria-labelledby="quote-title quote-description">',
            '<title id="quote-title">Quote of the day</title>',
            f'<desc id="quote-description">{description}</desc>',
            "<style>",
            ".mono{font-family:ui-monospace,Cascadia Code,Fira Mono,monospace}",
            ".quote{font-family:Georgia,serif;font-size:22px;font-style:italic}",
            ".meta{font-size:11px;letter-spacing:.14em;text-transform:uppercase}",
            "</style>",
            f'<rect width="760" height="220" rx="10" fill="{theme.background}"/>',
            '<rect x="24" y="24" width="4" height="172" rx="2" '
            f'fill="{theme.accent}"/>',
            f'<text x="36" y="48" class="mono meta" fill="{theme.accent}" '
            'font-weight="700">daily note / rotate at 00:00 UK</text>',
            *quote_lines,
            f'<text x="36" y="{author_y}" class="mono" font-size="13" '
            f'fill="{theme.muted}">- {html.escape(quote.author, quote=True)}</text>',
            "</svg>",
            "",
        ]
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--date", type=date.fromisoformat)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    day = args.date or datetime.now(ZoneInfo("Europe/London")).date()
    quote = quote_for_date(day)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, theme in (
        ("quote.svg", LIGHT_THEME),
        ("quote-dark.svg", DARK_THEME),
    ):
        destination = args.output_dir / filename
        destination.write_text(
            render_quote_svg(quote, theme), encoding="utf-8", newline="\n"
        )
        print(f"wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
