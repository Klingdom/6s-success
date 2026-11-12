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

    # 8b. "arrange" is the same kind of word as "organize", a task verb
    #     rather than a subject noun, just one we do not say ourselves. It
    #     must not count as an unmet content word either.
    cw = kd.content_words("how to arrange towels in guest bathroom")
    if "arrange" in cw:
        fails.append("content_words scored arrange as a subject word: %r" % cw)
    if cw != ["towels", "guest", "bathroom"]:
        fails.append("content_words on the arrange query: %r" % cw)

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

    # 17. The alphabetical tie-break silently favoured "Guest X" over its
    #     "Primary X" sibling on any query that did not name a room of ours
    #     literally, found live 2026-10-10 via "master bedroom closet
    #     organization ideas" resolving to Guest Bedroom's closet page. A
    #     room signal, including a household synonym like "master bedroom",
    #     must now win a genuine tie over url order.
    rooms = ["Guest Bedroom", "Primary Bedroom"]
    synonyms = {"Primary Bedroom": ["master bedroom"]}
    inv = [
        {"url": "/zones/guest-bedroom-the-guest-closet.html",
         "title": "How to organize the guest bedroom closet",
         "words": set(kd.words("How to organize the guest bedroom closet")),
         "room": "Guest Bedroom"},
        {"url": "/zones/primary-bedroom-the-primary-closet.html",
         "title": "How to organize the primary bedroom closet",
         "words": set(kd.words("How to organize the primary bedroom closet")),
         "room": "Primary Bedroom"},
    ]
    signal = kd.household_room_signal(
        "master bedroom closet organization ideas", rooms, synonyms)
    if signal != "Primary Bedroom":
        fails.append("household_room_signal missed the synonym: %r" % signal)
    page, score = kd.best_page(
        "master bedroom closet organization ideas", inv, signal)
    if page["url"] != "/zones/primary-bedroom-the-primary-closet.html":
        fails.append("best_page still favoured Guest on a synonym tie: %r"
                     % (page,))
    # A query that genuinely is about the guest room must still win on its
    # own word match, signal or not: the fix must not invert the pair.
    page, score = kd.best_page(
        "guest bedroom closet organization ideas", inv, signal)
    if page["url"] != "/zones/guest-bedroom-the-guest-closet.html":
        fails.append("best_page wrongly moved a real Guest query to Primary: %r"
                     % (page,))
    # With no room signal at all, url order must still decide, unchanged
    # from case 10 above: this is the regression a careless fix could cause.
    page, score = kd.best_page("how to organize a bedroom closet", inv, "")
    if page["url"] != "/zones/guest-bedroom-the-guest-closet.html":
        fails.append("best_page tie-break changed with no room signal: %r"
                     % (page,))
    # room_of must recover the right room from a page's own URL for every
    # shape this site actually uses: a zone page, a deck page and a room
    # page, and must not match a room whose slug is merely a substring.
    for url, want in (("/zones/guest-bathroom-the-guest-vanity-counter.html",
                       "Guest Bathroom"),
                      ("/primary-bathroom-deck.html", "Primary Bathroom"),
                      ("/rooms/guest-bedroom.html", "Guest Bedroom"),
                      ("/articles/why-is-my-house-always-messy.html", "")):
        got = kd.room_of(url, rooms + ["Guest Bathroom", "Primary Bathroom"])
        if got != want:
            fails.append("room_of(%r) was %r, wanted %r" % (url, got, want))

    # 18. British and Commonwealth spellings score as the American words the
    #     site is written in. "organisation" survived as a content word while
    #     "organization" was dropped as a format word, so every query typed
    #     in the UK, Australia or India carried a word nothing could match.
    #     Planted: an unfolded "organisation" must not survive.
    if kd.content_words("larder organisation and layout") !=             kd.content_words("larder organization and layout"):
        fails.append("organisation and organization score differently: %r"
                     % kd.content_words("larder organisation and layout"))
    for brit, us in (("colour", "color"), ("organiser", "organizer"),
                     ("centre", "center"), ("mouldy", "moldy")):
        if kd.words(brit) != [us]:
            fails.append("words(%r) was %r, wanted %r"
                         % (brit, kd.words(brit), [us]))
    # A word that merely contains the letters must not be rewritten.
    if kd.words("concentrate") != ["concentrate"]:
        fails.append("words() rewrote 'concentrate': %r"
                     % kd.words("concentrate"))

    # 19. Found live 2026-11-02 (BACKLOG-2026-09-07 section 76, the third
    #     instance of the same tie-break shape as case 17, after the
    #     master-bath room-signal case and the nightstand/drawers plural
    #     case): "organize grilling station" tied at an equal exact-word
    #     score between the real patio/deck grill page and the dining
    #     room's beverage station, because "grilling" never equals "grill"
    #     with no stemming. Neither page carries a room signal for this
    #     query, so the near-miss tie-break (_near_miss_count) must decide:
    #     the patio page's own "grill" is a near match for the unmatched
    #     "grilling", the dining page has no such near match for anything.
    dining_title = "How to organize the dining room beverage or coffee station"
    patio_title = "How to organize the patio or deck grill station"
    grill_inv = [
        {"url": "/zones/dining-room-the-beverage-or-coffee-station.html",
         "title": dining_title, "words": set(kd.words(dining_title)),
         "head_words": set(kd.words(dining_title)), "room": "Dining Room"},
        {"url": "/zones/patio-or-deck-the-grill-and-outdoor-cooking-zone.html",
         "title": patio_title, "words": set(kd.words(patio_title)),
         "head_words": set(kd.words(patio_title)), "room": "Patio or Deck"},
    ]
    page, score = kd.best_page("organize grilling station", grill_inv, "")
    if page["url"] != "/zones/patio-or-deck-the-grill-and-outdoor-cooking-zone.html":
        fails.append("best_page still favoured the wrong page on a "
                     "gerund near-miss tie: %r" % (page,))
    if score != 0.5:
        fails.append("the near-miss tie-break changed the SCORE, not just "
                     "the attribution, which must never happen: %r" % score)
    # A tie with no near-miss on either side (case 17's own query) must stay
    # exactly as it was: this is the regression a careless fix could cause.
    bedroom_inv = [
        {"url": "/zones/guest-bedroom-the-guest-closet.html",
         "title": "How to organize the guest bedroom closet",
         "words": set(kd.words("How to organize the guest bedroom closet")),
         "head_words": set(kd.words("How to organize the guest bedroom closet")),
         "room": "Guest Bedroom"},
        {"url": "/zones/primary-bedroom-the-primary-closet.html",
         "title": "How to organize the primary bedroom closet",
         "words": set(kd.words("How to organize the primary bedroom closet")),
         "head_words": set(kd.words("How to organize the primary bedroom closet")),
         "room": "Primary Bedroom"},
    ]
    page, score = kd.best_page("how to organize a bedroom closet", bedroom_inv, "")
    if page["url"] != "/zones/guest-bedroom-the-guest-closet.html":
        fails.append("best_page tie-break changed with no near-miss and no "
                     "room signal: %r" % (page,))
    # _morphology_variants must not over-reach: a word that already ends in
    # a double "s" (not a plural at all) must not be despluralized.
    if "dres" in kd._morphology_variants("dress"):
        fails.append("_morphology_variants('dress') wrongly despluralized "
                     "to 'dres': %r" % kd._morphology_variants("dress"))

    # 20. Found live 2026-11-05: score_rows() always set best_page/
    #     best_page_title from the TITLE surface, even on rows where the
    #     heading surface scored higher and matched_on already said so.
    #     room_guide_candidates.py and room_guide_underperformance.py both
    #     read best_page as "the page this query actually routes to", so a
    #     silent mismatch there misattributes the query to the wrong page,
    #     and when the two pages are in different rooms, to the wrong room
    #     entirely. Two shapes, both drawn from the live corpus:
    #
    #     20a. The heading surface wins outright (no tie): a page named
    #     "Shop" has no title match at all but answers the real question
    #     under its own heading, the same shape case 12b already proved for
    #     status; best_page must now point there too, not at an unrelated
    #     page that merely scored better on title alone.
    house_title = "Why is my house always messy?"
    combo_inv = [
        {"url": "/articles/how-to-declutter-a-house.html", "title": house_title,
         "words": set(kd.words(house_title)), "head_words": set(kd.words(house_title)),
         "room": "Living Room"},
        {"url": "/articles/how-to-organize-a-kitchen.html", "title": "Shop",
         "words": set(kd.words("Shop")),
         "head_words": set(kd.words("Shop " + house_title.replace("house", "kitchen"))),
         "room": "Kitchen"},
    ]
    rows = kd.score_rows({"why is my kitchen always messy":
                          {"query": "why is my kitchen always messy",
                           "sources": ["google"], "best_rank": 1,
                           "seeds": ["x"]}}, ["Living Room", "Kitchen"], combo_inv)
    r = rows[0]
    if r["best_page"] != "/articles/how-to-organize-a-kitchen.html":
        fails.append("best_page still pointed at the title-surface loser "
                     "once a different page won on heading: %r" % r["best_page"])
    if r["best_page_title"] != "Shop":
        fails.append("best_page_title did not follow best_page to the real "
                     "winning page: %r" % r["best_page_title"])
    if r["matched_on"] != "heading":
        fails.append("matched_on disagreed with which page was credited: %r"
                     % r["matched_on"])

    # 20b. An exact tie between the two surfaces, with a room signal: the
    #     real "master bedroom storage" case. Title surface ties to a Kids
    #     Bedroom zone (matches "bedroom"+"storage"); heading surface ties
    #     to Primary Bedroom's own room page, which carries "Also called the
    #     master bedroom" as a heading (matches "master"+"bedroom"). Both
    #     score 0.667. Without a room-signal preference between surfaces,
    #     title wins by bare default and credits the wrong room.
    kids_title = "How to organize the kids bedroom toy storage"
    primary_title = "How to organize a primary bedroom, zone by zone"
    tie_inv = [
        {"url": "/zones/kids-bedroom-the-toy-storage-zone.html", "title": kids_title,
         "words": set(kd.words(kids_title)), "head_words": set(kd.words(kids_title)),
         "room": "Kids Bedroom"},
        {"url": "/rooms/primary-bedroom.html", "title": primary_title,
         "words": set(kd.words(primary_title)),
         "head_words": set(kd.words(
             primary_title + " Also called the master bedroom. "
             "Same room, same micro zones.")),
         "room": "Primary Bedroom"},
    ]
    rows = kd.score_rows({"master bedroom storage":
                          {"query": "master bedroom storage",
                           "sources": ["google"], "best_rank": 1,
                           "seeds": ["x"]}}, ["Kids Bedroom", "Primary Bedroom"], tie_inv)
    r = rows[0]
    if r["best_page"] != "/rooms/primary-bedroom.html":
        fails.append("a title/heading tie on 'master bedroom storage' still "
                     "credited the wrong room: %r" % r["best_page"])
    if r["unmatched_words"] != ["storage"]:
        fails.append("unmatched_words did not match the page actually "
                     "credited: %r" % r["unmatched_words"])
    # And with no room signal at all (the query names no room either page
    # answers to), the tie must still resolve exactly as it always has:
    # this is the regression a careless fix could cause.
    rows = kd.score_rows({"bedroom storage":
                          {"query": "bedroom storage",
                           "sources": ["google"], "best_rank": 1,
                           "seeds": ["x"]}}, ["Kids Bedroom", "Primary Bedroom"], tie_inv)
    if rows[0]["matched_on"] != "title":
        fails.append("a tie with no room signal stopped defaulting to "
                     "title: %r" % rows[0]["matched_on"])

    # 21. Found live 2026-11-05: "Cleaning it properly, surface by surface"
    #     is byte-identical on all 114 zone pages (grep-confirmed), so it
    #     cannot discriminate between zones, yet it was still read into
    #     every page's head_words. Combined with a zone's own title word,
    #     that free "cleaning" silently turned an already-diagnosed false
    #     match ("cabinet to organize cleaning supplies", ruled unfixable
    #     because "cabinet" names seven zones) into a false 1.0 "covered"
    #     claim the moment any other word in the query was added anywhere.
    #     page_inventory() reads real files, so this proves the filter
    #     directly against a throwaway site tree rather than re-deriving it
    #     by hand a second time.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        zones_dir = os.path.join(tmp, "zones")
        os.makedirs(zones_dir)
        page = (
            "<html><head><title>How to organize the office supply "
            "cabinet</title></head><body>"
            "<h1>The Supply Cabinet</h1>"
            "<h2>Cleaning it properly, surface by surface</h2>"
            "</body></html>")
        with open(os.path.join(zones_dir, "office-the-supply-cabinet.html"),
                  "w", encoding="utf-8") as fh:
            fh.write(page)
        old_site = kd.SITE
        kd.SITE = tmp
        try:
            inv = kd.page_inventory(rooms=[])
        finally:
            kd.SITE = old_site
    if len(inv) != 1:
        fails.append("page_inventory() did not read the throwaway page: %r"
                     % inv)
    elif "cleaning" in inv[0]["head_words"]:
        fails.append("the boilerplate 'Cleaning it properly, surface by "
                     "surface' heading still leaked 'cleaning' into "
                     "head_words: %r" % inv[0]["head_words"])
    elif "cabinet" not in inv[0]["head_words"] or "supply" not in inv[0]["head_words"]:
        fails.append("the filter dropped real title words along with the "
                     "boilerplate heading: %r" % inv[0]["head_words"])

    # 22. Found live 2026-11-05: "how to organize hardware in garage" (room
    #     signal Garage) scored a false 1.0 "covered" on Workshop's own
    #     guide article, which separately covers "hardware" in one heading
    #     and "garage" in another, neither heading actually about this
    #     query. Garage's own zone page, the real answer, scored only 0.5
    #     and lost outright (not even a tie) because bag-of-words matching
    #     has no way to prefer a coherent single-page answer over an
    #     incoherent combination from two unrelated headings on someone
    #     else's page. _prefer_in_room_zone must replace a winning GUIDE
    #     ARTICLE from a different room with the query's own room's zone
    #     page once that zone clears the 0.5 partial threshold on its own.
    cross_room_title = "How to organize a workshop, step by step"
    cross_room_inv = [
        {"url": "/articles/how-to-organize-a-workshop.html", "title": cross_room_title,
         "words": set(kd.words(cross_room_title)),
         "head_words": set(kd.words(
             cross_room_title + " Step 4: The fastener and hardware zone. "
             "A workshop that lives in the garage.")),
         "room": "Workshop"},
        {"url": "/zones/garage-the-hand-tool-wall-and-cabinets.html",
         "title": "Hardware storage shelf",
         "words": set(kd.words("Hardware storage shelf")),
         "head_words": set(kd.words("Hardware storage shelf")),
         "room": "Garage"},
    ]
    rows = kd.score_rows({"how to organize hardware in garage":
                          {"query": "how to organize hardware in garage",
                           "sources": ["google"], "best_rank": 1,
                           "seeds": ["x"]}}, ["Garage", "Workshop"], cross_room_inv)
    r = rows[0]
    if r["best_page"] != "/zones/garage-the-hand-tool-wall-and-cabinets.html":
        fails.append("a cross-room guide article still beat the query's own "
                     "room's zone page: %r" % r["best_page"])
    if r["status"] != "partial":
        fails.append("the cross-room combination still claimed full "
                     "coverage instead of the zone's honest partial: %r"
                     % r["status"])
    # And when the query's own room has no zone page clearing 0.5, the
    # cross-room article must still win: a weak in-room page must never
    # displace a stronger cross-room one.
    weak_inv = [cross_room_inv[0],
                dict(cross_room_inv[1], title="Shelf",
                     words=set(kd.words("Shelf")),
                     head_words=set(kd.words("Shelf")))]
    rows = kd.score_rows({"how to organize hardware in garage":
                          {"query": "how to organize hardware in garage",
                           "sources": ["google"], "best_rank": 1,
                           "seeds": ["x"]}}, ["Garage", "Workshop"], weak_inv)
    if rows[0]["best_page"] != "/articles/how-to-organize-a-workshop.html":
        fails.append("a weak in-room page wrongly displaced a stronger "
                     "cross-room one: %r" % rows[0]["best_page"])

    # 23. Found live 2026-11-05, mining Living Room: "tips"/"techniques" are
    #     format words like "ideas" (already a stopword), not subject words,
    #     and were marking 52 real queries across the corpus (39 US +
    #     13 global for "tips", 5 US for "techniques") as less covered than
    #     they honestly are for a wording difference, the same shape the
    #     2026-10-13 "arrange" fix corrected. Checked for self-flattery
    #     first, same as that fix required: zero of our own page titles and
    #     only one heading anywhere on the live site carry the literal word
    #     "tips", so excluding it cannot inflate any page's score. Content
    #     words, not a page match, so nothing here should move which page a
    #     query routes to, only the score.
    if "tips" in kd.content_words("home organization tips for living room"):
        fails.append("'tips' is still a content word; the stopword "
                     "addition did not take")
    if "techniques" in kd.content_words("organize car maintenance techniques"):
        fails.append("'techniques' is still a content word; the stopword "
                     "addition did not take")
    tips_inv = [
        {"url": "/living-room-deck.html", "title": "The Living Room Pack",
         "words": set(kd.words("The Living Room Pack")),
         "head_words": set(kd.words(
             "The Living Room Pack Home organization for the living room")),
         "room": "Living Room"},
    ]
    before = {"best_page": None, "score": None}
    old_stop = kd.STOPWORDS
    kd.STOPWORDS = old_stop - {"tips", "techniques"}
    try:
        r0 = kd.score_rows(
            {"home organization tips for living room":
             {"query": "home organization tips for living room",
              "sources": ["google"], "best_rank": 1, "seeds": ["x"]}},
            ["Living Room"], tips_inv)[0]
        before["best_page"], before["score"] = r0["best_page"], r0["coverage"]
    finally:
        kd.STOPWORDS = old_stop
    r1 = kd.score_rows(
        {"home organization tips for living room":
         {"query": "home organization tips for living room",
          "sources": ["google"], "best_rank": 1, "seeds": ["x"]}},
        ["Living Room"], tips_inv)[0]
    if r1["best_page"] != before["best_page"]:
        fails.append("excluding 'tips' from content words changed which "
                     "page the query routes to: %r -> %r"
                     % (before["best_page"], r1["best_page"]))
    if not (r1["coverage"] > before["score"]):
        fails.append("excluding 'tips' did not improve the honest score: "
                     "%r -> %r" % (before["score"], r1["coverage"]))

    # 24. Found live 2026-11-05, mining Workshop: "practices" is the same
    #     format-word shape as "tips"/"techniques" ("best practices" is a
    #     generic listicle phrase, not a subject noun), and was marking
    #     "chemical storage best practices" as only 0.667 covered against
    #     the Finishing and Chemical Zone's own title, which already names
    #     chemical storage by name. Checked for self-flattery first, same
    #     as the tips/techniques fix required: zero of our own page titles
    #     or headings anywhere on the live site carry the literal word
    #     "practices", so excluding it cannot inflate any page's score.
    if "practices" in kd.content_words("chemical storage best practices"):
        fails.append("'practices' is still a content word; the stopword "
                     "addition did not take")
    practices_inv = [
        {"url": "/zones/workshop-the-finishing-and-chemical-zone.html",
         "title": "How to organize the workshop paint and chemical storage",
         "words": set(kd.words(
             "How to organize the workshop paint and chemical storage")),
         "head_words": set(kd.words("Chemical storage")),
         "room": "Workshop"},
    ]
    before2 = {"best_page": None, "score": None}
    old_stop2 = kd.STOPWORDS
    kd.STOPWORDS = old_stop2 - {"practices"}
    try:
        r2a = kd.score_rows(
            {"chemical storage best practices":
             {"query": "chemical storage best practices",
              "sources": ["bing"], "best_rank": 21, "seeds": ["x"]}},
            ["Workshop"], practices_inv)[0]
        before2["best_page"] = r2a["best_page"]
        before2["score"] = r2a["coverage"]
    finally:
        kd.STOPWORDS = old_stop2
    r2b = kd.score_rows(
        {"chemical storage best practices":
         {"query": "chemical storage best practices",
          "sources": ["bing"], "best_rank": 21, "seeds": ["x"]}},
        ["Workshop"], practices_inv)[0]
    if r2b["best_page"] != before2["best_page"]:
        fails.append("excluding 'practices' from content words changed "
                     "which page the query routes to: %r -> %r"
                     % (before2["best_page"], r2b["best_page"]))
    if not (r2b["coverage"] > before2["score"]):
        fails.append("excluding 'practices' did not improve the honest "
                     "score: %r -> %r" % (before2["score"], r2b["coverage"]))

    # 25. Found live 2026-11-05, mining Guest Bedroom: "ways" is the same
    #     task-verb-family shape as "arrange" ("ways to organize a
    #     nightstand" asks for the same thing as "how to organize a
    #     nightstand"), not the same-shape-as-"tips" generic-filler class, so
    #     it joined FORMAT_WORDS alongside "organize"/"arrange" rather than
    #     STOPWORDS. Checked for self-flattery first, same bar as "arrange"
    #     required: zero of our own page titles carry the literal word
    #     "ways", so excluding it from content words cannot inflate any
    #     page's score.
    if "ways" in kd.content_words("ways to organize a nightstand"):
        fails.append("'ways' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    ways_inv = [
        {"url": "/zones/guest-bedroom-the-guest-nightstand.html",
         "title": "The Guest Nightstand",
         "words": set(kd.words("The Guest Nightstand")),
         "head_words": set(kd.words("The Guest Nightstand")),
         "room": "Guest Bedroom"},
    ]
    before3 = {"best_page": None, "score": None}
    old_format = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format - {"ways"}
    try:
        r3a = kd.score_rows(
            {"ways to organize nightstand":
             {"query": "ways to organize nightstand",
              "sources": ["google"], "best_rank": 1, "seeds": ["x"]}},
            ["Guest Bedroom"], ways_inv)[0]
        before3["best_page"] = r3a["best_page"]
        before3["score"] = r3a["coverage"]
    finally:
        kd.FORMAT_WORDS = old_format
    r3b = kd.score_rows(
        {"ways to organize nightstand":
         {"query": "ways to organize nightstand",
          "sources": ["google"], "best_rank": 1, "seeds": ["x"]}},
        ["Guest Bedroom"], ways_inv)[0]
    if r3b["best_page"] != before3["best_page"]:
        fails.append("excluding 'ways' from content words changed which "
                     "page the query routes to: %r -> %r"
                     % (before3["best_page"], r3b["best_page"]))
    if not (r3b["coverage"] > before3["score"]):
        fails.append("excluding 'ways' did not improve the honest score: "
                     "%r -> %r" % (before3["score"], r3b["coverage"]))

    # 26. Found live 2026-11-06, mining Garage: "diy" is the same
    #     task-verb-family shape as "ways" ("diy garden tool storage" asks
    #     for the same thing as "garden tool storage"), not a different
    #     storage subject, so it joined FORMAT_WORDS. Checked for
    #     self-flattery first, same bar as "ways" required: 0 of our own
    #     page titles carry the literal word "diy", so excluding it from
    #     content words cannot inflate any page's score.
    if "diy" in kd.content_words("diy garden tool storage"):
        fails.append("'diy' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    diy_inv = [
        {"url": "/zones/garage-the-lawn-and-garden-tool-zone.html",
         "title": "The Lawn and Garden Tool Zone",
         "words": set(kd.words("The Lawn and Garden Tool Zone")),
         "head_words": set(kd.words("The Lawn and Garden Tool Zone")),
         "room": "Garage"},
    ]
    before4 = {"best_page": None, "score": None}
    old_format2 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format2 - {"diy"}
    try:
        r4a = kd.score_rows(
            {"diy garden tool storage":
             {"query": "diy garden tool storage",
              "sources": ["google"], "best_rank": 1, "seeds": ["x"]}},
            ["Garage"], diy_inv)[0]
        before4["best_page"] = r4a["best_page"]
        before4["score"] = r4a["coverage"]
    finally:
        kd.FORMAT_WORDS = old_format2
    r4b = kd.score_rows(
        {"diy garden tool storage":
         {"query": "diy garden tool storage",
          "sources": ["google"], "best_rank": 1, "seeds": ["x"]}},
        ["Garage"], diy_inv)[0]
    if r4b["best_page"] != before4["best_page"]:
        fails.append("excluding 'diy' from content words changed which "
                     "page the query routes to: %r -> %r"
                     % (before4["best_page"], r4b["best_page"]))
    if not (r4b["coverage"] > before4["score"]):
        fails.append("excluding 'diy' did not improve the honest score: "
                     "%r -> %r" % (before4["score"], r4b["coverage"]))

    # 27. Found live 2026-11-06, mining the Hall Closet handoff: "guide" and
    #     "tutorial" name the content format a searcher wants, not a
    #     different storage subject ("how to organize closet tutorial
    #     guide" asks for the same thing as "how to organize a closet"),
    #     same shape FORMAT_WORDS already exists for. Checked for
    #     self-flattery first, same bar as "ways"/"diy" required: "tutorial"
    #     is in 0 of 243 pages' titles or headings; "guide" is in 1 title
    #     (a product name, no room) and 1 heading (unrelated to any room or
    #     zone), so excluding either cannot inflate a room/zone page's score.
    if "guide" in kd.content_words("how to organize closet tutorial guide"):
        fails.append("'guide' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    if "tutorial" in kd.content_words("how to organize closet tutorial guide"):
        fails.append("'tutorial' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    closet_inv = [
        {"url": "/articles/how-to-organize-a-linen-closet.html",
         "title": "How to organize a linen closet: sheets, towels and shelves",
         "words": set(kd.words(
             "How to organize a linen closet: sheets, towels and shelves")),
         "head_words": set(kd.words(
             "How to organize a linen closet: sheets, towels and shelves")),
         "room": "Hall Closet"},
    ]
    before5 = {"best_page": None, "score": None}
    old_format3 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format3 - {"guide", "tutorial"}
    try:
        r5a = kd.score_rows(
            {"how to organize closet tutorial guide":
             {"query": "how to organize closet tutorial guide",
              "sources": ["bing"], "best_rank": 14, "seeds": ["x"]}},
            ["Hall Closet"], closet_inv)[0]
        before5["best_page"] = r5a["best_page"]
        before5["score"] = r5a["coverage"]
    finally:
        kd.FORMAT_WORDS = old_format3
    r5b = kd.score_rows(
        {"how to organize closet tutorial guide":
         {"query": "how to organize closet tutorial guide",
          "sources": ["bing"], "best_rank": 14, "seeds": ["x"]}},
        ["Hall Closet"], closet_inv)[0]
    if r5b["best_page"] != before5["best_page"]:
        fails.append("excluding 'guide'/'tutorial' from content words "
                     "changed which page the query routes to: %r -> %r"
                     % (before5["best_page"], r5b["best_page"]))
    if not (r5b["coverage"] > before5["score"]):
        fails.append("excluding 'guide'/'tutorial' did not improve the "
                     "honest score: %r -> %r"
                     % (before5["score"], r5b["coverage"]))

    # 28. Found live 2026-11-07, PM check-in: household_room_signal() used a
    #     plain substring check, so Family Room's 3-letter synonym "den"
    #     matched inside any word merely containing that letter run, no word
    #     boundary required. "nightstands with hidden storage" (a Primary
    #     Bedroom query) carried "hidden", which contains "den", and so
    #     wrongly signalled Family Room; counted live, 74 corpus rows shared
    #     this exact shape ("garden", "gardening", "wooden", "dental", etc),
    #     none of them actually about Family Room. A real word boundary must
    #     refuse the bare letter run while still matching a real synonym,
    #     including one inside a longer phrase or carrying a plural "s".
    rooms28 = ["Family Room", "Mudroom", "Primary Bedroom"]
    synonyms28 = {"Family Room": ["den"], "Mudroom": ["locker"],
                  "Primary Bedroom": ["master bedroom"]}
    sig28a = kd.household_room_signal(
        "nightstands with hidden storage", rooms28, synonyms28)
    if sig28a != "":
        fails.append("'den' inside 'hidden' still signals a room: %r"
                     % sig28a)
    sig28b = kd.household_room_signal(
        "best garden tool organizer", rooms28, synonyms28)
    if sig28b != "":
        fails.append("'den' inside 'garden' still signals a room: %r"
                     % sig28b)
    sig28c = kd.household_room_signal(
        "how to organize a den", rooms28, synonyms28)
    if sig28c != "Family Room":
        fails.append("a real 'den' query no longer signals Family Room: %r"
                     % sig28c)
    sig28d = kd.household_room_signal(
        "master bedroom closet organization ideas", rooms28, synonyms28)
    if sig28d != "Primary Bedroom":
        fails.append("a multi-word synonym inside a longer phrase broke: %r"
                     % sig28d)
    sig28e = kd.household_room_signal(
        "how to organize mudroom lockers", rooms28, synonyms28)
    if sig28e != "Mudroom":
        fails.append("a plural of a real synonym no longer matches: %r"
                     % sig28e)
    # A first version of this fix required a bare \bname\b with no plural
    # tolerance and broke three real matches a full-corpus diff caught
    # before shipping: a single-word synonym's plain "s" plural, standalone
    # (not backed by an exact room-name match the way "mudroom lockers"
    # above is), and a multi-word synonym's plural.
    rooms28b = ["Patio or Deck", "Pantry", "Primary Bedroom"]
    synonyms28b = {"Patio or Deck": ["backyard"], "Pantry": ["larder"],
                   "Primary Bedroom": ["master bedroom"]}
    sig28f = kd.household_room_signal(
        "grill stations ideas for backyards", rooms28b, synonyms28b)
    if sig28f != "Patio or Deck":
        fails.append("'backyards' (plural) no longer signals Patio or "
                     "Deck: %r" % sig28f)
    sig28g = kd.household_room_signal("larders own", rooms28b, synonyms28b)
    if sig28g != "Pantry":
        fails.append("'larders' (plural) no longer signals Pantry: %r"
                     % sig28g)
    sig28h = kd.household_room_signal(
        "types of master bedrooms", rooms28b, synonyms28b)
    if sig28h != "Primary Bedroom":
        fails.append("'master bedrooms' (plural) no longer signals "
                     "Primary Bedroom: %r" % sig28h)

    # 29. Found live 2026-11-09, mining Kitchen: "way" (singular) is the
    #     same task-verb-family shape as "ways" ("best way to organize
    #     kitchen cooking utensils" asks for the same thing as "how to
    #     organize kitchen cooking utensils"), simply never added alongside
    #     the plural when it joined FORMAT_WORDS on 2026-11-05. Checked for
    #     self-flattery first, same bar as "ways" required: zero of our own
    #     page titles carry the literal word "way".
    if "way" in kd.content_words("best way to organize kitchen utensils"):
        fails.append("'way' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    way_inv = [
        {"url": "/zones/kitchen-the-cooking-zone.html",
         "title": "How to organize the kitchen stove area",
         "words": set(kd.words("How to organize the kitchen stove area")),
         "head_words": set(kd.words("How to organize the kitchen stove "
                                     "area utensil crock")),
         "room": "Kitchen"},
    ]
    before5 = {"best_page": None, "score": None}
    old_format3 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format3 - {"way"}
    try:
        r5a = kd.score_rows(
            {"best way to organize kitchen cooking utensils":
             {"query": "best way to organize kitchen cooking utensils",
              "sources": ["bing"], "best_rank": 15, "seeds": ["x"]}},
            ["Kitchen"], way_inv)[0]
        before5["best_page"] = r5a["best_page"]
        before5["score"] = r5a["coverage"]
    finally:
        kd.FORMAT_WORDS = old_format3
    r5b = kd.score_rows(
        {"best way to organize kitchen cooking utensils":
         {"query": "best way to organize kitchen cooking utensils",
          "sources": ["bing"], "best_rank": 15, "seeds": ["x"]}},
        ["Kitchen"], way_inv)[0]
    if r5b["best_page"] != before5["best_page"]:
        fails.append("excluding 'way' from content words changed which "
                     "page the query routes to: %r -> %r"
                     % (before5["best_page"], r5b["best_page"]))
    if not (r5b["coverage"] > before5["score"]):
        fails.append("excluding 'way' did not improve the honest score: "
                     "%r -> %r" % (before5["score"], r5b["coverage"]))

    # 30. Found live 2026-11-10, mining Kitchen: every prior FORMAT_WORDS
    #     addition ("ways"/"diy"/"guide"/"tutorial"/"way"/"must"/"haves")
    #     was a framing or format word, where dropping it from
    #     content_words() cannot make a query's honest coverage worse,
    #     because the two phrasings ask for the same subject. A negation or
    #     scope word ("without", "only", "no", "except", "excluding") is a
    #     different shape: "a kitchen without cabinets" is a genuinely
    #     different situation than "a kitchen", not a wording choice, so
    #     treating it as free would mark a query `covered` by a page that
    #     does not actually address the missing feature, exactly the
    #     dishonest-coverage shape CLAUDE.md 0.4/5d exist to block. This
    #     pins that none of these words is ever silently added to
    #     FORMAT_WORDS the way "ways"/"diy"/"way" were.
    NEGATION_WORDS = ("without", "only", "no", "except", "excluding",
                      "besides", "unless", "instead")
    for _nw in NEGATION_WORDS:
        if _nw in kd.FORMAT_WORDS:
            fails.append("%r is a negation/scope word and must never be "
                         "in FORMAT_WORDS; it changes the query's real "
                         "subject, it does not just rephrase it" % _nw)

    # 31. Found live 2026-11-10, mining Garage: "quickly" scored as a
    #     content word was causing a real wrong tie-break, the same "diy"
    #     shape (case concerning case 2026-11-06 above): "how to organize a
    #     garage sale quickly" tied 2-of-3 between the Garage room page's
    #     own "Garage sale" heading (matching garage+sale, missing
    #     "quickly") and an unrelated article's "How do I declutter a
    #     garage quickly?" heading (matching garage+quickly, missing
    #     "sale"), and the tie-break happened to prefer the unrelated page.
    if "quickly" in kd.content_words(
            "how to organize a garage sale quickly"):
        fails.append("'quickly' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    quickly_inv = [
        {"url": "/rooms/garage.html",
         "title": "Garage",
         "words": set(kd.words("Garage Garage sale")),
         "head_words": set(kd.words("Garage sale")),
         "room": "Garage"},
        {"url": "/articles/how-to-organize-a-garage.html",
         "title": "How to organize a garage full of stuff, step by step",
         "words": set(kd.words("How do I declutter a garage quickly")),
         "head_words": set(kd.words("How do I declutter a garage "
                                     "quickly")),
         "room": "Garage"},
    ]
    old_format4 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format4 - {"quickly"}
    try:
        r6a = kd.score_rows(
            {"how to organize a garage sale quickly":
             {"query": "how to organize a garage sale quickly",
              "sources": ["bing"], "best_rank": 2, "seeds": ["x"]}},
            ["Garage"], quickly_inv)[0]
        before6_page = r6a["best_page"]
        before6_score = r6a["coverage"]
    finally:
        kd.FORMAT_WORDS = old_format4
    r6b = kd.score_rows(
        {"how to organize a garage sale quickly":
         {"query": "how to organize a garage sale quickly",
          "sources": ["bing"], "best_rank": 2, "seeds": ["x"]}},
        ["Garage"], quickly_inv)[0]
    if before6_page != "/articles/how-to-organize-a-garage.html":
        fails.append("test fixture no longer reproduces the pre-fix tie "
                     "break onto the unrelated article: %r" % before6_page)
    if r6b["best_page"] != "/rooms/garage.html":
        fails.append("excluding 'quickly' did not route the query to the "
                     "room's own 'Garage sale' section: got %r"
                     % r6b["best_page"])
    if not (r6b["coverage"] > before6_score):
        fails.append("excluding 'quickly' did not improve the honest "
                     "score: %r -> %r" % (before6_score, r6b["coverage"]))

    # 32. Found live 2026-11-11, mining Hall Closet's remaining partial
    #     tier: "how to organize closet review" asks for the same thing as
    #     "how to organize closet", "review" naming the write-up format
    #     wanted, the same role "guide"/"tutorial"/"overview" already play.
    if "review" in kd.content_words("how to organize closet review"):
        fails.append("'review' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    old_format5 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format5 - {"review"}
    try:
        if "review" not in kd.content_words("how to organize closet review"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'review' was dropped even with the "
                         "word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format5

    # 33. Found live 2026-11-11, same pass: "how to organize closet 2024"
    #     and "how to organize closet 2025" each failed on their bare year
    #     alone, and the same shape repeats across other rooms; a year
    #     suffix is a freshness qualifier, not a different subject, so
    #     content_words() now drops any bare 20xx token via a regex rather
    #     than a frozenset entry that would need yearly upkeep.
    if "2025" in kd.content_words("how to organize closet 2025"):
        fails.append("'2025' is still a content word; the year-suffix "
                     "regex did not take")
    if "2099" in kd.content_words("decorating ideas for 2099"):
        fails.append("a future year is still a content word; the "
                     "year-suffix regex is not general")
    old_year = kd._YEAR_WORD
    kd._YEAR_WORD = kd.re.compile(r"$never-matches$")
    try:
        if "2025" not in kd.content_words("how to organize closet 2025"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: '2025' was dropped even with the "
                         "year regex disabled")
    finally:
        kd._YEAR_WORD = old_year

    # 34. Found live 2026-11-11, mining Garage's remaining partial tier.
    #     "buy garden tool storage" asks the same thing as "garden tool
    #     storage", the same shopping-frame shape "deals" already covers.
    #     "cleaning equipment checklist template" asks the same thing as
    #     "cleaning equipment checklist", "template" naming the document
    #     format, the same role "guide"/"overview" already play.
    if "buy" in kd.content_words("buy garden tool storage"):
        fails.append("'buy' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    if "template" in kd.content_words("cleaning equipment checklist template"):
        fails.append("'template' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    old_format6 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format6 - {"buy", "template"}
    try:
        if "buy" not in kd.content_words("buy garden tool storage"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'buy' was dropped even with the "
                         "word removed from FORMAT_WORDS")
        if "template" not in kd.content_words("cleaning equipment checklist template"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'template' was dropped even with the "
                         "word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format6

    # 35. Found live 2026-11-11, mining Guest Bedroom's partial tier.
    #     "nightstand organizer for men" and "how to organize dresser men"
    #     ask the same organizing question regardless of the demographic
    #     named; "storage containers for linens" asks the same thing as
    #     "storage for linens", "containers" naming a product category the
    #     page already answers in generic terms.
    if "men" in kd.content_words("nightstand organizer for men"):
        fails.append("'men' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    if "containers" in kd.content_words("storage containers for linens"):
        fails.append("'containers' is still a content word; the "
                     "FORMAT_WORDS addition did not take")
    old_format7 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format7 - {"her", "him", "men", "women",
                                      "container", "containers"}
    try:
        if "men" not in kd.content_words("nightstand organizer for men"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'men' was dropped even with the "
                         "word removed from FORMAT_WORDS")
        if "containers" not in kd.content_words("storage containers for linens"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'containers' was dropped even with "
                         "the word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format7

    # 36. Found live 2026-11-11, mining Garage's partial tier. "car
    #     organisation essentials" asks the same thing as "car
    #     organisation", "essentials" naming the necessary-items framing,
    #     the same role "must"/"haves" already play.
    if "essentials" in kd.content_words("car organisation essentials"):
        fails.append("'essentials' is still a content word; the "
                     "FORMAT_WORDS addition did not take")
    old_format8 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format8 - {"essentials"}
    try:
        if "essentials" not in kd.content_words("car organisation essentials"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'essentials' was dropped even with "
                         "the word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format8

    # 37. Found live 2026-11-11, mining Hall Closet's remaining partial
    #     tier. "how to organize household cleaning supplies" asks the
    #     same thing as "how to organize cleaning supplies", "household"
    #     naming the same not-a-different-subject scope qualifier
    #     "essentials"/"men"/"women" already cover.
    if "household" in kd.content_words("how to organize household cleaning supplies"):
        fails.append("'household' is still a content word; the "
                     "FORMAT_WORDS addition did not take")
    old_format9 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format9 - {"household"}
    try:
        if "household" not in kd.content_words("how to organize household cleaning supplies"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'household' was dropped even with "
                         "the word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format9

    # 38. Found live 2026-11-11, mining Garage's remaining partial tier.
    #     "how to reorganize storage" asks the same thing as "how to
    #     organize storage", "reorganize" naming the same not-a-different-
    #     subject verb "rearrange" already covers.
    if "reorganize" in kd.content_words("how to reorganize storage"):
        fails.append("'reorganize' is still a content word; the "
                     "FORMAT_WORDS addition did not take")
    old_format10 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format10 - {"reorganize"}
    try:
        if "reorganize" not in kd.content_words("how to reorganize storage"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'reorganize' was dropped even with "
                         "the word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format10

    # 39. Found live 2026-11-11, same cycle. "daily equipment cleaning
    #     checklist" asks the same thing as "equipment cleaning checklist",
    #     "daily" naming the same frequency qualifier "quickly"/"routine"
    #     already cover.
    if "daily" in kd.content_words("daily equipment cleaning checklist"):
        fails.append("'daily' is still a content word; the "
                     "FORMAT_WORDS addition did not take")
    old_format11 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format11 - {"daily"}
    try:
        if "daily" not in kd.content_words("daily equipment cleaning checklist"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'daily' was dropped even with "
                         "the word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format11

    # 39b. Found live 2026-11-11, mining Home Office and Guest Bathroom's
    #     partial tiers. "desk organisation inspo" and "desk organisation
    #     inspiration" ask the same thing as "desk organisation", "inspo"/
    #     "inspiration" naming the same content-format wish "guide"/"ideas"
    #     already cover, not a different subject.
    if "inspo" in kd.content_words("desk organisation inspo"):
        fails.append("'inspo' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    if "inspiration" in kd.content_words("desk organisation inspiration"):
        fails.append("'inspiration' is still a content word; the "
                     "FORMAT_WORDS addition did not take")
    old_format11b = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format11b - {"inspo", "inspiration"}
    try:
        if "inspo" not in kd.content_words("desk organisation inspo"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'inspo' was dropped even with "
                         "the word removed from FORMAT_WORDS")
        if "inspiration" not in kd.content_words("desk organisation inspiration"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'inspiration' was dropped even with "
                         "the word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format11b

    # 40. Found live 2026-11-11: "organized bathroom cupboard" tied on
    #     headings between the real bathroom zone pages and the Hall
    #     Closet linen article, and the linen article won only because its
    #     own promotional band heading names "the bathroom towels", a
    #     different room's own words, not anything the linen article is
    #     about. page_inventory() must drop a band word from head_words
    #     only when that word identifies another room (>=3 zone-title
    #     occurrences, owned by <=2 rooms) and this page's own room is not
    #     one of them; a non-band heading, and a band word with too few
    #     occurrences to call room-specific (the "cabinets" case below,
    #     the regression a careless version of this fix produced live
    #     against the real corpus before it shipped), must never be
    #     touched.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        zones_dir = os.path.join(tmp, "zones")
        os.makedirs(zones_dir)

        def zone_page(fname, title, extra_head=""):
            with open(os.path.join(zones_dir, fname), "w",
                      encoding="utf-8") as fh:
                fh.write("<html><head><title>%s</title></head><body>"
                          "<h1>%s</h1>%s</body></html>" % (title, title, extra_head))

        # Three zone pages give "bathroom" 3 occurrences across exactly 2
        # rooms, clearing the room-identifying bar.
        zone_page("primary-bathroom-the-vanity-counter.html",
                   "The primary bathroom vanity counter")
        zone_page("primary-bathroom-the-shower-or-tub.html",
                   "The primary bathroom shower or tub")
        zone_page("guest-bathroom-the-vanity-counter.html",
                   "The guest bathroom vanity counter")
        # Two zone pages give "cabinets" only 2 occurrences, one short of
        # the bar, so it must stay unflagged everywhere.
        zone_page("kitchen-the-upper-cabinets.html",
                   "The kitchen upper cabinets")
        zone_page("kitchen-the-lower-cabinets.html",
                   "The kitchen lower cabinets")
        # The Hall Closet page itself: a real, non-band heading ("linen
        # shelf") plus a promotional band that leaks "bathroom" (foreign)
        # and "cabinets" (not foreign, below the bar) from other rooms.
        zone_page("hall-closet-the-linen-shelf-zone.html",
                   "How to organize the hall closet linen shelf zone",
                   '<section class="band"><h2>The linen shelf, the '
                   'bathroom towels and the cabinets, zone by zone</h2>'
                   '</section>')
        old_site = kd.SITE
        kd.SITE = tmp
        try:
            inv = kd.page_inventory(rooms=["Hall Closet", "Primary Bathroom",
                                           "Guest Bathroom", "Kitchen"])
        finally:
            kd.SITE = old_site
    by_url = {r["url"]: r for r in inv}
    hall = by_url.get("/zones/hall-closet-the-linen-shelf-zone.html")
    if hall is None:
        fails.append("page_inventory() did not read the Hall Closet "
                     "throwaway page")
    else:
        if "bathroom" in hall["head_words"]:
            fails.append("'bathroom', another room's own word, still "
                         "leaked into the Hall Closet page's head_words "
                         "via its band heading: %r" % hall["head_words"])
        if "cabinets" not in hall["head_words"]:
            fails.append("'cabinets' was dropped from the Hall Closet "
                         "page's band heading despite having too few "
                         "occurrences (2) to count as room-identifying: "
                         "%r" % hall["head_words"])
        if "linen" not in hall["head_words"] or "shelf" not in hall["head_words"]:
            fails.append("a real, non-band heading word was dropped "
                         "along with the band fix: %r" % hall["head_words"])
    primary = by_url.get("/zones/primary-bathroom-the-vanity-counter.html")
    if primary and "bathroom" not in primary["head_words"]:
        fails.append("'bathroom' was dropped from a Primary Bathroom "
                     "page's own title, which is not a band heading at "
                     "all: %r" % primary["head_words"])

    # 41. Found live 2026-11-11, chasing the "organized bathroom cupboard"
    #     misroute entry 40 above named as its own next lead:
    #     `/articles/index.html` mechanically repeats every one of its 56
    #     linked articles' own titles as its own <h2>, so it ties or beats
    #     the real destination page on hundreds of unrelated queries. A
    #     heading that is entirely one hyperlink to another page is that
    #     other page's own title, not this page's own content, and must be
    #     dropped from head_words; a real, non-link heading on the same
    #     page, and a heading that MIXES a link with its own prose, must
    #     both survive untouched.
    with tempfile.TemporaryDirectory() as tmp2:
        articles_dir = os.path.join(tmp2, "articles")
        os.makedirs(articles_dir)
        with open(os.path.join(articles_dir, "index.html"), "w",
                  encoding="utf-8") as fh:
            fh.write(
                "<html><head><title>Articles: an index</title></head>"
                "<body><h1>The reasoning behind the method</h1>"
                "<h2><a href=\"how-to-organize-an-attic\">How to organize "
                "an attic without overloading it</a></h2>"
                "<h2>Why mixed headings still count</h2>"
                "<h3>Not a link <a href=\"x\">at all</a>, real prose</h3>"
                "</body></html>")
        old_site2 = kd.SITE
        kd.SITE = tmp2
        try:
            inv2 = kd.page_inventory(rooms=[])
        finally:
            kd.SITE = old_site2
    idx = {r["url"]: r for r in inv2}.get("/articles/index.html")
    if idx is None:
        fails.append("page_inventory() did not read the throwaway "
                     "articles/index.html page")
    else:
        if "attic" in idx["head_words"] or "overloading" in idx["head_words"]:
            fails.append("a pure-hyperlink heading (another page's own "
                         "title) still leaked into index.html's own "
                         "head_words: %r" % idx["head_words"])
        if "mixed" not in idx["head_words"] or "headings" not in idx["head_words"]:
            fails.append("a real, non-link heading on the same hub page "
                         "was dropped along with the link-heading fix: "
                         "%r" % idx["head_words"])
        if "prose" not in idx["head_words"] or "link" not in idx["head_words"]:
            fails.append("a heading that mixes a link with its own prose "
                         "must still count as this page's own content: "
                         "%r" % idx["head_words"])

    # 42. Found live 2026-11-11, mining Kitchen's partial tier. "images",
    #     "efficiency", "chef", "modern", "rustic" and "simple" each name a
    #     format, goal, skill-level or style qualifier on the same organizing
    #     question, the same not-a-different-subject shape "guide"/"quickly"/
    #     "original" already cover, not a different subject.
    new_format_words = ("images", "efficiency", "chef", "modern", "rustic", "simple")
    samples = {
        "images": "kitchen organisation ideas images",
        "efficiency": "how to organize a kitchen for efficiency",
        "chef": "how to organize a kitchen like a chef",
        "modern": "declutter modern kitchen",
        "rustic": "declutter rustic kitchen ideas",
        "simple": "kitchen organization ideas simple",
    }
    for word in new_format_words:
        if word in kd.content_words(samples[word]):
            fails.append("%r is still a content word; the FORMAT_WORDS "
                         "addition did not take" % word)
    old_format12 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format12 - set(new_format_words)
    try:
        for word in new_format_words:
            if word not in kd.content_words(samples[word]):
                fails.append("test fixture no longer reproduces the "
                             "pre-fix behaviour: %r was dropped even with "
                             "the word removed from FORMAT_WORDS" % word)
    finally:
        kd.FORMAT_WORDS = old_format12

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # 43. Found live 2026-11-11, mining Family Room and Guest Bedroom's
    #     partial tiers. "choose" names the same decision the verb
    #     "organize"/"pick" already covers ("how to choose toy organizer",
    #     "how to choose nightstand"), not a different subject.
    if "choose" in kd.content_words("how to choose toy organizer"):
        fails.append("'choose' is still a content word; the FORMAT_WORDS "
                     "addition did not take")
    old_format13 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format13 - {"choose"}
    try:
        if "choose" not in kd.content_words("how to choose toy organizer"):
            fails.append("test fixture no longer reproduces the pre-fix "
                         "behaviour: 'choose' was dropped even with the "
                         "word removed from FORMAT_WORDS")
    finally:
        kd.FORMAT_WORDS = old_format13

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # 44. Found live 2026-11-11, mining Hall Closet's remaining partial
    #     tier. "deep" names the closet's own depth, a descriptive
    #     qualifier, not a different subject ("how to organize a deep hall
    #     closet" asks the same thing as "how to organize a hall closet").
    #     "hacks" names an informal tips format, the same role "tips"/
    #     "ideas" already play in STOPWORDS ("linen closet organization
    #     hacks" asks the same thing as "linen closet organization").
    new_format_words14 = ("deep", "hacks")
    samples14 = {
        "deep": "how to organize a deep hall closet",
        "hacks": "linen closet organization hacks",
    }
    for word in new_format_words14:
        if word in kd.content_words(samples14[word]):
            fails.append("%r is still a content word; the FORMAT_WORDS "
                         "addition did not take" % word)
    old_format14 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format14 - set(new_format_words14)
    try:
        for word in new_format_words14:
            if word not in kd.content_words(samples14[word]):
                fails.append("test fixture no longer reproduces the "
                             "pre-fix behaviour: %r was dropped even with "
                             "the word removed from FORMAT_WORDS" % word)
    finally:
        kd.FORMAT_WORDS = old_format14

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # 45. Found live 2026-11-11, mining Garage's remaining partial tier.
    #     "lots" names a quantity ("how to organize a garage with lots of
    #     tools" asks the same question as "...with tools"), not a
    #     different subject, so it joined FORMAT_WORDS.
    new_format_words15 = ("lots",)
    samples15 = {
        "lots": "how to organize a garage with lots of tools",
    }
    for word in new_format_words15:
        if word in kd.content_words(samples15[word]):
            fails.append("%r is still a content word; the FORMAT_WORDS "
                         "addition did not take" % word)
    old_format15 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format15 - set(new_format_words15)
    try:
        for word in new_format_words15:
            if word not in kd.content_words(samples15[word]):
                fails.append("test fixture no longer reproduces the "
                             "pre-fix behaviour: %r was dropped even with "
                             "the word removed from FORMAT_WORDS" % word)
    finally:
        kd.FORMAT_WORDS = old_format15

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # 46. Found live 2026-11-11, mining Hall Closet's remaining partial
    #     tier. "categories" names the structure of the answer wanted
    #     ("linen closet organization categories" asks the same question
    #     as "linen closet organization"), the same role "overview" already
    #     plays; "pro" is an informal-expertise qualifier on the tips
    #     wanted ("how to organize closet quickly pro tips"), the same
    #     shape "hacks" already covers. Both joined FORMAT_WORDS.
    new_format_words16 = ("categories", "pro")
    samples16 = {
        "categories": "linen closet organization categories",
        "pro": "how to organize closet quickly pro tips",
    }
    for word in new_format_words16:
        if word in kd.content_words(samples16[word]):
            fails.append("%r is still a content word; the FORMAT_WORDS "
                         "addition did not take" % word)
    old_format16 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format16 - set(new_format_words16)
    try:
        for word in new_format_words16:
            if word not in kd.content_words(samples16[word]):
                fails.append("test fixture no longer reproduces the "
                             "pre-fix behaviour: %r was dropped even with "
                             "the word removed from FORMAT_WORDS" % word)
    finally:
        kd.FORMAT_WORDS = old_format16

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # 47. Found live 2026-11-11, mining Home Office's remaining partial
    #     tier. "aesthetically" names the look wanted, not a different
    #     subject ("how to organize bookshelf aesthetically" asks the same
    #     thing as "how to organize bookshelf"), so it joined FORMAT_WORDS.
    new_format_words17 = ("aesthetically",)
    samples17 = {
        "aesthetically": "how to organize bookshelf aesthetically",
    }
    for word in new_format_words17:
        if word in kd.content_words(samples17[word]):
            fails.append("%r is still a content word; the FORMAT_WORDS "
                         "addition did not take" % word)
    old_format17 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format17 - set(new_format_words17)
    try:
        for word in new_format_words17:
            if word not in kd.content_words(samples17[word]):
                fails.append("test fixture no longer reproduces the "
                             "pre-fix behaviour: %r was dropped even with "
                             "the word removed from FORMAT_WORDS" % word)
    finally:
        kd.FORMAT_WORDS = old_format17

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # 48. Found live 2026-11-11, mining Garage's and Nursery's remaining
    #     partial tiers. "newborn" names the occupant's age, not a
    #     different subject ("newborn baby nursery organizer" asks the same
    #     thing as "baby nursery organizer"). "planning" is a task-verb
    #     synonym for the layout work "arrange" already covers ("planning a
    #     gallery wall" asks the same thing as "arranging a gallery wall").
    #     Both joined FORMAT_WORDS. "plan" (singular) was tried for the same
    #     tier and declined: it flips 2 literal floor-plan queries onto the
    #     wrong page.
    new_format_words18 = ("newborn", "planning")
    samples18 = {
        "newborn": "newborn baby nursery organizer",
        "planning": "planning a gallery wall",
    }
    for word in new_format_words18:
        if word in kd.content_words(samples18[word]):
            fails.append("%r is still a content word; the FORMAT_WORDS "
                         "addition did not take" % word)
    old_format18 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format18 - set(new_format_words18)
    try:
        for word in new_format_words18:
            if word not in kd.content_words(samples18[word]):
                fails.append("test fixture no longer reproduces the "
                             "pre-fix behaviour: %r was dropped even with "
                             "the word removed from FORMAT_WORDS" % word)
    finally:
        kd.FORMAT_WORDS = old_format18

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # 49. Found live 2026-11-11, mining Workshop's and Nursery's remaining
    #     partial tiers (BACKLOG-2026-09-07.md's own room-guide handoff).
    #     "workplace" names the setting, not a different subject ("safety
    #     gear in the workplace" asks the same thing as "safety gear",
    #     already answered by the Workshop's PPE zone). "disposal" is a
    #     noun form of "dispose", which the query already treats as the
    #     action word, not a different subject ("adult diaper disposal
    #     container" asks the same thing as "adult diaper container").
    #     "dispose" (verb) and "fold" and "front" were each tried for the
    #     same tiers and declined: a full before/after corpus rescore found
    #     2, 5 and 11 real best_page changes respectively, moving queries
    #     between pages rather than only moving status, the same risk shape
    #     "declutter" and "messy" were declined for in case 46.
    new_format_words19 = ("workplace", "disposal")
    samples19 = {
        "workplace": "safety gear in the workplace",
        "disposal": "adult diaper disposal container",
    }
    for word in new_format_words19:
        if word in kd.content_words(samples19[word]):
            fails.append("%r is still a content word; the FORMAT_WORDS "
                         "addition did not take" % word)
    old_format19 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format19 - set(new_format_words19)
    try:
        for word in new_format_words19:
            if word not in kd.content_words(samples19[word]):
                fails.append("test fixture no longer reproduces the "
                             "pre-fix behaviour: %r was dropped even with "
                             "the word removed from FORMAT_WORDS" % word)
    finally:
        kd.FORMAT_WORDS = old_format19

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # 50. Found live 2026-11-12, mining Hall Closet's remaining partial tier
    #     (the 2026-11-12 PM check-in's own handoff). "basket"/"baskets" name
    #     a storage product category the destination page already answers in
    #     generic terms, the same shopping-noun role "container"/"containers"
    #     already play, not a different subject ("linen closet organization
    #     baskets" asks the same thing as "linen closet organization").
    #     "design" was checked again for the same tier and declined again:
    #     a different search intent (interior decor), not a vocabulary gap,
    #     per the standing verdict in BACKLOG-2026-09-07-CLOSED-ARCHIVE.md.
    new_format_words20 = ("basket", "baskets")
    samples20 = {
        "basket": "how to arrange towels in a basket",
        "baskets": "linen closet organization baskets",
    }
    for word in new_format_words20:
        if word in kd.content_words(samples20[word]):
            fails.append("%r is still a content word; the FORMAT_WORDS "
                         "addition did not take" % word)
    old_format20 = kd.FORMAT_WORDS
    kd.FORMAT_WORDS = old_format20 - set(new_format_words20)
    try:
        for word in new_format_words20:
            if word not in kd.content_words(samples20[word]):
                fails.append("test fixture no longer reproduces the "
                             "pre-fix behaviour: %r was dropped even with "
                             "the word removed from FORMAT_WORDS" % word)
    finally:
        kd.FORMAT_WORDS = old_format20

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
