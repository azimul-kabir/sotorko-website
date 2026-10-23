#!/usr/bin/env python3
"""Builds the static site from content.py and data/privacy.json. No dependencies.

    python3 build.py

Writes index.html (Bangla, the default), en/index.html (English), privacy/index.html (both languages),
404.html, sitemap.xml and robots.txt. Links between pages are relative, so the site
works on the custom domain and under any other address (a preview URL, a local server) alike.
"""
import html
import json
import pathlib

from content import BN, DEVELOPER, DEVELOPER_SITE, EMAIL, EN, GITHUB, SITE

ROOT = pathlib.Path(__file__).resolve().parent
TODAY = "2026-10-23"
LOCALE = {"bn": "bn_BD", "en": "en_US"}
TILE_CLASS = {"message": "t-message", "number": "t-number", "family": "t-family", "hotline": "t-hotline", "sos": "t-sos"}
e = html.escape


def check_languages():
    missing = set(BN) ^ set(EN)
    assert not missing, f"keys differ between Bangla and English: {missing}"
    for k in BN:
        if isinstance(BN[k], (list, tuple, dict)):
            assert len(BN[k]) == len(EN[k]), f"'{k}' has a different number of items in Bangla and English"


def head(c, *, title, description, path, alt_links, base, og=True):
    """path is the page's address under SITE ('' for the root)."""
    alternates = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{p}">' for l, p in alt_links)
    return f"""<!doctype html>
<html lang="{c['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{SITE}{path}">
{alternates}
<meta name="theme-color" content="#0b6e4f">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{base}assets/fonts/NotoSansBengali.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}assets/style.css">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(BN['name'])} / {e(EN['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:locale" content="{LOCALE[c['lang']]}">
{'<meta property="og:image" content="' + SITE + '/assets/og.png">' + chr(10) + '<meta name="twitter:card" content="summary_large_image">' if (ROOT / 'assets/og.png').exists() and og else '<meta name="twitter:card" content="summary">'}
</head>
"""


def header(c, *, base, home, switch_href, nav=True):
    links = "".join(f'<a href="{home}#{i}">{e(t)}</a>' for i, t in c["nav"]) if nav else ""
    return f"""<body>
<a class="skip" href="#main">{e(c['skip'])}</a>
<header class="site-header">
<div class="wrap bar">
<a class="brand" href="{home}"><img src="{base}assets/logo.svg" alt="" width="40" height="40"><span>{e(c['name'])}</span></a>
<nav class="nav" aria-label="{e(c['name'])}">{links}</nav>
<a class="lang" href="{switch_href}" hreflang="{'en' if c['lang'] == 'bn' else 'bn'}" lang="{'en' if c['lang'] == 'bn' else 'bn'}" aria-label="{e(c['switch_aria'])}">{e(c['switch_label'])}</a>
</div>
</header>
"""


def footer(c, *, base, privacy_href):
    def href(h):
        return privacy_href if h == "/privacy/" else h
    links = "".join(f'<a href="{href(h)}">{e(t)}</a>' for t, h in c["footer_links"])
    return f"""<footer class="site-footer">
<div class="wrap">
<div class="foot">
<div><strong>{e(c['name'])}</strong><br>{e(c['copyright'])}</div>
<nav aria-label="{e(c['name'])}">{links}<a href="mailto:{EMAIL}">{e(c['contact'])}: {EMAIL}</a></nav>
</div>
<p class="small foot-note">{e(c['disclaimer'])}</p>
</div>
</footer>
</body>
</html>
"""


def phone(c, base):
    t = c["tiles"]
    def tile(key, cls):
        return f'<div class="mock-tile {cls}"><img src="{base}assets/icons/{key}.svg" alt="" width="50" height="50">{e(t[key])}</div>'
    return f"""<div class="phone" aria-hidden="true">
<div class="top"><img src="{base}assets/logo.svg" alt="" width="30" height="30"><span>{e(c['name'])}</span></div>
<p class="tag">{e(c['phone_tagline'])}</p>
<div class="mock-grid">
{tile('message', 't-message')}{tile('number', 't-number')}{tile('family', 't-family')}{tile('hotline', 't-hotline')}
<div class="mock-tile mock-wide t-sos"><img src="{base}assets/icons/sos.svg" alt="" width="40" height="40">{e(t['sos'])}</div>
</div>
</div>"""


def render_home(c, *, base, home, switch_href, privacy_href, path, alt_links):
    steps = "".join(f"<li><h3>{e(t)}</h3><p>{e(d)}</p></li>" for t, d in c["steps"])
    cards = "".join(
        f'<article class="card {TILE_CLASS[k]}"><img src="{base}assets/icons/{k}.svg" alt="" width="76" height="76"><h3>{e(t)}</h3><p>{e(d)}</p></article>'
        for k, t, d in c["features"])
    also = "".join(f"<li>{e(x)}</li>" for x in c["also"])
    stats = "".join(f'<div class="stat"><b>{e(a)}</b>{e(b)}</div>' for a, b in c["stats"])
    scams = "".join(
        f'<article class="scam"><h3>{e(t)}</h3><span class="label">{e(c["look"])}</span><p>{e(l)}</p><span class="label">{e(c["do"])}</span><p class="do">{e(d)}</p></article>'
        for t, l, d in c["scams"])
    points = "".join(f"<li>{e(x)}</li>" for x in c["privacy_points"])
    digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯") if c["lang"] == "bn" else {}
    hotlines = "".join(f'<a class="hotline" href="tel:{n}">{e(name)}<span>{n.translate(digits)}</span></a>' for name, n in c["hotlines"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in c["faq"])
    return (
        head(c, title=c["title"], description=c["description"], path=path, alt_links=alt_links, base=base)
        + header(c, base=base, home=home, switch_href=switch_href)
        + f"""<main id="main">
<section class="hero">
<div class="wrap hero-grid">
<div>
<h1>{e(c['hero_title'])}</h1>
<p class="lead">{e(c['hero_text'])}</p>
<div class="actions">
<span class="btn btn-soon">{e(c['soon'])}</span>
<a class="btn btn-ghost" href="#how">{e(c['how_link'])}</a>
</div>
<p class="small"><a href="mailto:{EMAIL}?subject=Sotorko">{e(c['notify'])}</a></p>
</div>
{phone(c, base)}
</div>
</section>

<section class="tint-green" aria-labelledby="why">
<div class="wrap">
<h2 id="why">{e(c['stats_title'])}</h2>
<div class="stats">{stats}</div>
<p class="small">{e(c['stats_source'])}</p>
</div>
</section>

<section id="how" aria-labelledby="how-h">
<div class="wrap">
<h2 id="how-h">{e(c['how_title'])}</h2>
<ol class="steps">{steps}</ol>
</div>
</section>

<section id="features" aria-labelledby="feat-h">
<div class="wrap">
<h2 id="feat-h">{e(c['features_title'])}</h2>
<div class="cards">{cards}</div>
<ul class="also">{also}</ul>
</div>
</section>

<section id="scams" class="tint-green" aria-labelledby="scam-h">
<div class="wrap">
<h2 id="scam-h">{e(c['scams_title'])}</h2>
<div class="scam-grid">{scams}</div>
</div>
</section>

<section id="privacy" aria-labelledby="priv-h">
<div class="wrap">
<h2 id="priv-h">{e(c['privacy_title'])}</h2>
<ul class="checks">{points}</ul>
<p><a class="btn btn-ghost" href="{privacy_href}">{e(c['privacy_link'])}</a></p>
</div>
</section>

<section class="tint-green" aria-labelledby="hot-h">
<div class="wrap">
<h2 id="hot-h">{e(c['hotlines_title'])}</h2>
<div class="hotline-grid">{hotlines}</div>
</div>
</section>

<section id="faq" aria-labelledby="faq-h">
<div class="wrap">
<h2 id="faq-h">{e(c['faq_title'])}</h2>
{faq}
</div>
</section>
</main>
"""
        + footer(c, base=base, privacy_href=privacy_href)
    )


def policy_section(d, lang):
    out = [f'<article class="policy" id="{lang}" lang="{lang}">', f"<h1>{e(d['title'])}</h1>", f'<p class="meta">{e(d["updated"])}</p>', f"<p>{e(d['intro'])}</p>"]
    for i, (heading, blocks) in enumerate(d["sections"], 1):
        out.append(f"<h2>{i}. {e(heading)}</h2>")
        for kind, items in blocks:
            out += (["<ul>"] + [f"<li>{e(t)}</li>" for t in items] + ["</ul>"]) if kind == "ul" else [f"<p>{e(t)}</p>" for t in items]
    out.append("</article>")
    return "\n".join(out)


def render_privacy(data):
    c = BN  # the page opens in Bangla, like the rest of the site
    title = f"{data['bn']['title']} · {data['en']['title']}"
    return (
        head(c, title=title, description=data["bn"]["intro"], path="/privacy/", alt_links=[("bn", "/privacy/"), ("x-default", "/privacy/")], base="../", og=False)
        + header(c, base="../", home="../", switch_href="#en", nav=False)
        + f"""<main id="main">
<div class="wrap">
{policy_section(data['bn'], 'bn')}
{policy_section(data['en'], 'en')}
</div>
</main>
"""
        + footer(c, base="../", privacy_href="./")
    )


def render_404():
    c = BN
    return (
        head(c, title=f"{BN['not_found_title']} · {EN['not_found_title']}", description=BN["not_found_text"], path="/404.html", alt_links=[], base="/", og=False)
        + header(c, base="/", home="/", switch_href="/en/", nav=False)
        + f"""<main id="main" class="wrap notfound">
<h1>{e(BN['not_found_title'])}</h1><p>{e(BN['not_found_text'])}</p>
<p><a class="btn btn-ghost" href="/">{e(BN['home'])}</a></p>
<h2 lang="en">{e(EN['not_found_title'])}</h2><p lang="en">{e(EN['not_found_text'])}</p>
<p lang="en"><a class="btn btn-ghost" href="/en/">{e(EN['home'])}</a></p>
</main>
"""
        + footer(c, base="/", privacy_href="/privacy/")
    )


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print("wrote", rel)


def main():
    check_languages()
    pair = [("bn", "/"), ("en", "/en/"), ("x-default", "/")]
    write("index.html", render_home(BN, base="", home="./", switch_href="en/", privacy_href="privacy/", path="/", alt_links=pair))
    write("en/index.html", render_home(EN, base="../", home="./", switch_href="../", privacy_href="../privacy/", path="/en/", alt_links=pair))
    write("privacy/index.html", render_privacy(json.loads((ROOT / "data/privacy.json").read_text())))
    write("404.html", render_404())
    urls = [("/", pair), ("/en/", pair), ("/privacy/", [])]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for path, alts in urls:
        sm.append(f"<url><loc>{SITE}{path}</loc><lastmod>{TODAY}</lastmod>" + "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{p}"/>' for l, p in alts) + "</url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    main()
