#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_linkedin_drafts_customer_count_current()
catches ops/linkedin_drafts.py's hardcoded "Customers to date: N" literal
disagreeing with GOALS.md's own baseline sentence.

Found 2026-09-19, cold-reading ops/linkedin_drafts.py per the standing
low-mention ops/*.py lane: every other factual claim in the daily draft
email is read from a live source at generation time, per that file's own
stated hard rule, but "Customers to date: 1, and that one was a referral."
is a plain literal. gate_linkedin_drafts_price_current already exists to
catch exactly this shape of drift one line above, for the eBook price.
This gate is the same idea applied to the customer count, cross-checked
against GOALS.md's own "$... lifetime, N customer" baseline sentence
instead of a live catalogue, because no live source for this fact reaches
this repository.

Run:  python ops/tests/test_gate_linkedin_drafts_customer_count_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

DRAFT_TMPL = (
    "L += [\"\", \"WHAT IS TRUE TODAY, so nothing above overstates it:\",\n"
    "      \"  Customers to date: %d, and that one was a referral.\", \"\"]\n"
)
GOALS_TMPL = "**Baseline:** $19 lifetime, %s customer, one sale (2026-08-21)."


def _run(draft_count, goals_text):
    tmp = tempfile.mkdtemp()
    ops_dir = os.path.join(tmp, "ops")
    os.makedirs(ops_dir)
    io.open(os.path.join(ops_dir, "linkedin_drafts.py"), "w",
            encoding="utf-8").write(DRAFT_TMPL % draft_count)
    if goals_text is not None:
        io.open(os.path.join(tmp, "GOALS.md"), "w",
                encoding="utf-8").write(goals_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_linkedin_drafts_customer_count_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: draft says 1, GOALS.md says two. Must fail.
    r, w = _run(1, GOALS_TMPL % "two")
    if not r or "linkedin-drafts-customer-count" != r[0][0]:
        fails.append("a stale draft count was not caught: %r" % (r,))

    # 2. Draft and GOALS.md agree (both one): no failure.
    r, w = _run(1, GOALS_TMPL % "one")
    if r:
        fails.append("matching counts were wrongly flagged: %r" % (r,))

    # 3. Draft and GOALS.md agree (both zero, a pre-launch shape): no failure.
    r, w = _run(0, GOALS_TMPL % "zero")
    if r:
        fails.append("matching zero counts were wrongly flagged: %r" % (r,))

    # 4. GOALS.md's sentence rewritten to a shape this gate does not
    #    recognise: warn, not fail, since the literal is unverified rather
    #    than proven wrong.
    r, w = _run(1, "Baseline: one $19 sale, ever, no customer count stated.")
    if r:
        fails.append("an unparseable GOALS.md sentence was failed instead "
                      "of warned: %r" % (r,))
    if not w:
        fails.append("an unparseable GOALS.md sentence produced no warning")

    # 5. GOALS.md missing entirely: warn, not fail, not a crash.
    r, w = _run(1, None)
    if r:
        fails.append("a missing GOALS.md was failed instead of warned: %r"
                     % (r,))

    # 6. The draft's own literal already rewritten to something this gate
    #    does not recognise (e.g. re-derived from a live source): silent,
    #    nothing left to fall out of step.
    tmp = tempfile.mkdtemp()
    ops_dir = os.path.join(tmp, "ops")
    os.makedirs(ops_dir)
    io.open(os.path.join(ops_dir, "linkedin_drafts.py"), "w",
            encoding="utf-8").write(
        "L += [\"  Customers to date: {f['customers']}\"]\n")
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(
        GOALS_TMPL % "two")
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_linkedin_drafts_customer_count_current()
        r, w = list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)
    if r or w:
        fails.append("a rewritten, no-longer-literal draft line was "
                      "wrongly flagged: %r / %r" % (r, w))

    # 7. The real committed files: clean today (both say "one").
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_linkedin_drafts_customer_count_current()
    if preflight.FAIL:
        fails.append("the real committed files failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_linkedin_drafts_customer_count_current, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
