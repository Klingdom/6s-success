#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_architecture_doc_current() catches
ARCHITECTURE.md asserting "no CI" or "no payment processing" once those
things exist in the repository.

Found 2026-09-11, this operator, cold-reading the 8 governance docs never
cited in ops/NIGHTLY-LOG.md. ARCHITECTURE.md, last verified 2026-08-17, still
said "no CI, no .github directory, no workflows" and closed with "it cannot
accept their money", while 9 real workflow files existed under
.github/workflows/ and a real Stripe Payment Link had already cleared one
sale (GOALS.md, 2026-08-21). RISKS.md already tracked both as CLOSED;
ARCHITECTURE.md never got the same correction.

Run:  python ops/tests/test_gate_architecture_doc_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

STALE_DOC = (
    "# Architecture\n\n"
    "- no analytics, advertising pixels, session recording, or third "
    "party trackers\n"
    "- no payment processing\n"
    "- no CI, no `.github` directory, no workflows\n\n"
    "Right now, exactly one thing qualifies: it cannot accept their "
    "money.\n"
)

FIXED_DOC = (
    "# Architecture\n\n"
    "- ~~no payment processing~~ Stripe-hosted Payment Links exist.\n"
    "- ~~no CI, no `.github` directory, no workflows~~ 9 workflows exist.\n\n"
    "Corrected 2026-09-11: it used to read exactly one thing qualifies: "
    "it cannot accept their money. That is no longer true.\n"
)

NO_MONEY_LINE_DOC = (
    "# Architecture\n\n"
    "- ~~no payment processing~~ fixed elsewhere in this doc.\n"
    "- ~~no CI, no `.github` directory, no workflows~~ fixed.\n"
)


def _run(doc, has_workflow, has_payment_link):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "ARCHITECTURE.md"), "w",
            encoding="utf-8").write(doc)
    if has_workflow:
        wf_dir = os.path.join(tmp, ".github", "workflows")
        os.makedirs(wf_dir)
        io.open(os.path.join(wf_dir, "checks.yml"), "w",
                encoding="utf-8").write("name: checks\n")
    site_dir = os.path.join(tmp, "site")
    os.makedirs(site_dir)
    body = "buy.stripe.com/abc123" if has_payment_link else "no link here"
    io.open(os.path.join(site_dir, "book.html"), "w",
            encoding="utf-8").write("<html>%s</html>" % body)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_architecture_doc_current()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real 2026-09-11 regression shape: stale doc, real CI, real
    #    payment link. Must fail, naming both defects.
    r = _run(STALE_DOC, has_workflow=True, has_payment_link=True)
    if len(r) != 2:
        fails.append("stale doc against real CI + payment link did not "
                      "fail both checks: %r" % (r,))

    # 2. Fixed doc (struck-through claims, corrected closing line), same
    #    real CI and payment link: must not fail.
    r = _run(FIXED_DOC, has_workflow=True, has_payment_link=True)
    if r:
        fails.append("a corrected doc was wrongly flagged: %r" % (r,))

    # 3. Stale doc, but CI and payment genuinely absent: claim matches
    #    reality, must not fail.
    r = _run(STALE_DOC, has_workflow=False, has_payment_link=False)
    if r:
        fails.append("a doc matching real absence was wrongly flagged: %r"
                      % (r,))

    # 4. A doc that struck the two absences but left a bare "it cannot
    #    accept their money" is not what this checks for directly (only
    #    the exact old closing sentence with no correction nearby);
    #    confirm the corrected-closing-line doc still passes.
    r = _run(NO_MONEY_LINE_DOC, has_workflow=True, has_payment_link=True)
    if r:
        fails.append("a doc with both claims struck was wrongly flagged: "
                      "%r" % (r,))

    # 5. The real, committed ARCHITECTURE.md: clean, since this cycle
    #    fixed both stale claims.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_architecture_doc_current()
    if preflight.FAIL:
        fails.append("the real committed ARCHITECTURE.md failed: %r" %
                      (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_architecture_doc_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
