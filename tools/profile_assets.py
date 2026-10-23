"""Generate deterministic, accessible profile assets from public GitHub data."""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
DEFAULT_USER = "AstorisTheBrave"
DEFAULT_EXCLUDED = {DEFAULT_USER.casefold()}
TOP_N = 8

LANGUAGE_COLORS = {
    "Astro": "#ff5a03",
    "C": "#555555",
    "C#": "#178600",
    "C++": "#f34b7d",
    "CSS": "#663399",
    "Dockerfile": "#384d54",
    "Go": "#00add8",
    "HTML": "#e34c26",
    "Java": "#b07219",
    "JavaScript": "#f1e05a",
    "Kotlin": "#a97bff",
    "Lua": "#000080",
    "MDX": "#fcb32c",
    "Python": "#3572a5",
    "Rust": "#dea584",
    "SCSS": "#c6538c",
    "Shell": "#89e051",
    "Swift": "#f05138",
    "TypeScript": "#3178c6",
    "Vue": "#41b883",
}
FALLBACK_COLOR = "#c24e2c"
OTHER_COLOR = "#928d84"


@dataclass(frozen=True, slots=True)
class Theme:
    background: str
    foreground: str
    muted: str
    accent: str
    track: str


@dataclass(frozen=True, slots=True)
class LanguageShare:
    name: str
    percent: float
    color: str


LIGHT_THEME = Theme(
    background="#f4f0e8",
    foreground="#1a1a1a",
    muted="#5e5a54",
    accent="#c24e2c",
    track="#e6e0d3",
)
DARK_THEME = Theme(
    background="#07070a",
    foreground="#ece7dc",
    muted="#a8a49b",
    accent="#e27a52",
    track="#1f1d1a",
)


class GitHubClient:
    """Small REST client with explicit timeout and version headers."""

    def __init__(self, token: str = "", timeout: float = 30.0) -> None:
        self.token = token
        self.timeout = timeout

    def get_json(self, path: str) -> object:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "astoris-profile-assets",
            "X-GitHub-Api-Version": API_VERSION,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(f"{API_ROOT}{path}", headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.load(response)


def collect_language_totals(
    client: GitHubClient,
    user: str,
    excluded: set[str],
) -> dict[str, int]:
    """Aggregate language bytes across owned, non-fork repositories."""

    totals: dict[str, int] = {}
    page = 1
    folded_exclusions = {name.casefold() for name in excluded}
    encoded_user = urllib.parse.quote(user, safe="")

    while True:
        path = f"/users/{encoded_user}/repos?per_page=100&type=owner&page={page}"
        payload = client.get_json(path)
        if not isinstance(payload, list):
            raise TypeError("GitHub repositories response must be a list")
        if not payload:
            break

        for item in payload:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            full_name = item.get("full_name")
            if not isinstance(name, str) or not isinstance(full_name, str):
                continue
            if item.get("fork") or item.get("private"):
                continue
            if name.casefold() in folded_exclusions:
                continue

            try:
                languages = client.get_json(
                    f"/repos/{urllib.parse.quote(full_name, safe='/')}/languages"
                )
            except (OSError, TimeoutError, urllib.error.URLError) as error:
                print(
                    json.dumps(
                        {"error": str(error), "level": "warning", "repo": full_name},
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                )
                continue

            if not isinstance(languages, dict):
                continue
            for language, byte_count in languages.items():
                if isinstance(language, str) and isinstance(byte_count, int):
                    totals[language] = totals.get(language, 0) + byte_count

        if len(payload) < 100:
            break
        page += 1

    return totals


def rank_languages(
    totals: Mapping[str, int], top_n: int = TOP_N
) -> list[LanguageShare]:
    """Turn byte totals into stable percentage shares and an Other bucket."""

    grand_total = sum(size for size in totals.values() if size > 0)
    if grand_total <= 0:
        return []

    ranked = sorted(
        ((name, size) for name, size in totals.items() if size > 0),
        key=lambda item: (-item[1], item[0].casefold(), item[0]),
    )
    entries = [
        LanguageShare(
            name=name,
            percent=100.0 * size / grand_total,
            color=LANGUAGE_COLORS.get(name, FALLBACK_COLOR),
        )
        for name, size in ranked[:top_n]
    ]
    remaining = sum(size for _, size in ranked[top_n:])
    if remaining:
        entries.append(
            LanguageShare(
                name="Other",
                percent=100.0 * remaining / grand_total,
                color=OTHER_COLOR,
            )
        )
    return entries


def render_language_svg(entries: Sequence[LanguageShare], theme: Theme) -> str:
    """Render a compact language-share card with an accessible text fallback."""

    width = 760
    padding = 28
    inner_width = width - 2 * padding
    bar_y = 70
    bar_height = 12
    row_height = 24
    rows = max(1, (len(entries) + 1) // 2)
    height = 126 + rows * row_height
    title = "Languages across public repositories"
    description = (
        "Share of detected language bytes across public, owned repositories."
        if entries
        else "No public language data available"
    )
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'role="img" aria-labelledby="title description">',
        f'<title id="title">{title}</title>',
        f'<desc id="description">{description}</desc>',
        "<style>",
        ".mono{font-family:ui-monospace,Cascadia Code,Fira Mono,monospace}",
        ".label{font-size:13px}",
        ".meta{font-size:11px;letter-spacing:.14em;text-transform:uppercase}",
        "</style>",
        f'<rect width="{width}" height="{height}" rx="10" fill="{theme.background}"/>',
        f'<text id="title" x="{padding}" y="34" class="mono meta" '
        f'fill="{theme.accent}" font-weight="700">signal / languages</text>',
        f'<text x="{padding}" y="54" class="mono label" fill="{theme.muted}">'
        "public, owned repositories · bytes, not proficiency</text>",
    ]

    if not entries:
        lines.extend(
            [
                f'<rect x="{padding}" y="{bar_y}" width="{inner_width}" '
                f'height="{bar_height}" rx="6" fill="{theme.track}"/>',
                f'<text x="{padding}" y="112" class="mono label" '
                f'fill="{theme.foreground}">No public language data available</text>',
            ]
        )
    else:
        lines.extend(
            [
                f'<rect x="{padding}" y="{bar_y}" width="{inner_width}" '
                f'height="{bar_height}" rx="6" fill="{theme.track}"/>',
                f'<clipPath id="bar"><rect x="{padding}" y="{bar_y}" '
                f'width="{inner_width}" height="{bar_height}" rx="6"/></clipPath>',
                '<g clip-path="url(#bar)">',
            ]
        )
        x = float(padding)
        for entry in entries:
            segment_width = inner_width * entry.percent / 100.0
            lines.append(
                f'<rect x="{x:.2f}" y="{bar_y}" width="{segment_width:.2f}" '
                f'height="{bar_height}" fill="{entry.color}"/>'
            )
            x += segment_width
        lines.append("</g>")

        for index, entry in enumerate(entries):
            column = index % 2
            row = index // 2
            x = padding + column * (inner_width / 2)
            y = 112 + row * row_height
            label = html.escape(entry.name, quote=True)
            lines.append(
                f'<circle cx="{x + 5:.1f}" cy="{y - 4:.1f}" r="5" '
                f'fill="{entry.color}"/>'
            )
            lines.append(
                f'<text x="{x + 18:.1f}" y="{y:.1f}" class="mono label" '
                f'fill="{theme.foreground}">{label} '
                f'<tspan fill="{theme.muted}">{entry.percent:.1f}%</tspan></text>'
            )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--user", default=DEFAULT_USER)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    client: GitHubClient | None = None,
) -> int:
    args = _parser().parse_args(argv)
    active_client = client or GitHubClient(
        token=os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    )
    totals = collect_language_totals(active_client, args.user, {args.user.casefold()})
    entries = rank_languages(totals)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "languages.svg": render_language_svg(entries, LIGHT_THEME),
        "languages-dark.svg": render_language_svg(entries, DARK_THEME),
    }
    for filename, content in outputs.items():
        destination = args.output_dir / filename
        destination.write_text(content, encoding="utf-8", newline="\n")
        print(f"wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
