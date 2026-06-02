# CLAUDE.md

Project memory for Claude Code sessions on this repository.

## Pull request workflow

- After opening a PR, post a comment `@codex review` to request an automated
  Codex review. **Wait for Codex's feedback and address it before merging** —
  don't merge instantly.

## About this repo

- This is the GitHub **profile README** repo (`AstorisTheBrave/AstorisTheBrave`),
  rendered at <https://github.com/AstorisTheBrave>.
- Live sections (stats card, languages bar, contribution snake) are rendered by
  GitHub Actions into **committed SVGs under `assets/`** and embedded with
  `<picture>` for light/dark. There are no view-time API calls, so the images
  always load. Do **not** swap them back to live third-party badge services
  (github-readme-stats, streak-stats, etc.) — they share a global rate limit and
  render broken images.
- Languages are aggregated across all public repos by `.github/scripts/render_languages.py`
  (the Actions token only sees this repo, so the metrics plugin can't do it).
