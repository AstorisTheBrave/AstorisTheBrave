# Maintaining the profile

This repository renders the public profile for `AstorisTheBrave`. `main` owns the
hand-authored profile and tooling; `output` owns generated metrics, language,
quote, and contribution SVGs.

## Toolchain and checks

Use Python 3.15.1 and uv 0.13.5. From the repository root, run:

```sh
uv sync --locked --dev
uv run ruff check .
uv run pytest -q
git diff --check
```

`uv run pytest tests/test_profile_assets.py -q` exercises fixture-backed light and
dark language rendering. For a live local preview, set `GH_TOKEN` and run:

```sh
uv run python -m tools.profile_assets --output-dir dist/profile-assets
```

## Update the current focus

Edit only the lines between the single marker pair in `README.md`:

```html
<!-- NOW:START -->
<!-- NOW:END -->
```

Keep unfinished work labeled `building` or `working on`. URSA is the only mature
case study until that project-status decision is explicitly changed.

## Refresh generated assets

`.github/workflows/profile-assets.yml` runs daily and can be dispatched manually:

```sh
gh workflow run profile-assets.yml --ref main
```

It renders `metrics*.svg`, `languages*.svg`, and `github-snake*.svg`, then commits
them only to `output`. Never commit those generated files to `main`.

`.github/workflows/daily-quote.yml` refreshes `quote*.svg` every day at midnight
in `Europe/London`. Dispatch it manually with:

```sh
gh workflow run daily-quote.yml --ref main
```

The built-in token covers public data. An optional repository Actions secret named
`METRICS_TOKEN` can supply broader account data; use only the minimum read scopes
needed and never place the token in source, logs, or generated assets.

## Rollback

Revert the source commit on `main`, let the quality workflow pass, then manually
run `profile-assets.yml` again. If only a generated card is bad, fix or revert the
source configuration first and regenerate; do not hand-edit the `output` artifact.

