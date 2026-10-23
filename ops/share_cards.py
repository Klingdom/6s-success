#!/usr/bin/env python3
"""
Link preview cards: one 1200x630 og:image per page, made from the page itself.

WHAT WAS WRONG
--------------
58 pages, every room page and every article among them, shared one og:image:
room-map.jpg, a book figure with "FIGURE 15-03" printed in its corner and a
headline of its own ("The Home as Activity Zones"). Eighteen more used four
other book figures the same way, the home page included. A link preview is the
first picture a stranger sees of this site, and LinkedIn, the one channel that
has ever sent visitors here (GOALS.md), shows nothing else. Every share looked
like every other share, and none said what was behind the link.

WHAT THIS MAKES
---------------
site/assets/img/share/<page>.jpg at 1200x630, the size LinkedIn, Facebook,
Bluesky and X all crop to, plus ops/share-cards.json, the manifest the page
generators read. Each card carries the page's own h1, so it cannot promise
anything the page does not say, and a picture only where one genuinely
belongs to the page: a room's own plan or book figure on its room page, a
product's own pages on its product page, the right room on the five articles
that are about one. Everything else is typographic on purpose; a loosely
related picture is worse than none.

HOW PAGES USE IT
----------------
Generators call card_url(page) and fall back to their old image when it
returns None, so a page without a card is unchanged and a deleted card can
never leave a broken preview. Hand-written pages are wired in place by
ops/wire_share_cards.py.

Run:  python ops/share_cards.py            # make missing cards, write manifest
      python ops/share_cards.py --force    # remake every card
      python ops/share_cards.py --manifest # manifest only, no browser
      python ops/share_cards.py --wire     # point hand-written articles at
                                           # their cards (run after drawing)
"""
import glob
import html as htmllib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
IMG = os.path.join(SITE, "assets", "img")
OUT_DIR = os.path.join(IMG, "share")
MANIFEST = os.path.join(ROOT, "ops", "share-cards.json")
BASE = "https://6s-success.com"
CW, CH = 1200, 630

# Top-level and index pages that get a card. Deck pages are left alone: their
# og:image is card art, guarded by gate_deck_og_image_honest.
TOP = ["index", "method", "resources", "book", "bundle", "shop", "standards",
       "corporate", "contact", "how-we-make-money", "accessibility",
       "affiliate-disclosure", "disclaimer", "privacy", "terms", "invest",
       "zones/index", "articles/index", "deck-gallery-mudroom"]

# page -> (picture under assets/img, what it shows, for the alt text).
# A picture is listed only where it really belongs to the page.
PRODUCT = {
    "book": ("product-ebook.jpg", "Chapter One's opening pages from the book"),
    "bundle": ("product-bundle.jpg",
               "pages from the book, the Manual and a Print Pack card"),
    "shop": ("product-bundle.jpg",
             "pages from the book, the Manual and a Print Pack card"),
    "standards": ("product-standards.jpg", "two real room standard sheets"),
    "corporate": ("product-corporate.jpg", "the real zone scoring sheet"),
    "articles/what-a-5s-engagement-costs": (
        "product-corporate.jpg", "the real zone scoring sheet"),
    "articles/why-5s-decays-after-six-months": (
        "product-corporate.jpg", "the real zone scoring sheet"),
}
ARTICLE_ROOM = {
    "articles/why-you-always-lose-your-keys": "Entryway",
    "articles/why-mail-piles-up-by-the-door": "Entryway",
    "articles/what-is-a-micro-zone": "Entryway",
    "articles/why-the-medicine-cabinet-never-gets-cleared-out":
        "Primary Bathroom",
    "articles/why-you-cant-find-the-right-charger": "Family Room",
    "index": "Entryway",
    "deck-gallery-mudroom": "Mudroom",
}
# How each room's pack picture was made (ops/build_pack_images.py).
BOOK_PLAN = {"Entryway", "Dining Room", "Kids Bedroom"}
BOOK_PAIR = {"Kitchen", "Living Room", "Primary Bedroom", "Guest Bedroom"}

EYEBROW = {"rooms": "Room guide", "articles": "The reasoning",
           "zones": "Micro zone"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def card_name(page):
    return slug(page.replace("/", "-")) + ".jpg"


def room_picture(room):
    f = "pack-%s.jpg" % slug(room)
    if room in BOOK_PLAN:
        what = "the book's overhead plan of the %s with its zones numbered" % room
    elif room in BOOK_PAIR:
        what = "the book's before and after illustration of the %s" % room
    else:
        what = "a drawn plan of the %s with its zones numbered" % room
    return f, what


def rooms_by_slug():
    corpus = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(corpus, encoding="utf-8"))["rooms"]
    return {slug(r["room"]): r["room"] for r in rooms}


def read_page(page):
    p = os.path.join(SITE, page + ".html")
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else None


def text_of(fragment):
    t = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", htmllib.unescape(t)).strip()


def h1_of(src):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S)
    return text_of(m.group(1)) if m else None


def desc_of(src):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', src)
    return htmllib.unescape(m.group(1)).strip() if m else ""


def og_of(src):
    m = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', src)
    return m.group(1) if m else ""


def targets():
    """Every page that gets a card, in a stable order."""
    pages = list(TOP)
    for d in ("rooms", "articles"):
        for f in sorted(glob.glob(os.path.join(SITE, d, "*.html"))):
            page = d + "/" + os.path.basename(f)[:-5]
            if page not in pages:
                pages.append(page)
    # Zone pages only where no approved photograph of the zone exists: a
    # zone with its own picture already previews as that picture.
    for f in sorted(glob.glob(os.path.join(SITE, "zones", "*.html"))):
        page = "zones/" + os.path.basename(f)[:-5]
        if page in pages:
            continue
        src = io.open(f, encoding="utf-8").read()
        if "/assets/zones/" not in og_of(src):
            pages.append(page)
    return [p for p in pages if read_page(p) is not None]


def visual_for(page, src, rooms):
    """(picture file under assets/img, what it shows) or (None, None)."""
    if page in PRODUCT:
        return PRODUCT[page]
    room = None
    if page.startswith("rooms/"):
        room = rooms.get(page.split("/", 1)[1])
    elif page in ARTICLE_ROOM:
        room = ARTICLE_ROOM[page]
    elif page.startswith("zones/") and page != "zones/index":
        m = re.search(r'href="\.\./rooms/([a-z-]+)(?:\.html)?"', src)
        room = rooms.get(m.group(1)) if m else None
    if room:
        f, what = room_picture(room)
        if os.path.exists(os.path.join(IMG, f)):
            return f, what
    return None, None


# Where a page's own eyebrow only makes sense beside its body copy.
EYEBROW_PAGE = {"book": "The book", "bundle": "The bundle",
                "resources": "Rooms", "standards": "The Standards Pack",
                "index": "One method, six moves",
                "articles/index": "The reasoning",
                "deck-gallery-mudroom": "Mudroom deck"}


def eyebrow_for(page, src):
    if page in EYEBROW_PAGE:
        return EYEBROW_PAGE[page]
    top = page.split("/", 1)[0]
    if top == "zones" and page != "zones/index":
        m = re.search(r'href="\.\./rooms/[a-z-]+(?:\.html)?">([^<]+)</a>', src)
        if m:
            return "%s · micro zone" % text_of(m.group(1))
    if top in EYEBROW and page not in ("zones/index", "articles/index"):
        return EYEBROW[top]
    m = re.search(r'class="eyebrow"[^>]*>(.*?)</', src, re.S)
    e = text_of(m.group(1)) if m else ""
    return e if 0 < len(e) <= 48 else ""


def plan():
    """The manifest: page -> everything needed to draw and wire its card."""
    rooms = rooms_by_slug()
    out = {}
    for page in targets():
        src = read_page(page)
        head = h1_of(src)
        if not head:
            continue
        pic, what = visual_for(page, src, rooms)
        alt = 'Link preview card for 6S Success reading "%s"' % head
        alt += ((", beside %s." % what) if what else
                ", beside the six steps: Sort, Straighten, Shine, Safety, "
                "Standardize, Sustain.")
        out[page] = {"file": "share/" + card_name(page), "headline": head,
                     "eyebrow": eyebrow_for(page, src),
                     "desc": "" if pic else desc_of(src),
                     "picture": pic, "alt": alt}
    return out


def load_manifest():
    try:
        return json.load(io.open(MANIFEST, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


_CACHE = {}


def card(page):
    """The manifest entry for a page, only if its card file is on disk."""
    if "m" not in _CACHE:
        _CACHE["m"] = load_manifest()
    e = _CACHE["m"].get(page)
    if e and os.path.exists(os.path.join(IMG, e["file"])):
        return e
    return None


def card_url(page):
    e = card(page)
    return "%s/assets/img/%s" % (BASE, e["file"]) if e else None


_OG = re.compile(r'(<meta\s+(?:property="og:image"|name="twitter:image")'
                 r'\s+content=")[^"]*(")')
_EXTRA = re.compile(r'\n?<meta\s+(?:property="og:image:(?:alt|width|height)"'
                    r'|name="twitter:image:alt")\s+content="[^"]*">')


def apply(page, src):
    """Point a page's og:image and twitter:image at its card, with alt and size.

    Idempotent: running it twice gives the same bytes. A page with no card
    on disk is returned unchanged, so a missing card can never leave a broken
    preview behind it."""
    e = card(page)
    if not e or "/assets/zones/" in og_of(src):
        return src
    url = "%s/assets/img/%s" % (BASE, e["file"])
    out = _EXTRA.sub("", src)
    out = _OG.sub(lambda m: m.group(1) + url + m.group(2), out)
    alt = htmllib.escape(e["alt"], quote=True)
    out = re.sub(r'(<meta\s+property="og:image"\s+content="[^"]*">)',
                 lambda m: m.group(1)
                 + '\n<meta property="og:image:alt" content="%s">' % alt
                 + '\n<meta property="og:image:width" content="1200">'
                 + '\n<meta property="og:image:height" content="630">',
                 out, count=1)
    out = re.sub(r'(<meta\s+name="twitter:image"\s+content="[^"]*">)',
                 lambda m: m.group(1)
                 + '\n<meta name="twitter:image:alt" content="%s">' % alt,
                 out, count=1)
    return out


# Pages no generator writes, wired in place by --wire. Every other card page
# gets its card from its own generator (build_seo, build_zone_pages,
# build_zone_index, build_articles), so a rebuild cannot undo it.
# Articles a generator writes; each calls apply() on its own output.
GENERATED = {"articles/what-is-6s",                      # build_articles.py
             "articles/how-long-does-it-take-to-organise-a-room",  # same
             "articles/why-is-my-house-always-messy"}    # build_messy_article


# Top-level pages no generator writes at all.
HAND_TOP = {"bundle"}


def hand_written():
    return [p for p in load_manifest()
            if (p.startswith("articles/") and p not in GENERATED)
            or p in HAND_TOP]


def wire():
    changed = 0
    for page in hand_written():
        path = os.path.join(SITE, page + ".html")
        src = io.open(path, encoding="utf-8", newline="").read()
        new = apply(page, src)
        if new != src:
            io.open(path, "w", encoding="utf-8", newline="").write(new)
            changed += 1
    print("  wired %d hand-written page(s) in place" % changed)


MARK = ('<svg class="sc-mark" viewBox="0 0 40 34" aria-hidden="true">'
        '<path d="M4 30 A16 16 0 0 1 36 30" fill="none" stroke="#E2D8C4" '
        'stroke-width="4" stroke-linecap="round"/>'
        '<path d="M4 30 A16 16 0 0 1 12 16.2" fill="none" stroke="#BC4B2A" '
        'stroke-width="4" stroke-linecap="round"/>'
        '<path d="M12 16.2 A16 16 0 0 1 28 16.2" fill="none" stroke="#DDA63A" '
        'stroke-width="4"/>'
        '<path d="M28 16.2 A16 16 0 0 1 36 30" fill="none" stroke="#6E8B5B" '
        'stroke-width="4" stroke-linecap="round"/>'
        '<line x1="20" y1="30" x2="29" y2="19" stroke="#2B2622" '
        'stroke-width="2.4" stroke-linecap="round"/>'
        '<circle cx="20" cy="30" r="3" fill="#2B2622"/></svg>')

CSS = """
html,body{margin:0;padding:0;background:#F7F2E9}
.sc-card{width:1200px;height:630px;position:relative;overflow:hidden;
 background:#F7F2E9;color:#2B2622;box-sizing:border-box}
.sc-card::after{content:"";position:absolute;left:0;right:0;bottom:0;height:10px;
 background:#2B2622}
.sc-txt{position:absolute;left:68px;top:58px;bottom:58px;display:flex;
 flex-direction:column}
.sc-pic .sc-txt{width:540px}
.sc-text .sc-txt{width:690px}
.sc-steps{position:absolute;right:68px;top:58px;bottom:58px;width:330px;
 border-left:1px solid #D9CDB6;padding-left:40px;display:flex;
 flex-direction:column;justify-content:center;gap:14px;box-sizing:border-box}
.sc-steps div{font-family:var(--serif);font-size:34px;line-height:1;
 color:#2B2622;display:flex;align-items:baseline;gap:18px}
.sc-steps b{font-family:var(--sans);font-size:17px;font-weight:600;
 color:#8A8076;width:16px}
.sc-brand{display:flex;align-items:center;gap:12px;font-family:var(--serif);
 font-size:30px;font-weight:600;letter-spacing:-.01em}
.sc-brand svg{width:46px;height:39px}
.sc-eyebrow{margin-top:44px;font-family:var(--sans);font-size:19px;
 font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#6A625A}
.sc-hl{margin:16px 0 0;font-family:var(--serif);font-weight:600;
 line-height:1.08;letter-spacing:-.015em}
.sc-desc{margin:24px 0 0;font-family:var(--sans);font-size:27px;line-height:1.42;
 color:#4A433D;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;
 overflow:hidden;max-width:960px;flex-shrink:0}
.sc-url{margin-top:auto;font-family:var(--sans);font-size:20px;color:#6A625A;
 letter-spacing:.02em}
.sc-frame{position:absolute;right:60px;top:50%;width:520px;height:390px;
 transform:translateY(-50%) rotate(1.2deg);background:#fff;
 border:1px solid #E2D8C4;box-shadow:0 18px 40px rgba(60,45,30,.18)}
.sc-frame img{display:block;width:100%;height:100%;object-fit:cover}
"""

FIT = """
document.fonts.ready.then(function(){
 document.querySelectorAll('.sc-card').forEach(function(c){
  var h=c.querySelector('.sc-hl'), t=c.querySelector('.sc-txt');
  var size=c.classList.contains('sc-pic')?60:66, min=30;
  h.style.fontSize=size+'px';
  while(size>min && t.scrollHeight>t.clientHeight+1){
   size-=2; h.style.fontSize=size+'px';}
  c.setAttribute('data-fit', size);
 });
 document.body.setAttribute('data-ready','1');
});
"""


def card_html(e):
    esc = htmllib.escape
    pic = e.get("picture")
    parts = ['<div class="sc-card %s">' % ("sc-pic" if pic else "sc-text"),
             '<div class="sc-txt">',
             '<div class="sc-brand">%s6S Success</div>' % MARK,
             ('<div class="sc-eyebrow">%s</div>' % esc(e["eyebrow"])
              if e["eyebrow"] else '<div class="sc-eyebrow">&nbsp;</div>'),
             '<h1 class="sc-hl">%s</h1>' % esc(e["headline"])]
    if e.get("desc"):
        parts.append('<p class="sc-desc">%s</p>' % esc(e["desc"]))
    parts.append('<div class="sc-url">6s-success.com</div></div>')
    if not pic:
        parts.append('<div class="sc-steps">' + "".join(
            '<div><b>%d</b>%s</div>' % (i + 1, w) for i, w in enumerate(
                ("Sort", "Straighten", "Shine", "Safety", "Standardize",
                 "Sustain"))) + "</div>")
    if pic:
        parts.append('<div class="sc-frame"><img src="assets/img/%s" alt=""></div>'
                     % esc(pic))
    parts.append("</div>")
    return "".join(parts)


def render_batch(entries, exe, extra):
    """Draw up to 20 cards in one page, screenshot it, slice it."""
    from PIL import Image
    page = ("<!doctype html><meta charset=utf-8>"
            '<link rel=stylesheet href="assets/css/site.css">'
            "<style>%s</style>%s<script>%s</script>"
            % (CSS, "".join(card_html(e) for e in entries), FIT))
    fd, probe = tempfile.mkstemp(prefix="_share_render_", suffix=".html",
                                 dir=SITE)
    os.close(fd)
    shot = probe[:-5] + ".png"
    try:
        io.open(probe, "w", encoding="utf-8").write(page)
        subprocess.run([exe, "--headless=new", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=%d,%d" % (CW, CH * len(entries)),
                        "--virtual-time-budget=6000"] + list(extra)
                       + ["--screenshot=" + shot,
                          "file:///" + probe.replace("\\", "/")],
                       capture_output=True, timeout=240)
        if not os.path.exists(shot):
            raise RuntimeError("browser wrote no screenshot")
        im = Image.open(shot).convert("RGB")
        im.load()
        if im.size != (CW, CH * len(entries)):
            raise RuntimeError("screenshot is %dx%d, expected %dx%d"
                               % (im.width, im.height, CW,
                                  CH * len(entries)))
        return [im.crop((0, i * CH, CW, (i + 1) * CH))
                for i in range(len(entries))]
    finally:
        for p in (probe, shot):
            if os.path.exists(p):
                os.remove(p)


def write_manifest(m):
    io.open(MANIFEST, "w", encoding="utf-8", newline="\n").write(
        json.dumps(m, indent=1, sort_keys=True, ensure_ascii=False) + "\n")


def main(argv):
    force = "--force" in argv
    before = load_manifest()
    manifest = plan()
    if "--manifest" in argv:
        write_manifest(manifest)
        print("  manifest: %d pages (no cards drawn)" % len(manifest))
        return 0
    if "--wire" in argv:
        wire()
        return 0
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import browser
    found = browser.find_browser()
    if not found:
        print("  no browser found: cards NOT drawn, manifest NOT changed")
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    # Missing, or drawn from different words than the page now says.
    todo = [(p, e) for p, e in manifest.items()
            if force or before.get(p) != e
            or not os.path.exists(os.path.join(IMG, e["file"]))]
    failed = []
    for i in range(0, len(todo), 20):
        batch = todo[i:i + 20]
        try:
            for (p, e), im in zip(batch, render_batch([e for _, e in batch],
                                                      *found)):
                im.save(os.path.join(IMG, e["file"]), "JPEG", quality=86,
                        optimize=True, progressive=True)
        except Exception as exc:          # reported, never silently skipped
            failed.extend((p, str(exc)) for p, _ in batch)
    # A card that failed keeps its old entry (or none), so the next run sees
    # it as still owed instead of believing it was drawn.
    for p, _ in failed:
        if p in before:
            manifest[p] = before[p]
        else:
            manifest.pop(p, None)
    write_manifest(manifest)
    print("  manifest: %d pages; drew %d, failed %d"
          % (len(manifest), len(todo) - len(failed), len(failed)))
    for p, why in failed:
        print("  FAILED %s: %s" % (p, why))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
