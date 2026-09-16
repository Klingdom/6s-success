#!/usr/bin/env python3
"""
A real dead link must still be caught; a legitimate href="#" placeholder
must not be false-flagged just because its script sets .href on a variable
instead of on the raw $("#id") call.

Found 2026-09-16: Phil's own commit 0ab37390 added the "Watch this zone"
row to quest.js, which does
    var watchLink = $("#c-watch-video");
    watchLink.href = "https://www.youtube.com/watch?v=" + c.zone.video;
instead of the single-line $("#c-watch-video").href = ... shape the
original _count_dead_links() heuristic required. That made a live,
correctly-wired link (verified by Phil in a real browser) read as
"1 dead link" on the executive dashboard, a false alarm rather than a
real defect. _count_dead_links() now also recognises the two-step
var-then-.href shape.

dashboard.py runs its whole pipeline at import, so the function is lifted
out of the source rather than imported, matching
test_dashboard_prev_state_fallback.py's own method for the same reason.

Run:  python ops/tests/test_dashboard_dead_links.py
"""
import glob
import os
import re
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "ops", "dashboard.py")

src = open(SRC, encoding="utf-8").read()
ns = {"glob": glob, "os": os, "re": re, "ROOT": ROOT}
m = re.search(r"^def read\(.*?(?=\n\n# ---)", src, re.S | re.M)
exec(m.group(0), ns)
m = re.search(r"^def _count_dead_links.*?(?=\n\nS\[)", src, re.S | re.M)
exec(m.group(0), ns)
count_dead_links = ns["_count_dead_links"]


def main() -> int:
    fails = []

    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "site", "assets", "js"))
        html = os.path.join(d, "page.html")
        js = os.path.join(d, "site", "assets", "js", "app.js")

        old_root = ns["ROOT"]
        ns["ROOT"] = d
        try:
            # A link with no script reference at all is genuinely dead.
            open(html, "w", encoding="utf-8").write(
                '<a id="c-real-dead" href="#">nowhere</a>')
            open(js, "w", encoding="utf-8").write(
                "// no reference to c-real-dead at all")
            n = count_dead_links([html])
            if n != 1:
                fails.append(f"a genuine dead link must be caught, got {n}")

            # The direct $("#id").href = ... shape (the original, still-
            # supported case) must not be flagged.
            open(html, "w", encoding="utf-8").write(
                '<a id="c-zone-link" href="#">read more</a>')
            open(js, "w", encoding="utf-8").write(
                '$("#c-zone-link").href = c.zone.url;')
            n = count_dead_links([html])
            if n != 0:
                fails.append(f"direct $(\"#id\").href shape false-flagged, got {n}")

            # The real regression shape: $("#id") assigned to a variable,
            # then .href set on that variable later. Must not be flagged.
            open(html, "w", encoding="utf-8").write(
                '<a id="c-watch-video" href="#" hidden>watch</a>')
            open(js, "w", encoding="utf-8").write(
                'var watchLink = $("#c-watch-video");\n'
                'watchLink.hidden = false;\n'
                'watchLink.href = "https://www.youtube.com/watch?v=x";')
            n = count_dead_links([html])
            if n != 0:
                fails.append(f"indirect var-then-.href shape false-flagged, got {n}")

            # A same-named variable used for an unrelated id must not mask
            # a genuinely dead second link.
            open(html, "w", encoding="utf-8").write(
                '<a id="c-watch-video" href="#" hidden>watch</a>'
                '<a id="c-other-dead" href="#">nowhere</a>')
            n = count_dead_links([html])
            if n != 1:
                fails.append(
                    "a real link's own script must not hide an unrelated "
                    f"dead link, got {n} (expected 1)")

            # An anchor with no id attribute at all must still count as dead.
            open(html, "w", encoding="utf-8").write('<a href="#">nowhere</a>')
            open(js, "w", encoding="utf-8").write("")
            n = count_dead_links([html])
            if n != 1:
                fails.append(f"an id-less href=\"#\" must count as dead, got {n}")
        finally:
            ns["ROOT"] = old_root

    total = 5
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
