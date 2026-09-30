#!/usr/bin/env python3
"""
Prove gate_risks_register_current reads RISKS.md's newest real review claim,
and not a date the file quotes while describing its own history.

WHY THIS EXISTS
---------------
On 2026-09-30 this gate failed the build, saying RISKS.md was 42 days stale.
The register had been re-read top to bottom that same morning. Two things
lined up:

  - a cycle rephrased the live header from "Last reviewed:" to "Re-reviewed",
    which the gate's pattern did not match; and
  - section 8 also quotes its own history, including the sentence
    'On the previous "Last reviewed: 2026-08-19" and what it cost'.

So the only match left was a deliberate historical citation, and the gate read
it as the current state. A gate that fails a correct file teaches people to
ignore it, which is worse than the drift it watches for.

Both directions are held here, because the obvious fix breaks the other one.
Taking the newest matching date fixes the false failure, but a QUOTED date
then sets a floor under the computed age: a genuinely abandoned register whose
real claims are older than the quote would be reported as fresher than it is.
That is the opposite failure and the worse one, so quoted dates are skipped.

Run:  python ops/tests/test_gate_risks_register_date.py
"""
import datetime as dt
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402

TABLE = """
| ID | Title | Severity | Status |
|---|---|---|---|
| RISK-0001 | something | HIGH | OPEN |
"""


def _run(body):
    """Run the gate against a throwaway RISKS.md and collect its findings."""
    tmp = tempfile.mkdtemp()
    real_root, real_fail, real_warn = P.ROOT, P.fail, P.warn
    found = []
    try:
        io.open(os.path.join(tmp, "RISKS.md"), "w",
                encoding="utf-8").write(body)
        P.ROOT = tmp
        P.fail = lambda k, m: found.append(m)
        P.warn = lambda k, m: found.append(m)
        P.gate_risks_register_current()
        return found
    finally:
        P.ROOT, P.fail, P.warn = real_root, real_fail, real_warn
        shutil.rmtree(tmp, ignore_errors=True)


def _doc(*lines):
    return "# 8. Register State\n\n" + "\n".join(lines) + "\n" + TABLE


def _ago(days):
    return (dt.date.today() - dt.timedelta(days=days)).isoformat()


def case_the_old_phrasing_still_works():
    assert _run(_doc("Last reviewed: %s" % _ago(3))) == []


def case_the_new_phrasing_is_accepted():
    """The rephrasing that broke this gate: 'Re-reviewed', no colon."""
    assert _run(_doc("Re-reviewed %s, scheduled operator." % _ago(3))) == []


def case_a_quoted_historical_date_is_not_the_current_state():
    """The exact sentence that failed the build on a correct file."""
    body = _doc(
        "Re-reviewed %s, scheduled operator." % _ago(2),
        "",
        'On the previous "Last reviewed: 2026-08-19" and what it cost.',
    )
    assert _run(body) == [], _run(body)


def case_a_quoted_date_cannot_mask_a_genuinely_stale_register():
    """The opposite failure, and the worse one: the quote must not be a floor."""
    body = _doc(
        "Re-reviewed %s, scheduled operator." % _ago(200),
        "",
        'On the previous "Last reviewed: %s" and what it cost.' % _ago(2),
    )
    out = _run(body)
    assert out, "a 200-day-old register passed because a quote looked recent"
    assert "200 days" in out[0], out


def case_a_genuinely_stale_register_still_fails():
    out = _run(_doc("Re-reviewed %s." % _ago(60)))
    assert out and "60 days" in out[0], out


def case_the_newest_real_claim_wins():
    body = _doc("Re-reviewed %s." % _ago(2),
                "Last reviewed before that: %s" % _ago(40))
    assert _run(body) == []


def case_no_date_at_all_is_reported_not_passed():
    out = _run(_doc("Reviewed whenever somebody remembers."))
    assert out, "a register with no review date silently passed"


def case_the_real_register_passes():
    src = io.open(os.path.join(ROOT, "RISKS.md"), encoding="utf-8").read()
    assert _run(src) == [], "the real, current RISKS.md is being failed again"


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
