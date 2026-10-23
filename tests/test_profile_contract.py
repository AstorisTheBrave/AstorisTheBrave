from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
README = ROOT / "README.md"
MAINTAINING = ROOT / "MAINTAINING.md"
ROLE_LINE = "Backend engineer growing into Site Reliability Engineering."
SUPPORTING_LINE = (
    "I build observable services, automate the repetitive parts, "
    "and learn by operating real systems."
)


def read_readme() -> str:
    return README.read_text(encoding="utf-8")


def local_image_paths(markdown: str) -> set[Path]:
    paths = re.findall(r'(?:src|srcset)="(\.?/[^"\s]+)', markdown)
    return {ROOT / path.removeprefix("./") for path in paths}


def test_now_markers_are_unique_and_ordered() -> None:
    markdown = read_readme()
    start = "<!-- NOW:START -->"
    end = "<!-- NOW:END -->"

    assert markdown.count(start) == 1
    assert markdown.count(end) == 1
    assert markdown.index(start) < markdown.index(end)


def test_local_readme_images_exist() -> None:
    missing = [path for path in local_image_paths(read_readme()) if not path.exists()]

    assert missing == []


def test_all_readme_images_have_alt_text() -> None:
    images = re.findall(r"<img\b[^>]*>", read_readme(), flags=re.IGNORECASE)

    assert images
    assert all(re.search(r'alt="[^"\s][^"]*"', image) for image in images)


def test_private_aegis_is_not_linked() -> None:
    assert "github.com/AstorisTheBrave/aegis" not in read_readme()


def test_timezone_copy_is_dst_safe() -> None:
    markdown = read_readme()

    assert not re.search(r"UTC\s*\+\s*5", markdown, flags=re.IGNORECASE)
    assert "UK time" in markdown


def test_generated_metrics_and_languages_are_embedded_from_output() -> None:
    markdown = read_readme()
    output_root = (
        "https://raw.githubusercontent.com/"
        "AstorisTheBrave/AstorisTheBrave/output/"
    )

    assert "./assets/metrics" not in markdown
    assert "./assets/languages" not in markdown
    assert f"{output_root}metrics.svg" in markdown
    assert f"{output_root}metrics-dark.svg" in markdown
    assert f"{output_root}languages.svg" in markdown
    assert f"{output_root}languages-dark.svg" in markdown
    assert f"{output_root}quote.svg" in markdown
    assert f"{output_root}quote-dark.svg" in markdown


def test_positioning_and_sections_are_sre_first() -> None:
    markdown = read_readme()
    headings = [
        "01 · CURRENT SIGNAL",
        "02 · RELIABILITY IN PRACTICE",
        "03 · OPERATIONAL TOOLKIT",
        "04 · LEARNING NEXT",
        "05 · OPEN SOURCE SIGNAL",
        "06 · QUOTE OF THE DAY",
        "07 · CONTACT",
    ]

    assert ROLE_LINE in markdown
    assert SUPPORTING_LINE in markdown
    positions = [markdown.index(heading) for heading in headings]
    assert positions == sorted(positions)
    for stage in ("observe", "define", "automate", "learn"):
        assert stage in markdown.casefold()


def test_ursa_is_the_only_completed_case_study() -> None:
    markdown = read_readme()
    start = markdown.index("02 · RELIABILITY IN PRACTICE")
    end = markdown.index("03 · OPERATIONAL TOOLKIT")
    completed = markdown[start:end].casefold()

    assert "https://github.com/greyfoundry/ursa-android" in completed
    assert "ursa" in completed
    for unfinished in ("argus", "rostra", "elah", "aegis"):
        assert unfinished not in completed


def test_in_progress_work_is_labeled_inside_now() -> None:
    markdown = read_readme()
    start = markdown.index("<!-- NOW:START -->")
    end = markdown.index("<!-- NOW:END -->")
    now = markdown[start:end].casefold()

    assert "building" in now or "working on" in now
    assert "argus" in now
    assert "rostra" in now


def test_learning_is_separate_from_tools_in_practice() -> None:
    markdown = read_readme()
    toolkit_start = markdown.index("03 · OPERATIONAL TOOLKIT")
    learning_start = markdown.index("04 · LEARNING NEXT")
    signal_start = markdown.index("05 · OPEN SOURCE SIGNAL")
    learning = markdown[learning_start:signal_start]
    normalized_learning = learning.casefold()

    assert toolkit_start < learning_start
    for topic in ("SLIs", "SLOs", "error budgets", "infrastructure as code"):
        assert topic.casefold() in normalized_learning


def test_vanity_and_tracking_features_are_removed() -> None:
    markdown = read_readme()

    for stale in ("komarev.com", "QUOTE:START", "STATS, LIVE"):
        assert stale not in markdown
    assert markdown.count("<details>") <= 2


def test_identity_assets_have_light_dark_and_reduced_motion_variants() -> None:
    markdown = read_readme()
    for stem in ("banner", "whoami"):
        light = ROOT / "assets" / f"{stem}.svg"
        dark = ROOT / "assets" / f"{stem}-dark.svg"
        assert light.exists()
        assert dark.exists()
        assert f'./assets/{stem}.svg' in markdown
        assert f'./assets/{stem}-dark.svg' in markdown
        assert "prefers-reduced-motion" in light.read_text(encoding="utf-8")
        assert "prefers-reduced-motion" in dark.read_text(encoding="utf-8")


def test_maintenance_runbook_covers_the_profile_lifecycle() -> None:
    runbook = MAINTAINING.read_text(encoding="utf-8")

    for required in (
        "<!-- NOW:START -->",
        "Python 3.15.1",
        "uv 0.13.5",
        "uv sync --locked --dev",
        "uv run ruff check .",
        "uv run pytest -q",
        "profile-assets.yml",
        "daily-quote.yml",
        "METRICS_TOKEN",
        "output",
        "rollback",
    ):
        assert required.casefold() in runbook.casefold()
    assert not (ROOT / "SETUP.md").exists()


def test_agent_guidance_preserves_generated_asset_boundaries() -> None:
    guidance = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

    assert "metrics" in guidance.casefold()
    assert "languages" in guidance.casefold()
    assert "daily quote" in guidance.casefold()
    assert "output" in guidance.casefold()
    assert ".github/scripts/render_languages.py" not in guidance
    assert ".github/workflows/snake.yml" not in guidance
