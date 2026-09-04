#!/usr/bin/env python3
"""
The kit a single micro zone actually needs, and the links to it when links exist.

WHY THIS EXISTS
---------------
Two files in this repository already know, per zone, exactly which product
types the method calls for, and neither of them reaches a single page of the
website.

  content/manual/source/zone_products.json   114 zones, 1,867 product rows,
                                             each with the phase it serves,
                                             what it is for, and its safety note
  ops/affiliate-catalogue.csv                123 product types, with the
                                             merchant, URL and link status

So a reader who has just been told to wipe the shelf with a neutral pH cleaner
and date every bottle has never been told, anywhere on the page, that they
need a neutral pH cleaner and a label maker before they start. The method
assumed a kit the page never named.

WHAT IT DOES NOT DO
-------------------
It does not invent a link, a price, a rating or a retailer. The catalogue is
owned by another agent and is only ever READ here. Today every one of its 123
rows carries `Link Status: Unverified` and an empty `Affiliate URL`, so every
product on every zone page renders as plain text: the type of thing, the
reason it is needed, and the safety note. That is the useful half and it works
with nothing bought.

The moment a row gains a verified URL, that one product becomes a link on
every zone page whose method calls for it, and the disclosure block appears
above it. Nothing here needs editing for that to happen.

THREE LINK STATES, ON PURPOSE
-----------------------------
  tracked    an approved affiliate programme AND a URL   -> rel="sponsored
             nofollow noopener", and ops/affiliate.py's disclosure above it
  plain      a verified retailer URL but no approved     -> rel="nofollow
             programme, so the click earns nothing          noopener"
  none       no URL, or a URL whose Link Status is not   -> plain text, no
             verified                                       anchor, no excuse

The third state is the one that has to be graceful, because it is the state
all 123 rows are in right now. It renders the product name in bold and says
nothing about links at all, because there is nothing to say: a page with no
outbound retailer link has no material connection to disclose, and printing
"no retailer link yet" 114 times would be noise about our own back office.

ORDERING
--------
Rarest first, measured across the 114 zones. A colour-coded microfiber cloth
set appears in every zone's kit and tells a reader nothing about the garage.
A self-closing oily rag can appears in four, and it is the whole reason the
garage's Safety pass reads the way it does. Leading with the shared items
would make 114 identical opening lines; leading with the rare ones puts the
distinctive thing first for the reader and for anything reading the page.

Read only. Never writes.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ZONE_PRODUCTS = os.path.join(ROOT, "content", "manual", "source",
                             "zone_products.json")
CATALOGUE = os.path.join(ROOT, "ops", "affiliate-catalogue.csv")

# Levels the manual assigns. The first two are the kit you cannot start
# without; the second two are "only if your zone has one of these".
NEEDED = ("Core", "Core Reset Kit")

# schema.org draws the line between a thing consumed by the procedure and a
# thing reused after it. A bottle of cleaner is a HowToSupply; a vacuum is a
# HowToTool. Getting this backwards is not a small thing, it is markup that
# describes a different procedure from the one on the page.
CONSUMED_UNITS = {"bottle", "pack", "roll", "box", "tags", "cloths", "can"}
CONSUMED_FAMILIES = {"Cleaning Supplies"}

_ZP = None
_CAT = None
_RARITY = None


def _zone_products() -> dict:
    global _ZP
    if _ZP is None:
        with io.open(ZONE_PRODUCTS, encoding="utf-8") as fh:
            _ZP = json.load(fh)
    return _ZP


def _catalogue() -> dict:
    """Product ID -> catalogue row. Empty dict if the file is unreadable,
    because a missing catalogue must degrade to "no links" rather than
    crashing a build of 114 pages."""
    global _CAT
    if _CAT is None:
        _CAT = {}
        try:
            with io.open(CATALOGUE, encoding="utf-8-sig") as fh:
                for row in csv.DictReader(fh):
                    pid = (row.get("Product ID") or "").strip()
                    if pid:
                        _CAT[pid] = row
        except Exception:                                     # noqa: BLE001
            _CAT = {}
    return _CAT


def _rarity() -> dict:
    """How many of the 114 zones call for each product id.

    Computed here rather than read from the catalogue's own `_zone_count`
    column, because that column lives in a file another agent is editing this
    cycle and a stale count would silently reorder every page.
    """
    global _RARITY
    if _RARITY is None:
        _RARITY = {}
        for items in _zone_products().values():
            for p in items:
                _RARITY[p["id"]] = _RARITY.get(p["id"], 0) + 1
    return _RARITY


# THE PROMISE GATE
# ----------------
# site/privacy.html says, in these words: "Today the only outbound links on
# this site go to Stripe ... There are no links to retailers, and no affiliate
# or tracking codes anywhere on the site ... We would say so on this page and
# on the page carrying the link."
#
# On 2026-09-04 the catalogue gained 121 verified retailer search URLs. Turning
# those into anchors on 134 pages would have made that paragraph false, and
# privacy.html belongs to another agent this cycle. preflight's gate_third_party
# caught it: 207 references to target.com and homedepot.com.
#
# So a URL only becomes a clickable link once its host is NAMED on privacy.html,
# which is the same test the gate applies and the same principle the gate's own
# docstring states: the rule is not "never link out", it is "never send a reader
# somewhere they were not told about". Nothing here needs editing when that
# paragraph is updated. The links appear by themselves, on all 134 pages, in the
# same run.
#
# Until then every product renders as plain text, which is the state this file
# was designed to make graceful in the first place.
_DISCLOSED = None


def _disclosed_hosts() -> set:
    global _DISCLOSED
    if _DISCLOSED is None:
        _DISCLOSED = set()
        priv = os.path.join(ROOT, "site", "privacy.html")
        try:
            import re
            body = io.open(priv, encoding="utf-8", errors="replace").read()
            body = re.sub(r"(?is)<head>.*?</head>", " ", body)
            _DISCLOSED = {h.lower() for h in
                          re.findall(r"\b((?:[a-z0-9-]+\.)+[a-z]{2,})\b", body)}
        except Exception:                                     # noqa: BLE001
            _DISCLOSED = set()
    return _DISCLOSED


def _host_disclosed(url: str) -> bool:
    import re
    m = re.match(r"https?://([a-z0-9.-]+)", url.lower())
    if not m:
        return False
    h = m.group(1)
    return any(h == d or h.endswith("." + d) for d in _disclosed_hosts())


def _link(row: dict) -> tuple:
    """(href, kind) for one catalogue row. kind is "tracked", "plain" or "".

    Deliberately conservative in both directions. A URL with a Link Status
    that is not verified is treated as absent, because the whole point of that
    column is that somebody checked the link resolves to the product it claims
    to. And an approved programme with no URL is still no link.
    """
    if not row:
        return "", ""
    url = (row.get("Affiliate URL") or "").strip()
    if not url.lower().startswith(("http://", "https://")):
        return "", ""
    status = (row.get("Link Status") or "").strip().lower()
    if not status.startswith("verified"):
        return "", ""
    # The promise gate. See _disclosed_hosts above: a verified URL to a host
    # privacy.html has not named is not publishable, however good the link is.
    if not _host_disclosed(url):
        return "", ""

    try:
        import affiliate as A
        tracked = A.build_link((row.get("Merchant") or "").strip().lower(), url)
    except Exception:                                         # noqa: BLE001
        tracked = None
    if tracked:
        return tracked, "tracked"
    return url, "plain"


def _room_allows(applicable: str, room: str) -> bool:
    """Does the catalogue think this product belongs in this room?

    The catalogue carries an `Applicable Rooms` column and nothing read it,
    so the manual's per-zone lists put impact-rated safety glasses, reason
    text and all, into the Pantry Baking Zone, the Kitchen Cooking Zone and
    eighteen other rooms it has no business in. Rarest-first ordering then
    made it the FIRST recommendation on those pages. The row itself says
    "Garage; Workshop; Patio or Deck".

    145 of the 1,867 zone-product pairs fail this check, 7.8 percent, and
    every one that was read by hand is a genuine mismatch: a food-area
    degreaser in a kids' bedroom, floor boundary tape in a family room, a
    moisture absorber in a living room.

    Fails OPEN, deliberately. An empty column, the word "All", or a value
    this cannot parse all keep the product, because dropping a needed item
    costs a reader more than showing a broadly applicable one. Room names
    are matched by containment in both directions, because the catalogue
    says "Bathroom" and "Closet" where the manual says "Primary Bathroom"
    and "Hall Closet", and exact matching silently dropped 34 correct rows.
    """
    ar = (applicable or "").strip()
    if not ar or ar.lower() == "all":
        return True
    r = room.strip().lower()
    for tok in (t.strip().lower() for t in ar.split(";")):
        if tok and (tok == r or tok in r or r in tok):
            return True
    return False


def kit(room: str, manual_zone: str) -> dict:
    """This zone's products, split into what it needs and what it might.

    Keys are the manual's own "Room||Zone Name" strings, which is why callers
    pass the MANUAL zone name and not the display name the site shows. The
    site and the manual name the same zone differently on purpose (see
    ops/zone-name-map.json); this function is on the manual's side of that
    line.
    """
    items = _zone_products().get(f"{room}||{manual_zone}") or []
    cat, rare = _catalogue(), _rarity()

    out = {"needed": [], "maybe": [], "links": 0, "tracked": 0,
           "amazon": False}
    for p in items:
        row = cat.get(p["id"], {})
        if not _room_allows(row.get("Applicable Rooms"), room):
            continue
        href, kind = _link(row)
        fam = (row.get("Product Family") or "").strip()
        unit = (p.get("unit") or "").strip().lower()
        rec = {
            "id": p["id"],
            "name": p["name"],
            "use": (p.get("use") or "").strip().rstrip("."),
            "phase": [s.strip().lower() for s in (p.get("phase") or "").split(";")
                      if s.strip()],
            "safety": (p.get("safety") or "").strip(),
            "qty": p.get("qty"),
            "unit": p.get("unit") or "",
            "href": href,
            "kind": kind,
            "merchant": (row.get("Merchant") or "").strip().lower(),
            "supply": fam in CONSUMED_FAMILIES or unit in CONSUMED_UNITS,
            "rarity": rare.get(p["id"], 999),
        }
        if kind:
            out["links"] += 1
            if kind == "tracked":
                out["tracked"] += 1
                if rec["merchant"] == "amazon":
                    out["amazon"] = True
        bucket = "needed" if p.get("level") in NEEDED else "maybe"
        out[bucket].append(rec)

    for b in ("needed", "maybe"):
        # Rarest first, then alphabetical so the order is stable between runs.
        out[b].sort(key=lambda r: (r["rarity"], r["name"]))
    return out


# ---------------------------------------------------------------- rendering

def _esc(t):
    import html
    return html.escape(str(t or ""), quote=True)


def _anchor(rec: str, prefix: str = "") -> str:
    """One product, linked only if there is genuinely a link."""
    name = f'<b>{_esc(rec["name"])}</b>'
    if rec["kind"] == "tracked":
        return (f'<a href="{_esc(rec["href"])}" rel="sponsored nofollow noopener" '
                f'target="_blank">{name}</a>')
    if rec["kind"] == "plain":
        return (f'<a href="{_esc(rec["href"])}" rel="nofollow noopener" '
                f'target="_blank">{name}</a>')
    return name


# Which of the six pass anchors on the page a product belongs to. The page
# gives every pass an id (see ops/build_zone_pages.py), so naming the pass is
# also an internal link to the paragraph that explains why the thing is
# needed. That is the "reason tied to the root cause" made navigable rather
# than asserted.
PASS_ORDER = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]


def _why(rec: dict, link_passes: bool = True) -> str:
    phases = [p for p in PASS_ORDER if p in rec["phase"]]
    if not phases:
        return _esc(rec["use"]) + "."
    # A room page has no #sort anchor on it, so linking the pass names there
    # would put six broken in-page links on all twenty room pages. Only the
    # zone pages render the six passes, so only they link them.
    parts = [f'<a href="#{p}">{p.title()}</a>' if link_passes else p.title()
             for p in phases]
    # "in the Shine, Safety passes" is not a sentence anybody wrote. An
    # Oxford-free join reads as English and is what a speech assistant
    # reading this page aloud has to say out loud.
    if len(parts) == 1:
        links = parts[0]
    elif len(parts) == 2:
        links = " and ".join(parts)
    else:
        links = ", ".join(parts[:-1]) + " and " + parts[-1]
    word = "pass" if len(phases) == 1 else "passes"
    return f'{_esc(rec["use"])}, in the {links} {word}.'


def _row_html(rec: dict, link_passes: bool = True) -> str:
    qty = ""
    if rec.get("qty") and str(rec["qty"]) not in ("1", "None"):
        qty = f' <span style="opacity:.7">&times;{_esc(rec["qty"])}</span>'
    safety = ""
    if rec["safety"]:
        safety = (f'<br><span style="font-size:14.5px;opacity:.85">'
                  f'{_esc(rec["safety"])}.</span>')
    return (f'<li style="margin:0 0 10px">{_anchor(rec)}{qty}'
            f'<br>{_why(rec, link_passes)}{safety}</li>')


# site.css has no .disclosure rule: the only page that used the block before
# now (kit.html) carries its own <style> for it, and site.css belongs to
# another agent this cycle. Unstyled, a legal disclosure renders as ordinary
# body copy, which is the one thing it must not look like. So the opening tag
# is restyled inline to match the site's own .notice callout, at 15px and
# full --ink rather than .notice's 13.5px --soft, because 13.5px grey is too
# quiet for the sentence that tells somebody whether we are paid.
#
# Only the tag's attributes are touched. The wording, including Amazon's
# verbatim sentence, stays exactly as ops/affiliate.py wrote it, and the id
# the affiliate gate looks for is preserved.
_DISCLOSURE_STYLE = (
    'style="font-family:var(--sans);font-size:15px;line-height:1.55;'
    'color:var(--ink);background:var(--panel);border:1px dashed var(--line-2);'
    'border-radius:12px;padding:16px 18px;margin:18px 0;max-width:66ch"')


def _styled(block: str) -> str:
    return block.replace('<aside class="disclosure" id=',
                         f'<aside {_DISCLOSURE_STYLE} class="disclosure" id=',
                         1)


def render(room: str, manual_zone: str, display_name: str,
           prefix: str = "../") -> str:
    """The "What you need" section, or "" when this zone has no kit recorded.

    Returns a self-contained block: disclosure first (only when the page
    genuinely has outbound retailer links), then the needed kit, then the
    conditional half folded away so it cannot bury the method.
    """
    k = kit(room, manual_zone)
    if not k["needed"] and not k["maybe"]:
        return ""

    out = []
    out.append('<h2 id="what-you-need">What to have on hand before you start</h2>')
    out.append('<p>These are types of thing, not brands. If you already own '
               'something that does the job, that is the right one to use. '
               'Each says which pass needs it and what to watch out for.</p>')

    # The disclosure appears whenever the page carries an outbound retailer
    # link at all, and its WORDING is chosen by whether any of those links
    # actually pay us. Those are two different questions and conflating them
    # is the exact error ops/affiliate.py's own docstring records twice:
    # passing has_links=True with no approved programme prints "6S Success
    # may earn a commission" above links that earn nothing, which is claiming
    # a material connection we do not have.
    #
    # Today every link is a plain retailer search, no programme is approved,
    # so this renders "Nothing on this page earns us anything", which is true
    # and is the thing a reader is owed before they click out.
    if k["links"]:
        try:
            import affiliate as A
            out.append(_styled(
                # has_links means "are there links on this page", not
                # "do any of them pay us". Passing tracked made 114 zone
                # pages print "Nothing on this page earns us anything...
                # not one product below carries a paying link" directly
                # above fifteen live retailer links, which reads as
                # though there are no links at all. Both sentences are
                # true; only one of them describes the page.
                A.disclosure(k["amazon"], bool(k["links"]), prefix)))
        except Exception:                                     # noqa: BLE001
            pass

    if k["needed"]:
        out.append('<ul style="max-width:66ch">')
        out += [_row_html(r) for r in k["needed"]]
        out.append('</ul>')

    if k["maybe"]:
        # display_name arrives as the common noun the page title uses
        # ("automotive care zone", "medicine cabinet"), NOT the site's
        # display name. "Only if your The Automotive Care Zone has one"
        # is what the display name produces, and it shipped once.
        noun = _esc(display_name.strip().lower())
        out.append('<details style="margin:18px 0 0">'
                   f'<summary style="cursor:pointer;font-family:var(--sans);'
                   f'font-weight:600">Only if your {noun} has one: '
                   f'{len(k["maybe"])} more</summary>'
                   f'<p style="margin:12px 0 8px">Not every {noun} needs '
                   'these. Each one is here because some do, and the reason '
                   'is next to it.</p>'
                   '<ul style="max-width:66ch">')
        out += [_row_html(r) for r in k["maybe"]]
        out.append('</ul></details>')
    return "\n".join(out)


def room_kit(room: str, manual_zones) -> list:
    """The Core kit for a whole room, deduplicated across its zones.

    A room page reader has not chosen a zone yet, so per-zone lists would be
    five near identical lists on one page. The union, rarest first, is the
    honest answer to "what do I need to buy or find before I start on this
    room at all".
    """
    seen, out = set(), []
    for mz in manual_zones:
        for rec in kit(room, mz)["needed"]:
            if rec["id"] in seen:
                continue
            seen.add(rec["id"])
            out.append(rec)
    out.sort(key=lambda r: (r["rarity"], r["name"]))
    return out


def render_room(room: str, manual_zones, room_lower: str,
                prefix: str = "../") -> str:
    items = room_kit(room, manual_zones)
    if not items:
        return ""
    links = sum(1 for r in items if r["kind"])
    tracked = sum(1 for r in items if r["kind"] == "tracked")
    amazon = any(r["kind"] == "tracked" and r["merchant"] == "amazon"
                 for r in items)
    out = ['<h2 id="what-you-need">The kit for the whole '
           f'{_esc(room_lower)}</h2>',
           '<p>Every zone below draws from this. These are types of thing, '
           'not brands, and anything you already own that does the job is '
           'the right one to use. Each zone page names the smaller list that '
           'zone actually needs.</p>']
    if links:
        try:
            import affiliate as A
            out.append(_styled(A.disclosure(amazon, bool(tracked), prefix)))
        except Exception:                                     # noqa: BLE001
            pass
    out.append('<ul style="max-width:66ch">')
    out += [_row_html(r, link_passes=False) for r in items]
    out.append('</ul>')
    return "\n".join(out)


def schema(room: str, manual_zone: str) -> tuple:
    """(supply, tool) lists for the page's HowTo, from the needed kit only.

    Only the "needed" half is marked up. A conditional item is by definition
    not required to complete the procedure, and HowToSupply means required.
    """
    k = kit(room, manual_zone)
    supply, tool = [], []
    for r in k["needed"]:
        node = {"@type": "HowToSupply" if r["supply"] else "HowToTool",
                "name": r["name"]}
        (supply if r["supply"] else tool).append(node)
    return supply, tool


def _report() -> int:
    zp = _zone_products()
    cat = _catalogue()
    linked = 0
    for key in zp:
        room, zone = key.split("||", 1)
        k = kit(room, zone)
        linked += k["links"]
    ids = {p["id"] for v in zp.values() for p in v}
    print(f"  zones with a kit      {len(zp)}")
    print(f"  distinct product ids  {len(ids)}")
    print(f"  missing from catalogue {sorted(ids - set(cat)) or 'none'}")
    print(f"  product links that would render on all zone pages: {linked}")
    urls = sum(1 for r in cat.values() if (r.get("Affiliate URL") or "").strip())
    verified = sum(1 for r in cat.values()
                   if (r.get("Link Status") or "").strip().lower()
                   .startswith("verified"))
    print(f"  catalogue rows with a URL: {urls}, of which verified: {verified}")
    print(f"  hosts named on privacy.html: "
          f"{sorted(h for h in _disclosed_hosts() if '.' in h and not h.endswith(('.html', '.js', '.css', '.xml')))[:6]}")
    if not linked:
        print("  0 links render. Either no row is verified, or the retailer's")
        print("  host is not named on privacy.html yet, which says in so many")
        print("  words that there are no links to retailers on this site.")
        print("  Both are correct reasons to render plain text.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_report())
