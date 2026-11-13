#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_keyword_demand_no_content_words() (and its pure
helper, keyword_demand_unscoreable_rows()) catches a harvested query left with
zero scoreable content words.

Why this gate exists. A query whose content_words() is empty cannot score
above 0.0 against any page in the corpus, ever, however good a page the site
later publishes, because there is nothing left to match on. It reads exactly
like a genuine uncovered query while being invisible to every room tally built
on the same data.

The shape had already appeared three times when this was written. A114 caught
it for "bonus"/"den" and A120 caught it for "steps", both declined before
shipping because a full corpus diff showed real rows falling to gap. A116
shipped "recipes" anyway, and no diff could have flagged it: "how to organize
recipes" was ALREADY gap, so emptying its content words changed no status at
all. That blind spot is the whole point of this gate, and case 4 below
reproduces it against the real committed corpus rather than a fixture.

Run:  python ops/tests/test_gate_keyword_demand_no_content_words.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import keyword_demand as kd                                    # noqa: E402


def main() -> int:
    fails = []

    # A stub content_words: every word is content except the ones named,
    # so a query made only of those scores against nothing.
    empty_for = {"how to organize recipes", "how to organize pc"}

    def content_words(query):
        return [] if query in empty_for else ["real"]

    def on_topic(query):
        return "pc" not in query.split()

    # 1. Nothing to score: no rows, no complaint.
    bad = preflight.keyword_demand_unscoreable_rows([], content_words,
                                                    on_topic)
    if bad:
        fails.append("empty rows wrongly reported: %r" % bad)

    # 2. An on-topic query with no content words IS the defect.
    rows = [{"query": "how to organize recipes"},
            {"query": "how to organize a pantry"}]
    bad = preflight.keyword_demand_unscoreable_rows(rows, content_words,
                                                    on_topic)
    if bad != ["how to organize recipes"]:
        fails.append("the unscoreable on-topic row was not reported: %r"
                     % bad)

    # 3. An off-topic query with no content words is NOT the defect: the
    #    ranking tool already excludes it, so failing on it would be noise.
    rows = [{"query": "how to organize pc"}]
    bad = preflight.keyword_demand_unscoreable_rows(rows, content_words,
                                                    on_topic)
    if bad:
        fails.append("an off-topic empty row wrongly reported: %r" % bad)

    # 4. FAIL-THEN-PASS against the REAL corpus, not a fixture. Put
    #    "recipes" back into the real FORMAT_WORDS exactly as A116 shipped
    #    it and confirm the real gate fails on the real committed file.
    real_format_words = kd.FORMAT_WORDS
    try:
        kd.FORMAT_WORDS = frozenset(set(real_format_words) | {"recipes"})
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_keyword_demand_no_content_words()
        if not preflight.FAIL:
            fails.append("re-adding 'recipes' to FORMAT_WORDS did not fail "
                         "the real gate, so the gate cannot catch the exact "
                         "defect it was built for")
        elif not any("how to organize recipes" in m
                     for _, m in preflight.FAIL):
            fails.append("the gate failed but did not name the real "
                         "offending query: %r" % (preflight.FAIL,))
    finally:
        kd.FORMAT_WORDS = real_format_words

    # 5. Restored: today's real shipped state must be clean.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_keyword_demand_no_content_words()
    if preflight.FAIL:
        fails.append("the real committed corpus fails today: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("test_gate_keyword_demand_no_content_words: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
