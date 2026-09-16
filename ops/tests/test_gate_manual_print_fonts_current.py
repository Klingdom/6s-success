#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_manual_print_fonts_current() catches
content/manual/print/6S-Micro-Zone-Manual-PRINT-7x10.html embedding font data
that no longer matches site/assets/fonts/*.woff2.

Real shape found 2026-09-16: commit 7e7d1db7 (2026-09-15, Phil) re-cut two
font files from full variable fonts down to the single weight the CSS
actually declares, roughly halving their size. Nothing reran
ops/build_manual_print.py afterward, so the committed print edition kept
embedding the old, larger font bytes for both faces, invisible to
gate_front_matter_filled (the only check already mapped to this generator,
and it only looks at the copyright page) and to gate_generator_ownership
(which never reaches this generator, since it lives outside ops/... no,
inside ops/ but the print file's font-embedding step is not part of that
gate's own diff set). Same regenerate-and-diff method as
gate_kdp_cover_current: a small fixture stands in for the real generator's
font-embedding contract (read a font file, base64 it into the print HTML),
so this test never touches the real, large woff2 files or the real
content.json/products.json pipeline the real script also needs.

Run:  python ops/tests/test_gate_manual_print_fonts_current.py
"""
import base64
import io
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

OUT_REL = "content/manual/print/6S-Micro-Zone-Manual-PRINT-7x10.html"
MANUAL_REL = "content/manual/6S Home Micro Zone SOP Field Manual v3.html"
PUBLISHABLE_REL = "content/manual/micro-zone-manual-publishable.html"

# A faithful, minimal stand-in for the real build_manual_print.py: same
# contract for the one thing this gate protects (embed the current font
# file's bytes as base64 into the print edition), so the gate under test
# runs the real subprocess path rather than a mock.
FIXTURE_SCRIPT = """\
import base64, io, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT = os.path.join(ROOT, "site", "assets", "fonts", "Fake-400-normal.woff2")
OUT = os.path.join(ROOT, "content", "manual", "print",
                    "6S-Micro-Zone-Manual-PRINT-7x10.html")


def main():
    b64 = base64.b64encode(io.open(FONT, "rb").read()).decode("ascii")
    doc = "<html><style>@font-face{src:url(data:font/woff2;base64,%s)}" \\
          "</style></html>\\n" % b64
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="").write(doc)
    print("wrote " + OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""

RAISER_SCRIPT = "raise SystemExit('regenerate refused: no source')\n"


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args),
                          capture_output=True, text=True)


def _repo(font_bytes=b"FAKE-FONT-V1", script=FIXTURE_SCRIPT,
          run_fixture_first=True):
    """A fresh git repo with a committed font file, script and print file."""
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "ops"))
    os.makedirs(os.path.join(tmp, "site", "assets", "fonts"))
    os.makedirs(os.path.join(tmp, "content", "manual", "print"))
    io.open(os.path.join(tmp, "site", "assets", "fonts", "Fake-400-normal.woff2"),
            "wb").write(font_bytes)
    io.open(os.path.join(tmp, "ops", "build_manual_print.py"),
            "w", encoding="utf-8").write(script)
    # The other two files the real generator also writes. Their content
    # never matters to this gate (they carry no embedded font), only that
    # git has something to restore them to.
    io.open(os.path.join(tmp, MANUAL_REL), "w", encoding="utf-8").write("<html></html>\n")
    io.open(os.path.join(tmp, PUBLISHABLE_REL), "w", encoding="utf-8").write("<html></html>\n")
    _git(tmp, "init", "-q")
    _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A")
    _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t",
         "commit", "-q", "-m", "initial")
    if run_fixture_first:
        subprocess.run([sys.executable, os.path.join(tmp, "ops", "build_manual_print.py")],
                       cwd=tmp, capture_output=True)
        _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A")
        _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t",
             "commit", "-q", "-m", "rendered print edition")
    return tmp


def _run_gate(tmp):
    old_root, old_py = preflight.ROOT, preflight.PY
    preflight.ROOT = tmp
    preflight.PY = sys.executable
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_manual_print_fonts_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT, preflight.PY = old_root, old_py


def main() -> int:
    fails = []
    repos = []

    # 1. The real, current shape: the print file really was produced by the
    #    script from the current font file. Clean, and the tree stays clean.
    tmp = _repo()
    repos.append(tmp)
    r, w = _run_gate(tmp)
    if r:
        fails.append("a genuinely current print file was wrongly failed: %r" % (r,))
    if _git(tmp, "status", "--porcelain").stdout.strip():
        fails.append("gate left the tree dirty on a clean run: %r"
                     % (_git(tmp, "status", "--porcelain").stdout,))

    # 2. The real regression shape: the font file changes (a re-cut face)
    #    after the print file was last committed, so the two now disagree.
    tmp = _repo()
    repos.append(tmp)
    io.open(os.path.join(tmp, "site", "assets", "fonts", "Fake-400-normal.woff2"),
            "wb").write(b"FAKE-FONT-V2-SMALLER")
    r, w = _run_gate(tmp)
    if not r or "PRINT-7x10.html" not in r[0][1] or "stale font data" not in r[0][1]:
        fails.append("a real font/print-file drift was not caught by name: %r" % (r,))
    status = _git(tmp, "status", "--porcelain").stdout
    if OUT_REL.split("/")[-1] in status:
        fails.append("the gate left the print file modified instead of "
                     "restoring it: %r" % (status,))
    if "Fake-400-normal.woff2" not in status:
        fails.append("the test's own font edit vanished unexpectedly")

    # 3. The print file already differs from HEAD before the gate even
    #    runs: refuse to check rather than diff against a dirty baseline.
    tmp = _repo()
    repos.append(tmp)
    out = os.path.join(tmp, OUT_REL)
    with open(out, "ab") as fh:
        fh.write(b"<!-- dirty -->")
    r, w = _run_gate(tmp)
    if not r or "already differs from HEAD" not in r[0][1]:
        fails.append("a pre-dirty print file was not refused by name: %r" % (r,))

    # 4. The script itself cannot regenerate (its real-world analogue: a
    #    missing source). A real problem with the mechanism, not a clean
    #    bill of health just because nothing moved on disk.
    tmp = _repo(script=RAISER_SCRIPT, run_fixture_first=False)
    repos.append(tmp)
    # Still need a committed print file to diff against.
    io.open(os.path.join(tmp, OUT_REL), "w", encoding="utf-8").write("<html>placeholder</html>\n")
    _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A")
    _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t",
         "commit", "-q", "-m", "placeholder print edition")
    r, w = _run_gate(tmp)
    if not r or "could not regenerate" not in r[0][1]:
        fails.append("the regenerator's own failure was not surfaced: %r" % (r,))

    # 5. Neither the script nor the rendered file exists yet: nothing to
    #    check, not a failure.
    tmp = tempfile.mkdtemp()
    repos.append(tmp)
    os.makedirs(os.path.join(tmp, "ops"))
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
    print("OK: gate_manual_print_fonts_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
