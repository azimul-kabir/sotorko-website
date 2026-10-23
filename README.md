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

`build.py` writes `index.html`, `en/index.html`, `privacy/index.html`, `404.html`, `sitemap.xml`, `robots.txt` and `CNAME`. **Commit the generated files**: GitHub Pages serves them as they are. The build refuses to run if the two languages get out of step.

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

## Putting it online (GitHub Pages)

1. **Settings, Pages**: deploy from branch `main`, folder `/ (root)`.
2. **Custom domain**: `sotorko.azimulkabir.com` (the `CNAME` file already says so). At your domain registrar add a DNS record: type `CNAME`, name `sotorko`, value `azimul-kabir.github.io`.
3. When GitHub shows the domain as verified, tick **Enforce HTTPS**.

The app's About screen links to `https://sotorko.azimulkabir.com/privacy`, so that address must work before the app is published.

## Credits and licence

- The font is Noto Sans Bengali under the SIL Open Font License 1.1 (see `assets/fonts`).
- The call handset in the Hotlines illustration is the Material Icons "call" glyph (Apache License 2.0).
- The site's code and text are not licensed for reuse yet; all rights are reserved by Azimul Kabir Apu until a licence is added.

Sotorko is an independent app. bKash, Nagad and other names belong to their owners.
