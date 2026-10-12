#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_image_prompts_tiers_current() catches the
three committed content/images/prompts/tier-*-prompts.md files drifting
from what ops/build_image_prompts.py would write right now.

Added 2026-10-12, cold-reading ops/build_image_prompts.py: content.json's
own text had been swept from British to American spelling, but tier-1 and
tier-2-prompts.md, which copy that text verbatim, were never regenerated.
No prior gate covered this (gate_no_british_spellings_shipped deliberately
scopes to site/**/*.html and ops/cardtext/build_*.py, not this internal
intake file), so the committed prompt files could drift from their own
generator indefinitely with nothing to catch it. Mirrors
test_gate_feed_current.py's own regenerate-and-diff proof shape.

Run:  python ops/tests/test_gate_image_prompts_tiers_current.py
"""
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_image_prompts as bip                              # noqa: E402

TIER1 = os.path.join(ROOT, "content", "images", "prompts", "tier-1-prompts.md")


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_image_prompts_tiers_current()
    return list(preflight.FAIL), list(preflight.WARN)


def main() -> int:
    fails = []

    # 1. The real, committed tier files: clean.
    f, w = _run()
    if f:
        fails.append("the real committed tier prompt files failed: %r" % (f,))

    # 2. A stale tier-1 file (one word hand-edited back to British spelling)
    #    must fail, named, pointing at the right file.
    real = io.open(TIER1, encoding="utf-8").read()
    if "unlabeled" not in real:
        fails.append("tier-1-prompts.md no longer contains \"unlabeled\"; "
                      "the planted-regression word needs updating")
    stale = real.replace("unlabeled", "unlabelled", 1)
    backup = TIER1 + ".bak"
    shutil.copy2(TIER1, backup)
    try:
        io.open(TIER1, "w", encoding="utf-8", newline="").write(stale)
        f, w = _run()
        if not f or "image-prompts-tiers-current" not in f[0][0]:
            fails.append("a stale, hand-edited tier-1-prompts.md was not "
                         "caught by name: %r" % (f,))
        elif "tier-1-prompts.md" not in f[0][1]:
            fails.append("the gate failed but did not name tier-1-prompts.md: "
                         "%r" % (f,))
    finally:
        shutil.copy2(backup, TIER1)
        os.remove(backup)

    # 3. A missing tier-1 file must fail, naming it as missing.
    shutil.move(TIER1, TIER1 + ".bak2")
    try:
        f, w = _run()
        if not f or "missing" not in f[0][1]:
            fails.append("a missing tier-1-prompts.md was not caught: %r"
                         % (f,))
    finally:
        shutil.move(TIER1 + ".bak2", TIER1)

    # 4. bip.all_items() actually found real prompts, so check #1 above was
    #    not vacuously passing on an empty corpus.
    items = bip.all_items()
    if len(items) < 100:
        fails.append("build_image_prompts.all_items() found only %d prompts, "
                      "expected 200+; the loader may be silently failing to "
                      "match the real content.json shape." % len(items))

    # 5. Re-verify the real files are clean after the restore, not left
    #    dirty by test 2 or 3's swap.
    f, w = _run()
    if f:
        fails.append("the tier prompt files were left dirty after the drift "
                     "test: %r" % (f,))

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_image_prompts_tiers_current, 5/5 checks pass "
          "(%d real prompts)" % len(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
