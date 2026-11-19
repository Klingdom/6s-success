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

Case 4 no longer hardcodes "recipes"/"how to organize recipes": that one row
fell out of the harvest on 2026-11-19 (keyword-demand.yml narrowed to
--source google, and the row turned out to be Bing-only), which let the
self-test pass for the wrong reason and shipped a real CI failure. It now
finds any current on-topic query with exactly one content word and plants
that word instead, so a future source change cannot silently defang it
again.

Run:  python ops/tests/test_gate_keyword_demand_no_content_words.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import keyword_demand as kd                                    # noqa: E402
import room_guide_candidates as rgc                            # noqa: E402


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

    # 4. FAIL-THEN-PASS against the REAL corpus, not a fixture. The original
    #    version of this case hardcoded "recipes" and "how to organize
    #    recipes" (A116's own shipped defect), and silently stopped testing
    #    anything on 2026-11-19 when that one row fell out of the harvest:
    #    keyword-demand.yml was narrowed to --source google the same day
    #    (Bing's osjson.aspx returning HTTP 204 to its own canary), "how to
    #    organize recipes" turned out to be Bing-only, and the gate then had
    #    no real row left to find, so it reported clean for the wrong
    #    reason. Caught live by checks.yml (run 44547908641), not by this
    #    test, which is exactly the blind spot CLAUDE.md 0.4 names. Fixed to
    #    stop depending on one named row: scan the REAL committed corpus for
    #    any on-topic query that currently has exactly one content word
    #    (using the same on_topic rule the real gate applies), plant THAT
    #    word into FORMAT_WORDS, and confirm the real gate fails and names
    #    that exact query. Whatever the harvest looks like on the day this
    #    runs, some on-topic query having exactly one content word is a
    #    structural near-certainty across thousands of short queries, so
    #    this no longer depends on any one phrase surviving a source change.
    def on_topic(query):
        if rgc.OFF_TOPIC_CONTEXT.search(query):
            return False
        if rgc.DIGITAL.search(query):
            return False
        return bool(rgc.ON_TOPIC.search(query))

    rows = []
    for name in ("keyword-demand.json", "keyword-demand-global.json"):
        path = os.path.join(ROOT, "ops", name)
        rows += json.loads(io.open(path, encoding="utf-8").read())["rows"]

    target_query, target_word = None, None
    for row in rows:
        query = row.get("query", "")
        if not query or not on_topic(query):
            continue
        cw = kd.content_words(query)
        if len(cw) == 1:
            target_query, target_word = query, cw[0]
            break

    if target_query is None:
        fails.append("no on-topic query in the real committed corpus has "
                     "exactly one content word today, so case 4 has "
                     "nothing real to plant a defect against; widen the "
                     "search or accept this as a real, reportable gap "
                     "rather than skip the check silently")
    else:
        real_format_words = kd.FORMAT_WORDS
        try:
            kd.FORMAT_WORDS = frozenset(set(real_format_words)
                                        | {target_word})
            preflight.FAIL, preflight.WARN = [], []
            preflight.gate_keyword_demand_no_content_words()
            if not preflight.FAIL:
                fails.append(
                    "re-adding %r to FORMAT_WORDS (the sole content word "
                    "of the real query %r) did not fail the real gate, so "
                    "the gate cannot catch the exact defect it was built "
                    "for" % (target_word, target_query))
            elif not any(target_query in m for _, m in preflight.FAIL):
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
