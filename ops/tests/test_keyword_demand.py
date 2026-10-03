#!/usr/bin/env python3
"""
Prove ops/keyword_demand.py cannot report a demand reading it did not take.

The tool reads public autocomplete endpoints, which fail in the one way this
repository keeps getting hurt by: a refused request comes back as a valid,
empty, HTTP 200. A naive harvester writes "0 gaps" and exits 0, and the next
cycle reads that as evidence.

So the cases below are mostly about refusal, not about parsing. In particular
case 4 pins the correction the first real run forced: "why is my entryway
always messy" genuinely has no completions, and an earlier version counted
that as a failure, which would have voided an otherwise complete harvest. A
genuine zero and a refusal look identical in one response, so they are told
apart across the run, by the canary.

No network. Every endpoint is stubbed.

Run:  python ops/tests/test_keyword_demand.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import keyword_demand as kd                                    # noqa: E402


def attempts(ok=0, empty=0, error=0):
    out = []
    out += [{"seed": "s", "source": "google", "count": 5, "error": None,
             "outcome": "ok"} for _ in range(ok)]
    out += [{"seed": "s", "source": "google", "count": 0, "error": None,
             "outcome": "empty"} for _ in range(empty)]
    out += [{"seed": "s", "source": "google", "count": 0, "error": "http 429",
             "outcome": "error"} for _ in range(error)]
    return out


GOOD_CANARY = {"google": (True, "")}


def main():
    fails = []

    # 1. A clean run writes. 100 ok attempts, no empties, canary good.
    r = kd.refusal_reason(attempts(ok=100), GOOD_CANARY)
    if r:
        fails.append("clean run refused: %s" % r)

    # 2. A failed canary voids the run even when every attempt returned rows.
    #    This is the whole point of the canary: the rows are real, they are
    #    just not the whole picture, and a partial picture overwriting a
    #    complete one reads as a collapse in demand.
    r = kd.refusal_reason(attempts(ok=100), {"google": (False, "empty 200")})
    if not r or "canary" not in r:
        fails.append("failed canary did not void the run: %r" % r)

    # 3. Error rate over the ceiling is refused.
    r = kd.refusal_reason(attempts(ok=80, error=20), GOOD_CANARY)
    if not r or "error rate" not in r:
        fails.append("20 percent errors not refused: %r" % r)

    # 3b. Exactly at the ceiling is allowed, so the ceiling is a ceiling and
    #     not an off-by-one.
    r = kd.refusal_reason(attempts(ok=90, error=10), GOOD_CANARY)
    if r:
        fails.append("10 percent errors wrongly refused: %s" % r)

    # 4. The regression the first real run found: genuine zeros below the
    #    empty ceiling must NOT void a harvest.
    r = kd.refusal_reason(attempts(ok=80, empty=20), GOOD_CANARY)
    if r:
        fails.append("genuine zeros wrongly refused: %s" % r)

    # 5. But an endpoint answering 200-with-nothing for most of the run is
    #    refused even if the canary happened to squeak through.
    r = kd.refusal_reason(attempts(ok=30, empty=70), GOOD_CANARY)
    if not r or "empty rate" not in r:
        fails.append("70 percent empty not refused: %r" % r)

    # 6. No attempts at all is a refusal, not a clean empty result.
    r = kd.refusal_reason([], GOOD_CANARY)
    if not r:
        fails.append("zero attempts not refused")

    # 7. Parsing: the real OpenSearch shape, and three malformed ones.
    out, err = kd._parse_opensearch('["seed", ["a", "b"], [], {}]')
    if err or out != ["a", "b"]:
        fails.append("real shape misparsed: %r %r" % (out, err))
    for bad in ('not json', '{"a": 1}', '["seed"]', '["seed", "notalist"]'):
        out, err = kd._parse_opensearch(bad)
        if not err:
            fails.append("malformed payload accepted: %r" % bad)

    # 8. Coverage scoring must not flatter itself. Every title on this site
    #    carries some form of "organize", so if that counted, a query would
    #    score partial coverage against any page at all.
    cw = kd.content_words("how to organize a mudroom")
    if cw != ["mudroom"]:
        fails.append("content_words kept filler: %r" % cw)
    if kd.content_words("how to organize it"):
        fails.append("a query with no subject scored content words")

    # 9. classify boundaries, including the float case that made 2 words of 3
    #    round to 1.0 in an earlier draft.
    for score, want in ((1.0, "covered"), (0.999, "covered"),
                        (0.998, "partial"), (0.5, "partial"),
                        (0.499, "gap"), (0.0, "gap")):
        got = kd.classify(score)
        if got != want:
            fails.append("classify(%s) was %s, wanted %s" % (score, got, want))

    # 10. best_page picks the better title and breaks ties by url, so two runs
    #     over the same corpus cannot disagree.
    inv = [
        {"url": "/a.html", "title": "How to organize the mudroom bench",
         "words": set(kd.words("How to organize the mudroom bench"))},
        {"url": "/b.html", "title": "How to organize a mudroom, zone by zone",
         "words": set(kd.words("How to organize a mudroom, zone by zone"))},
        {"url": "/c.html", "title": "Shop", "words": set(kd.words("Shop"))},
    ]
    page, score = kd.best_page("how to organize mudroom bench", inv)
    if page["url"] != "/a.html" or score != 1.0:
        fails.append("best_page missed the exact match: %r %r" % (page, score))
    page, score = kd.best_page("how to organize a mudroom", inv)
    if page["url"] != "/a.html":
        fails.append("best_page tie not broken by url: %r" % (page,))
    page, score = kd.best_page("how to organize a foyer", inv)
    if score != 0.0:
        fails.append("unknown subject scored above zero: %r" % score)

    # 11. Room attribution must prefer the longer name, or every Guest
    #     Bathroom query would be filed under Primary Bathroom's room and the
    #     by-room table would be wrong in the direction nobody checks.
    rooms = ["Primary Bathroom", "Guest Bathroom", "Primary Bedroom",
             "Kids Bedroom", "Kitchen"]
    for query, want in (("guest bathroom ideas", "Guest Bathroom"),
                        ("kids bedroom storage", "Kids Bedroom"),
                        ("how to organize a kitchen", "Kitchen"),
                        ("how to organize a garage", "")):
        got = kd.attribute_room(query, rooms)
        if got != want:
            fails.append("attribute_room(%r) was %r, wanted %r"
                         % (query, got, want))

    # 12. harvest() classifies a 200-with-nothing as empty, not error, and an
    #     exception as error. Stubbed, no network.
    def stub(seed):
        if seed == "boom":
            return [], "URLError: refused"
        if seed == "quiet":
            return [], None
        return ["%s one" % seed, "%s two" % seed], None

    real = dict(kd.SOURCES)
    try:
        kd.SOURCES.clear()
        kd.SOURCES["stub"] = stub
        rows, atts, failures, pages = kd.harvest(
            ["stub"], ["loud", "quiet", "boom"], verbose=False, sleep=False)
        got = sorted(a["outcome"] for a in atts)
        if got != ["empty", "error", "ok"]:
            fails.append("harvest outcomes were %r" % got)
        if len(failures) != 1:
            fails.append("harvest counted %d failures, wanted 1"
                         % len(failures))
        if len(rows) != 2:
            fails.append("harvest kept %d rows, wanted 2" % len(rows))
        if pages < 100:
            fails.append("page inventory read only %d titles, which is too "
                         "few for this corpus and means the walk is broken"
                         % pages)
    finally:
        kd.SOURCES.clear()
        kd.SOURCES.update(real)

    # 12b. Headings count, and they must not quietly inflate the title score.
    #      Added with the heading pass on 2026-10-01: a page can answer a
    #      question properly under its own <h2> and still have a title that
    #      does not carry the word, which the title-only reading called a gap.
    #      The two scores are kept apart on purpose, so this asserts both that
    #      the status improves AND that `coverage` stays title-only, because a
    #      measurement that silently got more generous would be worse here
    #      than one that was too strict.
    inv2 = [{"url": "/a.html",
             "title": "Why is my house always messy?",
             "words": set(kd.words("Why is my house always messy?")),
             "head_words": set(kd.words("Why is my house always messy? "
                                        "Why is my kitchen always messy?"))}]
    rows = kd.score_rows({"why is my kitchen always messy":
                          {"query": "why is my kitchen always messy",
                           "sources": ["google"], "best_rank": 1,
                           "seeds": ["x"]}}, ["Kitchen"], inv2)
    r = rows[0]
    if r["status"] != "covered":
        fails.append("a question answered under its own heading scored %r"
                     % r["status"])
    if r["matched_on"] != "heading":
        fails.append("matched_on was %r, wanted 'heading'" % r["matched_on"])
    if r["coverage"] >= 0.999:
        fails.append("the title-only score was inflated by a heading: %r"
                     % r["coverage"])
    if r["heading_coverage"] < 0.999:
        fails.append("heading score did not reach 1.0: %r"
                     % r["heading_coverage"])

    # 12c. And a page with neither still reads as a gap, so the heading pass
    #      cannot turn the whole corpus green.
    inv3 = [{"url": "/b.html", "title": "Shop",
             "words": set(kd.words("Shop")),
             "head_words": set(kd.words("Shop Buy the deck"))}]
    rows = kd.score_rows({"why is my garage always messy":
                          {"query": "why is my garage always messy",
                           "sources": ["google"], "best_rank": 1,
                           "seeds": ["x"]}}, ["Garage"], inv3)
    if rows[0]["status"] != "gap":
        fails.append("an uncovered query scored %r" % rows[0]["status"])

    # 13. Seeds are deterministic and deduplicated, so two harvests are
    #     comparable line by line.
    s1, s2 = kd.build_seeds(), kd.build_seeds()
    if s1 != s2:
        fails.append("build_seeds is not deterministic")
    if len(s1) != len(set(s1)):
        fails.append("build_seeds emitted a duplicate")
    if len(s1) < 80:
        fails.append("only %d seeds built, which is fewer than the 20 rooms "
                     "times 4 templates this corpus guarantees" % len(s1))

    # 14. The report must carry its own caveat. The single likeliest way this
    #     tool does damage is somebody quoting a rank as a monthly volume, so
    #     the disclaimer is load-bearing text, not decoration.
    payload = {
        "checked_at": "2026-10-01T00:00:00Z", "sources": ["google"],
        "seeds": 1, "attempts": 1, "ok_attempts": 1, "empty_attempts": 0,
        "failed_attempts": 0, "pages_checked": 1, "failures": [],
        "canaries": {"google": {"ok": True, "note": ""}},
        "rows": [{"query": "how to organize a foyer", "sources": ["google"],
                  "best_rank": 1, "seeds": ["x"], "room": "",
                  "best_page": "/a.html", "best_page_title": "A",
                  "coverage": 0.0, "status": "gap"}],
    }
    text = kd.report(payload)
    for needed in ("not search volume", "fabrication", "triage score"):
        if needed not in text:
            fails.append("report dropped its caveat: %r" % needed)
    if "how to organize a foyer" not in text:
        fails.append("report omitted its only gap row")

    # 15. The report must disclose WHEN it was scored, not just when it was
    #     harvested. LRN-0032: a stored status is a fact about a moment, and
    #     this repository's corpus changes several times an hour, so a
    #     coverage figure read without its scoring date describes a site that
    #     no longer exists. A payload with no scoring date must say so rather
    #     than quietly print the number.
    dated = dict(payload, scored_at="2026-10-02T14:00:00Z",
                 scored_against_commit="abc123def")
    text = kd.report(dated)
    for needed in ("**Scored:**", "2026-10-02T14:00:00Z", "abc123def",
                   "not when the queries were harvested"):
        if needed not in text:
            fails.append("report omitted the scoring disclosure: %r" % needed)
    undated = kd.report(payload)
    if "unknown age" not in undated:
        fails.append("a payload with no scored_at did not say its statuses "
                     "are of unknown age")

    # 16. An argument main() does not recognise must be refused, and --help
    #     must print and stop. Found live 2026-10-03: neither was a flag, so
    #     both fell through every branch and ran the default action, a full
    #     live harvest of both engines that overwrites keyword-demand.json.
    #     Proved here by making the two expensive calls explode: if either
    #     path still reaches them, this case fails loudly instead of quietly
    #     fetching the internet during a test run.
    def _must_not_run(*a, **k):
        raise AssertionError('main() reached the network/write path')
    saved = (kd.harvest, kd.write_outputs, kd.build_seeds, kd.canary_ok)
    kd.harvest = _must_not_run
    kd.write_outputs = _must_not_run
    kd.build_seeds = _must_not_run
    kd.canary_ok = _must_not_run
    try:
        for argv, want in ((['--help'], 0), (['-h'], 0),
                           (['--statuss'], 2), (['--rescor'], 2),
                           (['extra-positional'], 2), (['--source'], 2)):
            try:
                got = kd.main(list(argv))
            # Any exception, not just the planted AssertionError. Proving
            # this case by deleting the guard showed why: without it,
            # main(['--source']) raises IndexError on argv[index+1] before
            # the harvest stub is ever reached, which crashed the whole test
            # file instead of reporting the defect. A test that dies on the
            # defect it exists to catch tells a reader less than one that
            # names it.
            except Exception as exc:                     # noqa: BLE001
                fails.append('main(%r) raised %s: %s'
                             % (argv, type(exc).__name__, exc))
                continue
            if got != want:
                fails.append('main(%r) returned %r, expected %r'
                             % (argv, got, want))
        # And a flag it DOES know must still be accepted as one, or this
        # guard would have fixed the hole by breaking the tool: --source
        # takes a value, and that value must not read as an unknown
        # argument.
        try:
            kd.main(['--source', 'bing'])
        except AssertionError:
            pass                  # reached harvest, which is correct here
        else:
            fails.append('main([--source, bing]) returned without reaching the harvest path, so a valid flag is being refused')
    finally:
        kd.harvest, kd.write_outputs, kd.build_seeds, kd.canary_ok = saved

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    # Counted from the numbered cases in this file rather than typed, because
    # a hardcoded tally goes stale the first time somebody adds a case and
    # then the test reports a number that is simply false. It said 14/14
    # with fifteen cases in it.
    import re as _re
    n = len(_re.findall(r"^    # \d+[a-z]?\. ",
                        io.open(__file__, encoding="utf-8").read(),
                        _re.M))
    print("OK: keyword_demand, %d numbered case(s), no problems" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
