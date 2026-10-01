#!/usr/bin/env python3
"""
Prove ops/review_deck_art.py's mark() preserves a prior --why note across a
later re-mark, instead of destroying it.

Found 2026-10-01, cold-reading ops/review_deck_art.py per the standing
cold-read lane. ops/review_heroes.py's own mark() carried this identical
defect until 2026-09-21: it wrote a fresh two-key {"verdict", "sha"} dict on
every mark, so any reason recorded beside a verdict was silently destroyed
the next time somebody re-marked that image (see that file's own comment on
the fix). review_deck_art.py never got the fix, and never had a --why flag
at all: it reviews card sheets, the same kind of one-off human judgement
call, for the same reason a reviewer would want to record ("callout pin
points at the wrong drawer") and have it survive. No live data loss has
happened yet (ops/deck-art-verdicts.json has never been created, since card
generation is still billing-gated), which is exactly why this is worth
fixing now rather than waiting for the first real rejection to lose its own
reason the way ET-003's did before the sibling fix.

Run:  python ops/tests/test_review_deck_art.py
"""
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "ops", "review_deck_art.py")


def _load_isolated(stage_dir, verdicts_path):
    spec = importlib.util.spec_from_file_location("review_deck_art_iso", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.STAGE = stage_dir
    mod.CONTACT = os.path.join(stage_dir, "_contact")
    mod.INDEX = os.path.join(mod.CONTACT, "index.json")
    mod.VERDICTS = verdicts_path
    return mod


def _make_sheet(stage_dir, deck, name, content=b"not a real image, just bytes"):
    d = os.path.join(stage_dir, deck)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "wb") as fh:
        fh.write(content)
    return f"{deck}/{name}"


def main() -> int:
    fails = []
    tmp = tempfile.mkdtemp()
    try:
        stage = os.path.join(tmp, "deck-review")
        os.makedirs(stage)
        rel = _make_sheet(stage, "entryway", "sheet-001.png")
        verdicts_path = os.path.join(tmp, "deck-art-verdicts.json")
        mod = _load_isolated(stage, verdicts_path)

        # Build the index by hand rather than calling sheets(): that function
        # imports PIL to render contact sheets, which this sandbox does not
        # have, and the index format (a plain {"1": "deck/file"} map) is a
        # stable, documented contract independent of the rendering step.
        mod.save(mod.INDEX, {"1": rel})

        # 1. Reject with a reason.
        mod.mark("no", "1", "callout pin points at the wrong drawer")
        v = mod.load(mod.VERDICTS)
        rec = v.get(rel, {})
        if rec.get("verdict") != "no":
            fails.append("first mark did not record verdict=no: %r" % (rec,))
        if rec.get("why") != "callout pin points at the wrong drawer":
            fails.append("first mark did not record why: %r" % (rec,))

        # 2. Re-mark the SAME image (sha unchanged) with no --why: the reason
        #    must survive, matching review_heroes.py's own fixed behaviour.
        mod.mark("no", "1")
        v = mod.load(mod.VERDICTS)
        rec = v.get(rel, {})
        if rec.get("why") != "callout pin points at the wrong drawer":
            fails.append(
                "re-mark with no --why destroyed the prior reason: %r" % (rec,))
        if rec.get("verdict") != "no":
            fails.append("re-mark lost the verdict itself: %r" % (rec,))

        # 3. A new --why on a later mark replaces the old one (explicit,
        #    not silent): the reviewer said something different this time.
        mod.mark("no", "1", "actually: colour drifted from the rest of the deck")
        v = mod.load(mod.VERDICTS)
        rec = v.get(rel, {})
        if rec.get("why") != "actually: colour drifted from the rest of the deck":
            fails.append("explicit new --why was not applied: %r" % (rec,))

        # 4. The sheet's pixels change (regenerated): verdict_of() must treat
        #    the old verdict as not-about-this-image any more.
        with open(os.path.join(stage, "entryway", "sheet-001.png"), "wb") as fh:
            fh.write(b"different bytes entirely")
        stale = mod.verdict_of(rel, mod.load(mod.VERDICTS))
        if stale != "":
            fails.append(
                "verdict_of() returned %r for a sheet whose pixels changed, "
                "should be '' (unjudged)" % (stale,))

        # 5. approve() path also preserves prior data (ok, not just no).
        mod.mark("ok", "1")
        v = mod.load(mod.VERDICTS)
        rec = v.get(rel, {})
        if rec.get("verdict") != "ok":
            fails.append("ok mark did not stick: %r" % (rec,))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS (5/5)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
