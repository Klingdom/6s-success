#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_prerender_shop_current() catches
site/shop.html's pre-rendered product grid going stale against what
ops/prerender_shop.py would produce today, and leaves a clean checkout
alone.

Found 2026-09-17, cold-reading ops/prerender_shop.py per this backlog's
own standing cold-read lane: it is a real generator (it drives a headless
browser to write a committed block into site/shop.html, the same shape as
build_etsy_assets.py and build_kdp_cover.py, both already protected by a
dedicated regenerate-and-diff gate), but it was in neither
GENERATOR_OWNERSHIP_CHAIN nor GENERATOR_PROTECTED_ELSEWHERE, and
gate_every_generator_has_a_protection_plan's own glob only ever looks for
`build_*.py`, so a file named prerender_shop.py was invisible to that
meta-gate too, not merely unlisted by it. gate_shop_prerendered only
checks that a pre-rendered block exists and clears a 100-card floor, so
the shop's 159 cards could go stale against a changed catalogue (a price,
a product added or dropped) while staying above that floor forever.

Uses a detached git worktree sharing the real repository's object
database, the same approach test_gate_kitchen_deck_current.py and
test_generator_ownership.py use: prerender_shop.py needs the real
site/shop.html, shop.js and data.js to render anything at all, so a tiny
fixture page cannot stand in for it the way build_kdp_cover.py's fixture
script can.

Run:  python ops/tests/test_gate_prerender_shop_current.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def git(*args, cwd=ROOT, check=True):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                       text=True, timeout=300)
    if check and r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr[:300]))
    return r.stdout


def _run_gate(wt):
    old_root = preflight.ROOT
    preflight.ROOT = wt
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_prerender_shop_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    if os.environ.get("SIXS_UNDER_PREFLIGHT"):
        print("  skipped: preflight is the caller, exercising this gate here "
              "would re-render shop.html mid-run. Run this test directly to "
              "exercise the gate.")
        return 0

    if not shutil.which("git"):
        print("  no git here, cannot exercise the gate. NOT VERIFIED.")
        return 0

    if not preflight.B.find_browser():
        print("  no Chromium-family browser here, cannot exercise the real "
             "render path. NOT VERIFIED.")
        return 0

    tmp = tempfile.mkdtemp(prefix="6s-preshop-")
    wt = os.path.join(tmp, "wt")
    fails = []
    try:
        try:
            git("worktree", "add", "--detach", wt, "HEAD")
        except RuntimeError as e:
            print("  could not create a worktree (%s). NOT VERIFIED." % e)
            return 0

        shop_path = os.path.join(wt, "site", "shop.html")
        if not os.path.exists(shop_path):
            print("  site/shop.html not in this checkout. NOT VERIFIED.")
            return 0

        # 1. The real, current shape: the committed pre-rendered block really
        #    was produced by the real generator from the real catalogue. Clean.
        r, w = _run_gate(wt)
        if r:
            fails.append("a genuinely current shop.html was wrongly failed: "
                         "%r" % (r,))
        status = git("status", "--porcelain", cwd=wt)
        if status.strip():
            fails.append("the gate left the worktree dirty on a clean run: %r"
                         % (status,))

        # 2. The real regression shape: a hand edit inside the pre-rendered
        #    block that the generator itself would never produce (the shape
        #    a stale re-render after a catalogue change would leave behind).
        original = open(shop_path, encoding="utf-8").read()
        needle = "prerendered-shop:start"
        if needle not in original:
            print("  fixture assumption (%r in shop.html) no longer holds. "
                 "NOT VERIFIED." % needle)
            return 0
        start = original.index(needle)
        mutated = (original[:start] + "<!-- stale product grid injected by "
                   "the test -->" + original[start:])
        with open(shop_path, "w", encoding="utf-8") as fh:
            fh.write(mutated)

        r, w = _run_gate(wt)
        if not r or "shop.html" not in r[0][1]:
            fails.append("a real hand edit to the pre-rendered block was not "
                         "caught by name: %r" % (r,))

        # 3. The gate must restore the file either way, win or lose, so a
        #    failed run does not leave the working tree looking like the
        #    fix already happened.
        after = open(shop_path, encoding="utf-8").read()
        if after != mutated:
            fails.append("the gate did not restore the file it diffed "
                         "against back to the mutated on-disk state")

        # 4. Put the real file back and confirm clean again.
        with open(shop_path, "w", encoding="utf-8") as fh:
            fh.write(original)
        r, w = _run_gate(wt)
        if r:
            fails.append("gate not clean after restoring the real file: %r"
                         % (r,))

        # 5. A dirty site/shop.html sitting ahead of HEAD before the gate
        #    even runs must refuse to check, not diff against a moving
        #    target and report a false result either way.
        with open(shop_path, "w", encoding="utf-8") as fh:
            fh.write(original + "\n<!-- uncommitted local edit -->")
        r, w = _run_gate(wt)
        if not r or "already differs from HEAD" not in r[0][1]:
            fails.append("a dirty shop.html ahead of HEAD was not refused: "
                         "%r" % (r,))
        with open(shop_path, "w", encoding="utf-8") as fh:
            fh.write(original)
        git("checkout", "--", "site/shop.html", cwd=wt)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", wt],
                       cwd=ROOT, capture_output=True, text=True)
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_prerender_shop_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
