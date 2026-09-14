"""gate_quest_finisher_count_dated: privacy.html's Quest-finisher count must
stay dated, not evergreen.

Found 2026-09-14 cold-reading privacy.html for content honesty (CLAUDE.md
8-10, the standing handoff naming privacy.html and accessibility.html as the
last two hand-maintained pages without an individual read). "two people have
ever finished a card" was written 2026-09-07 (`94a36cc6`), sourced from
`ops/experiments.py`'s EXP-004 query against the live Umami database at that
moment. No sandbox this week and no credentialed CI job can re-derive that
number, so left undated it can only ever go stale silently while still
reading as a current fact.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import preflight as P  # noqa: E402

# The real pre-fix wording from commit 94a36cc6 (site/privacy.html), copied
# here as a literal so this case does not depend on git history depth: CI
# checks out with --depth=1, where an old commit's blob can be unreachable.
PRE_FIX_TEXT = (
    "That event records which of the six passes it was and how many cards "
    "you have finished in the session. We count it because we genuinely do "
    "not otherwise know whether the app helps anybody: two people have "
    "ever finished a card."
)


def _wrap(body: str) -> str:
    return f"<html><body><p>{body}</p></body></html>"


def main() -> int:
    bad = []

    # Case 1: no "finished a card" text anywhere must never fail.
    if P.check_quest_finisher_count_dated(_wrap("Nothing about the Quest here.")) != []:
        bad.append("case 1: no 'finished a card' claim at all must never fail")

    # Case 2: the undated claim must be caught.
    problems = P.check_quest_finisher_count_dated(
        _wrap("two people have ever finished a card."))
    if not problems:
        bad.append("case 2: an undated 'finished a card' claim must be caught")

    # Case 3: a dated claim, in the actual fixed phrasing, must pass.
    fixed = ("the last time this was checked, on 7 September 2026, two "
             "people had ever finished a card. This page is not wired to "
             "a live counter, so treat that as a dated snapshot, not a "
             "running total.")
    if P.check_quest_finisher_count_dated(_wrap(fixed)) != []:
        bad.append("case 3: the actual fixed, dated wording must pass clean")

    # Case 4: a differently-worded but still-dated claim must also pass,
    # since the gate checks for a real calendar date nearby, not one exact
    # sentence shape.
    other_dated = "As of 1 January 2027, three people had finished a card."
    if P.check_quest_finisher_count_dated(_wrap(other_dated)) != []:
        bad.append("case 4: any real calendar date near the claim must pass")

    # Case 5: a date that exists in the document but far from the claim
    # must not count as covering it.
    far = ("Last updated 19 August 2026. " + ("filler word " * 40) +
           "two people have ever finished a card.")
    if not P.check_quest_finisher_count_dated(_wrap(far)):
        bad.append("case 5: a date far from the claim must not satisfy it")

    # Case 6: the real pre-fix commit's wording must fail by name.
    if not P.check_quest_finisher_count_dated(_wrap(PRE_FIX_TEXT)):
        bad.append("case 6: the real pre-fix wording (commit 94a36cc6) must fail")

    # Case 7: the real, current site/privacy.html must pass clean.
    live_path = os.path.join(ROOT, "site", "privacy.html")
    live_text = io.open(live_path, encoding="utf-8").read()
    if P.check_quest_finisher_count_dated(live_text) != []:
        bad.append("case 7: the real current site/privacy.html must pass clean")

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  7 of 7 cases pass: no claim is always clean, an undated "
              "claim is caught, the real fixed wording and any other dated "
              "wording both pass, a far-away date does not count, the real "
              "pre-fix commit fails by name, and the real current file is "
              "clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
