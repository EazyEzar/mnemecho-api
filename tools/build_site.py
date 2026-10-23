"""Build the static mnemecho.com site from site-src/ into site/.

Each page in site-src/pages/<lang>/<name>.html starts with header lines
(title:, description:), a line '---', then its body HTML. The build wraps every
body in one layout, so the header, language switch and company footer never drift
between pages. Stdlib only; Cloudflare Pages serves site/ as built (no build step).

    python3 tools/build_site.py          build
    python3 tools/build_site.py --check  build, then fail on a placeholder or dash
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site-src"
OUT = ROOT / "site"
LANGS = ("en", "nl")

CHROME = {
    "en": {
        "nav": [("", "Home"), ("pricing", "Pricing"), ("docs", "API docs"), ("status", "Status")],
        "switch": "Nederlands",
        "legal": [("terms", "Terms"), ("privacy", "Privacy"), ("refunds", "Refunds"), ("credits", "Credits")],
        "company": "mnemEcho is a product of",
        "draft": "Draft: these terms are not in force yet. They take effect when paid plans open.",
        "skip": "Skip to content",
    },
    "nl": {
        "nav": [("", "Home"), ("pricing", "Prijzen"), ("docs", "API-docs"), ("status", "Status")],
        "switch": "English",
        "legal": [("terms", "Voorwaarden"), ("privacy", "Privacy"), ("refunds", "Terugbetaling"), ("credits", "Credits")],
        "company": "mnemEcho is een product van",
        "draft": "Concept: deze voorwaarden gelden nog niet. Ze gaan in wanneer de betaalde abonnementen openen.",
        "skip": "Naar de inhoud",
    },
}
LEGAL_PAGES = {"terms", "privacy", "refunds"}


def url_of(lang: str, name: str) -> str:
    return f"/{lang}/{name + '/' if name else ''}"


def read_page(path: Path) -> tuple[dict[str, str], str]:
    head, sep, body = path.read_text(encoding="utf-8").partition("\n---\n")
    if not sep:
        raise ValueError(f"{path}: no '---' line after the header")
    meta = dict(line.split(":", 1) for line in head.strip().splitlines())
    return {k.strip(): v.strip() for k, v in meta.items()}, body


def fill(text: str, site: dict) -> str:
    """{{key}} from site.json; an unknown key is an error, never left in the page."""
    def one(m: re.Match) -> str:
        key = m.group(1)
        if key not in site:
            raise KeyError(f"unknown placeholder {{{{{key}}}}}")
        return html.escape(str(site[key]))
    return re.sub(r"\{\{(\w+)\}\}", one, text)


def render(lang: str, name: str, meta: dict, body: str, site: dict) -> str:
    c = CHROME[lang]
    other = "nl" if lang == "en" else "en"
    nav = "".join(
        f'<a href="{url_of(lang, n)}"{" aria-current=\"page\"" if n == name else ""}>{label}</a>'
        for n, label in c["nav"])
    legal = " · ".join(f'<a href="{url_of(lang, n)}">{label}</a>' for n, label in c["legal"])
    alternates = "".join(
        f'<link rel="alternate" hreflang="{l}" href="{site["base_url"]}{url_of(l, name)}">' for l in LANGS)
    draft = (f'<p class="draft" role="note">{c["draft"]}</p>'
             if site["legal_draft"] and name in LEGAL_PAGES else "")
    title = meta["title"] if not name else f'{meta["title"]} · mnemEcho'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta["description"])}">
<link rel="canonical" href="{site["base_url"]}{url_of(lang, name)}">
{alternates}<link rel="alternate" hreflang="x-default" href="{site["base_url"]}/">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css">
<script src="/assets/site.js" defer></script>
</head>
<body class="page-{name or 'home'}">
<a class="skip" href="#main">{c["skip"]}</a>
<header class="top">
  <a class="brand" href="{url_of(lang, "")}" aria-label="mnemEcho">
    <img class="logo-light" src="/assets/mnemecho-lockup.svg" alt="mnemEcho" width="150" height="31">
    <img class="logo-dark" src="/assets/mnemecho-lockup-dark.svg" alt="" width="150" height="31">
  </a>
  <nav class="nav">{nav}</nav>
  <a class="lang" href="{url_of(other, name)}" hreflang="{other}" lang="{other}" data-lang="{other}">{c["switch"]}</a>
</header>
<main id="main">
{draft}{fill(body, site)}
</main>
<footer class="foot">
  <p>{c["company"]} {html.escape(site["company"])} · KvK {site["kvk"]} · {html.escape(site["address"])}</p>
  <p><a href="mailto:{site["contact"]}">{site["contact"]}</a> · {legal}</p>
</footer>
</body>
</html>
"""


ROOT_INDEX = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>mnemEcho</title>
<meta name="description" content="mnemEcho: speak Dutch from memory, with feedback on every sound. A pronunciation API for Dutch.">
<link rel="alternate" hreflang="en" href="{base}/en/">
<link rel="alternate" hreflang="nl" href="{base}/nl/">
<link rel="alternate" hreflang="x-default" href="{base}/">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
<script>
(function () {{
  var pick = null;
  try {{ pick = localStorage.getItem("lang"); }} catch (e) {{}}
  if (pick !== "en" && pick !== "nl") {{
    pick = /^nl\\b/i.test(navigator.language || "") ? "nl" : "en";
    try {{ localStorage.setItem("lang", pick); }} catch (e) {{}}
  }}
  location.replace("/" + pick + "/");
}})();
</script>
</head>
<body class="page-root">
<main id="main" class="chooser">
  <img class="logo-light" src="/assets/mnemecho-lockup.svg" alt="mnemEcho" width="220" height="45">
  <img class="logo-dark" src="/assets/mnemecho-lockup-dark.svg" alt="mnemEcho" width="220" height="45">
  <p><a href="/en/" hreflang="en">English</a> · <a href="/nl/" hreflang="nl" lang="nl">Nederlands</a></p>
</main>
</body>
</html>
"""

NOT_FOUND = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Not found · mnemEcho</title><link rel="stylesheet" href="/assets/site.css"></head>
<body class="page-root"><main id="main" class="chooser">
<h1>Not found</h1>
<p>This page does not exist. <a href="/en/">Home</a> · <a href="/nl/" lang="nl">Naar de startpagina</a></p>
</main></body></html>
"""

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.mnemecho.com; frame-ancestors 'none'; base-uri 'self'
/assets/*
  Cache-Control: public, max-age=86400
/openapi.json
  Access-Control-Allow-Origin: *
/llms.txt
  Content-Type: text/plain; charset=utf-8
"""


def build() -> list[Path]:
    site = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    written = []
    urls = []
    for lang in LANGS:
        for name in site["pages"]:
            src = SRC / "pages" / lang / f"{name or 'index'}.html"
            meta, body = read_page(src)
            target = OUT / lang / name / "index.html" if name else OUT / lang / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(lang, name, meta, body, site), encoding="utf-8")
            written.append(target)
            urls.append(site["base_url"] + url_of(lang, name))
    (OUT / "index.html").write_text(ROOT_INDEX.format(base=site["base_url"]), encoding="utf-8")
    (OUT / "404.html").write_text(NOT_FOUND, encoding="utf-8")
    (OUT / "_headers").write_text(HEADERS, encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site['base_url']}/sitemap.xml\n")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{site['updated']}</lastmod></url>\n" for u in urls)
        + "</urlset>\n")
    for name in ("llms.txt", "openapi.json"):
        shutil.copy(ROOT / name, OUT / name)
    written += [OUT / "index.html", OUT / "404.html", OUT / "llms.txt"]
    return written


def check(paths: list[Path]) -> list[str]:
    """Problems that must never ship: a placeholder, an em or en dash, a TODO."""
    bad = []
    for p in list(paths) + [ROOT / "README.md", ROOT / "openapi.json", ROOT / "CHANGELOG.md"]:
        text = p.read_text(encoding="utf-8")
        for pattern, why in ((r"PENDING|TODO|\{\{", "placeholder"), ("[–—]", "dash")):
            for m in re.finditer(pattern, text):
                line = text.count("\n", 0, m.start()) + 1
                bad.append(f"{p.relative_to(ROOT)}:{line}: {why}")
    return bad


if __name__ == "__main__":
    pages = build()
    print(f"built {len(pages)} pages into {OUT.relative_to(ROOT)}/")
    if "--check" in sys.argv:
        problems = check(pages)
        for line in problems:
            print(line)
        sys.exit(1 if problems else 0)
