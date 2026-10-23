# CLAUDE.md

Project memory for agent sessions on this repository.

## Pull request workflow

- After opening a PR, post a comment `@codex review` to request an automated
  Codex review. **Wait for Codex's feedback and address it before merging** —
  don't merge instantly.

## About this repo

- This is the GitHub **profile README** repo (`AstorisTheBrave/AstorisTheBrave`),
  rendered at <https://github.com/AstorisTheBrave>.
- `main` owns the README, hand-authored identity SVGs, tests, and generators.
- `output` owns generated light/dark metrics, languages, quote, and contribution
  SVGs. Only the two publishing workflows may write there.
- Metrics, languages, and the daily quote are critical profile signals. Keep all
  three visible; change their content or presentation only with explicit approval.
- `tools/profile_assets.py` aggregates language bytes across public repositories.
  The pinned metrics action renders account context and the full-year calendar.
- URSA is the only mature/complete case study. Keep other projects explicitly in
  progress inside `/NOW` or omit them from completed evidence.
- Preserve the exact SRE role line, `UK time`, and the `/NOW` marker pair.
- Run `uv run ruff check .`, `uv run pytest -q`, and `git diff --check` before
  committing. See `MAINTAINING.md` for refresh and rollback operations.
