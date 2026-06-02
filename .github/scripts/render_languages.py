#!/usr/bin/env python3
"""Render a "most used languages" bar from a user's public repositories.

Uses the GitHub REST API with the built-in Actions GITHUB_TOKEN (which has
read access to public data), so no Personal Access Token is required. Counts
bytes per language across every public, non-fork repo - skipping the profile
repo itself, which is HTML and takes an automated commit every week - and
writes two palette-matched SVGs (light + dark) that the README embeds.
"""

import json
import math
import os
import sys
import urllib.error
import urllib.request

USER = "AstorisTheBrave"
SKIP_REPOS = {"astoristhebrave"}          # the profile repo (lower-cased)
TOP_N = 8                                 # languages shown individually
OUT_LIGHT = "assets/languages.svg"
OUT_DARK = "assets/languages-dark.svg"

# GitHub's official language colors (subset covering this account + common ones).
LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "Go": "#00ADD8", "C": "#555555", "C++": "#f34b7d", "C#": "#178600",
    "Lua": "#000080", "HTML": "#e34c26", "CSS": "#563d7c", "SCSS": "#c6538c",
    "MDX": "#fcb32c", "Shell": "#89e051", "Ruby": "#701516", "Rust": "#dea584",
    "Java": "#b07219", "Kotlin": "#A97BFF", "PHP": "#4F5D95", "Swift": "#F05138",
    "Dockerfile": "#384d54", "Makefile": "#427819", "Vue": "#41b883",
    "Jupyter Notebook": "#DA5B0B", "Svelte": "#ff3e00", "Astro": "#ff5a03",
}
OTHER_COLOR = "#928d84"
FALLBACK = "#c24e2c"

THEMES = {
    OUT_LIGHT: {"bg": "#f4f0e8", "title": "#c24e2c", "text": "#1a1a1a",
                "sub": "#5e5a54", "track": "#e6e0d3"},
    OUT_DARK: {"bg": "#07070a", "title": "#e27a52", "text": "#ece7dc",
               "sub": "#a8a49b", "track": "#1f1d1a"},
}


def api(path):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Authorization": f"Bearer {token}" if token else "",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": f"{USER}-profile-languages",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def collect():
    """Aggregate bytes per language across public, non-fork repos."""
    totals = {}
    page = 1
    while True:
        repos = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        if not repos:
            break
        for repo in repos:
            if repo.get("fork") or repo.get("private"):
                continue
            if repo["name"].lower() in SKIP_REPOS:
                continue
            try:
                langs = api(f"/repos/{repo['full_name']}/languages")
            except urllib.error.HTTPError:
                continue
            for lang, size in langs.items():
                totals[lang] = totals.get(lang, 0) + int(size)
        if len(repos) < 100:
            break
        page += 1
    return totals


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(entries, theme):
    """entries: list of (name, pct, color). Returns an SVG string."""
    W, pad = 480, 20
    inner = W - 2 * pad
    bar_y, bar_h = 38, 10
    legend_y = bar_y + bar_h + 24
    row_h = 18
    rows = max(1, math.ceil(len(entries) / 2))
    H = legend_y + rows * row_h + 6

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="most used languages">',
        f'<rect width="{W}" height="{H}" rx="6" fill="{theme["bg"]}"/>',
        f'<text x="{pad}" y="24" font-family="ui-monospace,SFMono-Regular,'
        f'Consolas,monospace" font-size="13" fill="{theme["title"]}" '
        f'font-weight="600">Most used languages</text>',
        f'<rect x="{pad}" y="{bar_y}" width="{inner}" height="{bar_h}" rx="5" '
        f'fill="{theme["track"]}"/>',
        f'<clipPath id="bar"><rect x="{pad}" y="{bar_y}" width="{inner}" '
        f'height="{bar_h}" rx="5"/></clipPath>',
        f'<g clip-path="url(#bar)">',
    ]

    x = pad
    for _, pct, color in entries:
        seg = inner * pct / 100.0
        out.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{seg:.2f}" '
                   f'height="{bar_h}" fill="{color}"/>')
        x += seg
    out.append("</g>")

    font = ('font-family="ui-monospace,SFMono-Regular,Consolas,monospace" '
            'font-size="12"')
    for i, (name, pct, color) in enumerate(entries):
        col, row = i % 2, i // 2
        cx = pad + col * (inner / 2)
        cy = legend_y + row * row_h
        out.append(f'<circle cx="{cx + 4:.1f}" cy="{cy - 4:.1f}" r="4" '
                   f'fill="{color}"/>')
        out.append(f'<text x="{cx + 14:.1f}" y="{cy:.1f}" {font} '
                   f'fill="{theme["text"]}">{esc(name)} '
                   f'<tspan fill="{theme["sub"]}">{pct:.1f}%</tspan></text>')

    out.append("</svg>")
    return "\n".join(out)


def main():
    totals = collect()
    grand = sum(totals.values())
    if grand == 0:
        print("no public language bytes found", file=sys.stderr)
        return 1

    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    entries = []
    for name, size in ranked[:TOP_N]:
        entries.append((name, 100.0 * size / grand,
                        LANG_COLORS.get(name, FALLBACK)))
    rest = sum(s for _, s in ranked[TOP_N:])
    if rest > 0:
        entries.append(("Other", 100.0 * rest / grand, OTHER_COLOR))

    for path, theme in THEMES.items():
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build_svg(entries, theme))
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
