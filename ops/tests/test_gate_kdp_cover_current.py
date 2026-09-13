#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kdp_cover_current() catches
build/listings/kdp/cover-kdp.jpg going stale against build/cover.png.

build/listings/build_kdp_cover.py is the only thing that produces that file,
and it lives under build/listings/, outside GENERATOR_OWNERSHIP_CHAIN (which
only reruns generators under ops/) and outside
gate_every_generator_has_a_protection_plan's own ops/build_*.py glob. So a
future edit to build/cover.png could leave the cover Phil is told to upload
to KDP (OWNER-ACTIONS.md item 14) silently out of date, the same
"source corrected, artifact never re-derived" shape this repository's own
gates exist to catch elsewhere. This gate closes that gap with the same
regenerate-and-diff method gate_generator_ownership uses, scoped to this one
file since it sits outside that gate's ops/-only reach.

Builds a small, isolated git repository per case rather than touching the
real, large build/cover.png, the same fixture-over-real-asset approach
test_gate_kdp_word_count_current.py already uses for its EPUB.

Run:  python ops/tests/test_gate_kdp_cover_current.py
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

try:
    from PIL import Image
except ImportError:
    Image = None

WIDTH, HEIGHT = 60, 80
BAND_TOP, BAND_BOTTOM = 40, 50
BACKGROUND = (247, 242, 233)
BAND_COLOR = (10, 10, 10)

# A faithful, smaller stand-in for the real build_kdp_cover.py: same
# contract (read build/cover.png, paint the band with the sampled
# background, refuse without writing if there is nothing to remove or the
# source is missing), so the gate under test runs the real subprocess path
# rather than a mock.
FIXTURE_SCRIPT = '''\
import os, sys
from PIL import Image, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "build", "cover.png")
OUT = os.path.join(ROOT, "build", "listings", "kdp", "cover-kdp.jpg")
BAND_TOP, BAND_BOTTOM = %d, %d


def main():
    if not os.path.exists(SRC):
        print("FAIL: no source cover")
        return 1
    img = Image.open(SRC).convert("RGB")
    width, height = img.size
    background = img.getpixel((2, height - 2))
    before = img.crop((0, BAND_TOP, width, BAND_BOTTOM))
    blank = Image.new("RGB", before.size, background)
    if not ImageChops.difference(before, blank).getbbox():
        print("Nothing to remove")
        return 1
    img.paste(blank, (0, BAND_TOP))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "JPEG", quality=92)
    print("wrote " + OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (BAND_TOP, BAND_BOTTOM)

RAISER_SCRIPT = (
    "import sys\n"
    "sys.path.insert(0, '/does/not/exist')\n"
    "import totally_not_a_real_pillow_module\n"
)


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args),
                          capture_output=True, text=True)


def _make_cover(path, band_color=BAND_COLOR, corner=BACKGROUND):
    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    px = img.load()
    px[2, HEIGHT - 2] = corner
    for y in range(BAND_TOP, BAND_BOTTOM):
        for x in range(WIDTH):
            px[x, y] = band_color
    img.save(path)


def _repo(cover_band_color=BAND_COLOR, run_fixture_first=True):
    """A fresh git repo with a committed cover.png, script and cover-kdp.jpg."""
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "build", "listings"))
    _make_cover(os.path.join(tmp, "build", "cover.png"), cover_band_color)
    io.open(os.path.join(tmp, "build", "listings", "build_kdp_cover.py"),
            "w", encoding="utf-8").write(FIXTURE_SCRIPT)
    _git(tmp, "init", "-q")
    _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A")
    _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t",
         "commit", "-q", "-m", "initial")
    if run_fixture_first:
        subprocess.run([sys.executable,
                        os.path.join(tmp, "build", "listings",
                                     "build_kdp_cover.py")],
                       cwd=tmp, capture_output=True)
        _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A")
        _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t",
             "commit", "-q", "-m", "rendered cover")
    return tmp


def _run_gate(tmp):
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_kdp_cover_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    if Image is None:
        print("SKIP: Pillow not installed in this environment")
        return 0

    fails = []
    repos = []

    # 1. The real, current shape: cover-kdp.jpg really was produced by the
    #    script from the current cover.png. Clean.
    tmp = _repo()
    repos.append(tmp)
    r, w = _run_gate(tmp)
    if r:
        fails.append("a genuinely current cover was wrongly failed: %r" % (r,))
    if _git(tmp, "status", "--porcelain").stdout.strip():
        fails.append("gate left the tree dirty on a clean run: %r"
                     % (_git(tmp, "status", "--porcelain").stdout,))

    # 2. The real regression shape: cover.png changes (a new strapline)
    #    after cover-kdp.jpg was last committed, so the two now disagree.
    tmp = _repo()
    repos.append(tmp)
    _make_cover(os.path.join(tmp, "build", "cover.png"), corner=(1, 2, 3))
    r, w = _run_gate(tmp)
    if not r or "cover-kdp.jpg" not in r[0][1] or "stale cover" not in r[0][1]:
        fails.append("a real cover/cover-kdp.jpg drift was not caught by "
                     "name: %r" % (r,))
    status = _git(tmp, "status", "--porcelain").stdout
    if "cover-kdp.jpg" in status:
        fails.append("the gate left cover-kdp.jpg modified instead of "
                     "restoring it: %r" % (status,))
    if "cover.png" not in status:
        fails.append("the test's own cover.png edit vanished unexpectedly")

    # 3. cover-kdp.jpg already differs from HEAD before the gate even runs:
    #    refuse to check rather than diff against a dirty baseline, and do
    #    not touch the fixture script (would leave a mid-air rewrite).
    tmp = _repo()
    repos.append(tmp)
    out = os.path.join(tmp, "build", "listings", "kdp", "cover-kdp.jpg")
    with open(out, "ab") as fh:
        fh.write(b"\\x00\\x00")
    r, w = _run_gate(tmp)
    if not r or "already differs from HEAD" not in r[0][1]:
        fails.append("a pre-dirty cover-kdp.jpg was not refused by name: %r"
                     % (r,))

    # 4. The regenerator cannot even import Pillow: UNCHECKED, never a
    #    silent pass and never a hard fail for an environment gap.
    tmp = _repo()
    repos.append(tmp)
    io.open(os.path.join(tmp, "build", "listings", "build_kdp_cover.py"),
            "w", encoding="utf-8").write(RAISER_SCRIPT)
    r, w = _run_gate(tmp)
    if r:
        fails.append("a missing-dependency environment was failed instead "
                     "of warned: %r" % (r,))
    if not w or "Pillow" not in w[0][1]:
        fails.append("a missing-dependency environment produced no useful "
                     "warning: %r" % (w,))

    # 5. The script itself refuses to write (its own "nothing to remove"
    #    safety check trips, e.g. the band moved and the script's
    #    coordinates no longer find it): a real problem with the mechanism,
    #    not a clean bill of health just because nothing moved on disk.
    tmp = _repo()
    repos.append(tmp)
    _make_cover(os.path.join(tmp, "build", "cover.png"),
                band_color=BACKGROUND)  # band already == background
    r, w = _run_gate(tmp)
    if not r or "could not regenerate" not in r[0][1]:
        fails.append("the regenerator's own safety refusal was not "
                     "surfaced as a real failure: %r" % (r,))

    # 6. Neither the script nor the rendered file exists yet: nothing to
    #    check, not a failure.
    tmp = tempfile.mkdtemp()
    repos.append(tmp)
    os.makedirs(os.path.join(tmp, "build", "listings"))
    r, w = _run_gate(tmp)
    if r or w:
        fails.append("an environment with neither file present was not "
                     "silently skipped: FAIL=%r WARN=%r" % (r, w))

    for tmp in repos:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_kdp_cover_current, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
