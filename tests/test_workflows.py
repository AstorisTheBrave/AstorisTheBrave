from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
FULL_SHA_ACTION = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert isinstance(data, dict)
    return data


def workflow_files() -> list[Path]:
    return sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])


def iter_uses(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "uses" and isinstance(child, str):
                found.append(child)
            else:
                found.extend(iter_uses(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(iter_uses(child))
    return found


def test_actions_are_full_sha_pinned() -> None:
    unpinned = {
        f"{path.name}: {action}"
        for path in workflow_files()
        for action in iter_uses(load_yaml(path))
        if not action.startswith("./") and not FULL_SHA_ACTION.fullmatch(action)
    }

    assert unpinned == set()


def test_quality_permissions_are_read_only() -> None:
    quality = load_yaml(WORKFLOWS / "quality.yml")

    assert quality["permissions"] == {"contents": "read"}
    assert all("permissions" not in job for job in quality["jobs"].values())


def test_publish_job_is_only_writer() -> None:
    writers: list[str] = []
    for path in workflow_files():
        workflow = load_yaml(path)
        if workflow.get("permissions", {}).get("contents") == "write":
            writers.append(f"{path.name}: top-level")
        for name, job in workflow.get("jobs", {}).items():
            if job.get("permissions", {}).get("contents") == "write":
                writers.append(f"{path.name}: {name}")

    assert writers == ["daily-quote.yml: publish", "profile-assets.yml: publish"]


def test_asset_schedule_is_daily() -> None:
    workflow = load_yaml(WORKFLOWS / "profile-assets.yml")
    triggers = workflow["on"]

    assert triggers["schedule"] == [{"cron": "17 4 * * *"}]
    assert "workflow_dispatch" in triggers


def test_quote_schedule_is_midnight_uk_time() -> None:
    workflow = load_yaml(WORKFLOWS / "daily-quote.yml")
    triggers = workflow["on"]

    assert triggers["schedule"] == [
        {"cron": "0 0 * * *", "timezone": "Europe/London"}
    ]
    assert "workflow_dispatch" in triggers
    source = (WORKFLOWS / "daily-quote.yml").read_text(encoding="utf-8")
    assert "quote.svg" in source
    assert "quote-dark.svg" in source
    assert "git push origin output" in source


def test_main_is_not_a_publish_target() -> None:
    workflow = (WORKFLOWS / "profile-assets.yml").read_text(encoding="utf-8")

    assert "ref: output" in workflow
    assert "git push origin output" in workflow
    assert "git push origin main" not in workflow


def test_profile_assets_include_metrics_languages_and_snake() -> None:
    workflow = (WORKFLOWS / "profile-assets.yml").read_text(encoding="utf-8")

    assert workflow.count(
        "lowlighter/metrics@65836723097537a54cd8eb90f61839426b4266b6"
    ) == 2
    for filename in (
        "metrics.svg",
        "metrics-dark.svg",
        "languages.svg",
        "languages-dark.svg",
        "github-snake.svg",
        "github-snake-dark.svg",
    ):
        assert filename in workflow
    assert workflow.count("output_action: none") == 2


def test_dependabot_covers_actions_and_uv() -> None:
    config = load_yaml(ROOT / ".github" / "dependabot.yml")
    ecosystems = {entry["package-ecosystem"] for entry in config["updates"]}

    assert ecosystems == {"github-actions", "uv"}
    for entry in config["updates"]:
        assert entry["directory"] == "/"
        assert entry["open-pull-requests-limit"] == "5"
