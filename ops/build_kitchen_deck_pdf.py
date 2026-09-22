#!/usr/bin/env python3
"""
The Kitchen deck as a real, downloadable PDF, not a browser print dialog.

WHY
---
site/kitchen-deck.html's "Print the 72 fronts" button opens the browser's own
print dialog against a real @media print sheet (all 72 card fronts, 2.5x3.5in,
three to a row on US Letter). That is real, but it is not a downloadable file:
closing the tab loses it. GitHub issue #34 names the gap plainly: eight
Kitchen SKUs are held for retirement on a "the deck is downloadable" condition
a print dialog does not meet, the way the Entryway deck's own PDF
(ops/build_deck_pdf.py, linked from deck.html) does.

WHY NOT THE ENTRYWAY PIPELINE
------------------------------
build_deck_pdf.py draws card art directly from build/cards-rendered PNGs,
because the Entryway deck is photographed. The Kitchen deck has no
photography yet (BACKLOG-2026-09-07.md B1): every card is CSS and text, the
same @media print layout window.print() already renders correctly in a
browser. So instead of a second, hand-built layout that could drift from what
a visitor actually sees, this renders the exact page headless Chromium prints,
straight to a PDF file, and ships that.

STALENESS
---------
The print sheet is fully generated from the corpus by
ops/build_kitchen_deck_page.py; nothing here is hand authored. Staleness is
checked the way ops/check_sitemap_current.py checks the sitemap: a content
hash of the print-only sheet, recorded at PDF-build time, compared against a
fresh hash of the live page's print-only sheet on every check. A PDF whose
source has moved on is worse than an honest "not built yet", the same
corrected-source-never-rederived shape this repository keeps finding.

Needs a real Chromium (ops/browser.py). Without one this says UNCHECKED and
exits 1 on build, 0 on --check, because "could not render" and "verified
current" are different claims.

Run:  python ops/build_kitchen_deck_pdf.py
      python ops/build_kitchen_deck_pdf.py --check
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

SRC = os.path.join(ROOT, "site", "kitchen-deck.html")
OUT = os.path.join(ROOT, "site", "downloads", "6S-Kitchen-Deck-PrintAndPlay.pdf")
HASH_FILE = os.path.join(ROOT, "ops", "kitchen-deck-pdf-hash.json")

# Known markers a real, current render must contain: the deck's own title
# card and its last event card, one from each end of the 72. If either goes
# missing the PDF is not this deck, whatever its page count says.
MARKERS = ("PRIMARY PREP COUNTER", "GUESTS IN THE KITCHEN")


def sheet_hash(html: str) -> str:
    """Content hash of the print-only sheet: everything from its opening div
    to </main>. Nothing else sits between them in the template
    (ops/build_kitchen_deck_page.py), so this is the whole sheet plus
    whitespace, not a guess at its boundary."""
    i = html.find('<div class="print-only"')
    j = html.find("</main>")
    if i == -1 or j == -1 or j <= i:
        raise ValueError("print-only sheet not found in kitchen-deck.html")
    return hashlib.sha256(html[i:j].encode("utf-8")).hexdigest()


def current_hash() -> str:
    return sheet_hash(io.open(SRC, encoding="utf-8").read())


def check() -> dict:
    """{'ok': bool, 'reason': str}. Never raises."""
    if not os.path.exists(SRC):
        return {"ok": False, "reason": "site/kitchen-deck.html does not exist"}
    if not os.path.exists(OUT):
        return {"ok": False, "reason": "no PDF built yet"}
    if not os.path.exists(HASH_FILE):
        return {"ok": False, "reason": "no hash record; PDF predates this check"}
    try:
        record = json.load(io.open(HASH_FILE, encoding="utf-8"))
    except Exception as e:                                      # noqa: BLE001
        return {"ok": False, "reason": f"hash record unreadable: {e}"}
    want = current_hash()
    if record.get("sheet_hash") != want:
        return {"ok": False,
                 "reason": "kitchen-deck.html's print sheet changed since "
                            "the PDF was built; rerun "
                            "ops/build_kitchen_deck_pdf.py"}
    return {"ok": True, "reason": "PDF matches the live print sheet"}


def main() -> int:
    if "--check" in sys.argv:
        r = check()
        print("  %s: %s" % ("current" if r["ok"] else "STALE", r["reason"]))
        return 0 if r["ok"] else 1

    import browser as B
    found = B.find_browser()
    if not found:
        print("  no Chromium available; cannot render. UNCHECKED, not built.")
        return 1
    exe, extra_args = found

    if not os.path.exists(SRC):
        print("  site/kitchen-deck.html does not exist; run "
              "ops/build_kitchen_deck_page.py first.")
        return 1
    html = io.open(SRC, encoding="utf-8").read()
    want_hash = sheet_hash(html)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    subprocess.run(
        [exe, "--headless=new", "--disable-gpu",
         "--run-all-compositor-stages-before-draw",
         "--virtual-time-budget=15000",
         "--print-to-pdf=" + OUT, "--print-to-pdf-no-header",
         *extra_args,
         "file:///" + os.path.abspath(SRC).replace(os.sep, "/")],
        capture_output=True, timeout=120)

    if not os.path.exists(OUT) or os.path.getsize(OUT) < 10_000:
        print("  render failed: no usable PDF written")
        return 1

    data = io.open(OUT, "rb").read()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    size_kb = len(data) / 1024
    print("  wrote %s  %d pages  %.0f KB"
          % (os.path.relpath(OUT, ROOT), pages, size_kb))

    # Verify real content landed, not a blank or error page. pymupdf is
    # already a hard dependency of this repository's own preflight gates
    # (ops/requirements.txt), so it is never an optional import here.
    import pymupdf
    doc = pymupdf.open(OUT)
    # Chromium's print layout wraps a long title across lines, and
    # get_text() follows that wrap with a real newline ("PRIMARY PREP\n
    # COUNTER"), so a marker check against raw text would fail on content
    # that is genuinely present. Collapsed whitespace is what "is this text
    # on the page" actually means here.
    text = " ".join("".join(p.get_text() for p in doc).split())
    doc.close()
    missing = [m for m in MARKERS if m not in text]
    if missing:
        print("  MISSING from the rendered text: %s. The PDF was written "
              "but does not contain the deck." % missing)
        return 1
    if pages < 6:
        print("  only %d page(s); 72 cards at 6 to a page should print "
              "well over a dozen. The render is short." % pages)
        return 1

    json.dump({"sheet_hash": want_hash, "pages": pages},
               io.open(HASH_FILE, "w", encoding="utf-8", newline=""),
               indent=1)
    print("  content verified: both end markers present, %d page(s)" % pages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
