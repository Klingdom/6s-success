#!/usr/bin/env python3
"""
Regenerate the site's free-sample HTML from the book source, with images
degraded to text descriptions.

The chapter images live only on the Desktop: content/**/*.jpg and
content/**/*.png are gitignored, 1.78 GB of binaries this repository never
carries. The free sample was shipped with raw <img> tags pointing at those
files, on both copies it has, content/book/... (the master) and
site/downloads/... (what actually deploys). The result: every one of the 172
figures shows as a broken image icon to a visitor who clicks "Read chapters 1
to 30 free", the button on the book page and this site's primary lead magnet.
Two of the three stylesheet links pointed the same way: assets/fonts.css never
shipped its font files to site/downloads/ at all.

ops/build_epub.py already solved the same problem for the EPUB, on the same
source markup: embed an image if the file exists, degrade to its alt text (a
"Figure description" panel) if it does not. This applies the identical
transform to the HTML mirror rather than re-deriving it, and repoints the
fonts link at what the site already ships, ../assets/css/fonts.css, instead of
duplicating font files a second time.

Run:  python ops/build_sample_html.py --check     report only, changes nothing
      python ops/build_sample_html.py --apply     write the output
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The source in content/book/ has never carried this: it was added by hand
# only to the shipped copy at ship time, so every regeneration from source
# silently dropped analytics from this site's primary lead magnet with no
# error and no visible sign, the same "generator does not know about
# hand-added content" shape issue #26 already names for other generators.
# Same snippet, same id, as every other page on the site.
ANALYTICS = ('<script defer src="/stats/script.js" '
             'data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a" '
             'data-host-url="https://6s-success.com/stats"></script>')
NAME = "6S Success Home Edition - Sample (Chapters 1-30).html"
SRC = os.path.join(ROOT, "content", "book", NAME)
OUT = os.path.join(ROOT, "site", "downloads", NAME)
BOOK_CSS_SRC = os.path.join(ROOT, "content", "book", "assets", "book.css")
BOOK_CSS_OUT = os.path.join(ROOT, "site", "downloads", "assets", "book.css")

# Matches the EPUB build's panel exactly, so the same visual language means
# the same thing everywhere a figure is not shipped: a photograph is missing,
# not that anything else about the book is unfinished.
FIGALT_CSS = """
/* a figure whose image file is not shipped degrades to its description */
.figalt{font-family:var(--sans); font-size:.86em; line-height:1.5; color:var(--soft);
        background:var(--panel); border:1px solid var(--rule); border-radius:10px;
        padding:12px 14px; margin:0;}
.figalt-lbl{display:block; font-size:.8em; letter-spacing:.16em; text-transform:uppercase;
            font-weight:600; color:var(--terra); margin-bottom:.35em;}
"""


def degrade_images(html):
    """Every <img> becomes its alt text in a labelled panel. None of the 172
    source images ship in this repository, so this is not a fallback path,
    it is the only path."""
    degraded = 0

    def repl(m):
        nonlocal degraded
        tag = m.group(0)
        alt_m = re.search(r'alt="([^"]*)"', tag)
        alt = alt_m.group(1) if alt_m else ""
        degraded += 1
        if not alt:
            return ""
        return ('<p class="figalt"><span class="figalt-lbl">Figure description</span> '
                + alt + "</p>")

    html = re.sub(r"<img\b[^>]*/?>", repl, html)
    return html, degraded


def main(apply_it):
    if not os.path.exists(SRC):
        raise SystemExit(f"missing source: {os.path.relpath(SRC, ROOT)}")

    html = open(SRC, encoding="utf-8").read()
    before_img = len(re.findall(r"<img\b[^>]*/?>", html))
    html, degraded = degrade_images(html)

    # The site already ships these font files at site/assets/fonts/; do not
    # duplicate them under site/downloads/. site/assets/css/fonts.css declares
    # the same @font-face rules this page needs, so point at it instead of a
    # fonts.css that never carried its files here.
    html, n = re.subn(r'href="assets/fonts\.css"', 'href="../assets/css/fonts.css"', html)
    fonts_fixed = n

    analytics_added = False
    if ANALYTICS not in html:
        if "</body>" in html:
            html = html.replace("</body>", ANALYTICS + "\n</body>", 1)
        else:
            html = html.rstrip() + "\n" + ANALYTICS + "\n"
        analytics_added = True

    css = open(BOOK_CSS_SRC, encoding="utf-8").read()
    if ".figalt" not in css:
        css = css.rstrip("\n") + "\n" + FIGALT_CSS

    print(f"source images: {before_img}")
    print(f"degraded to figure descriptions: {degraded}")
    print(f"fonts.css link repointed: {'yes' if fonts_fixed else 'no (already correct)'}")
    print(f"analytics tag: {'added' if analytics_added else 'already present'}")
    print(f"book.css: {'adding .figalt rule' if '.figalt' not in open(BOOK_CSS_SRC, encoding='utf-8').read() else 'already has .figalt'}")

    if not apply_it:
        print("\nRun with --apply to write the output.")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(html)
    os.makedirs(os.path.dirname(BOOK_CSS_OUT), exist_ok=True)
    with open(BOOK_CSS_OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(css)
    print(f"\nwrote {os.path.relpath(OUT, ROOT)}")
    print(f"wrote {os.path.relpath(BOOK_CSS_OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(len(sys.argv) > 1 and sys.argv[1] == "--apply"))
