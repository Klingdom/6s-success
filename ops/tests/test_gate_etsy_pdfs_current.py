#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_etsy_pdfs_current() catches a delivered Etsy
PDF going stale against the HTML it is rendered from.

Found 2026-09-13: build/listings/build_etsy_assets.py renders each listing's
PDF once, by hand, and nothing had ever re-run it since 2026-09-03, even
though build/6S-Whole-House-Print-Pack.html was substantively regenerated
2026-09-07 (the Sustain rewrite) and the Kitchen pack's own source carries
the same rewrite. check_etsy.py only checks page/card COUNTS, both of which
stayed identical because no card was added or removed, only its text
improved, so a listing this stale sailed through every existing check.

Builds a small, isolated git repository per case with a real, tiny HTML
fixture rendered through the real headless-Chromium path (this operator
sandbox ships one at /opt/pw-browsers/chromium; $ETSY_BROWSER overrides), the
same "run the real subprocess, not a mock" approach
test_gate_kdp_cover_current.py already uses for Pillow.

Run:  python ops/tests/test_gate_etsy_pdfs_current.py
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
    import pymupdf
except ImportError:
    pymupdf = None


def _find_real_browser():
    for c in ("/opt/pw-browsers/chromium",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(c):
            return c
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


# A faithful, tiny stand-in for the real build_etsy_assets.py: same contract
# (find_browser(), a LISTINGS/INSTRUCTIONS table, render one HTML to PDF via
# --print-to-pdf), so the gate under test runs the real subprocess and the
# real render path rather than a mock, just against fixture-sized content.
FIXTURE_SCRIPT = '''\
import os, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.join(ROOT, "build", "listings")
OUT = os.path.join(HERE, "etsy")

LISTINGS = [("T1-tiny", "build/tiny-source.html", "Tiny-Pack.pdf")]
INSTRUCTIONS = ("build/listings/print-instructions.html", "How-to-print.pdf")


def find_browser():
    override = os.environ.get("ETSY_BROWSER")
    if override and os.path.exists(override):
        return override
    for c in (r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
              "/opt/pw-browsers/chromium"):
        if os.path.exists(c):
            return c
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def render(browser, src_rel, dest):
    url = "file:///" + os.path.abspath(os.path.join(ROOT, src_rel)).replace(os.sep, "/")
    flags = [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             "--print-to-pdf=" + dest, url]
    if os.name != "nt" and hasattr(os, "geteuid") and os.geteuid() == 0:
        flags.insert(1, "--no-sandbox")
    subprocess.run(flags, capture_output=True, timeout=120)


def main():
    browser = find_browser()
    if not browser:
        print("FAIL: no headless Chromium-family browser found (checked "
              "Edge on Windows, Playwright's Chromium, and PATH).")
        return 1
    for slug, src, pdfname in LISTINGS:
        ddir = os.path.join(OUT, slug, "files")
        os.makedirs(ddir, exist_ok=True)
        dest = os.path.join(ddir, pdfname)
        render(browser, src, dest)
        if not os.path.exists(dest):
            print("FAIL: no PDF produced for " + slug)
            return 1
    for slug in sorted({s for s, _, _ in LISTINGS}):
        dest = os.path.join(OUT, slug, "files", INSTRUCTIONS[1])
        render(browser, INSTRUCTIONS[0], dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args),
                          capture_output=True, text=True)


def _body(text):
    return ("<!doctype html><html><head><meta charset='utf-8'></head>"
            "<body><p>%s</p></body></html>" % text)


def _write_fixture(tmp, body_text, browser_disabled=False):
    os.makedirs(os.path.join(tmp, "build", "listings"), exist_ok=True)
    script = FIXTURE_SCRIPT
    if browser_disabled:
        script = script.replace(
            "def find_browser():\n    override = os.environ.get(\"ETSY_BROWSER\")\n"
            "    if override and os.path.exists(override):\n        return override\n",
            "def find_browser():\n    return None\n")
    io.open(os.path.join(tmp, "build", "listings", "build_etsy_assets.py"),
            "w", encoding="utf-8").write(script)
    io.open(os.path.join(tmp, "build", "tiny-source.html"),
            "w", encoding="utf-8").write(_body(body_text))
    io.open(os.path.join(tmp, "build", "listings", "print-instructions.html"),
            "w", encoding="utf-8").write(_body("How to print these cards."))


def _repo(body_text="Original tiny listing text.", render_first=True,
         browser_disabled=False):
    tmp = tempfile.mkdtemp()
    _write_fixture(tmp, body_text, browser_disabled=browser_disabled)
    _git(tmp, "init", "-q")
    _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A")
    _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t",
         "commit", "-q", "-m", "initial")
    if render_first:
        env = {**os.environ}
        browser = _find_real_browser()
        if browser:
            env["ETSY_BROWSER"] = browser
        subprocess.run([sys.executable,
                        os.path.join(tmp, "build", "listings",
                                     "build_etsy_assets.py")],
                       cwd=tmp, capture_output=True, env=env)
        _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A")
        _git(tmp, "-c", "user.email=t@example.com", "-c", "user.name=t",
             "commit", "-q", "-m", "rendered pdfs")
    return tmp


def _run_gate(tmp, browser=None):
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    old_env = os.environ.get("ETSY_BROWSER")
    if browser:
        os.environ["ETSY_BROWSER"] = browser
    try:
        preflight.gate_etsy_pdfs_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        if old_env is None:
            os.environ.pop("ETSY_BROWSER", None)
        else:
            os.environ["ETSY_BROWSER"] = old_env


def main() -> int:
    if pymupdf is None:
        print("SKIP: pymupdf not installed in this environment")
        return 0
    browser = _find_real_browser()
    if not browser:
        print("SKIP: no headless Chromium-family browser in this environment")
        return 0

    fails = []
    repos = []

    # 1. The real, current shape: the PDF really was rendered from the
    #    current source HTML. Clean.
    tmp = _repo()
    repos.append(tmp)
    r, w = _run_gate(tmp, browser)
    if r:
        fails.append("a genuinely current listing was wrongly failed: %r" % (r,))
    status = _git(tmp, "status", "--porcelain").stdout.strip()
    if status:
        fails.append("gate left the tree dirty on a clean run: %r" % (status,))

    # 2. The real regression shape: the source HTML changes (a rewrite, same
    #    as the real Sustain rewrite) after the PDF was last rendered, so the
    #    two now disagree in TEXT while nothing else about the file moved.
    tmp = _repo()
    repos.append(tmp)
    io.open(os.path.join(tmp, "build", "tiny-source.html"), "w",
            encoding="utf-8").write(_body("Rewritten tiny listing text."))
    r, w = _run_gate(tmp, browser)
    if not r or "Tiny-Pack.pdf" not in r[0][1]:
        fails.append("a real source/PDF text drift was not caught by name: %r"
                     % (r,))
    status = _git(tmp, "status", "--porcelain").stdout
    if "Tiny-Pack.pdf" in status:
        fails.append("the gate left the stale PDF modified instead of "
                     "restoring it: %r" % (status,))

    # Note: two back-to-back real renders of identical source are proven
    # byte-different (own metadata/ids) elsewhere in this change, so case 1
    # above, which lets the gate's own internal re-render diff against a
    # commit made by an earlier, separate render, already exercises
    # "byte-different, text-identical must read clean" for real; a dedicated
    # third case here would only repeat it.

    # 3. The Etsy output already differs from HEAD before the gate even
    #    runs: refuse to check rather than diff against a dirty baseline.
    tmp = _repo()
    repos.append(tmp)
    out = os.path.join(tmp, "build", "listings", "etsy", "T1-tiny", "files",
                       "Tiny-Pack.pdf")
    with open(out, "ab") as fh:
        fh.write(b"\x00\x00")
    r, w = _run_gate(tmp, browser)
    if not r or "already differs from HEAD" not in r[0][1]:
        fails.append("a pre-dirty Etsy output was not refused by name: %r"
                     % (r,))

    # 4. No Chromium-family browser can be found: UNCHECKED, never a silent
    #    pass and never a hard fail for an environment gap. The fixture's own
    #    find_browser() always returns None, so the initial render in
    #    _repo() already failed and produced no PDF, matching "cannot
    #    regenerate" rather than a stale-and-dirty tree.
    tmp = _repo(browser_disabled=True)
    repos.append(tmp)
    r, w = _run_gate(tmp)
    if r:
        fails.append("a missing-browser environment was failed instead of "
                     "warned: %r" % (r,))
    if not w or "Chromium-family browser" not in w[0][1]:
        fails.append("a missing-browser environment produced no useful "
                     "warning: %r" % (w,))

    # 5. Neither the script nor the delivered PDFs exist yet: nothing to
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
    print("OK: gate_etsy_pdfs_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
