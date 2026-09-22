#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_deck_pdf_current() catches a Kitchen
deck PDF that has fallen behind the live page's print sheet, or is missing
entirely once the page links it.

GitHub issue #34: the Kitchen deck's only "get the deck" action used to be a
browser print dialog, not a saved file. ops/build_kitchen_deck_pdf.py renders
a real PDF from the page's own @media print sheet and records a content hash
of that sheet at build time (ops/kitchen-deck-pdf-hash.json). This proves the
staleness check that hash record exists for: a corpus edit that changes the
print sheet after the PDF was last built must fail the gate, not ship a
customer a deck that disagrees with the page still advertising it.

Uses a temporary directory and monkeypatches the module's own path
constants, so it never touches the real committed site or build/kitchen-deck-
pdf-hash.json.

Run:  python ops/tests/test_gate_kitchen_deck_pdf_current.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_kitchen_deck_pdf as KP                            # noqa: E402
import preflight                                                # noqa: E402

PAGE_TEMPLATE = (
    '<!doctype html><html><body><main>'
    '<div class="print-only" aria-hidden="true"><div class="ksheet">%s</div>'
    '</div>\n\n</main></body></html>'
)


def write_page(site_dir: str, sheet: str) -> str:
    fp = os.path.join(site_dir, "kitchen-deck.html")
    io.open(fp, "w", encoding="utf-8", newline="").write(PAGE_TEMPLATE % sheet)
    return fp


def main() -> int:
    fails = []
    tmp = tempfile.mkdtemp(prefix="6s-kitchen-pdf-gate-")
    site_dir = os.path.join(tmp, "site")
    dl_dir = os.path.join(site_dir, "downloads")
    os.makedirs(dl_dir)

    old_src, old_out, old_hash = KP.SRC, KP.OUT, KP.HASH_FILE
    old_site = preflight.SITE
    try:
        html_fp = write_page(site_dir, "<div>card one</div>")
        KP.SRC = html_fp
        KP.OUT = os.path.join(dl_dir, "6S-Kitchen-Deck-PrintAndPlay.pdf")
        KP.HASH_FILE = os.path.join(tmp, "kitchen-deck-pdf-hash.json")
        preflight.SITE = site_dir

        page_with_link = PAGE_TEMPLATE % "<div>card one</div>"
        page_with_link = page_with_link.replace(
            "<body>", '<body><a href="downloads/'
                      '6S-Kitchen-Deck-PrintAndPlay.pdf">get it</a>')

        # 1. Page links the PDF, nothing built yet: the gate must fail, not
        #    silently pass on a page whose main CTA 404s.
        io.open(html_fp, "w", encoding="utf-8", newline="").write(page_with_link)
        problems = KP.check()
        if problems["ok"]:
            fails.append("no PDF built at all was wrongly reported ok")

        # 2. Build a PDF and a matching hash record by hand (skipping the
        #    real Chromium render, which this pure-logic test does not need):
        #    the hash must match sheet_hash() of the current page.
        io.open(KP.OUT, "wb").write(b"%PDF-1.4 not a real pdf but present\n")
        record = {"sheet_hash": KP.sheet_hash(
            io.open(html_fp, encoding="utf-8").read()), "pages": 1}
        json.dump(record, io.open(KP.HASH_FILE, "w", encoding="utf-8"))
        r = KP.check()
        if not r["ok"]:
            fails.append("a PDF matching the current page was wrongly "
                         "flagged stale: %s" % r["reason"])

        # 3. The corpus moves on (a card's text changes) after the PDF was
        #    built: the recorded hash no longer matches. This is the exact
        #    defect class the gate exists to catch.
        io.open(html_fp, "w", encoding="utf-8", newline="").write(
            page_with_link.replace("card one", "card one, rewritten"))
        r = KP.check()
        if r["ok"]:
            fails.append("a page whose print sheet changed since the PDF "
                         "was built was wrongly reported current")
        elif "print sheet changed" not in r["reason"]:
            fails.append("stale PDF caught, but for the wrong reason: %s"
                         % r["reason"])

        # 4. Wire the preflight-level gate itself: page links the PDF, but
        #    the hash record is missing entirely (never built).
        os.remove(KP.HASH_FILE)
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_kitchen_deck_pdf_current()
        if not preflight.FAIL:
            fails.append("gate_kitchen_deck_pdf_current did not fail on a "
                         "linked-but-unbuilt PDF")
        elif preflight.FAIL[0][0] != "kitchen-deck-pdf-current":
            fails.append("failed under the wrong gate name: %r"
                         % (preflight.FAIL,))

        # 5. Restore a valid record and confirm the real gate passes clean.
        record["sheet_hash"] = KP.sheet_hash(
            io.open(html_fp, encoding="utf-8").read())
        json.dump(record, io.open(KP.HASH_FILE, "w", encoding="utf-8"))
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_kitchen_deck_pdf_current()
        if preflight.FAIL:
            fails.append("a current PDF was wrongly failed: %r"
                         % (preflight.FAIL,))

    finally:
        KP.SRC, KP.OUT, KP.HASH_FILE = old_src, old_out, old_hash
        preflight.SITE = old_site
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kitchen_deck_pdf_current: 5/5 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
