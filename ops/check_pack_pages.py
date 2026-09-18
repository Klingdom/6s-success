#!/usr/bin/env python3
"""
The free Standards Pack must print as the twenty sheets it says it is.

Found 2026-09-18 by printing the real file to PDF with headless Edge and
counting: 21 pages for a pack whose own sheets read "sheet 1 of 20" through
"sheet 20 of 20". The extra was page 3, carrying ten words of orphaned
signature strip pushed off the Kitchen's sheet by its seven zones.

That matters more than its size suggests. This pack is the single asset search
actually sends people to, printing it is the whole point of it, and a stranger
who prints the free thing and gets a wasted page with a stray footer has
learned something about how carefully the rest was made.

No other check in this repository can see it. The HTML validates, every link
resolves, the visual audit passes at two widths, and all of that is true of a
document that paginates wrong, because pagination only exists once something
lays the pages out.

    python ops/check_pack_pages.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "site", "downloads", "6S-Standards-Pack.html")
MARKER = re.compile(r"SHEET (\d+) OF (\d+)", re.I)


def render(pdf_path: str):
    """(ok, detail). ok is None when this environment cannot render at all."""
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import browser as B
        exe, extra = B.find_browser()
    except Exception as e:                                      # noqa: BLE001
        return None, "no browser here (%s)" % type(e).__name__
    if not exe:
        return None, "no browser here"
    src = os.path.abspath(PACK).replace(os.sep, "/")
    cmd = ([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            "--print-to-pdf=" + pdf_path, "--virtual-time-budget=8000"]
           + list(extra or []) + ["file:///" + src])
    try:
        subprocess.run(cmd, capture_output=True, timeout=300)
    except Exception as e:                                      # noqa: BLE001
        return None, "render failed (%s)" % type(e).__name__
    if not os.path.exists(pdf_path):
        return None, "renderer wrote no file"
    return True, ""


def audit():
    """(pages, claimed, orphans, note). pages is None when unchecked."""
    if not os.path.exists(PACK):
        return None, None, [], "the pack is not in this checkout"
    tmp = os.path.join(tempfile.mkdtemp(), "pack.pdf")
    ok, detail = render(tmp)
    if ok is None:
        return None, None, [], detail
    try:
        from pypdf import PdfReader
    except ImportError:
        return None, None, [], "pypdf is not installed here"
    r = PdfReader(tmp)
    claimed, orphans = None, []
    for i, page in enumerate(r.pages, 1):
        text = " ".join((page.extract_text() or "").split())
        m = MARKER.search(text)
        if m:
            claimed = int(m.group(2))
        else:
            orphans.append(i)
    return len(r.pages), claimed, orphans, ""


def main() -> int:
    pages, claimed, orphans, note = audit()
    if pages is None:
        print("  UNCHECKED: %s. This run proves nothing about the printed pack."
              % note)
        return 0
    print("  pages when printed  %d" % pages)
    print("  sheets it claims    %s" % claimed)
    print("  pages with no sheet marker  %s" % (orphans or "none"))
    if claimed and pages != claimed:
        print("\n  The pack prints %d pages and calls itself %d sheets. A "
              "reader printing it wastes paper on %d page(s)."
              % (pages, claimed, pages - claimed))
        return 1
    if orphans:
        print("\n  Orphaned page(s) carrying no sheet: %s" % orphans)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
