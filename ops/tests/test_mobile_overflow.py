"""Prove ops/shoot_mobile.py can return both verdicts, not just the one the
site happens to be in today.

Every page currently measures clean, so a broken probe and a healthy site are
indistinguishable from the gate's output. This builds a page that genuinely
overflows and a page that genuinely does not, and requires the tool to tell
them apart. Without this the gate could silently become a rubber stamp, which
is the exact failure this project has already hit several times.
"""
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
TOOL = os.path.join(ROOT, "ops", "shoot_mobile.py")

EDGES = (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
         r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")

SHELL = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>probe fixture</title></head><body>%s</body></html>"""

WIDE = SHELL % '<div style="width:900px;height:40px;background:#333"></div>'
NARROW = SHELL % '<div style="width:100%;height:40px;background:#333"></div>'
CONTAINED = SHELL % ('<div style="overflow-x:auto"><div style="width:900px;'
                     'height:40px;background:#333"></div></div>')


def measure(name: str, html: str) -> str:
    path = os.path.join(SITE, name)
    io.open(path, "w", encoding="utf-8", newline="").write(html)
    try:
        r = subprocess.run([sys.executable, TOOL, "site/" + name], cwd=ROOT,
                           capture_output=True, text=True, timeout=300,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    finally:
        os.remove(path)
        # The tool writes a screenshot per page it renders. Leaving three
        # fixture PNGs behind in build/shots makes a review of that directory
        # show pages that are not part of the site.
        stem = os.path.splitext(name)[0]
        for w in (360, 390, 768):
            shot = os.path.join(ROOT, "build", "shots", "%s-%d.png" % (stem, w))
            if os.path.exists(shot):
                os.remove(shot)
    return (r.stdout or "") + (r.stderr or "")


def main() -> int:
    if not any(os.path.exists(e) for e in EDGES):
        print("  no Edge here, cannot exercise the probe. NOT VERIFIED.")
        return 0
    if not os.path.exists(TOOL):
        print("  FAIL ops/shoot_mobile.py is missing")
        return 1

    bad = []

    out = measure("_fixture_wide.html", WIDE)
    if "OVERFLOWING" not in out:
        bad.append("a 900px block on a 390px screen was NOT reported:\n" + out)

    out = measure("_fixture_narrow.html", NARROW)
    if "clean at 390px" not in out:
        bad.append("a page that fits was not reported clean:\n" + out)

    out = measure("_fixture_contained.html", CONTAINED)
    if "clean at 390px" not in out:
        bad.append("a wide block inside overflow-x:auto is contained by "
                   "design and must not be reported:\n" + out)

    # The tool must refuse to report on a viewport it did not get.
    out = measure("_fixture_narrow.html", NARROW)
    if "viewport" in out and "390px" not in out:
        bad.append("reported on a width it did not render:\n" + out)

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  probe distinguishes overflow, fit, and contained overflow")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
