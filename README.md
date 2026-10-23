# Sotorko website

The website for [Sotorko (সতর্ক)](https://sotorko.azimulkabir.com), an Android app that helps people spot mobile-money scams. Bangla by default, English too.

| Address | What |
| --- | --- |
| `/` | Home page in Bangla (the default) |
| `/en/` | Home page in English |
| `/privacy/` | The app's privacy policy, Bangla first, then English |

It is plain static HTML and CSS: no JavaScript, no trackers, no requests to other sites (the Bangla font is self-hosted), and it respects light and dark mode and reduced motion. It is hosted on Cloudflare Workers (static assets). All links between pages are relative, so it also works under any other address, such as a preview URL.

## Editing

Everything you read on the site lives in [`content.py`](content.py), in Bangla and English side by side. Edit the words there, then rebuild:

```bash
python3 build.py        # needs only Python 3, no packages
```

`build.py` writes `index.html`, `en/index.html`, `privacy/index.html`, `404.html`, `sitemap.xml` and `robots.txt`. **Commit the generated files**: they are what gets published, and CI fails if they are stale. The build refuses to run if the two languages get out of step.

Look at it locally with `python3 -m http.server` and open http://localhost:8000.

### The privacy policy

The text of the policy belongs to the app, so it is written in the app repository (`tools/build_privacy.py`) and copied here as data:

```bash
# in the app repository
python3 tools/build_privacy.py --site ../sotorko-website
# then here
python3 build.py
```

Never edit `data/privacy.json` or `privacy/index.html` by hand.

### Screenshots

The phone pictures are real screenshots of the app (a made-up example message, no real data), in Bangla and English, as small WebP files in `assets/shots/`. They go stale when the app's screens change, so refresh them then:

```bash
# in the app repository, with an emulator or phone connected and a debug build installed
python3 tools/capture_screenshots.py /tmp/raw
# then here (needs Pillow: pip install pillow)
python3 scripts/optimize_shots.py /tmp/raw
python3 build.py && python3 scripts/check_site.py
```

The same raw captures work for the Play Store listing. The check script fails the build if an image lacks alt text or fixed dimensions.

### Illustrations

`assets/icons/*.svg` are exported from the app's own tile art (`python3 tools/build_icons.py --svg ../sotorko-website/assets/icons` in the app repository), so the site and the app match. `assets/logo.svg` and `favicon.svg` use the app's launcher letter.

## Publishing (Cloudflare Workers)

The site is served by a Cloudflare Worker with static assets: no Worker code, only files. Everything it needs is in the repo:

| File | Purpose |
| --- | --- |
| `wrangler.jsonc` | Names the project (`sotorko-website`), serves `_site/`, shows `404.html` for unknown addresses, and attaches the custom domain `sotorko.azimulkabir.com` on deploy (its DNS is on Cloudflare, so the record is created for you). |
| `scripts/optimize_shots.py` | (Not part of the build.) Turns raw app screenshots into WebP. |
| `scripts/stage.py` | Collects exactly what is served into `_site/`. Build scripts, data and docs are never published. |
| `cloudflare/_headers` | Security headers (a strict Content Security Policy that allows only this site's own files, no framing, no sensors) and cache times. |
| `cloudflare/_redirects` | `/policy` and `/privacy-policy` go to `/privacy/`. |

### One-time setup in the Cloudflare dashboard

1. **Workers & Pages, Create, Import a repository** (connect GitHub, choose `azimul-kabir/sotorko-website`).
2. **Project name**: `sotorko-website` (it must match `name` in `wrangler.jsonc`).
3. **Build command**: `python3 build.py && python3 scripts/check_site.py && python3 scripts/stage.py`
   **Deploy command**: `npx wrangler deploy` (the default).
4. Save and deploy. After this, every push to `main` builds and publishes by itself.

Because the checks are part of the build command, **a failing check stops the deploy**: the previous version stays live. Other branches and pull requests get preview URLs and are never published to the real domain.

The first deploy also creates the DNS record for `sotorko.azimulkabir.com` and issues its HTTPS certificate (usually a minute or two). Check it under the Worker's **Settings, Domains & Routes**. The app's About screen links to `https://sotorko.azimulkabir.com/privacy`, so this must work before the app is published.

### Without the dashboard

```bash
npm install                  # once, installs wrangler
npx wrangler login           # once, opens the browser
npm run deploy               # build, check, stage, publish
npm run preview              # same, but serves it on http://localhost:8787
```

### GitHub

[`.github/workflows/check.yml`](.github/workflows/check.yml) runs the same build, freshness check, link check and staging on every push and pull request, so there is a pass or fail on GitHub too. It does not publish. Dependabot keeps its actions and wrangler current (monthly).

Run the checks yourself before pushing:

```bash
python3 build.py && python3 scripts/check_site.py && python3 scripts/stage.py
```

## Credits and licence

- The font is Noto Sans Bengali under the SIL Open Font License 1.1 (see `assets/fonts`).
- The call handset in the Hotlines illustration is the Material Icons "call" glyph (Apache License 2.0).
- The site's code and text are not licensed for reuse yet; all rights are reserved by Azimul Kabir Apu until a licence is added.

Sotorko is an independent app. bKash, Nagad and other names belong to their owners.
