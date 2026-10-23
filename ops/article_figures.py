#!/usr/bin/env python3
"""
One figure from the book in each article, chosen for what the article argues.

WHAT WAS WRONG
--------------
Thirty-five articles of about 1,900 words each, on the surface built for
search and answer engines, with nothing to look at: zero content images
(PLAN-VISUAL-STRATEGY.md, "The surface this plan did not have"). Meanwhile
the book holds over two hundred captioned figures for chapters 1 to 30, each
drawn to make exactly one of the arguments these articles make.

WHAT THIS DOES
--------------
FIGURES maps an article to the one book figure that makes its point: "Why is
my house always messy?" gets Figure 28-02, the symptom and the cause; "More
storage will not fix a messy room" gets Buy Storage Last. An article with no
close match gets nothing; a loosely related picture is worse than none.

* --import (only where the book's master folder exists, i.e. Phil's machine)
  copies each chosen figure into site/assets/img/book/ at 1200 wide, makes
  the 420 and 840 jpg and webp variants, and records its size, alt text and
  caption, both taken from the book's own final.html, in
  ops/article-figures.json. Run ops/build_avif.py --encode afterwards.
* apply(page, html) puts the figure into an article before its second
  section heading, between markers, so it is idempotent and replaceable.
  Generators call it on their own output; --wire does the hand-written ones.

The caption names the chapter it comes from. Nothing here is a photograph of
a real home, and the figures do not pretend to be.

Run:  python ops/article_figures.py --import   # copy figures, write manifest
      python ops/article_figures.py --wire     # put them into the articles
"""
import glob
import html as htmllib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
IMG = os.path.join(SITE, "assets", "img")
OUT = os.path.join(IMG, "book")
MANIFEST = os.path.join(ROOT, "ops", "article-figures.json")
MASTER = os.path.join(
    os.path.expanduser("~"), "Desktop", "Process Kaizen", "Process Kaizen",
    "Work Folder", "Nova Consulting", "06 - Lean Six Sigma Initiative",
    "07 - 6S Materials", "6S Environment", "Master",
    "6S Success Home Edition")

# article page -> (chapter, figure file in that chapter's folder)
FIGURES = {
    "articles/decluttering-vs-organizing": (12, "ch12-image0b.jpg"),
    "articles/everyday-things-out-of-reach": (13, "ch13-image2.jpg"),
    "articles/everything-needs-an-assigned-home": (12, "ch12-image1.jpg"),
    "articles/family-wont-put-things-back": (12, "ch12-image3.jpg"),
    "articles/how-long-does-it-take-to-organise-a-room": (19, "ch19-image10.jpg"),
    "articles/how-long-to-keep-a-maybe": (10, "ch10-image8.jpg"),
    "articles/how-to-organize-a-basement": (15, "ch15-image6.jpg"),
    "articles/how-to-organize-a-junk-drawer": (2, "ch2-image2.jpg"),
    "articles/how-to-organize-an-attic": (13, "ch13-image4.jpg"),
    "articles/is-that-really-a-backup": (9, "ch9-image7.jpg"),
    "articles/more-storage-wont-fix-clutter": (8, "ch8-image13a.jpg"),
    "articles/sentimental-items-without-guilt": (10, "ch10-image3a.jpg"),
    "articles/tidy-is-not-the-same-as-safe": (21, "ch21-image03.jpg"),
    "articles/what-is-6s": (2, "ch2-image6.jpg"),
    "articles/what-is-a-micro-zone": (15, "ch15-image7.jpg"),
    "articles/where-to-start-decluttering": (4, "ch4_image7.jpg"),
    "articles/why-5s-decays-after-six-months": (26, "ch26-image01.jpg"),
    "articles/why-a-shared-zone-never-stays-reset": (24, "ch24-image07.jpg"),
    "articles/why-everyone-in-your-house-disagrees-about-clean":
        (25, "ch25-image01.jpg"),
    "articles/why-is-my-house-always-messy": (28, "ch28-image02.jpg"),
    "articles/why-it-lives-in-one-room-but-gets-used-in-another":
        (13, "ch13-image6.jpg"),
    "articles/why-mail-piles-up-by-the-door": (8, "ch8-image08.jpg"),
    "articles/why-the-medicine-cabinet-never-gets-cleared-out":
        (22, "ch22-image06.jpg"),
    "articles/why-the-same-spot-never-gets-clean": (18, "ch18-image04.jpg"),
    "articles/why-you-always-lose-your-keys": (12, "ch12-image4.jpg"),
    "articles/why-you-cant-find-the-right-charger": (12, "ch12-image2.jpg"),
    "articles/why-you-cant-see-your-own-clutter": (6, "ch6-image3.jpg"),
    "articles/why-you-have-to-dig-for-what-you-need": (3, "ch3-image6.jpg"),
    "articles/why-you-keep-buying-things-you-already-own":
        (14, "ch14-image03.jpg"),
    "articles/why-you-keep-running-out-of-things": (14, "ch14-image05.jpg"),
    "articles/why-you-never-finish-a-zone": (19, "ch19-image05.jpg"),
    "articles/why-your-house-gets-messy-again": (19, "ch19-image09.jpg"),
    "articles/zone-too-small-for-what-it-holds": (7, "ch7-image2.jpg"),
}
# Written by a generator, which calls apply() on its own output.
GENERATED = {"articles/what-is-6s",
             "articles/how-long-does-it-take-to-organise-a-room",
             "articles/why-is-my-house-always-messy"}
START, END = "<!-- article-figure:start -->", "<!-- article-figure:end -->"


def stem(fname):
    return "book-" + os.path.splitext(fname)[0].replace("_", "-")


def sentences(text, n, limit):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    out = ""
    for p in parts[:n]:
        if out and len(out) + len(p) + 1 > limit:
            break
        out = (out + " " + p).strip()
    return out


def book_meta(chapter, fname):
    """(alt, caption) for one figure, from the chapter's own final.html."""
    f = glob.glob(os.path.join(MASTER, "6S-Success-Chapter-%d" % chapter,
                               "chapter_*_final.html"))
    if not f:
        raise RuntimeError("no final.html for chapter %d" % chapter)
    src = io.open(f[0], encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"<figure[^>]*>(.*?)</figure>", src, re.S):
        b = m.group(1)
        if 'src="%s"' % fname not in b:
            continue
        alt = re.search(r'alt="([^"]*)"', b)
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", b, re.S)
        alt = htmllib.unescape(alt.group(1)) if alt else ""
        alt = re.sub(r"^Figure \d+-\d+,\s*", "", alt)
        cap = htmllib.unescape(re.sub(r"<[^>]+>", " ", cap.group(1))) if cap else ""
        cap = re.sub(r"\s+", " ", cap).strip()
        return sentences(alt, 2, 240), sentences(cap, 2, 260)
    raise RuntimeError("chapter %d has no figure %s" % (chapter, fname))


def do_import():
    from PIL import Image
    if not os.path.isdir(MASTER):
        print("  the book's master folder is not on this machine; nothing "
              "imported, manifest unchanged")
        return 1
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(IMG, "w"), exist_ok=True)
    manifest, failed = {}, []
    for page, (ch, fname) in sorted(FIGURES.items()):
        try:
            path = os.path.join(MASTER, "6S-Success-Chapter-%d" % ch, fname)
            im = Image.open(path).convert("RGB")
            if im.width > 1200:
                im = im.resize((1200, round(im.height * 1200 / im.width)),
                               Image.LANCZOS)
            s = stem(fname)
            im.save(os.path.join(OUT, s[5:] + ".jpg"), "JPEG", quality=84,
                    optimize=True, progressive=True)
            for w in (420, 840):
                v = im.resize((w, round(im.height * w / im.width)),
                              Image.LANCZOS)
                base = os.path.join(IMG, "w", "%s-%d" % (s, w))
                v.save(base + ".jpg", "JPEG", quality=82, optimize=True,
                       progressive=True)
                v.save(base + ".webp", "WEBP", quality=80, method=6)
            alt, cap = book_meta(ch, fname)
            if not alt or not cap:
                raise RuntimeError("figure has no alt or no caption in the book")
            manifest[page] = {"chapter": ch, "file": "book/" + s[5:] + ".jpg",
                              "stem": s, "width": im.width,
                              "height": im.height, "alt": alt,
                              "caption": cap}
        except Exception as exc:          # reported, never silently skipped
            failed.append((page, str(exc)))
    io.open(MANIFEST, "w", encoding="utf-8", newline="\n").write(
        json.dumps(manifest, indent=1, sort_keys=True, ensure_ascii=False)
        + "\n")
    print("  imported %d figure(s), failed %d" % (len(manifest), len(failed)))
    for p, why in failed:
        print("  FAILED %s: %s" % (p, why))
    return 1 if failed else 0


def load_manifest():
    try:
        return json.load(io.open(MANIFEST, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def figure_html(e):
    esc = lambda s: htmllib.escape(s, quote=True)
    w = "../assets/img/w/" + e["stem"]
    srcset = lambda ext: ", ".join("%s-%d.%s %dw" % (w, n, ext, n)
                                   for n in (420, 840))
    sizes = "(max-width: 820px) 100vw, 760px"
    return (START + "\n"
            '<figure class="article-figure" style="margin:30px 0 34px">'
            "<picture>"
            '<source type="image/avif" srcset="%s" sizes="%s">'
            '<source type="image/webp" srcset="%s" sizes="%s">'
            '<img src="../assets/img/%s" width="%d" height="%d" alt="%s" '
            'loading="lazy" decoding="async" style="display:block;width:100%%;'
            'height:auto;border-radius:12px;border:1px solid var(--line)">'
            "</picture>"
            '<figcaption style="font-family:var(--sans);font-size:14px;'
            'line-height:1.55;color:var(--soft);margin-top:10px">%s '
            'From Chapter %d of <a href="../book.html">6S Success: Home '
            "Edition</a>.</figcaption></figure>\n" + END) % (
                srcset("avif"), sizes, srcset("webp"), sizes, e["file"],
                e["width"], e["height"], esc(e["alt"]), esc(e["caption"]),
                e["chapter"])


_BLOCK = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)


def apply(page, src):
    """Put the page's figure before its second section heading. Idempotent."""
    e = load_manifest().get(page)
    out = _BLOCK.sub("", src)
    if not e or not os.path.exists(os.path.join(IMG, e["file"])):
        return out
    m = re.search(r"<main[^>]*>", out)
    if not m:
        return out
    heads = [h.start() for h in re.finditer(r"<h2[\s>]", out[m.end():])]
    if not heads:
        return out
    at = m.end() + (heads[1] if len(heads) > 1 else heads[0])
    return out[:at] + figure_html(e) + "\n" + out[at:]


def hand_written():
    return [p for p in load_manifest() if p not in GENERATED]


def wire():
    n = 0
    for page in hand_written():
        path = os.path.join(SITE, page + ".html")
        if not os.path.exists(path):
            continue
        src = io.open(path, encoding="utf-8", newline="").read()
        new = apply(page, src)
        if new != src:
            io.open(path, "w", encoding="utf-8", newline="").write(new)
            n += 1
    print("  wired %d hand-written article(s)" % n)
    return 0


if __name__ == "__main__":
    if "--import" in sys.argv:
        sys.exit(do_import())
    if "--wire" in sys.argv:
        sys.exit(wire())
    print(__doc__)
