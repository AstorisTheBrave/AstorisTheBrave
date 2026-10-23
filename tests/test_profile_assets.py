from __future__ import annotations

import json
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tools.profile_assets import (
    DARK_THEME,
    LIGHT_THEME,
    GitHubClient,
    LanguageShare,
    collect_language_totals,
    main,
    rank_languages,
    render_language_svg,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> object:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FixtureClient(GitHubClient):
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.requested: list[str] = []

    def get_json(self, path: str) -> object:
        self.requested.append(path)
        response = self.responses[path]
        if isinstance(response, Exception):
            raise response
        return response


def repo_path(page: int) -> str:
    return f"/users/AstorisTheBrave/repos?per_page=100&type=owner&page={page}"


def language_path(repo: str) -> str:
    return f"/repos/{repo}/languages"


def test_collects_all_pages() -> None:
    first_page = load_fixture("repos-page-1.json")
    second_page = load_fixture("repos-page-2.json")
    assert isinstance(first_page, list)
    assert isinstance(second_page, list)
    page_of_100 = first_page * 50
    languages = load_fixture("languages.json")
    assert isinstance(languages, dict)
    client = FixtureClient(
        {
            repo_path(1): page_of_100,
            repo_path(2): second_page,
            language_path("AstorisTheBrave/alpha"): languages[
                "AstorisTheBrave/alpha"
            ],
            language_path("AstorisTheBrave/beta"): languages[
                "AstorisTheBrave/beta"
            ],
        }
    )

    totals = collect_language_totals(
        client, "AstorisTheBrave", {"astoristhebrave", "forked"}
    )

    assert totals == {"Python": 35100, "Shell": 15000, "Go": 900}
    assert repo_path(2) in client.requested


def test_skips_forks_private_and_profile_repo() -> None:
    repos = [
        {
            "name": "forked",
            "full_name": "AstorisTheBrave/forked",
            "fork": True,
            "private": False,
        },
        {
            "name": "private",
            "full_name": "AstorisTheBrave/private",
            "fork": False,
            "private": True,
        },
        {
            "name": "AstorisTheBrave",
            "full_name": "AstorisTheBrave/AstorisTheBrave",
            "fork": False,
            "private": False,
        },
    ]
    client = FixtureClient({repo_path(1): repos})

    totals = collect_language_totals(
        client, "AstorisTheBrave", {"astoristhebrave"}
    )

    assert totals == {}
    assert all("/languages" not in path for path in client.requested)


def test_language_endpoint_failure_is_reported_and_skipped(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repos = [
        {
            "name": "broken",
            "full_name": "AstorisTheBrave/broken",
            "fork": False,
            "private": False,
        }
    ]
    error = urllib.error.HTTPError("url", 503, "unavailable", {}, None)
    client = FixtureClient(
        {repo_path(1): repos, language_path("AstorisTheBrave/broken"): error}
    )

    totals = collect_language_totals(client, "AstorisTheBrave", set())

    warning = json.loads(capsys.readouterr().err)
    assert totals == {}
    assert warning == {
        "error": "HTTP Error 503: unavailable",
        "level": "warning",
        "repo": "AstorisTheBrave/broken",
    }


def test_rank_is_deterministic_for_ties() -> None:
    ranked = rank_languages({"Zig": 100, "Go": 100, "Python": 200})

    assert [entry.name for entry in ranked] == ["Python", "Go", "Zig"]


def test_other_bucket_preserves_total() -> None:
    ranked = rank_languages({"Python": 70, "Go": 20, "Shell": 10}, top_n=2)

    assert [entry.name for entry in ranked] == ["Python", "Go", "Other"]
    assert sum(entry.percent for entry in ranked) == pytest.approx(100.0)


def test_xml_metacharacters_are_escaped() -> None:
    svg = render_language_svg(
        [LanguageShare(name='C<&"', percent=100.0, color="#123456")], LIGHT_THEME
    )

    ET.fromstring(svg)
    assert "C&lt;&amp;&quot;" in svg


def test_empty_totals_render_an_accessible_empty_state() -> None:
    svg = render_language_svg([], DARK_THEME)
    root = ET.fromstring(svg)

    assert root.attrib["role"] == "img"
    assert "No public language data available" in svg
    child_names = {child.tag.rsplit("}", 1)[-1] for child in root}
    assert {"title", "desc"} <= child_names
    element_ids = [
        element.attrib["id"] for element in root.iter() if "id" in element.attrib
    ]
    assert len(element_ids) == len(set(element_ids))


def test_cli_writes_light_and_dark_svg(tmp_path: Path) -> None:
    languages = load_fixture("languages.json")
    assert isinstance(languages, dict)
    repos = load_fixture("repos-page-2.json")[:1]
    client = FixtureClient(
        {
            repo_path(1): repos,
            language_path("AstorisTheBrave/beta"): languages[
                "AstorisTheBrave/beta"
            ],
        }
    )

    exit_code = main(
        ["--output-dir", str(tmp_path), "--user", "AstorisTheBrave"],
        client=client,
    )

    assert exit_code == 0
    for name in ("languages.svg", "languages-dark.svg"):
        output = tmp_path / name
        assert output.exists()
        ET.parse(output)
