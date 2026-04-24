# Pushing this to GitHub — step by step

This folder is **ready to commit** to a repo named `AstorisTheBrave/AstorisTheBrave`
(the "profile repo" — same name as your username — is what GitHub renders on
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

Refresh your profile page — the editorial banner should appear.

## 3 · Turn on the Actions

All three workflows live under `.github/workflows/`. They are enabled
automatically on first push. A few need one-time secrets.

### 3a · Snake (no setup)

Runs every 6h. First run takes a minute. After that, the snake SVG will
start appearing at the top of section 05.

You can force a run from **Actions → snake → Run workflow**.

### 3b · Quote (no setup)

Rotates the daily quote at 07:00 UTC. Nothing to configure.

### 3c · Spotify (one-time setup)

You need a Spotify app + a refresh token, then three repo secrets.

1. Create an app at <https://developer.spotify.com/dashboard>
2. Get a refresh token — I recommend the walk-through at
   <https://benwiz.com/notes/create-spotify-refresh-token/>
3. In **Settings → Secrets and variables → Actions → New repository secret**,
   add:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_REFRESH_TOKEN`
4. The workflow re-runs every 5 min and rewrites the block between
   `<!-- SPOTIFY:START -->` and `<!-- SPOTIFY:END -->`.

If you don't want this, **delete `.github/workflows/spotify.yml`** and
the placeholder block from the README.

## 4 · Editing the `/now` block by hand

Find this in the README:

```html
<!-- NOW:START -->
...
<!-- NOW:END -->
```

Edit the lines between the markers whenever your focus changes. That's
the whole ritual. Don't automate it.

## 5 · The easter egg

Section 08 has three `<details>` blocks. One is a `man astoris` page,
one is a shell alias, one is a little ASCII box. Readers have to click
to open them. If you want more, just add another `<details>` block —
GitHub's markdown renders them inline.

## What I omitted (and why)

- **Trophy wall, visitor-count leaderboard** — felt noisy for the voice.
  If you want them back, they're one badge each.
- **Dev.to / blog feed** — only wire this up once you have writing live.
- **WakaTime** — great but requires a separate account & tracker.

## Files in this package

```
github-profile/
├─ README.md                             ← the profile README
├─ assets/
│   ├─ banner.svg                        ← editorial typewriter banner
│   └─ whoami.svg                        ← terminal whoami animation
├─ .github/workflows/
│   ├─ snake.yml                         ← contribution snake (6h)
│   ├─ spotify.yml                       ← now-playing (5min, needs secrets)
│   └─ quote.yml                         ← daily quote rotation
├─ preview.html                          ← local preview of the whole thing
└─ SETUP.md                              ← this file
```

## One more thing

The README is designed to look **the same** in light and dark mode —
the SVGs swap palettes via `prefers-color-scheme`, the stat cards do too
with `<picture>`. If you force-set a mode in your GitHub settings,
you'll only ever see one half of the design; flip it back to
**System** to see both.
