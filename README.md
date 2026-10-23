# Sotorko website

The website for [Sotorko (সতর্ক)](https://sotorko.azimulkabir.com), an Android app that helps people spot mobile-money scams. Bangla by default, English too.

| Address | What |
| --- | --- |
| `/` | Home page in Bangla (the default) |
| `/en/` | Home page in English |
| `/privacy/` | The app's privacy policy, Bangla first, then English |

It is plain static HTML and CSS: no JavaScript, no trackers, no requests to other sites (the Bangla font is self-hosted), and it respects light and dark mode and reduced motion. All links between pages are relative, so it works on the custom domain and on the `github.io` project address.

## Editing

Everything you read on the site lives in [`content.py`](content.py), in Bangla and English side by side. Edit the words there, then rebuild:

```bash
python3 build.py        # needs only Python 3, no packages
```

`build.py` writes `index.html`, `en/index.html`, `privacy/index.html`, `404.html`, `sitemap.xml`, `robots.txt` and `CNAME`. **Commit the generated files**: they are what gets published, and CI fails if they are stale. The build refuses to run if the two languages get out of step.

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

### Illustrations

`assets/icons/*.svg` are exported from the app's own tile art (`python3 tools/build_icons.py --svg ../sotorko-website/assets/icons` in the app repository), so the site and the app match. `assets/logo.svg` and `favicon.svg` use the app's launcher letter.

## Publishing (automatic)

Every push to `main` is published by [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml). You never deploy by hand.

1. **check**: rebuilds the pages with `build.py` and fails if what is committed differs (so you cannot forget to commit the generated files), then runs `scripts/check_site.py` (links, images, in-page anchors, page basics, sitemap).
2. **deploy**: only if the check passes and only on `main`; publishes just the files the site serves to GitHub Pages.

Pull requests run the checks but publish nothing. Run the same checks locally before pushing:

```bash
python3 build.py && python3 scripts/check_site.py
```

The workflow's actions are kept current by Dependabot (monthly).

### One-time setup

- **Pages source** is set to **GitHub Actions** (Settings, Pages). Already done.
- **Custom domain** `sotorko.azimulkabir.com`:
  1. At the domain registrar add a DNS record: type `CNAME`, name `sotorko`, value `azimul-kabir.github.io`.
  2. When DNS has spread, set the domain: Settings, Pages, Custom domain (or `gh api -X PUT repos/azimul-kabir/sotorko-website/pages -f cname=sotorko.azimulkabir.com`), then tick **Enforce HTTPS**.

  Set the domain only after the DNS record exists; before that, the site is reachable at https://azimul-kabir.github.io/sotorko-website/.

The app's About screen links to `https://sotorko.azimulkabir.com/privacy`, so the custom domain must work before the app is published.

## Credits and licence

- The font is Noto Sans Bengali under the SIL Open Font License 1.1 (see `assets/fonts`).
- The call handset in the Hotlines illustration is the Material Icons "call" glyph (Apache License 2.0).
- The site's code and text are not licensed for reuse yet; all rights are reserved by Azimul Kabir Apu until a licence is added.

Sotorko is an independent app. bKash, Nagad and other names belong to their owners.
