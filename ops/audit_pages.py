#!/usr/bin/env python3
"""
Audit every published page for defects that a reader or a crawler would hit.

WHY THIS EXISTS
---------------
The site is 158 pages, 134 of them generated. Nobody can eyeball that, and
"improve the pages" without measuring first is how you end up rewriting the
three pages you happened to open while the other 155 keep the same fault.

Everything here is a defect with a reader on the other end of it, not a style
preference:

  accessibility   a missing alt, a skipped heading level, no page language, no
                  way to skip the nav. Each one is somebody who cannot use the
                  page.
  search          a missing or duplicate title or description. Duplicates are
                  worse than absences: two pages competing to answer the same
                  query beat each other.
  correctness     an internal link that 404s, an image that is not on disk.
  house style     em dashes, en dashes, "Set in Order". These have a build gate
                  for the control layer and had none for the site itself.
  performance     an above the fold image left to lazy load, which delays the
                  one thing the reader is waiting for.

Findings are counted, grouped, and printed worst first, so the fix goes where
the pages are rather than where the last screenshot was.

Generated pages must be fixed in ops/build_zone_pages.py, never by hand. This
prints which findings sit on generated pages so that mistake is visible rather
than discovered after 134 hand edits are overwritten.

Run:  python ops/audit_pages.py
      python ops/audit_pages.py --detail alt      list every case of one check
"""
from __future__ import annotations

import collections
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# Pages built by ops/build_zone_pages.py. A finding here is a generator bug.
GENERATED = re.compile(r"[\\/](rooms|zones)[\\/]")

# The book sample is a 50 chapter export, not a page anybody authored. Holding
# it to the same heading and title rules would drown every real finding.
SKIP = ("downloads/",)


def pages() -> list[str]:
    out = []
    for p in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, SITE).replace("\\", "/")
        if not any(rel.startswith(s) for s in SKIP):
            out.append(p)
    return out


def text_of(html: str) -> str:
    """Visible text, with script, style and svg removed."""
    t = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))


def check(path: str, html: str) -> list[tuple[str, str]]:
    """Return [(check_name, detail)] for one page."""
    found = []

    def add(name, detail=""):
        found.append((name, detail))

    # ---- document ----
    if not re.search(r'<html[^>]*\blang=', html, re.I):
        add("lang", "no lang on <html>, so screen readers guess the language")
    if not re.search(r'name="viewport"', html, re.I):
        add("viewport", "no viewport meta, page will not scale on a phone")

    # A page marked noindex was deliberately kept out of search, so the rules
    # about title and description length do not apply to it. The cart and the
    # order confirmation are both correctly noindex, and flagging their short
    # titles was the checker being wrong rather than the pages.
    indexed = not re.search(r'name="robots"[^>]+content="[^"]*noindex', html, re.I)

    # ---- title ----
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if not m or not m.group(1).strip():
        add("title-missing", "no title")
    else:
        t = re.sub(r"\s+", " ", m.group(1)).strip()
        if indexed and len(t) > 65:
            add("title-long", f"{len(t)} chars, truncated in results: {t[:52]}...")
        elif indexed and len(t) < 25:
            add("title-short", f"{len(t)} chars: {t}")

    # ---- description ----
    m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', html, re.I)
    if not m or not m.group(1).strip():
        add("desc-missing", "no meta description")
    else:
        d = m.group(1).strip()
        if indexed and len(d) > 160:
            add("desc-long", f"{len(d)} chars, truncated")
        elif indexed and len(d) < 60:
            add("desc-short", f"{len(d)} chars")

    # A not-found page has no canonical address, because it is not a page.
    # Giving it one would point a crawler at a URL that does not represent
    # anything, and self-referencing it would assert that /404.html is the
    # preferred version of whatever the visitor actually asked for. It carries
    # noindex instead, which is the correct instrument.
    if not re.search(r'rel="canonical"', html, re.I)             and os.path.basename(path) != "404.html":
        add("canonical", "no canonical link")

    # ---- headings ----
    h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.S | re.I)
    if len(h1s) == 0:
        add("h1-none", "no h1")
    elif len(h1s) > 1:
        add("h1-many", f"{len(h1s)} h1 elements")

    levels = [int(x) for x in re.findall(r"<h([1-6])\b", html, re.I)]
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            add("heading-skip", f"h{a} followed by h{b}")
            break

    # ---- images ----
    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    for tag in imgs:
        if not re.search(r'\balt=', tag, re.I):
            src = (re.search(r'src="([^"]*)"', tag) or [None, "?"])[1]
            add("alt", f"img with no alt: {src}")
        src = re.search(r'src="([^"]*)"', tag)
        # cart.html builds its img tags in JavaScript, so the "src" caught here
        # is a template fragment like assets/img/' + esc(i.img) + ' rather than
        # a path. Reporting it as a missing file is a false positive, and a
        # checker that cries wolf gets ignored along with its real findings.
        if src and ("'" in src.group(1) or "+" in src.group(1) or "${" in src.group(1)):
            src = None
        if src and not src.group(1).startswith(("http", "data:", "/")):
            target = os.path.normpath(os.path.join(os.path.dirname(path),
                                                   src.group(1).split("?")[0]))
            if not os.path.exists(target):
                add("img-missing", f"file not on disk: {src.group(1)}")
    # The first image on a page is almost always above the fold. Lazy loading
    # it delays the one thing the reader is actually waiting for.
    if imgs and 'loading="lazy"' in imgs[0] and "eager" not in imgs[0]:
        add("hero-lazy", "first image is lazy loaded")

    # ---- links ----
    for href in set(re.findall(r'href="([^"]+)"', html)):
        if href.startswith(("http", "#", "mailto:", "tel:", "/")):
            continue
        rel = re.split(r"[?#]", href)[0]
        if not rel:
            continue
        target = os.path.normpath(os.path.join(os.path.dirname(path), rel))
        if not (os.path.exists(target) or os.path.exists(target + ".html")):
            add("link-broken", href)

    # ---- house style ----
    body = text_of(html)
    if "—" in body:
        add("em-dash", f"{body.count(chr(0x2014))} em dash(es)")
    if "–" in body:
        add("en-dash", f"{body.count(chr(0x2013))} en dash(es)")
    if re.search(r"set in order", body, re.I):
        add("set-in-order", "uses the term the method rejects")

    # ---- analytics ----
    if "stats/script.js" not in html:
        add("no-analytics", "page records nothing")

    return found


def main(detail: str | None) -> int:
    ps = pages()
    per_page: dict[str, list] = {}
    counts = collections.Counter()
    gen_counts = collections.Counter()
    titles, descs = collections.defaultdict(list), collections.defaultdict(list)

    for p in ps:
        html = io.open(p, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(p, SITE).replace("\\", "/")
        f = check(p, html)
        if f:
            per_page[rel] = f
        for name, _ in f:
            counts[name] += 1
            if GENERATED.search(p):
                gen_counts[name] += 1
        m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
        if m:
            titles[re.sub(r"\s+", " ", m.group(1)).strip()].append(rel)
        m = re.search(r'name="description"[^>]+content="([^"]*)"', html, re.I)
        if m:
            descs[m.group(1).strip()].append(rel)

    # Duplicates are a whole-site property, not a per-page one.
    dup_t = {k: v for k, v in titles.items() if len(v) > 1 and k}
    dup_d = {k: v for k, v in descs.items() if len(v) > 1 and k}

    if detail:
        print(f"  every page with '{detail}':\n")
        n = 0
        for rel, f in per_page.items():
            for name, d in f:
                if name == detail:
                    print(f"    {rel:56} {d}")
                    n += 1
        print(f"\n  {n} case(s)")
        return 0

    print(f"  {len(ps)} pages audited, {sum(counts.values())} finding(s) "
          f"across {len(per_page)} page(s)\n")
    if counts:
        print(f"  {'check':16} {'total':>6} {'generated':>10}   where the fix goes")
        for name, n in counts.most_common():
            g = gen_counts[name]
            where = ("ops/build_zone_pages.py" if g == n else
                     "hand written pages" if g == 0 else
                     "both, generator first")
            print(f"  {name:16} {n:>6} {g:>10}   {where}")
    print()
    print(f"  duplicate titles       {len(dup_t)} set(s)")
    for t, v in list(dup_t.items())[:4]:
        print(f"    {len(v):>3} pages share: {t[:58]}")
    print(f"  duplicate descriptions {len(dup_d)} set(s)")
    for d, v in list(dup_d.items())[:4]:
        print(f"    {len(v):>3} pages share: {d[:58]}")

    if not counts and not dup_t and not dup_d:
        print("\n  Clean.")
        return 0
    print("\n  python ops/audit_pages.py --detail CHECK lists every case.")
    return 1


if __name__ == "__main__":
    d = None
    if "--detail" in sys.argv:
        i = sys.argv.index("--detail")
        d = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
    sys.exit(main(d))
