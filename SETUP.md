# Pushing this to GitHub - step by step

This folder is **ready to commit** to a repo named `AstorisTheBrave/AstorisTheBrave`
(the "profile repo" - same name as your username - is what GitHub renders on
your profile page).

## 1 · Create the repo

1. Go to <https://github.com/new>
2. **Repository name:** `AstorisTheBrave` (must exactly match your username)
3. **Public**. Initialize with nothing (no README, no .gitignore).
4. Create.

## 2 · Push this folder

From the root of this project, in a terminal:

```bash
cd github-profile
git init -b main
git add .
git commit -m "profile: initial readme"
git remote add origin git@github.com:AstorisTheBrave/AstorisTheBrave.git
git push -u origin main
```

Refresh your profile page - the banner should appear.

## 3 · Turn on the Actions

All workflows live under `.github/workflows/`. They are enabled automatically
on first push.

### 3a · Snake (no setup)

Runs every 6h. First run takes a minute. After that, the snake SVG appears in
section 05. Force a run from **Actions -> snake -> Run workflow**.

### 3b · Quote (no setup)

Rotates the daily quote at 07:00 UTC. Nothing to configure.

## 4 · Editing the `/now` block by hand

Find this in the README:

```html
<!-- NOW:START -->
...
<!-- NOW:END -->
```

Edit the lines between the markers whenever your focus changes. That's the
whole ritual. Don't automate it.

## 5 · The easter egg

Section 07 has three `<details>` blocks. Readers have to click to open them.
Add more by copying any `<details>` block and editing the content.

## What I omitted (and why)

- **Spotify / now-playing** - removed. Needs OAuth setup and burns Actions
  minutes on a 5-minute cron. Not worth the friction.
- **Trophy wall, visitor leaderboard** - felt noisy. One badge each if you want.
- **Dev.to / blog feed** - wire up once you have writing live.
- **WakaTime** - great but requires a separate account and browser extension.

## Files in this package

```
github-profile/
├─ README.md                             <- the profile README
├─ assets/
│   ├─ banner.svg                        <- editorial typewriter banner
│   └─ whoami.svg                        <- terminal whoami animation
├─ .github/workflows/
│   ├─ snake.yml                         <- contribution snake (6h)
│   └─ quote.yml                         <- daily quote rotation
├─ preview.html                          <- local preview of the whole thing
└─ SETUP.md                              <- this file
```

## One more thing

The README is designed to look the same in light and dark mode - the SVGs
swap palettes via `prefers-color-scheme`, the stat cards too with `<picture>`.
If you force-set a mode in your GitHub settings you'll only see one half of
the design; flip it back to **System** to see both.
