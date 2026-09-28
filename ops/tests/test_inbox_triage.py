#!/usr/bin/env python3
"""
Prove a third-party message with a recorded conclusion stops being reported,
and that everything else still is.

WHY THIS EXISTS
---------------
gate_owner_waiting searches IMAP UNSEEN, which only says whether a human has
clicked a message in a mail client. Four third-party messages from 29 August
sat there for a month reading as "may need a decision" when every one had been
opened and found to need nothing:

  Impact "Application Update"   the decline of Media Partner 7700618, already
                                recorded across the affiliate documents
  CJ "Changes made to account"  routine confirmation that user information
                                changed during the sign-up, CID 8057711 already
                                tracked
  CJ "Changes made to account"  the same for company information, 15 min later
  Google "Security alert"       Rakuten Advertising granted access to Google
                                account data in the same sign-up round; Rakuten
                                is already a tracked network

A warning that repeats a resolved item forever is how a real one gets skimmed
past, and this repository's most expensive defect was a correctly reported
problem nobody acted on.

The mailbox is never written to. Marking somebody else's mail read would hide
it from them, and the claim being made is "a cycle read this and concluded X",
which belongs in the repository.

Run:  python ops/tests/test_inbox_triage.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import owner_inbox as O                                        # noqa: E402

INTERESTING = re.compile(r"affiliate|payment|domain|dispute|impact|cj\.com"
                         r"|security|account", re.I)


def case_triaged_message_is_retired():
    t = {"<abc@x>": {"conclusion": "nothing to do"}}
    assert not O.should_report("<abc@x>", "Impact <n@impact.com>",
                               "Application Update", INTERESTING, t)


def case_untriaged_message_still_reports():
    t = {"<abc@x>": {"conclusion": "nothing to do"}}
    assert O.should_report("<new@x>", "Impact <n@impact.com>",
                           "Application Update", INTERESTING, t)


def case_empty_ledger_retires_nothing():
    """Fail safe: the failure mode must be a warning that repeats."""
    for ledger in ({}, None):
        assert O.should_report("<abc@x>", "cj <no@cj.com>",
                               "Changes made to account", INTERESTING, ledger)


def case_uninteresting_mail_is_still_ignored():
    assert not O.should_report("<zzz@x>", "A Friend <f@example.com>",
                               "lunch tomorrow", INTERESTING, {})


def case_triage_wins_over_interesting():
    """A dispute that has been read and answered must not keep shouting."""
    t = {"<d@x>": {"conclusion": "answered 2026-09-28"}}
    assert not O.should_report("<d@x>", "bank <no@bank.com>",
                               "dispute opened", INTERESTING, t)


def case_missing_message_id_never_retires():
    """No id means no recorded conclusion, so it must be reported."""
    t = {"<abc@x>": {"conclusion": "done"}}
    assert O.should_report("", "Impact <n@impact.com>", "payment", INTERESTING, t)


def case_the_real_ledger_is_wellformed():
    fp = os.path.join(ROOT, "ops", "inbox-state.json")
    d = json.load(io.open(fp, encoding="utf-8"))
    tri = d.get("triaged") or {}
    assert tri, "no triage recorded at all"
    for mid, rec in tri.items():
        assert mid.startswith("<") and mid.endswith(">"), mid
        for field in ("conclusion", "triaged_on", "from", "subject"):
            assert rec.get(field), (mid, field)
        assert len(rec["conclusion"]) > 40, (
            mid + ": a conclusion that short is not a conclusion")


def case_loader_reads_the_real_file():
    assert len(O._triaged()) >= 4


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
