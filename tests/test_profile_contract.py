from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
README = ROOT / "README.md"


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


@pytest.mark.xfail(reason="Task 3 replaces the private case-study link", strict=True)
def test_private_aegis_is_not_linked() -> None:
    assert "github.com/AstorisTheBrave/aegis" not in read_readme()


@pytest.mark.xfail(reason="Task 3 replaces the fixed UTC offset", strict=True)
def test_timezone_copy_is_dst_safe() -> None:
    markdown = read_readme()

    assert not re.search(r"UTC\s*\+\s*5", markdown, flags=re.IGNORECASE)
    assert "UK time" in markdown


@pytest.mark.xfail(reason="Task 3 moves generated assets to output", strict=True)
def test_generated_assets_are_not_embedded_from_main() -> None:
    markdown = read_readme()
    output_root = (
        "https://raw.githubusercontent.com/"
        "AstorisTheBrave/AstorisTheBrave/output/"
    )

    assert "./assets/metrics" not in markdown
    assert "./assets/languages" not in markdown
    assert f"{output_root}languages.svg" in markdown
    assert f"{output_root}languages-dark.svg" in markdown
