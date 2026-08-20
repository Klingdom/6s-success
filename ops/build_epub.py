#!/usr/bin/env python3
"""Build a valid EPUB 3 of "6S Success: Home Edition" from the finished chapter HTML.

Inputs  (all read-only):
    content/book/6s_success_chapter 1/chapter_01_final.html
    content/book/6S-Success-Chapter-N/chapter_NN_final.html   (N = 2..50)
    content/book/6S-Success-Front-Matter/FRONT_MATTER.md
    content/book/assets/book.css
    content/book/assets/fonts.css            (+ assets/fonts/*.woff2, optional)

Output:
    build/6S-Success-Home-Edition.epub

Reading order: title page, copyright, safety notice, how to use, Chapter 1..50,
table of contents.

What is stripped, and why:
    .chnav blocks          cross-file "previous / next chapter" website navigation
    span.artnote           illustrator direction ("Final book: full-bleed ...")
    [VISUAL]/[INFOGRAPHIC]/[ILLUSTRATION] spec blocks   production direction
    "DRAFT for review" blocks                            review-status notes
    <style> / <script>     replaced by one shared stylesheet
What is deliberately KEPT:
    aside.six-s-disclaimer  the safety notice, in full, on every chapter
    p.companion             the companion resources link
    inline <svg> figures    legal and useful in EPUB 3

Missing images are expected in a text-only mirror of the repository. When an
image file is present it is embedded and manifested; when it is absent the
figure degrades to its alt text, which in this book is a full description.

Run:  python ops/build_epub.py [--verbose]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import re
import sys
import uuid
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

REPO = Path(__file__).resolve().parents[1]
BOOK = REPO / "content" / "book"
ASSETS = BOOK / "assets"
FRONT_MATTER_MD = BOOK / "6S-Success-Front-Matter" / "FRONT_MATTER.md"
OUT_DIR = REPO / "build"
OUT_EPUB = OUT_DIR / "6S-Success-Home-Edition.epub"

BOOK_TITLE = "6S Success: Home Edition"
BOOK_ID_SEED = "https://6s-success.com/book/home-edition"
LANG = "en"

# House style: no em dash (U+2014), no en dash (U+2013), anywhere in the output.
FORBIDDEN_CHARS = {"—": "em dash", "–": "en dash"}

VOID_TAGS = ("img", "br", "hr", "input", "col", "source", "area", "base", "wbr", "embed")
SPEC_MARKERS = ("[VISUAL", "[INFOGRAPHIC", "[ILLUSTRATION")

# Named entities that are legal in HTML but not in XHTML without a DTD.
NAMED_ENTITY_RE = re.compile(r"&([a-zA-Z][a-zA-Z0-9]*);")
XML_SAFE_ENTITIES = {"amp", "lt", "gt", "quot", "apos"}


class BuildError(Exception):
    pass


# --------------------------------------------------------------------------
# discovery
# --------------------------------------------------------------------------
def find_chapters() -> list[tuple[int, Path]]:
    """Return [(number, html_path)] for every chapter, sorted by number.

    Chapter 1 lives in a differently named folder ("6s_success_chapter 1"), so
    the glob is deliberately loose. Do not rename that folder: other tooling in
    this repository globs on *hapter* too.
    """
    found: dict[int, Path] = {}
    for path in BOOK.glob("*hapter*/chapter_*_final.html"):
        m = re.search(r"chapter_(\d+)_final\.html$", path.name)
        if not m:
            continue
        num = int(m.group(1))
        if num in found:
            raise BuildError(f"two files claim chapter {num}: {found[num]} and {path}")
        found[num] = path
    if not found:
        raise BuildError(f"no chapter HTML found under {BOOK}")
    missing = [n for n in range(1, max(found) + 1) if n not in found]
    if missing:
        raise BuildError(f"chapter gap: {missing}")
    return sorted(found.items())


# --------------------------------------------------------------------------
# HTML -> XHTML helpers
# --------------------------------------------------------------------------
def strip_comments(s: str) -> str:
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def strip_element(s: str, tag: str, class_name: str) -> tuple[str, int]:
    """Remove <tag class="...class_name..."> ... </tag>, nesting-aware for one level."""
    pattern = re.compile(
        r"<%s\b[^>]*class=\"[^\"]*\b%s\b[^\"]*\"[^>]*>.*?</%s>" % (tag, re.escape(class_name), tag),
        re.S,
    )
    out, n = pattern.subn("", s)
    return out, n


def strip_draft_blocks(s: str) -> tuple[str, int]:
    """Remove any block element whose text opens with a DRAFT-for-review note."""
    count = 0
    for tag in ("blockquote", "aside", "div", "p", "section"):
        pattern = re.compile(
            r"<%s\b[^>]*>\s*(?:<[^>]+>\s*)*(?:STATUS:\s*)?DRAFT\b.{0,400}?</%s>" % (tag, tag),
            re.S | re.I,
        )
        s, n = pattern.subn("", s)
        count += n
    return s, count


def strip_spec_blocks(s: str) -> tuple[str, int]:
    """Remove [VISUAL] / [INFOGRAPHIC] / [ILLUSTRATION] production spec blocks."""
    count = 0
    marker = r"\[(?:VISUAL|INFOGRAPHIC|ILLUSTRATION)\b[^\]]*\]"
    # (a) whole block elements that open with a marker
    for tag in ("p", "div", "pre", "section", "aside"):
        pattern = re.compile(r"<%s\b[^>]*>\s*%s.*?</%s>" % (tag, marker, tag), re.S)
        s, n = pattern.subn("", s)
        count += n
    # (b) bare marker plus its Description/Purpose/Placement/Caption lines
    pattern = re.compile(
        marker + r"(?:\s*\n(?:Description|Purpose|Placement|Caption|Data or labels):[^\n]*)*",
    )
    s, n = pattern.subn("", s)
    return s, count + n


def close_void_tags(s: str) -> str:
    for tag in VOID_TAGS:
        s = re.sub(r"<(%s)(\b[^>]*?)\s*/?>" % tag, r"<\1\2/>", s)
    return s


def fix_named_entities(s: str) -> str:
    def repl(m: re.Match) -> str:
        name = m.group(1)
        if name in XML_SAFE_ENTITIES:
            return m.group(0)
        ch = html.unescape(m.group(0))
        if ch == m.group(0):  # unknown entity, leave the ampersand escaped
            return "&amp;" + name + ";"
        return "&#%d;" % ord(ch)

    return NAMED_ENTITY_RE.sub(repl, s)


def namespace_svg(s: str) -> str:
    """Declare the SVG namespaces, and mirror <use href> as xlink:href.

    The source markup is HTML, where the SVG namespace is implied. In XHTML it
    has to be declared. <use> uses the SVG 2 'href' form, so the SVG 1.1
    'xlink:href' is added alongside it for older rendering engines.
    """
    needs_xlink = "<use " in s

    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        if "xmlns=" in attrs:
            return m.group(0)
        ns = ' xmlns="http://www.w3.org/2000/svg"'
        if needs_xlink:
            ns += ' xmlns:xlink="http://www.w3.org/1999/xlink"'
        return "<svg" + ns + attrs + ">"

    s = re.sub(r"<svg(\s[^>]*)>", repl, s)
    if needs_xlink:
        s = re.sub(
            r'<use\b([^>]*?)href="([^"]+)"',
            lambda m: '<use%shref="%s" xlink:href="%s"' % (m.group(1), m.group(2), m.group(2)),
            s,
        )
    return s


def demote_headings(s: str) -> str:
    """The masthead h1 stays; nothing else needs changing. Kept as a hook."""
    return s


def handle_images(s: str, chapter_dir: Path, images_out: dict[str, Path], verbose: bool):
    """Embed images that exist; degrade the rest to their alt text.

    The text-only mirror of this repository intentionally omits binaries, so an
    absent file is NOT evidence of a broken book.
    """
    embedded = 0
    degraded = 0

    def repl(m: re.Match) -> str:
        nonlocal embedded, degraded
        tag = m.group(0)
        src_m = re.search(r'src="([^"]*)"', tag)
        alt_m = re.search(r'alt="([^"]*)"', tag)
        alt = alt_m.group(1) if alt_m else ""
        if src_m:
            candidate = (chapter_dir / src_m.group(1)).resolve()
            if candidate.is_file():
                name = f"{chapter_dir.name}-{candidate.name}".replace(" ", "-")
                images_out[name] = candidate
                embedded_tag = re.sub(r'src="[^"]*"', 'src="../images/%s"' % name, tag)
                embedded += 1
                return embedded_tag
        degraded += 1
        if not alt:
            return ""
        return (
            '<p class="figalt"><span class="figalt-lbl">Figure description</span> '
            + alt
            + "</p>"
        )

    s = re.sub(r"<img\b[^>]*/?>", repl, s)
    if verbose and degraded:
        print(f"      images: {embedded} embedded, {degraded} shown as descriptions")
    return s, embedded, degraded


def extract(pattern: str, text: str, what: str, path: Path) -> str:
    m = re.search(pattern, text, re.S)
    if not m:
        raise BuildError(f"could not find {what} in {path}")
    return m.group(1)


def text_of(xhtml_body: str) -> str:
    """Rough plain text of a fragment, with SVG contents removed."""
    s = re.sub(r"<svg\b.*?</svg>", " ", xhtml_body, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


# --------------------------------------------------------------------------
# chapter conversion
# --------------------------------------------------------------------------
class Chapter:
    def __init__(self, number: int, title: str, body: str, words: int, part: str):
        self.number = number
        self.title = title
        self.body = body
        self.words = words
        self.part = part
        self.file = f"ch{number:02d}.xhtml"
        self.item_id = f"ch{number:02d}"


def build_chapter(num: int, path: Path, images_out: dict, stats: dict, verbose: bool) -> Chapter:
    raw = path.read_text(encoding="utf-8")

    title = html.unescape(extract(r"<title>(.*?)</title>", raw, "<title>", path)).strip()
    title = title.replace(" · ", " · ")  # normalise the book's own separator

    main = extract(r"<main class=\"book\">(.*?)</main>", raw, "<main>", path)

    part_m = re.search(r"<p class=\"chno\">(.*?)</p>", raw, re.S)
    part = html.unescape(part_m.group(1)).strip() if part_m else "Chapters"

    # the companion link and the safety notice sit outside <main>; both are KEPT
    companion_m = re.search(r"<p class=\"companion\">.*?</p>", raw, re.S)
    disclaimer_m = re.search(r"<aside class=\"six-s-disclaimer\".*?</aside>", raw, re.S)
    if disclaimer_m is None:
        raise BuildError(f"{path.name}: safety notice (six-s-disclaimer) not found, refusing to build")

    body = strip_comments(main)
    body, n = strip_element(body, "nav", "chnav")
    stats["chnav"] += n
    body, n = re.subn(r"<span class=\"artnote\">.*?</span>", "", body, flags=re.S)
    stats["artnote"] += n
    body, n = strip_draft_blocks(body)
    stats["draft"] += n
    body, n = strip_spec_blocks(body)
    stats["spec"] += n
    body, n = re.subn(r"<style\b.*?</style>", "", body, flags=re.S)
    stats["style"] += n
    body, n = re.subn(r"<script\b.*?</script>", "", body, flags=re.S)
    stats["script"] += n

    tail = ""
    if companion_m:
        tail += "\n" + companion_m.group(0)
        stats["companion"] += 1
    tail += "\n" + disclaimer_m.group(0)
    stats["disclaimer"] += 1
    body = body + tail

    body, emb, deg = handle_images(body, path.parent, images_out, verbose)
    stats["img_embedded"] += emb
    stats["img_degraded"] += deg

    body = fix_named_entities(body)
    body = close_void_tags(body)
    body = namespace_svg(body)
    body = demote_headings(body)

    words = len(text_of(body).split())
    return Chapter(num, title, '<main class="book">' + body + "</main>", words, part)


# --------------------------------------------------------------------------
# front matter
# --------------------------------------------------------------------------
class Page:
    def __init__(self, item_id: str, file: str, title: str, body: str, words: int = 0):
        self.item_id = item_id
        self.file = file
        self.title = title
        self.body = body
        self.words = words


def md_inline(s: str) -> str:
    s = xml_escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def md_block(md: str) -> str:
    """Minimal markdown to XHTML for the front matter: paragraphs, bold, italics."""
    out: list[str] = []
    for para in re.split(r"\n\s*\n", md.strip()):
        para = para.strip()
        if not para or para == "---":
            continue
        if para.startswith("#"):
            level = len(para) - len(para.lstrip("#"))
            out.append(f"<h{level}>{md_inline(para.lstrip('#').strip())}</h{level}>")
            continue
        lines = [ln.strip() for ln in para.split("\n")]
        if all(ln.startswith("- ") for ln in lines):
            items = "".join("<li>%s</li>" % md_inline(ln[2:]) for ln in lines)
            out.append("<ul>%s</ul>" % items)
            continue
        # Short stacked lines (imprint, address, ISBNs) are laid out, not wrapped,
        # so keep their line breaks. Long lines are soft wrapping and get joined.
        if len(lines) > 1 and all(len(ln) < 70 for ln in lines):
            out.append("<p>%s</p>" % "<br/>".join(md_inline(ln) for ln in lines))
            continue
        out.append("<p>%s</p>" % md_inline(" ".join(lines)))
    return "\n".join(out)


def build_front_matter(stats: dict) -> list[Page]:
    md = FRONT_MATTER_MD.read_text(encoding="utf-8")

    # drop the review-status block that opens the file
    before = md
    md = re.sub(r"^> \*\*STATUS: DRAFT[^\n]*\n(?:> [^\n]*\n)*", "", md, flags=re.M)
    if md != before:
        stats["draft"] += 1

    sections: dict[str, str] = {}
    order: list[str] = []
    current = None
    buf: list[str] = []
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m:
            if current:
                sections[current] = "\n".join(buf)
            current = m.group(1).strip()
            order.append(current)
            buf = []
        elif current:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf)

    def need(key_start: str) -> tuple[str, str]:
        for key in order:
            if key.lower().startswith(key_start):
                return key, sections[key]
        raise BuildError(f"front matter section starting '{key_start}' not found")

    pages: list[Page] = []

    # 1. title page (hand-set so the bracketed placeholders stay legible)
    _, title_md = need("title page")
    lines = [ln.strip() for ln in title_md.split("\n") if ln.strip() and ln.strip() != "---"]
    parts = ['<section class="fm fm-title" epub:type="titlepage">']
    for i, ln in enumerate(lines):
        content = md_inline(re.sub(r"^\*\*(.*)\*\*$", r"\1", ln))
        content = re.sub(r"^\*(.*)\*$", r"\1", content)
        if i == 0:
            parts.append(f"<h1 class=\"fm-booktitle\">{content}</h1>")
        elif i == 1:
            parts.append(f"<p class=\"fm-edition\">{content}</p>")
        elif i == 2:
            parts.append(f"<p class=\"fm-sixs\">{content}</p>")
        else:
            parts.append(f"<p class=\"fm-byline\">{content}</p>")
    parts.append("</section>")
    pages.append(Page("fm-title", "front-title.xhtml", "Title Page", "\n".join(parts)))

    # 2. copyright
    _, copy_md = need("copyright")
    pages.append(
        Page(
            "fm-copyright",
            "front-copyright.xhtml",
            "Copyright",
            '<section class="fm fm-copyright" epub:type="copyright-page">'
            "<h1>Copyright</h1>\n" + md_block(copy_md) + "</section>",
        )
    )

    # 3. safety notice, kept whole and never weakened
    notice_key, notice_md = need("important notice")
    pages.append(
        Page(
            "fm-safety",
            "front-safety.xhtml",
            notice_key,
            '<section class="fm fm-safety" role="doc-preface" epub:type="preface">'
            f"<h1>{md_inline(notice_key)}</h1>\n" + md_block(notice_md) + "</section>",
        )
    )

    # 4. how to use this book
    how_key, how_md = need("how to use")
    pages.append(
        Page(
            "fm-howto",
            "front-howto.xhtml",
            how_key,
            '<section class="fm fm-howto" role="doc-preface" epub:type="preface">'
            f"<h1>{md_inline(how_key)}</h1>\n" + md_block(how_md) + "</section>",
        )
    )

    for p in pages:
        p.words = len(text_of(p.body).split())
    return pages


# --------------------------------------------------------------------------
# page / package templates
# --------------------------------------------------------------------------
XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}" xml:lang="{lang}">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="../styles/book.css"/>
</head>
<body epub:type="{body_type}">
{body}
</body>
</html>
"""

NAV_XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}" xml:lang="{lang}">
<head>
<meta charset="utf-8"/>
<title>Table of Contents</title>
<link rel="stylesheet" type="text/css" href="styles/book.css"/>
</head>
<body epub:type="frontmatter">
<section class="fm fm-toc">
<nav epub:type="toc" role="doc-toc" id="toc">
<h1>Contents</h1>
<ol class="toc">
{items}
</ol>
</nav>
<nav epub:type="landmarks" role="doc-toc" id="landmarks" hidden="hidden">
<h2>Landmarks</h2>
<ol>
<li><a epub:type="titlepage" href="text/front-title.xhtml">Title Page</a></li>
<li><a epub:type="toc" href="nav.xhtml">Table of Contents</a></li>
<li><a epub:type="bodymatter" href="text/ch01.xhtml">Start of Content</a></li>
</ol>
</nav>
</section>
</body>
</html>
"""

CONTAINER = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="EPUB/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

OPF = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="{lang}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="pub-id">urn:uuid:{uuid}</dc:identifier>
    <dc:title id="title">{title}</dc:title>
    <dc:creator id="creator">{creator}</dc:creator>
    <dc:language>{lang}</dc:language>
    <dc:publisher>{publisher}</dc:publisher>
    <dc:description>{description}</dc:description>
    <dc:subject>Home organization</dc:subject>
    <dc:subject>Housekeeping</dc:subject>
    <dc:subject>6S</dc:subject>
    <meta property="dcterms:modified">{modified}</meta>
    <meta property="title-type" refines="#title">main</meta>
    <meta property="role" refines="#creator" scheme="marc:relators">aut</meta>
{cover_meta}  </metadata>
  <manifest>
{manifest}
  </manifest>
  <spine toc="ncx">
{spine}
  </spine>
</package>
"""

NCX = """<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{uuid}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{title}</text></docTitle>
  <navMap>
{points}
  </navMap>
</ncx>
"""

EPUB_CSS_SUPPLEMENT = """
/* ---- EPUB adaptation ------------------------------------------------- */
/* Reading systems own the base type size, so do not pin it in pixels. */
body{font-size:1em; line-height:1.55;}
.book{max-width:none; padding:0 0 1.5em;}
.prose > p,.prose > .what,.prose > h2,.prose > h3,.prose > .pull,.prose > ul{max-width:none;}
img{max-width:100%; height:auto;}
svg{max-width:100%; height:auto;}
figure{margin:1.4em 0; page-break-inside:avoid; break-inside:avoid;}
h1,h2,h3{page-break-after:avoid; break-after:avoid;}
.callout,.idea,.defbox,.next,.zone,.checklist,.six-s-disclaimer{page-break-inside:avoid; break-inside:avoid;}
/* fixed pixel sizes do not scale with a reader's type setting */
figcaption{font-size:.85em; max-width:none;}
.keylist{columns:auto; column-gap:normal; font-size:.9em; max-width:none;}
/* the plate already draws the frame, so the description inside it does not */
.plate > .figalt{border:0; border-radius:0; background:transparent; padding:14px;}
/* a figure whose image file is not shipped degrades to its description */
.figalt{font-family:var(--sans); font-size:.86em; line-height:1.5; color:var(--soft);
        background:var(--panel); border:1px solid var(--rule); border-radius:10px;
        padding:12px 14px; margin:0;}
.figalt-lbl{display:block; font-size:.8em; letter-spacing:.16em; text-transform:uppercase;
            font-weight:600; color:var(--terra); margin-bottom:.35em;}
/* the companion resources line, normally set in each chapter file */
.companion{max-width:664px; margin:2.6em auto 0; padding-top:16px;
           border-top:1px solid var(--rule2); font-family:var(--sans);
           font-size:.85em; line-height:1.5; color:var(--soft);}
.companion b{color:var(--ink)}
.companion a{color:var(--terra)}
/* front matter and contents */
.fm{max-width:664px; margin:0 auto; padding:1.5em 0;}
.fm h1{font-family:var(--display); font-weight:600; font-size:1.7em; line-height:1.12;
       margin:.2em 0 .8em; color:var(--ink);}
.fm p{margin:0 0 1em;}
.fm-title{text-align:center; padding-top:3em;}
.fm-booktitle{font-size:2.6em; letter-spacing:.02em;}
.fm-edition{font-family:var(--serif); font-style:italic; font-size:1.3em; color:var(--soft);}
.fm-sixs{font-family:var(--sans); font-size:.8em; letter-spacing:.16em;
         text-transform:uppercase; color:var(--terra);}
.fm-byline{font-family:var(--sans); font-size:.95em; color:var(--soft); margin-top:2em;}
.fm-safety strong{color:var(--ink);}
ol.toc{list-style:none; padding:0; margin:0;}
ol.toc li{margin:.35em 0; font-family:var(--serif);}
ol.toc li.toc-part{margin-top:1.4em;}
ol.toc li.toc-part > span{display:block; font-family:var(--sans); font-size:.78em;
                          letter-spacing:.18em; text-transform:uppercase; color:var(--terra);
                          margin-bottom:.3em;}
ol.toc ol{list-style:none; padding:0 0 0 1em; margin:0;}
ol.toc a{color:var(--ink); text-decoration:none;}
"""


def build_css(verbose: bool) -> tuple[str, dict[str, Path]]:
    """One stylesheet for the whole book. Fonts embedded only if present."""
    base = (ASSETS / "book.css").read_text(encoding="utf-8")

    # .zone / .inspect are defined only inside the room-chapter <style> blocks
    room = BOOK / "6S-Success-Chapter-31" / "chapter_31_final.html"
    extra = ""
    if room.is_file():
        inline = re.findall(r"<style>(.*?)</style>", room.read_text(encoding="utf-8"), re.S)
        if inline:
            base_selectors = {
                s.strip()
                for m in re.finditer(r"([^{}]+)\{", re.sub(r"/\*.*?\*/", "", base, flags=re.S))
                for s in m.group(1).split(",")
            }
            rules = re.finditer(
                r"([^{}]+)\{([^{}]*)\}", re.sub(r"/\*.*?\*/", "", inline[0], flags=re.S)
            )
            picked = [
                f"{sel.strip()}{{{body.strip()}}}"
                for sel, body in ((m.group(1), m.group(2)) for m in rules)
                if sel.strip() not in base_selectors and sel.strip().startswith(".zone")
            ]
            if picked:
                extra = "\n/* ---- room-chapter zone blocks ---- */\n" + "\n".join(picked) + "\n"

    fonts: dict[str, Path] = {}
    font_css = ""
    fonts_css_path = ASSETS / "fonts.css"
    if fonts_css_path.is_file():
        declared = re.findall(r"url\('([^']+)'\)", fonts_css_path.read_text(encoding="utf-8"))
        present = {rel: (ASSETS / rel) for rel in declared if (ASSETS / rel).is_file()}
        if present and len(present) == len(set(declared)):
            font_css = fonts_css_path.read_text(encoding="utf-8")
            for rel, src in present.items():
                fonts[Path(rel).name] = src
            font_css = re.sub(r"url\('fonts/([^']+)'\)", r"url('../fonts/\1')", font_css)
            if verbose:
                print(f"  fonts: embedding {len(fonts)} woff2 files")
        elif verbose:
            print(
                f"  fonts: {len(present)}/{len(set(declared))} woff2 files present, "
                "degrading to the system font stack"
            )

    css = font_css + "\n" + base + extra + EPUB_CSS_SUPPLEMENT
    return css, fonts


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------
def media_type(name: str) -> str:
    ext = name.rsplit(".", 1)[-1].lower()
    return {
        "xhtml": "application/xhtml+xml",
        "css": "text/css",
        "ncx": "application/x-dtbncx+xml",
        "woff2": "font/woff2",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "webp": "image/webp",
    }.get(ext, "application/octet-stream")


def build(verbose: bool = False) -> dict:
    stats = dict.fromkeys(
        (
            "chnav",
            "artnote",
            "draft",
            "spec",
            "style",
            "script",
            "companion",
            "disclaimer",
            "img_embedded",
            "img_degraded",
        ),
        0,
    )

    print(f"Repository: {REPO}")
    front = build_front_matter(stats)
    print(f"  front matter: {len(front)} pages")

    images: dict[str, Path] = {}
    chapters: list[Chapter] = []
    for num, path in find_chapters():
        chapters.append(build_chapter(num, path, images, stats, verbose))
    print(f"  chapters:     {len(chapters)} ({chapters[0].number} to {chapters[-1].number})")

    css, fonts = build_css(verbose)

    # ---- files -----------------------------------------------------------
    files: dict[str, bytes] = {}
    for page in front:
        files["EPUB/text/" + page.file] = XHTML.format(
            lang=LANG, title=xml_escape(page.title), body_type="frontmatter", body=page.body
        ).encode("utf-8")
    for ch in chapters:
        files["EPUB/text/" + ch.file] = XHTML.format(
            lang=LANG, title=xml_escape(ch.title), body_type="bodymatter", body=ch.body
        ).encode("utf-8")
    files["EPUB/styles/book.css"] = css.encode("utf-8")
    # Cover page and image. Retailers reject an ebook without a cover, and readers
    # show it as the book's face in their library.
    _cover_src = OUT_DIR / "cover.jpg"
    if _cover_src.exists():
        files["EPUB/images/cover.jpg"] = _cover_src.read_bytes()
        files["EPUB/text/cover.xhtml"] = XHTML.format(
            lang=LANG, title="Cover", body_type="cover",
            body='<section epub:type="cover" class="cover">'
                 '<img src="../images/cover.jpg" alt="6S Success: Home Edition. '
                 'A calm home, built one S at a time. Fifty chapters, twenty rooms, '
                 'one hundred and fourteen micro zones."/></section>',
        ).encode("utf-8")
    for name, src in sorted(images.items()):
        files["EPUB/images/" + name] = src.read_bytes()
    for name, src in sorted(fonts.items()):
        files["EPUB/fonts/" + name] = src.read_bytes()

    # ---- navigation ------------------------------------------------------
    # The nav groups the chapters under the book's own nine parts. Each part is a
    # <span> heading with a nested <ol>, which is the EPUB 3 nav content model.
    nav_items: list[str] = []
    for page in front:
        nav_items.append(
            f'<li><a href="text/{page.file}">{xml_escape(page.title)}</a></li>'
        )
    current_part = None
    for ch in chapters:
        if ch.part != current_part:
            if current_part is not None:
                nav_items.append("</ol></li>")
            nav_items.append(
                f'<li class="toc-part"><span>{xml_escape(ch.part)}</span>\n<ol>'
            )
            current_part = ch.part
        nav_items.append(f'<li><a href="text/{ch.file}">{xml_escape(ch.title)}</a></li>')
    if current_part is not None:
        nav_items.append("</ol></li>")
    files["EPUB/nav.xhtml"] = NAV_XHTML.format(lang=LANG, items="\n".join(nav_items)).encode("utf-8")

    book_uuid = uuid.uuid5(uuid.NAMESPACE_URL, BOOK_ID_SEED)
    newest = max(p.stat().st_mtime for p in [FRONT_MATTER_MD] + [c for _, c in find_chapters()])
    modified = _dt.datetime.fromtimestamp(newest, _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    points = []
    for i, item in enumerate([*front, *chapters], start=1):
        points.append(
            f'    <navPoint id="np{i}" playOrder="{i}">'
            f"<navLabel><text>{xml_escape(item.title)}</text></navLabel>"
            f'<content src="text/{item.file}"/></navPoint>'
        )
    files["EPUB/toc.ncx"] = NCX.format(
        uuid=book_uuid, title=xml_escape(BOOK_TITLE), points="\n".join(points)
    ).encode("utf-8")

    # ---- package ---------------------------------------------------------
    manifest = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '    <item id="css" href="styles/book.css" media-type="text/css"/>',
    ]
    # Cover. Retailers reject an ebook without one, and readers show it in the
    # library. Generated by ops/build_cover.py from the book's own design system;
    # if it has not been generated yet the book still builds, without a cover.
    cover_src = OUT_DIR / "cover.jpg"
    has_cover = cover_src.exists()
    if has_cover:
        manifest.append('    <item id="cover-image" href="images/cover.jpg" '
                        'media-type="image/jpeg" properties="cover-image"/>')
        manifest.append('    <item id="cover" href="text/cover.xhtml" '
                        'media-type="application/xhtml+xml"/>')
    spine = []
    if has_cover:
        spine.append('    <itemref idref="cover" linear="yes"/>')
    for item in [*front, *chapters]:
        props = ' properties="svg"' if "<svg" in item.body else ""
        manifest.append(
            f'    <item id="{item.item_id}" href="text/{item.file}" '
            f'media-type="application/xhtml+xml"{props}/>'
        )
        spine.append(f'    <itemref idref="{item.item_id}" linear="yes"/>')
    for name in sorted(images):
        manifest.append(
            f'    <item id="img-{re.sub(r"[^A-Za-z0-9]", "-", name)}" href="images/{name}" '
            f'media-type="{media_type(name)}"/>'
        )
    for name in sorted(fonts):
        manifest.append(
            f'    <item id="font-{re.sub(r"[^A-Za-z0-9]", "-", name)}" href="fonts/{name}" '
            f'media-type="{media_type(name)}"/>'
        )
    spine.append('    <itemref idref="nav" linear="yes"/>')

    creator = "[AUTHOR NAME]"  # placeholder, deliberately unfilled pending the owner
    publisher = "[IMPRINT / PUBLISHER NAME]"
    description = (
        "Sort, Straighten, Shine, Safety, Standardize, Sustain. A plain-English method for "
        "making a home easier to live in, followed by twenty room playbooks."
    )
    files["EPUB/content.opf"] = OPF.format(
        lang=LANG,
        uuid=book_uuid,
        title=xml_escape(BOOK_TITLE),
        creator=xml_escape(creator),
        publisher=xml_escape(publisher),
        description=xml_escape(description),
        modified=modified,
        # EPUB 3 marks the cover with properties="cover-image" on the manifest
        # item, but KDP, Kobo and older readers still look for this EPUB 2 meta.
        # Emitting both costs one line and avoids a retailer rejecting the file.
        cover_meta=('    <meta name="cover" content="cover-image"/>\n' if has_cover else ""),
        manifest="\n".join(manifest),
        spine="\n".join(spine),
    ).encode("utf-8")
    files["META-INF/container.xml"] = CONTAINER.encode("utf-8")

    # ---- write the zip ---------------------------------------------------
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_EPUB.exists():
        OUT_EPUB.unlink()
    ts = (2026, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(OUT_EPUB, "w") as zf:
        info = zipfile.ZipInfo("mimetype", date_time=ts)
        info.compress_type = zipfile.ZIP_STORED
        info.external_attr = 0o644 << 16
        zf.writestr(info, b"application/epub+zip")
        for name in ["META-INF/container.xml", "EPUB/content.opf", "EPUB/nav.xhtml"] + sorted(
            k for k in files if k not in ("META-INF/container.xml", "EPUB/content.opf", "EPUB/nav.xhtml")
        ):
            info = zipfile.ZipInfo(name, date_time=ts)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, files[name])

    return {
        "front": front,
        "chapters": chapters,
        "stats": stats,
        "files": files,
        "images": images,
        "fonts": fonts,
        "uuid": str(book_uuid),
    }


# --------------------------------------------------------------------------
# verification (epubcheck is not available here, so these run instead)
# --------------------------------------------------------------------------
def verify(result: dict) -> int:
    import xml.etree.ElementTree as ET

    failures: list[str] = []
    checks: list[str] = []

    def ok(name: str, condition: bool, detail: str = "") -> None:
        checks.append(name)
        if condition:
            print(f"  PASS  {name}{(' :: ' + detail) if detail else ''}")
        else:
            print(f"  FAIL  {name}{(' :: ' + detail) if detail else ''}")
            failures.append(name)

    print("\nVerification (epubcheck and java are not installed on this machine;")
    print("the following structural checks were written and run instead)\n")

    ok("epub file exists", OUT_EPUB.is_file(), str(OUT_EPUB))
    with zipfile.ZipFile(OUT_EPUB) as zf:
        ok("zip is readable and not corrupt", zf.testzip() is None)
        names = zf.namelist()
        first = zf.infolist()[0]
        ok("first zip entry is 'mimetype'", first.filename == "mimetype", first.filename)
        ok("mimetype entry is stored, not deflated", first.compress_type == zipfile.ZIP_STORED)
        ok("mimetype has no extra field", len(first.extra) == 0, f"{len(first.extra)} bytes")
        mime = zf.read("mimetype")
        ok(
            "mimetype content is exactly 'application/epub+zip'",
            mime == b"application/epub+zip",
            repr(mime),
        )

        # container -> opf
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
        rootfile = container.find(".//c:rootfile", ns).get("full-path")
        ok("container.xml points at an existing package document", rootfile in names, rootfile)

        opf_xml = zf.read(rootfile)
        opf = ET.fromstring(opf_xml)
        opfns = {"o": "http://www.idpf.org/2007/opf", "dc": "http://purl.org/dc/elements/1.1/"}
        manifest = {
            it.get("id"): it.get("href") for it in opf.findall("./o:manifest/o:item", opfns)
        }
        spine = [ir.get("idref") for ir in opf.findall("./o:spine/o:itemref", opfns)]

        base = rootfile.rsplit("/", 1)[0]
        missing = [h for h in manifest.values() if f"{base}/{h}" not in names]
        ok("every manifest item exists in the zip", not missing, str(missing[:5]))

        in_manifest = {f"{base}/{h}" for h in manifest.values()} | {"mimetype", rootfile,
                                                                   "META-INF/container.xml"}
        orphans = [n for n in names if n not in in_manifest]
        ok("no file in the zip is missing from the manifest", not orphans, str(orphans[:5]))

        ok("every spine itemref resolves to a manifest item", all(i in manifest for i in spine))
        ok("exactly one nav document is declared",
           sum(1 for it in opf.findall("./o:manifest/o:item", opfns)
               if "nav" in (it.get("properties") or "").split()) == 1)
        ok("package declares dcterms:modified",
           any(m.get("property") == "dcterms:modified" for m in opf.findall("./o:metadata/o:meta", opfns)))
        ok("package has a unique identifier",
           opf.find("./o:metadata/dc:identifier", opfns) is not None)

        # spine order
        front = result["front"]
        chapters = result["chapters"]
        # The cover, when one has been generated, is the first spine item. It is
        # deliberately absent from the nav: readers reach it from the library, not
        # from the table of contents.
        expected = (["cover"] if "cover" in spine else []) \
            + [p.item_id for p in front] + [c.item_id for c in chapters] + ["nav"]
        ok(
            "spine order is cover, front matter, chapters 1 to 50, then the contents",
            spine == expected,
            f"{len(spine)} items; first={spine[:2]}, last={spine[-2:]}",
        )
        ok("all 50 chapters are in the spine", len([s for s in spine if s.startswith("ch")]) == 50)
        ok(
            "chapter spine ids are strictly ascending",
            [s for s in spine if re.fullmatch(r"ch\d\d", s)]
            == [f"ch{n:02d}" for n in range(1, 51)],
        )

        # every xhtml parses as XML, and the nav titles match the chapters
        xhtml_names = [n for n in names if n.endswith(".xhtml")]
        bad_xml = []
        for n in xhtml_names:
            try:
                ET.fromstring(zf.read(n))
            except ET.ParseError as exc:
                bad_xml.append(f"{n}: {exc}")
        ok(f"all {len(xhtml_names)} XHTML documents are well formed XML", not bad_xml, str(bad_xml[:3]))

        nav = zf.read(f"{base}/nav.xhtml").decode("utf-8")
        nav_links = re.findall(r'<li[^>]*><a href="([^"]+)">([^<]+)</a></li>', nav)
        ok(
            "nav lists every front matter page and every chapter",
            len(nav_links) == len(front) + len(chapters),
            f"{len(nav_links)} links",
        )
        parts = re.findall(r'<li class="toc-part"><span>([^<]+)</span>', nav)
        ok("nav groups the chapters under the book's nine parts", len(parts) == 9,
           f"{len(parts)} parts: {parts[0] if parts else ''} ... {parts[-1] if parts else ''}")
        bad_targets = [h for h, _ in nav_links if f"{base}/{h}" not in names]
        ok("every nav link resolves to a file in the epub", not bad_targets, str(bad_targets[:3]))
        expected_titles = [p.title for p in front] + [c.title for c in chapters]
        actual_titles = [html.unescape(t) for _, t in nav_links]
        ok("nav titles match the chapter titles exactly", actual_titles == expected_titles,
           str([(a, b) for a, b in zip(actual_titles, expected_titles) if a != b][:3]))

        # house style and stripped content
        em = en = 0
        text_bytes = 0
        leftovers = {"chnav": 0, "artnote": 0, "DRAFT for review": 0, "spec block": 0}
        for n in xhtml_names + [f"{base}/styles/book.css", rootfile, f"{base}/toc.ncx"]:
            s = zf.read(n).decode("utf-8")
            text_bytes += len(s)
            em += s.count("—")
            en += s.count("–")
            leftovers["chnav"] += len(re.findall(r'class="chnav', s))
            leftovers["artnote"] += len(re.findall(r'class="artnote', s))
            leftovers["DRAFT for review"] += len(re.findall(r"DRAFT for review", s, re.I))
            leftovers["spec block"] += sum(s.count(m) for m in SPEC_MARKERS)
        ok(f"zero em dashes (U+2014) in the output", em == 0, f"count={em}")
        ok(f"zero en dashes (U+2013) in the output", en == 0, f"count={en}")
        for key, count in leftovers.items():
            ok(f"no '{key}' left in the output", count == 0, f"count={count}")

        # safety content must survive
        disclaimers = sum(
            zf.read(f"{base}/text/{c.file}").decode("utf-8").count("six-s-disclaimer")
            for c in chapters
        )
        ok("safety notice present on all 50 chapters", disclaimers == 50, f"count={disclaimers}")
        companions = sum(
            zf.read(f"{base}/text/{c.file}").decode("utf-8").count('class="companion"')
            for c in chapters
        )
        ok("companion resources link present on all 50 chapters", companions == 50,
           f"count={companions}")
        safety_page = zf.read(f"{base}/text/front-safety.xhtml").decode("utf-8")
        ok("front matter safety notice page is present and substantial",
           "Never mix cleaning products" in safety_page and len(safety_page) > 3000,
           f"{len(safety_page)} bytes")
        # The copyright page must never look finished while questions are still
        # unanswered, because a blank that has quietly vanished reads as a
        # decision somebody made. This used to assert "[YEAR]" was present, but
        # YEAR turned out to be answerable without Phil, so the sentinel went
        # away while ISBN, author and imprint were all still open. The real
        # condition is the one below: unanswered means visibly bracketed.
        copyright_page = zf.read(f"{base}/text/front-copyright.xhtml").decode("utf-8")
        brackets = len(re.findall(r"\[[A-Z][A-Za-z0-9 ,._/-]+\]", copyright_page))
        answers_path = REPO / "ops" / "front-matter.json"
        unanswered = 0
        if answers_path.exists():
            answers = json.loads(answers_path.read_text(encoding="utf-8"))
            unanswered = sum(1 for k, v in answers.items()
                             if not k.startswith("_") and not v)
        if unanswered:
            ok("unanswered front matter stays visibly bracketed", brackets > 0,
               f"{unanswered} unanswered, {brackets} bracketed on the page")
        else:
            ok("front matter fully resolved, no blanks left", brackets == 0,
               f"{brackets} bracketed on the page")

        # terminology
        sio = sum(zf.read(n).decode("utf-8").count("Set in Order") for n in xhtml_names)
        print(f"  NOTE  'Set in Order' appears {sio} time(s): author text in Chapter 2 and the "
              "How To Use page that names the term other books use, then rejects it.")

        # svg preserved
        svg_files = [n for n in xhtml_names if "<svg" in zf.read(n).decode("utf-8")]
        ok("inline SVG figures kept", len(svg_files) > 0, f"{len(svg_files)} documents contain SVG")

        words = sum(c.words for c in chapters) + sum(p.words for p in front)
        size = OUT_EPUB.stat().st_size

    print("\nFigures")
    print(f"  chapters:            {len(result['chapters'])}")
    print(f"  front matter pages:  {len(result['front'])}")
    print(f"  spine items:         {len(spine)}")
    print(f"  words (front + chapters, SVG text excluded): {words:,}")
    print(f"  em dashes: {em}    en dashes: {en}")
    print(f"  images embedded: {result['stats']['img_embedded']}, "
          f"shown as descriptions: {result['stats']['img_degraded']}")
    print(f"  fonts embedded: {len(result['fonts'])}")
    print(f"  file size: {size:,} bytes ({size/1024/1024:.2f} MB)")
    print("\nStripped")
    for key in ("chnav", "artnote", "draft", "spec", "style", "script"):
        print(f"  {key}: {result['stats'][key]}")

    print(f"\n{len(checks) - len(failures)}/{len(checks)} checks passed")
    if failures:
        print("FAILED: " + ", ".join(failures))
        return 1
    print(f"OK  {OUT_EPUB}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--no-verify", action="store_true")
    args = ap.parse_args()
    try:
        result = build(verbose=args.verbose)
    except BuildError as exc:
        print(f"BUILD ERROR: {exc}", file=sys.stderr)
        return 2
    if args.no_verify:
        return 0
    return verify(result)


if __name__ == "__main__":
    sys.exit(main())
