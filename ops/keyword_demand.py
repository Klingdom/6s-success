#!/usr/bin/env python3
"""
What people actually type, read from the engines themselves, with no account.

WHY THIS EXISTS
---------------
GOALS.md has said the same thing for a month: "What we still cannot see is
impressions and queries, and that needs Search Console, which is
OWNER-ACTIONS.md 1a." Half of that is true and half of it is not, and the
difference decides whether a cycle can do useful discovery work today.

Search Console is the only way to see OUR impressions: which of our pages were
shown, for what, and how often they were clicked. Nothing here replaces that,
and this file does not try to.

But the other half, WHAT PEOPLE TYPE, is public. Google and Bing both expose
their autocomplete endpoints without a key, without an account and without a
referrer check. That is the half that decides what to write, and we have never
once looked at it. Every search term this site targets was invented by reading
the Micro Zone Manual, which is why 115 pages carry internal vocabulary like
"coats and outerwear" and "landing zone" while the suggestion list for the same
room is full of "cubbies", "lockers", "small mudroom" and "shoes".

This tool harvests those suggestions for every room and zone in the real
corpus, then asks one question of each: do we have a page for this, and does
its title use these words?

WHAT THIS DATA IS, AND WHAT IT IS NOT
-------------------------------------
It is NOT search volume. Nothing here reports a number of searches per month
and nothing here may be presented as one. An autocomplete suggestion proves
only that an engine considers the phrase a likely completion, which means real
people type it often enough to be worth predicting. That is weaker than volume
and much stronger than the nothing we have today.

The client=chrome response carries google:suggestrelevance, which orders the
suggestions against each other within one response. It is a relative rank
inside one seed result, not a cross-seed quantity, so this file keeps only the
rank (1 is the top suggestion) and refuses to add relevance across seeds.
Summing them would produce a confident-looking number that means nothing, which
is the failure mode CLAUDE.md section 25 names.

HOW IT REFUSES TO LIE
---------------------
The dominant defect class in this repository is a check that could not fail,
and a harvester is an easy place to reproduce it: an engine that rate-limits
returns a valid, empty, HTTP 200 response, and a naive run would write
"0 gaps found" and exit 0. So:

  * every seed outcome is recorded individually as ok, empty or error
  * an empty 200 is NOT counted as a success, and NOT counted as a failure
    either. The first version of this file called it a failure, and the very
    first run proved that wrong: "why is my entryway always messy" genuinely
    has no completions, and calling that a failure would have voided an
    otherwise clean harvest. Blocking and a genuine zero look identical in one
    response, so they are told apart across the run instead
  * a CANARY seed with completions nobody doubts is fetched first and again
    last. If either canary comes back empty, the endpoint is answering 200
    with nothing and the whole run is void, however many other rows arrived
  * nothing is written if the error rate exceeds MAX_ERROR_RATE, or the empty
    rate exceeds MAX_EMPTY_RATE, or a canary is empty. A partial harvest must
    never overwrite a complete one, because the diff would read as
    "demand collapsed"
  * the output records checked_at, the sources, the seed count and the full
    failure list, so a reader can always tell what was not looked at

Run:  python ops/keyword_demand.py                 harvest Google, write outputs
      python ops/keyword_demand.py --source bing   harvest Bing instead
      python ops/keyword_demand.py --source both   harvest both, union the queries
      python ops/keyword_demand.py --dry-run       first 6 seeds only, write nothing
      python ops/keyword_demand.py --status        read the last harvest, write nothing
      python ops/keyword_demand.py --rescore       re-derive coverage against
                                                   the current site: no network,
                                                   no new demand data
      python ops/keyword_demand.py --help          print this and stop

An argument this file does not recognise is REFUSED, not ignored. Found
2026-10-03: --help was not a flag here, so it fell through every check above
and started a full live harvest of both engines, which is the one thing a
reader asking for help cannot have meant. Nothing that writes files or
touches the network may be reachable by a typo.
"""
import datetime
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CONTENT = os.path.join(ROOT, "mcp", "content.json")
ZONE_TERMS = os.path.join(ROOT, "ops", "zone-search-terms.json")
ROOM_ALSO_CALLED = os.path.join(ROOT, "ops", "room-also-called.json")
OUT_JSON = os.path.join(ROOT, "ops", "keyword-demand.json")
OUT_MD = os.path.join(ROOT, "ops", "KEYWORD-DEMAND.md")

# Polite by design. These endpoints are public but they are not ours, and a
# burst is how a client earns a block: the session that wrote this file lost
# DuckDuckGo for the rest of an hour by firing eight requests in twelve
# seconds, which is the whole reason the delay is here and not tunable.
DELAY = (0.9, 1.8)
TIMEOUT = 20
MAX_ERROR_RATE = 0.10
# Long complaint-style seeds often have no completions at all, so a high empty
# rate is normal. This ceiling is here to catch the other case: an endpoint
# that has started answering 200 with nothing for everything.
MAX_EMPTY_RATE = 0.50
# A phrase whose completions are not in doubt. If this one comes back empty we
# are being refused, whatever the rest of the run looks like.
CANARY = "how to organize a kitchen"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Four intents, because they are four different jobs and a room ranks for them
# separately: the how-to, the shopping-adjacent "ideas" phrasing, the
# decluttering entry point, and the complaint, which is how somebody searches
# before they know organising is the answer.
ROOM_TEMPLATES = (
    "how to organize a {room}",
    "{room} organization ideas",
    "how to declutter a {room}",
    "why is my {room} always messy",
)

# THE SEEDS DECIDE WHAT CAN BE FOUND, AND OURS CAME FROM OUR OWN VOCABULARY.
#
# Found 2026-10-01, after the first harvest. Every seed was built from the
# twenty room names in content.json plus the sixty hand-written zone search
# terms, so the harvest could only ever discover phrases that an engine
# suggests from words WE already use. "master bedroom" does not appear once in
# 2,622 queries, not because nobody types it, but because nothing asked. The
# same blind spot covers "foyer", "utility room", "den" and "larder".
#
# These are the probe seeds for that. They are not claims that anybody searches
# these phrases; they are the question, put to the engine, so the next harvest
# can answer it. Each is a word a household might use for a room this site
# names differently, and the thing worth reading in the result is whether the
# engine suggests MORE around the synonym than around our name for it.
VOCABULARY_PROBES = (
    "master bedroom organization",
    "master bathroom organization",
    "foyer organization ideas",
    "entrance hall organization",
    "utility room organization",
    "larder organization",
    "den organization ideas",
    "bonus room organization",
    "linen closet organization",
    "coat closet organization",
    "back porch organization",
    "basement organization ideas",
    "attic organization ideas",
    "walk in closet organization",
)

STOPWORDS = frozenset("""
a an and are at be best by can do does for from get good have how i ideas in
into is it its my of on or practices should so that the their there these
this tips techniques to too what when where which who why will with you your
""".split())

# Words that describe the format of a query rather than its subject. Left out
# of coverage scoring because nearly every one of our titles carries one and
# the score would flatter itself.
#
# "arrange" and its family joined 2026-10-13 for the opposite reason: not one
# of our titles carries it, so there is no self-flattery risk, but it is the
# same kind of word, a task verb rather than a subject noun. "how to arrange
# towels in guest bathroom" and "how to organize the guest bathroom towels"
# ask for the same thing about the same subject; scoring "arrange" as an
# unmet content word was marking 71 real queries as less covered than they
# are for a wording difference, not a subject difference. Checked against
# the live corpus before landing: every one of those 71 queries keeps the
# exact same best-matching page after this change, only the score moves, so
# this corrects the word-choice penalty without changing which page wins.
FORMAT_WORDS = frozenset(("organize", "organizing", "organization", "organiser",
                          "organizer", "organizers", "organise", "organising",
                          "arrange", "arranging", "arranged", "arrangement",
                          "arrangements", "rearrange", "rearranging",
                          "rearranged", "reorganize", "reorganizing",
                          "reorganized", "ways", "way", "diy", "guide",
                          "tutorial", "must", "haves", "quickly",
                          "original", "deals", "overview", "routine", "setup",
                          "review", "buy", "template", "her", "him", "men",
                          "women", "container", "containers", "essentials",
                          "household", "daily", "inspo", "inspiration",
                          "images", "efficiency", "chef", "modern", "rustic",
                          "simple", "choose", "deep", "hacks", "lots",
                          "categories", "pro", "aesthetically", "newborn",
                          "planning"))

# "deep" and "hacks" joined 2026-11-11, mining Hall Closet's remaining
# partial tier. "how to organize a deep hall closet" and "deep hall closet
# organization ideas" ask the same question as "how to organize a hall
# closet", "deep" naming the closet's own depth, a descriptive qualifier on
# the subject rather than a different one, the same shape "small"/"narrow"
# would be if either were safe to add (checked and declined: "small" is not
# a format word here, since /articles/zone-too-small-for-what-it-holds.html
# is a real page about small spaces specifically, so dropping "small" from
# scoring risks a false match there). "linen closet organization hacks"
# asks the same question as "linen closet organization", "hacks" naming an
# informal tips format, the same role "tips"/"ideas" already play in
# STOPWORDS. Self-flattery checked first, using the same head_words/
# title_words fields the scorer itself reads (not a raw grep across page
# body text, which is what incorrectly sank "systems" below; body text is
# never scored): "deep" appears in 0 of 243 page titles and 6 of 243
# headings, well under the "household" bar (11/243) already cleared;
# "hacks" appears in 0 of 243 titles and 0 of 243 headings. Checked the
# full corpus before adding: "deep" is the sole unmatched word on 6 live
# rows across both corpora (2 Hall Closet, 1 Primary Bathroom, 1 Pantry, 2
# a stray nightstand/drawers row), each already routed to its own correct
# page; "hacks" is the sole unmatched word on 2 live rows per corpus
# (3 unique: Hall Closet's linen closet article and the unrelated walk-in-
# closet article), also each already correctly routed. None can move the
# other way, same reasoning as every prior FORMAT_WORDS addition.

# "aesthetically" joined 2026-11-11, mining Home Office's remaining partial
# tier. "how to organize bookshelf aesthetically" asks for the same thing as
# "how to organize bookshelf", "aesthetically" naming the look wanted, the
# same style-qualifier role "quickly"/"original"/"simple" already play, not a
# different subject. Checked the page itself before touching the scorer: the
# zone's own diagnosis already names shelving by color or category (not by
# use) as a cause of not finding a book, so a genuine content note was added
# to the zone's own `variants` answering the "by color"/"by genre" framing
# directly rather than pretending the page agrees with it; those two words
# stay real content words, unmatched, since the honest answer argues against
# the literal query rather than for it, and FORMAT_WORDS only drops words
# that do not change the subject. Self-flattery checked first: "aesthetically"
# appears in 0 of 243 page titles or headings, well under the "household" bar.
# Checked the full corpus before adding: it is the sole unmatched word on
# exactly 1 live row per harvest (the same query, duplicated once as
# "arrange" in the global harvest), both already routed to the correct page;
# nothing else in either corpus carries the word, so this cannot change any
# other row's match.

# "lots" joined 2026-11-11, mining Garage's remaining partial tier. "how to
# organize a garage with lots of tools" asks the same question as "how to
# organize a garage with tools", "lots" naming a quantity rather than a
# different subject, the same role "too much"/"many" would play if either
# were already in scope. Self-flattery checked first: 0 of 244 page titles
# or headings carry "lots" at all, well under the "household" bar (11/243)
# already cleared. "much" and "items" were checked for the same slot and
# declined: both appear in well over 100 of 244 page headings (naturally,
# in genuine content like "too much stuff" and "sentimental items", not
# gaming), and a direct before/after rescore of the full corpus with each
# added to FORMAT_WORDS changed which page several rows credit as their
# best_page (e.g. "how to organize cleaning items" moved from the Garage's
# own Automotive Care Zone to /disclaimer.html), the exact silent
# misattribution class the 2026-11-05 best_page/heading-surface fix above
# exists to prevent. "lots" produces zero best_page changes across either
# corpus when tested the same way, only status moves. Checked the full
# corpus before adding: "lots" is the sole unmatched word on 3 live rows
# (1 Garage, 1 Guest Bathroom vanity-storage, 1 global bedroom-closet row),
# each already routed to its own correct page. None can move the other way.

# "categories" and "pro" joined 2026-11-11, mining Hall Closet's remaining
# partial tier. "linen closet organization categories" asks the same
# question as "linen closet organization", "categories" naming the
# structure of the answer wanted (a breakdown by type), the same role
# "overview" already plays; "how to organize closet quickly pro tips" and
# "simple decluttering pro tips" ask the same question as their plain
# "quickly"/"simple" forms, "pro" an informal-expertise qualifier on the
# tips wanted, the same shape "hacks" already covers. Self-flattery checked
# first, using head_words/title_words: both 0 of 243 page titles and 0 of
# 243 headings, under every prior bar cleared. Checked the full corpus
# before adding: because neither word appears in any page's own title or
# heading words, removing either from scoring cannot change any row's
# best_page (a page can only be credited for words it already carries), so
# this is a status-only improvement everywhere it fires; "categories" is
# the sole unmatched word on 1 live row (Hall Closet linen closet),
# "pro" on 2 (same Hall Closet row plus a Decluttering vs Organizing row),
# with a third row ("explore decluttering pro guide") left honestly a gap
# since "explore" stays an unmatched content word there too.

# "images", "efficiency" and "chef" joined 2026-11-11, mining Kitchen's
# partial tier. "kitchen organisation ideas images" and "linen closet
# organization images" ask the same question with "images" naming the
# visual format wanted, the same role "inspo"/"guide" already play, not a
# different subject. "how to organize a kitchen for efficiency" and "...like
# a chef" are a goal and a skill-level qualifier on the same task, the same
# shape "quickly"/"original" already cover. Self-flattery checked first: 0
# of 244 page titles or headings carry any of the three. Checked the full
# corpus before adding: "images" is the sole unmatched word on 5 of its 6
# live rows (the 6th, "images of primary bedrooms", keeps a second genuine
# unmatched word, "bedrooms", a separate plural-stemming gap not touched
# here, and only moves closer); "efficiency" is the sole unmatched word on
# both its rows (the same US query duplicated in the global harvest);
# "chef" is the sole unmatched word on its one row. None can move the other
# way.
#
# "modern" and "rustic" joined the same cycle. "declutter modern kitchen"
# and "declutter rustic kitchen ideas" ask the same question about any
# kitchen; the decor style does not change which page answers it, the same
# not-a-different-subject reasoning "original" already uses for a style
# qualifier. Self-flattery checked first: 0 of 244 pages carry either word
# in a title or heading. Checked the full corpus before adding: "modern" is
# the sole unmatched word on 4 of its 12 live rows, pairs only with the
# separate already-real word "design" on 6 more (unaffected, since "design"
# stays unmatched), and is paired with "decluttering" on the remaining one
# (also unaffected); "rustic" is the sole unmatched word on both its rows.
# None can move the other way.
#
# "simple" joined the same cycle. "kitchen organization ideas simple" and
# "simple closet organization ideas" ask the same question with "simple"
# naming the style wanted (easy, uncomplicated), the same shape "quickly"
# already covers. Self-flattery checked first: 2 of 244 page headings and 1
# title carry the word, both well under the bar "household" (11 of 243)
# already cleared. Checked the full corpus before adding: of 18 live rows,
# 9 keep "simple" as the sole unmatched word and move partial to covered;
# the rest keep a second genuine unmatched word each ("beginners", "pro",
# "decorating", "pictures", "walkway", "design") and only move closer, or
# (the 2 already-covered rows) are unaffected since they have no unmatched
# words to drop. None can move the other way.

# "inspo"/"inspiration" joined 2026-11-11, mining Home Office and Guest
# Bathroom's remaining partial rows: "desk organisation inspo" and "desk
# organisation inspiration" ask for the same thing about the same subject,
# naming the content format wanted (visual inspiration), the same role
# "ideas"/"guide" already play, not a different subject. Self-flattery
# checked first, same bar every prior addition cleared: 0 of 244 pages'
# titles or headings carry either word. Checked the full corpus before
# adding: 9 live rows across both corpora (6 "inspo", 3 "inspiration") have
# one of these as their only unmatched word, or paired only with "design"
# (a separate already-real word, unaffected); each already routes to its
# own correct room or zone page (Home Office desk, Guest Bathroom vanity
# and linen zones, Family Room, Attic, Hall Closet, Primary/Kids Bedroom).
# All 9 can only improve (partial toward covered); none can move the other
# way, same reasoning as every prior FORMAT_WORDS addition.

# "reorganize"/"reorganizing"/"reorganized" joined 2026-11-11, mining
# Garage's remaining partial tier. "how to reorganize storage" and "buy
# items in bulk to reorganize storage" ask the same question as "how to
# organize storage", the same not-a-different-subject shape "rearrange"
# already covers two lines above; "reorganize" is already folded from its
# British spelling "reorganise" by `_SPELLING`, so adding the American form
# here covers both. Checked the full corpus before adding: "reorganize" is
# the sole unmatched word on both of its live rows (both US, 0 global), each
# already routed to its own correct page (the garage bulk-and-overhead zone,
# and the generic more-storage-wont-fix-clutter article); self-flattery is
# not a risk here since 10 pages already use some form of the word in body
# text and this only drops a word from scoring, it cannot create a false
# match on a page that never otherwise matches.
#
# "daily" joined the same cycle. "daily equipment cleaning checklist" asks
# the same thing as "equipment cleaning checklist", a frequency qualifier on
# the task, not a different subject, the same shape "quickly"/"routine"
# already cover. Self-flattery checked first: "daily" appears in 7 of 243
# headings, under the bar "household" (11/243) already cleared. Checked the
# full corpus before adding: 3 live rows (all US) contain "daily"; one
# ("daily equipment cleaning checklist") has it as the sole unmatched word
# and moves partial to covered, the other two still carry a second genuine
# unmatched word each ("gardening", "starter") and only move closer, never
# the other way, same reasoning as every prior FORMAT_WORDS addition.

# "household" joined 2026-11-11, mining Hall Closet's remaining partial tier.
# "how to organize household cleaning supplies" asks the same question as
# "how to organize cleaning supplies", the same not-a-different-subject
# shape "essentials"/"men"/"women" already cover: naming the supplies as
# household ones (rather than industrial or commercial) does not change
# which page answers it. Not a self-flattery risk by the usual bar (11 of
# 243 headings already carry the word, from zone names like "Paper and
# Household Backstock"), and this only drops a word from scoring, so it
# cannot create a false match on a page that never otherwise matches.
# Checked the full corpus before adding: "household" is the sole unmatched
# word on exactly 1 live row per harvest (the same query, "how to organize
# household cleaning supplies"), already routed to the correct page
# (Hall Closet's Cleaning Supply Zone) at 2 of 3 words; moves it to
# covered, 0 regressions anywhere else in either corpus.

# "her", "him", "men" and "women" joined 2026-11-11, mining Guest Bedroom's
# partial tier. "nightstand organizer for her/men/women" and "how to
# organize dresser men" ask the same organizing question as "nightstand
# organizer" and "how to organize dresser"; naming a demographic does not
# change the answer on a site with no gendered storage advice anywhere in
# its own content, the same not-a-different-subject reasoning "original"/
# "quickly" already use. Self-flattery checked first: 0 of 243 page titles
# or headings carry any of the four words. Checked the full corpus before
# adding: "her" is the sole unmatched word on exactly 1 live row, "him" on
# 0, "men" on 7 (Guest Bedroom, Family Room, Hall Closet/Linen Closet
# article, all genuine organizing queries), "women" on 2; every one is
# already partial and can only move toward covered.
#
# "container"/"containers" joined the same cycle, mining the same tier.
# "storage containers for linens" asks the same thing as "storage for
# linens"; "containers" names a storage product category the query's own
# page already answers in generic terms (bins, totes, bins), not a
# different subject, the same shopping-frame role "buy" already plays
# for a product noun rather than a format noun. Checked the full corpus
# first: 8 headings and 0 titles already use "container"/"containers"
# (above the 0-heading bar some prior additions cleared, but this change
# only drops a word from scoring, it cannot create a false match to a page
# that never otherwise matches); "containers" is the sole unmatched word on
# exactly 4 live rows (Guest Bedroom, Laundry Room, Pantry, Primary
# Bathroom), all genuine organizing queries already routed to their own
# room's correct page, so this can only move partial toward covered, never
# the other way.

# "buy" and "template" joined 2026-11-11, mining Garage's remaining partial
# tier. "buy garden tool storage" asks the same thing as "garden tool
# storage", "buy" marking a shopping frame on an already-covered subject,
# the same role "deals" already plays. "cleaning equipment checklist
# template" asks the same thing as "cleaning equipment checklist", "template"
# naming the kind of document wanted, the same role "guide"/"overview"
# already play, not a different subject. Checked the full corpus before
# adding, not just the room's own tier: "buy" is the sole or partial
# unmatched word on exactly 2 live rows, both Garage, neither elsewhere;
# "template" is the sole unmatched word on exactly 1 live row (4 other
# "template" rows are an off-topic cribbage-tournament cluster that stays
# gap on other unmatched words regardless), so this cannot suppress a
# genuine match anywhere in either corpus.

# "review" joined 2026-11-11, mining Hall Closet's remaining partial tier:
# "how to organize closet review" asks for the same thing as "how to
# organize closet", "review" naming the kind of write-up wanted (an
# opinion piece), the same role "guide"/"tutorial"/"overview" already play,
# not a different storage subject. Self-flattery checked first, same bar
# every prior addition used: "review" appears in 0 of 244 page titles and 0
# headings, well under the bar that blocked "systems". Checked the full
# corpus before adding: it is the sole unmatched word on exactly 1 live row
# (no global-harvest match), which can only move toward covered, never the
# other way, same reasoning as every prior FORMAT_WORDS addition.

# "essentials" joined 2026-11-11, mining Garage's remaining partial tier.
# "car organisation essentials" asks for the same thing as "car
# organisation", "essentials" naming the necessary-items framing, the same
# role "must"/"haves" already play, not a different storage subject.
# Self-flattery checked first, same bar every prior addition cleared:
# "essentials" appears in 0 of 243 page titles or headings. Checked the full
# corpus before adding: it is the sole unmatched word on exactly 1 live row
# (the Garage query above). Checked, not assumed, what happens to the one
# other row carrying it ("updated decluttering essentials tips", "updated"
# also unmatched): dropping "essentials" from its unmatched list moves it
# gap to partial, a genuine coverage gain, not the no-op the word's
# Garage role alone would suggest. Nothing moves the other way.

# "overview", "routine" and "setup" joined 2026-11-11, mining Garage's
# remaining partial tier. "organize car maintenance overview" and "organize
# car maintenance routine" ask for the same thing as "organize car
# maintenance", the query only naming the kind of write-up it wants (a
# summary, a recurring habit description), not a different storage subject,
# the same role "guide"/"tutorial" already play. "setup declutter garage"
# asks for the same thing as "declutter garage", "setup" marking an action
# synonym for "organize" itself, the same shape "arrange" already covers.
# Self-flattery checked first, same bar every prior addition cleared:
# "overview" appears in 0 of 243 page titles or headings; "routine" appears
# in 0 titles and 1 heading (an unrelated FAQ, no room or zone); "setup"
# appears in 0 titles and 2 headings (also-called style zone subheadings,
# not a room/zone name), all well under the bar "systems" failed. Checked
# the full corpus before adding: "overview" and "routine" are each the sole
# unmatched word on exactly one live row (the two Garage queries named
# above); "setup" is the sole unmatched word on 4 live rows (the two above
# plus "dining room setup ideas" and "how to setup charging station"), all
# genuine organize/declutter queries already routed to their correct page.
# All can only improve (partial toward covered); none can move the other
# way, since dropping a required word from a match can only raise a score.

# "original" and "deals" joined 2026-11-11, mining Mudroom's remaining
# partial tier. "original coat hooks with storage" and "coat hooks with
# storage" ask for the same thing about the same subject; "original" marks a
# style/authenticity qualifier, the same shape "ways"/"diy" already cover,
# not a different subject. "shop deals on mudroom organization ideas" and
# "mudroom organization ideas" are the same question wrapped in a shopping
# frame, the same shape "guide"/"tutorial" already cover. Self-flattery
# checked first, same bar every prior FORMAT_WORDS addition used: 0 of this
# site's page titles and at most 1 of its headings carry either word.
# Checked the full corpus before adding: "original" is the sole unmatched
# word on exactly 1 on-topic row (2 more exist but fail ON_TOPIC entirely,
# so this change cannot touch them); "deals" is the sole unmatched word on
# exactly 1 row (duplicated across the US and global harvest, one real
# query). Both can only move gap/partial toward covered, never the other
# way, same reasoning as every prior FORMAT_WORDS addition.

# "ways" joined 2026-11-05, same shape as "arrange": "ways to organize a
# nightstand" and "how to organize a nightstand" ask for the same thing about
# the same subject, so scoring "ways" as an unmet content word penalizes a
# wording choice, not a real subject gap. Checked for self-flattery first: 0
# of our titles and 6 of 243 pages' headings carry it, well under the bar
# that blocked "systems". 25 live queries (22 US, 3 global), all partial but
# one already covered, move toward covered; none can move the other way,
# since dropping a required word from a match can only raise a score.

# "diy" joined 2026-11-06, mining Garage: 6 of its own partial rows (diy
# garden tool storage, diy power tool storage, diy tool wall organizer,
# garden tool organizer diy, power tool organizer diy, tool wall organizer
# diy) failed on this one word alone. "diy garden tool storage" and "garden
# tool storage" ask for the same thing about the same subject, same
# task-verb-family shape as "ways": it marks a how-to-yourself framing, not
# a different storage subject. Checked for self-flattery first: 0 of 243
# pages' titles and only 1 of 243 headings (a generic article unrelated to
# any single room or zone) carry the literal word "diy", well under the bar
# "ways" cleared. Checked the full corpus before adding, not just Garage: 63
# live rows (across both the US and global harvest) have "diy" as their only
# unmatched word. A deeper check found this was not just a score-politeness
# fix: several of those rows (e.g. "garage organization ideas diy", "laundry
# room organization ideas diy", "how to organize a craft room diy") were
# being mis-routed to an unrelated generic article that happens to say
# "diy" once in a heading, instead of to their own room's real guide or zone
# page, because that one incidental word was winning the tie. Removing it
# from content_words fixes the routing to the correct page for 17 rows (11
# US, 6 global) as a side effect, not just the score. Verified directly: 0
# regressions across the full corpus (no row's status or coverage score
# ever decreases), 63 rows improve (44 US, 19 global), all from partial/gap
# toward covered; none can move the other way, since dropping a required
# word from a match can only raise a score or fix a wrong tie-break toward
# the honestly better page.

# "guide" and "tutorial" joined 2026-11-06, mining the Hall Closet handoff:
# "how to organize closet tutorial guide" and "how to organize a closet" ask
# for the same thing about the same subject, the query only naming the
# content format it wants (a guide, a tutorial), which is the shape
# FORMAT_WORDS already exists for, not a different storage subject.
# Self-flattery checked first, same bar "ways"/"diy" required: "tutorial"
# appears in 0 of 243 pages' titles or headings; "guide" appears in 1 title
# (shop.html, a product name, no room) and 1 heading (invest.html, unrelated
# to any room or zone), so excluding either word from content_words cannot
# inflate a room or zone page's score. Checked the full corpus before
# adding: only 3 live rows (all US; 0 global) have "guide" and/or "tutorial"
# as their only unmatched word(s) ("how to organize closet tutorial guide",
# "organize car maintenance guide", "room by room declutter guide"); none of
# the three sit in the cheap/budget/DIY cluster GOALS.md cites by word
# boundary, so that citation does not move. All three can only improve
# (gap/partial toward covered or partial), none can move the other way,
# same reasoning as every prior FORMAT_WORDS addition.

# "way" (singular) joined 2026-11-09, mining Kitchen's remaining partial
# rows: "best way to organize kitchen cooking utensils" and "how to organize
# kitchen cooking utensils" ask for the same thing about the same subject;
# the plural "ways" already carried this exact reasoning on 2026-11-05 and
# the singular form was simply never added alongside it. Self-flattery
# checked first, same bar as every prior addition: 0 of 114 zone titles and
# 0 of 243 page titles carry the literal word "way"; it appears in 4 of 243
# pages' <h3> "watch for" questions only (idiomatic uses like "out of the
# way" and "the rest of the way", not a subject noun), well under the bar
# "systems" failed. Checked the full corpus before adding: 13 live rows (7
# US, 6 global) have "way" as their only unmatched word, all genuine
# "best way to organize X" queries already routed to the correct page. All
# 13 can only improve (partial toward covered); none can move the other
# way, same reasoning as every prior FORMAT_WORDS addition.

# "quickly" joined 2026-11-10, mining Garage: "how to organize a garage
# sale quickly" asks for the same thing as "how to organize a garage sale",
# a speed qualifier on the task, not a different subject, same shape as
# every entry above. It was also causing a real wrong-tie-break, the same
# "diy" shape: with "quickly" scored as a content word, the query tied at
# 2 of 3 words between the Garage room page's own "Garage sale" heading
# (matching "garage"+"sale", missing "quickly") and the article's unrelated
# "How do I declutter a garage quickly?" heading (matching "garage"+
# "quickly", missing "sale"), and the tie-break happened to prefer the
# article, leaving the room's own on-topic "Garage sale" section unused by
# this query entirely. Self-flattery checked first, same bar every prior
# addition cleared: "quickly" appears in 0 of 243 page titles and only 2 of
# 243 headings (the garage declutter FAQ above, and an unrelated "why does
# my house get messy again so quickly" FAQ), well under the bar "systems"
# failed. Checked the full corpus before adding: of the 7 live rows (both
# corpora) containing "quickly" at all, 2 already read `covered`, 2 move
# from `partial` to `covered` on the garage-sale wording (now routed
# honestly to the room's own "Garage sale" section instead of the
# unrelated article), and 2 more ("how to organize closet quickly",
# "how to declutter bedroom quickly") move from `partial` to `covered` on
# their own already-correct page once the lone remaining word matches.
# None can move the other way, same reasoning as every prior FORMAT_WORDS
# addition.

# "must" and "haves" joined 2026-11-09, mining Garage's own gap row: "car
# organisation must haves" ("organisation" normalises to "organization"
# upstream in words() and was already a FORMAT_WORD, so that part of the
# query was never the problem). "must haves" names the kind of list a reader
# wants (its essential items), the same role "ideas" and "tips" already play
# in STOPWORDS, not a storage subject of its own; "have" is already a
# STOPWORD but its plural noun form "haves" (as in "must-haves") was never
# added alongside it, and "must" was never added at all. Self-flattery
# checked first, same bar every prior addition cleared: "must" appears in 0
# of 243 page titles or headings; "haves" (the noun, distinct from the verb
# "have", which is the literal STOPWORD and appears in 43 headings in its
# own right) appears in 0 of 243 titles or headings. Neither word can ever
# win a page a point it does not already have. Checked the full corpus
# before adding: only 2 live rows (1 US, 1 global) have "must" and/or
# "haves" as their only unmatched word(s) ("must have baking supplies",
# "car organisation must haves"), both already routed to the correct page
# and both moving toward covered; a third row ("detergents and cleaners
# must be stored") has other unmatched words regardless and does not move.
# None can move the other way, same reasoning as every prior FORMAT_WORDS
# addition.

# "newborn" and "planning" joined 2026-11-11, mining Garage's and Nursery's
# remaining partial tiers. "newborn baby nursery organizer" and "how to
# organize dresser for newborn" ask the same organizing question as
# "baby nursery organizer"/"how to organize dresser", "newborn" naming the
# occupant's age rather than a different subject, the same
# not-a-different-subject role "her"/"him"/"men"/"women" already play for a
# demographic qualifier. "planning a gallery wall" and "nursery planning
# ideas" ask the same thing as "arranging a gallery wall"/"nursery ideas",
# "planning" a task-verb synonym for the layout work "arrange" already
# covers, not a different activity (checked against "plan", singular,
# which was tried for the same tier and declined: a full before/after
# corpus rescore found 2 literal architectural-blueprint queries, "railings
# in floor plan" and "stove on floor plan", flip their best_page onto the
# Entryway's door-mat zone on the word "floor" alone once "plan" stopped
# distinguishing them, the exact silent misattribution class the
# 2026-11-05 best_page/heading-surface fix exists to prevent; "planning",
# the gerund, produces zero such moves against the same two queries or
# anywhere else in either corpus, a different word with different
# collision behaviour, not the same fix tried twice). Declined in the same
# pass: "activities" ("activities to do in a nursery", "ideas for nursery
# activities") is not a format word here, because it asks what to DO in the
# room, a different question from how to organize it, and the deck page it
# would route to answers neither; marking it covered would be the
# dishonest-labelling shape CLAUDE.md section 8 forbids, so it stays
# partial even though it is technically safe (zero misattribution) by the
# mechanical test alone. "messy" was also tried and declined hard: every
# style-qualifier shape it might fit ("messy room", "why is my X always
# messy") is itself a real distinguishing content word on several pages
# (the complaint-cluster article, the before/after-photo rows), and a full
# corpus rescore found 44 best_page changes, by far the largest
# misattribution risk any FORMAT_WORDS candidate has produced in this
# file's history. Self-flattery checked first for the two words that
# shipped: "newborn" is 0 of 243 page titles or headings; "planning" is 1
# of 243 (same low bar every prior addition cleared). Checked the full
# corpus before adding: "newborn" is the sole unmatched word on 2 live rows
# (1 US, 1 global), "planning" on 6 (4 US: a gallery wall, a workshop, a
# nursery-setting query, a help-planning-a-garden query that keeps a second
# unmatched word and stays honestly gap; 2 global: guest bedroom, nursery),
# zero best_page changes across either corpus for either word, confirmed by
# a direct before/after score_rows() diff, not assumed from the self-
# flattery count alone.


def room_names():
    with open(CONTENT, encoding="utf-8") as fh:
        data = json.load(fh)
    return [r["room"] for r in data["rooms"]]


def room_synonyms():
    """Household words for a room, keyed back to the room's own real name.

    Reads ops/room-also-called.json, the same measured file
    gate_also_called_is_heading already holds current. Missing or malformed
    is read as "no synonyms", never an error: this file must still harvest
    and score without it.
    """
    try:
        with open(ROOM_ALSO_CALLED, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    out = {}
    for room, entry in data.get("rooms", {}).items():
        names = entry.get("names") if isinstance(entry, dict) else None
        if names:
            out[room] = [str(n).lower() for n in names]
    return out


def room_slug(room):
    return room.lower().replace(" ", "-")


def guide_article_rooms():
    """Reverse of build_zone_pages.ROOM_GUIDES: {article url: owning room}.

    Found 2026-11-05: every room's own guide article genuinely belongs to
    one room (ROOM_GUIDES is a hand-curated 1:1 list), but room_of() gave
    it no room at all, same as every other article. That let a DIFFERENT
    room's guide out-score the query's own room on a query that room's own
    zone page already answers, purely because the other guide's title and
    headings happen to combine two unrelated words the query needs (see
    _prefer_in_room_zone). Scoped to just the 20 curated guides, not every
    article: most articles genuinely answer no single room, and should
    keep carrying no room signal.
    """
    import build_zone_pages as bzp
    out = {}
    for room, guides in bzp.ROOM_GUIDES.items():
        name = guides[0][0].rsplit("/", 1)[-1]
        out["/articles/" + name] = room
    return out


def room_of(url, rooms, guide_rooms=None):
    """Which real room a page belongs to, by its own URL slug, longest room
    name first so "Guest Bathroom" claims its pages before "Bathroom" would
    (no room here is literally named that, but the rule is the same one
    attribute_room already uses and for the same reason).

    Returns "" for a page that is not a room/deck/zone page, nor one of the
    20 curated guide articles (the homepage, articles with no single-room
    answer, the shop), which is the common case and correctly carries no
    room signal.
    """
    if guide_rooms and url in guide_rooms:
        return guide_rooms[url]
    base = url.rsplit("/", 1)[-1]
    if base.endswith(".html"):
        base = base[:-5]
    for room in sorted(rooms, key=len, reverse=True):
        slug = room_slug(room)
        if base == slug or base.startswith(slug + "-"):
            return room
    return ""


def household_room_signal(query, rooms, synonyms):
    """Which room a query is ABOUT, including a household synonym ("master
    bedroom", "foyer") the site itself never uses as a room name.

    Found 2026-10-10: attribute_room() alone only catches a query that uses
    our own room name literally. "master bedroom closet organization ideas"
    contains no room name of ours, so it returned "", best_page() and
    best_by() had no room signal to apply, and title/heading word-overlap
    tied between Guest Bedroom's and Primary Bedroom's near-identical zone
    pages ("...the guest closet" vs "...the primary closet"). The existing
    tie-break, alphabetically-earliest URL, then silently favoured Guest on
    every such query, which is how the identical "master bathroom vanity"
    shape first surfaced as A25 and was fixed only for that one zone. This
    closes the whole class: any query naming a room by its household word
    now carries the same room signal a literal room name would.

    Found 2026-11-07, PM check-in: a plain substring check (`name in low`)
    let Family Room's 3-letter synonym "den" match inside any word that
    merely contains that letter run, never mind a word boundary. Tracing why
    "nightstands with hidden storage" (a Primary Bedroom query) scored a
    Family Room room_signal found it: "den" is a substring of "hidden",
    which then won a tie-break against the actual Primary Bedroom nightstand
    pages that Family Room's zone page had no real business winning. Counted
    directly against the live corpus before fixing: 74 rows, all "den"
    inside "garden"/"gardening"/"wooden"/"dental"/etc, none of them actually
    about Family Room. Now requires a real word boundary, so a multi-word
    synonym ("master bedroom") still matches inside a longer phrase
    ("...master bedroom closet...") but a bare letter run inside an
    unrelated word does not.

    A first version required `\bname\b` with no tolerance at all and broke
    three real, previously-correct matches found by diffing every row of
    both corpora against the old substring behaviour before shipping:
    "backyards" (plural of "backyard"), "larders own" (plural of "larder")
    and "types of master bedrooms" (plural of "master bedroom"), none of
    which a bare trailing \b allows since the 's' it would need to swallow
    is itself a word character with no boundary before it. A single
    optional trailing 's' restores all three without reopening the
    original bug: the boundary that rejects "den" inside "garden" is the
    one BEFORE "den", which an optional suffix after the match does not
    touch.
    """
    exact = attribute_room(query, rooms)
    if exact:
        return exact
    low = query.lower()
    best_room, best_len = "", 0
    for room, names in synonyms.items():
        for name in names:
            if (len(name) > best_len
                    and re.search(r"\b" + re.escape(name) + r"s?\b", low)):
                best_room, best_len = room, len(name)
    return best_room


def zone_terms():
    """The hand-written retailer search terms, reused as seeds.

    They were written for product search links, not for SEO, which is exactly
    what makes them useful here: they are the plain-English noun a person would
    reach for ("drop zone", "blanket storage") rather than the Manual internal
    zone name, so they seed the suggestion space from the human side.
    """
    if not os.path.exists(ZONE_TERMS):
        return []
    with open(ZONE_TERMS, encoding="utf-8") as fh:
        data = json.load(fh)
    seen, out = set(), []
    for term in data.values():
        t = str(term).strip().lower()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def build_seeds():
    seeds = []
    for room in room_names():
        low = room.lower()
        for tpl in ROOM_TEMPLATES:
            seeds.append(tpl.format(room=low))
    for term in zone_terms():
        seeds.append("how to organize " + term)
    seeds.extend(VOCABULARY_PROBES)
    # Deterministic order so two runs are comparable line by line.
    out, seen = [], set()
    for s in seeds:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _fetch(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def _parse_opensearch(body):
    """Both endpoints answer in the OpenSearch suggestions shape."""
    try:
        payload = json.loads(body)
    except ValueError:
        return None, "unparseable response"
    if not isinstance(payload, list) or len(payload) < 2:
        return None, "unexpected response shape"
    if not isinstance(payload[1], list):
        return None, "unexpected response shape"
    return [s for s in payload[1] if isinstance(s, str)], None


def google_suggest(seed):
    url = ("https://suggestqueries.google.com/complete/search"
           "?client=chrome&hl=en&gl=us&q=" + urllib.parse.quote(seed))
    try:
        status, body = _fetch(url)
    except Exception as exc:                      # reported, never hidden
        return [], "%s: %s" % (type(exc).__name__, exc)
    if status != 200:
        return [], "http %s" % status
    out, err = _parse_opensearch(body)
    return (out or []), err


def bing_suggest(seed):
    url = "https://api.bing.com/osjson.aspx?query=" + urllib.parse.quote(seed)
    try:
        status, body = _fetch(url)
    except Exception as exc:                      # reported, never hidden
        return [], "%s: %s" % (type(exc).__name__, exc)
    if status != 200:
        return [], "http %s" % status
    out, err = _parse_opensearch(body)
    return (out or []), err


SOURCES = {"google": google_suggest, "bing": bing_suggest}


# British and Commonwealth spellings, folded to the American forms the site
# is written in. Search engines treat "organise" and "organize" as one word;
# this scorer did not, and since "organization" is a FORMAT_WORD (dropped)
# while "organisation" was not, every query typed in the UK, Australia or
# India carried one extra word no page here could ever match. Found
# 2026-10-23 when "larder organisation and layout" scored gap against a
# pantry page headed "Also called the larder" (ops/keyword_demand_global.py).
_SPELLING = (
    (re.compile(r"^organis"), "organiz"),
    (re.compile(r"^reorganis"), "reorganiz"),
    (re.compile(r"^colour"), "color"),
    (re.compile(r"^favourite"), "favorite"),
    (re.compile(r"^centre(s?)$"), r"center\1"),
    (re.compile(r"^mould"), "mold"),
)


def _fold(word):
    for pat, rep in _SPELLING:
        word = pat.sub(rep, word)
    return word


def words(text):
    return [_fold(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w]


def _morphology_variants(word):
    """A small set of plausible base forms of `word`, for tie-break near-miss
    matching only. Never used in the primary score, so it cannot reclassify
    any query's gap/partial/covered status, only which tied page is credited.

    Deliberately narrow: handles the two real shapes this repository has
    found so far, a dropped plural ("drawers" vs "drawer", BACKLOG-2026-09-07
    section 75) and a gerund ("grilling" vs "grill", section 76), not general
    stemming. A third tied page sharing no exact word at all is unaffected.
    """
    variants = {word}
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        variants.add(word[:-1])                           # drawers -> drawer
    if len(word) > 5 and word.endswith("ing"):
        base = word[:-3]
        variants.add(base)                                # grilling -> grill
        if len(base) >= 2 and base[-1] == base[-2] and base[-1] not in "wxy":
            variants.add(base[:-1])                        # running -> run
        variants.add(base + "e")                           # baking -> bake
    return variants


def _near_miss_count(page, cw, field="words"):
    """How many of `cw` are NOT an exact hit on `page[field]` but have a
    morphology variant that is. A query word already an exact hit is not a
    near miss. `field` matches whichever surface the tie is on (best_page's
    "words" or best_by's own field, e.g. "head_words")."""
    hay = page[field]
    count = 0
    for w in cw:
        if w in hay:
            continue
        if any(v in hay for v in _morphology_variants(w)):
            count += 1
    return count


# Found 2026-11-11, mining Hall Closet: "how to organize closet 2024" and
# "how to organize closet 2025" each failed on their bare year alone, and
# the same shape repeats 32 times across at least 8 rooms (dining room,
# family room, guest bedroom, living room, primary bedroom among them),
# none of them already covered. A year suffix on a decorating/organizing
# query ("ideas for 2025") marks a freshness qualifier, the same role
# "ways"/"guide"/"overview" already play, not a different subject; unlike
# those, a literal year is not a fixed vocabulary word (2027 is coming), so
# a frozenset entry would need manual upkeep every January. A regex check
# is the same one-line fix without that maintenance cost. Checked the full
# corpus before adding: every row this matches is gap/partial already
# (0 covered rows contain a bare 20xx year), so this can only improve a
# score, never suppress a genuine match.
_YEAR_WORD = re.compile(r"^20\d\d$")


def content_words(query):
    """The words a coverage check should care about."""
    return [w for w in words(query)
            if w not in STOPWORDS and w not in FORMAT_WORDS and len(w) > 2
            and not _YEAR_WORD.fullmatch(w)]


# A zone-page template heading verified byte-identical across all 114 zone
# pages (counted live, 2026-11-05: `grep -c 'id="shine-detail"' site/zones/*`
# is 114/114, always the same wording). A heading that reads the same on
# every zone cannot discriminate between zones, so its words have never once
# been the honest reason any zone matched a query; counting them only adds
# noise. Found live: "Cleaning it properly, surface by surface" (every
# zone's Shine detail section) contributed the word "cleaning" to literally
# every zone's head_words. Adding "office supplies" to Home Office's Supply
# Cabinet zone (content.json-backed, a genuine fix) combined with that free
# "cleaning" and the zone's own title word "cabinet" to silently flip
# "cabinet to organize cleaning supplies" from its correct `partial` (this
# same cycle re-confirmed it as already diagnosed and deliberately left
# alone, because "cabinet" alone names seven other zones) to a false 1.0
# "covered" claim on an unrelated zone. Scoped to only this one proven
# phrase rather than every other heading that also happens to repeat
# verbatim (several do: "Related reading", "Common items here" and others),
# because only this one has been shown to cause a real collision; widening
# the exclusion further is speculative until a second instance is found.
# Also not touching the six 6S pass-name headings (Sort/Straighten/Shine/
# Safety/Standardize/Sustain), identical across every zone for the same
# reason, because they are core method vocabulary a query might genuinely
# search on and removing them is a larger, untested change than this fix
# needs. An earlier attempt this same cycle to drop every page's
# promotional cross-sell "band" heading wholesale was tried and reverted,
# because those headings vary per room and often carry real zone-naming
# signal (a room article's own zone list), unlike this one.
BOILERPLATE_HEADINGS = {
    "cleaning it properly, surface by surface",
}


def _band_and_body_text(body):
    """Split a page's <body> into (band heading text, everything else).

    A promotional "band" (`<section class="band">`, see `offer()`/
    `room_offer()` in build_zone_pages.py) is the one place on the site
    whose <h2> is a sales pitch, not a description of this page's own
    content. Most bands are self-referential (a zone's band says "Carry
    The Under-Sink Cabinet into the room"; Pantry's room-pack band names
    only Pantry's own zones), but a room with no room-specific pack (e.g.
    Hall Closet) falls back to a hand-authored Whole House Pack band that
    can legitimately name OTHER rooms' zones (linen storage shows up in a
    bathroom too). Both kinds are read here; `page_inventory` below is the
    one that decides, per word, whether a band word naming another room
    is allowed to count.
    """
    band_sections = re.findall(r'(?is)<section\s+class="band".*?</section>',
                               body)
    rest = body
    for b in band_sections:
        rest = rest.replace(b, " ", 1)
    return " ".join(band_sections), rest


def _page_headings(text):
    out = []
    for h in re.findall(r"(?is)<h[1-3][^>]*>(.*?)</h[1-3]>", text):
        # A heading that is entirely one hyperlink to another page is that
        # other page's own title, repeated here as a directory pointer,
        # not anything this page is itself about, the same leak shape the
        # band filter already guards against for a promotional section.
        # Found 2026-11-11, chasing the "organized bathroom cupboard"
        # misroute (see page_inventory): `/articles/index.html` mechanically
        # repeats every one of its 56 linked articles' own titles as its
        # own <h2>, so it ties or beats the real destination page on
        # hundreds of unrelated queries, crediting a directory listing
        # instead of the specific page that actually answers each one.
        # Checked site-wide before adding (CLAUDE.md 5d), not assumed
        # narrow: of 244 published pages, exactly 3 ever have a heading
        # built this way (`/articles/index.html`, `/resources.html`,
        # `/how-to-clean-anything.html`, all directory/index pages by
        # design); every zone, room, deck and article page's own headings
        # are real prose, not a link, so this cannot drop a legitimate
        # heading anywhere else on the site. A general structural rule
        # (any heading shaped like this), not a per-URL special case, so
        # a future hub page built the same way is covered automatically.
        if re.fullmatch(r'(?is)\s*<a\s+href="[^"]*"[^>]*>.*?</a>\s*', h):
            continue
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()
        if t and t.lower() not in BOILERPLATE_HEADINGS:
            out.append(t)
    return out


def _room_identifying_words(raw_pages):
    """Words that name one room (or two, e.g. "bathroom") on the strength
    of the room's own zone-page titles, not a single coincidental hit.

    Found 2026-11-11, fixing the Hall Closet "organized bathroom cupboard"
    misroute (see page_inventory). A first attempt required only 2
    occurrences, and "cabinets" qualified on that bar (Kitchen's own "Upper
    Cabinets" and "Lower Cabinets and Cookware" zones), which then wrongly
    stripped "cabinets" out of Primary Bathroom's own, genuinely self-
    referential band heading ("the drawers, the cabinets and the linen
    shelf"), regressing "master bathroom storage cabinets" from covered to
    partial. Checked directly against the live corpus before shipping
    (CLAUDE.md 5d), the same run that caught it: requiring 3 lifts
    "cabinets" (2 occurrences) out of the map entirely, which only means
    nobody treats it as room-specific any more, the safe default. The
    words this fix actually needs, "bathroom" (12 occurrences) and "guest"
    (10), both clear 3 easily. A second attempt at 2 also flagged "zone"
    itself (1 of 114 zone pages, "the entryway drop zone", happens to carry
    the literal word), which would have stripped "zone" from the "zone by
    zone" phrase on nearly every other room's own band heading; 3 clears
    that too.
    """
    counts = {}
    for p in raw_pages:
        if not p["url"].startswith("/zones/") or not p["room"]:
            continue
        for w in set(words(p["title"])):
            counts.setdefault(w, []).append(p["room"])
    return {w: set(rs) for w, rs in counts.items()
            if len(rs) >= 3 and len(set(rs)) <= 2}


def page_inventory(rooms=None):
    """Every published page as its title and its section headings.

    HEADINGS, ADDED 2026-10-01, AND WHY THEY ARE KEPT SEPARATE.

    The first reading scored a query against page titles only. That is the
    strictest reading and it understates real coverage in one specific way:
    a page can answer a question properly in an <h2> with its own id, which
    is a legitimate target for that query, and still score as a gap because
    the word is not in the title. The article shipped this same day is the
    example. It answers "why is my kitchen always messy" under exactly that
    heading, and reads as `partial` because its title says house.

    So headings are now read as well, and the two scores are kept APART
    rather than merged into one friendlier number. `coverage` stays
    title-only, so it is still comparable with the first reading, and the
    heading score is reported next to it with the surface that matched. A
    measurement that quietly got more generous would be the worse outcome
    here than one that was too strict.

    BAND HEADINGS, ADDED 2026-11-11, AND WHY A WORD CAN BE DROPPED FROM ONE.

    Found live: "organized bathroom cupboard" tied 0.667 on headings
    between the correct page (`/zones/primary-bathroom-the-under-sink-
    cabinet.html`) and `/articles/how-to-organize-a-linen-closet.html`, and
    the linen article won the tie only because its own promotional band
    heading ("The linen shelf, the bathroom towels and the guest bed, zone
    by zone") names Primary/Guest Bathroom's own zones, not anything this
    page is actually about. A prior cycle tried dropping every band heading
    site-wide and reverted it: Pantry's own band ("the cans, the baking
    bin...") names only Pantry's own zones and genuinely helps Pantry
    queries, so losing it was a real regression on 6 pages.
    The distinction neither attempt drew is PER WORD, not per heading: a
    band word that is one of a ROOM's own identifying words (built by
    `_room_identifying_words` from the real zone-page titles) is dropped
    from `head_words` only when that room is not this page's own room;
    every other band word, and every word of a non-band heading, counts as
    it always has. This cannot touch any page with no room signal (most
    articles), since there is nothing to compare "foreign" against.
    """
    if rooms is None:
        rooms = room_names()
    guide_rooms = guide_article_rooms()
    raw = []
    for dirpath, _dirs, files in os.walk(SITE):
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            if name.startswith("_") or name == "404.html":
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    whole = fh.read()
            except OSError:
                continue
            m = re.search(r"<title>(.*?)</title>", whole, re.S)
            if not m:
                continue
            title = re.sub(r"[ \n\t]+", " ", m.group(1)).strip()
            title = title.split("|")[0].strip()
            body = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", whole)
            band_text, rest_text = _band_and_body_text(body)
            url = "/" + os.path.relpath(path, SITE).replace(os.sep, "/")
            raw.append({"url": url, "title": title,
                        "own_heads": " ".join(_page_headings(rest_text)),
                        "band_heads": " ".join(_page_headings(band_text)),
                        "room": room_of(url, rooms, guide_rooms)})
    room_words = _room_identifying_words(raw)
    rows = []
    for r in raw:
        head_words = set(words(r["title"] + " " + r["own_heads"]))
        band_words = set(words(r["band_heads"]))
        if r["room"]:
            band_words = {w for w in band_words
                          if w not in room_words
                          or r["room"] in room_words[w]}
        head_words |= band_words
        rows.append({"url": r["url"],
                     "title": r["title"],
                     "words": set(words(r["title"])),
                     "head_words": head_words,
                     "room": r["room"]})
    return sorted(rows, key=lambda r: r["url"])


def _tie_break(page, best, room_signal, cw=None, field="words"):
    """True if `page` should replace `best` on an exact score tie.

    Found 2026-10-10: with no room signal, a tie always fell to the
    alphabetically-earliest URL, which silently favoured every "Guest X" page
    over its "Primary X" sibling (near-identical titles, "guest-" sorts before
    "primary-"). When the query carries a room signal (its own room name, or a
    household synonym like "master bedroom", see household_room_signal), a
    page that is actually IN that room now wins the tie instead; only when
    neither tied page matches the signal, or there is no signal at all, does
    the next check decide, which is what the pre-existing test for this
    function (a query naming no room) still checks.

    Found 2026-11-02, third instance of the same shape (after the master-bath
    room-signal case above and the "nightstand"/"drawers" plural case,
    BACKLOG-2026-09-07 section 76): "organize grilling station" tied between
    the real patio/deck grill page and the dining room's beverage station on
    an exact-word match, because the scorer compares exact word forms with
    no stemming and "grilling" never equals "grill". When the room signal
    does not decide either (as here: the query names no room), a page with a
    near-miss morphology match (_near_miss_count) for an otherwise-unmatched
    content word now wins over a page with none, before url order. This does
    not touch the score itself, only which tied page is credited, so it
    cannot move any query off gap/partial/covered.
    """
    if room_signal:
        want = page.get("room") == room_signal
        have = best.get("room") == room_signal
        if want and not have:
            return True
        if have and not want:
            return False
    if cw:
        p_near = _near_miss_count(page, cw, field)
        b_near = _near_miss_count(best, cw, field)
        if p_near != b_near:
            return p_near > b_near
    return page["url"] < best["url"]


def _prefer_in_room_zone(inventory, room_signal, best, score, field, cw):
    """A different room's guide article can out-score the query's own room
    on a bag-of-words tie it should not win.

    Found 2026-11-05: "how to organize power tools in garage" (room
    signal Garage) scored 1.0 "covered" on Workshop's own guide article,
    which separately covers "power tool storage" in one heading ("Step 3:
    Power tool storage") and "garage" in another ("A workshop that lives
    in the garage"), neither heading actually about this query's exact
    question. Garage's own Power Tool and Battery Zone, the real answer,
    scored only 0.667 because title/heading matching has no way to credit
    a coherent single-page answer over an incoherent combination from two
    unrelated headings on someone else's page. Six real queries carried
    this shape when checked against the live corpus, all cases where the
    query's own room already had a zone page clearing the 0.5 partial
    threshold on its own.

    Scoped narrowly: only replaces a WINNING GUIDE ARTICLE (not a zone, not
    a deck) that belongs to a different room than the query's own room
    signal, and only when that room's own ZONE page already clears 0.5 on
    the same surface being scored. A weaker in-room page never displaces a
    stronger cross-room one; this only fixes the case where the in-room
    answer was already good enough to stand on its own.
    """
    if not (room_signal and best and best["url"].startswith("/articles/")
            and best.get("room") and best["room"] != room_signal):
        return best, score
    alt, alt_score = None, -1.0
    for page in inventory:
        if page.get("room") != room_signal or not page["url"].startswith("/zones/"):
            continue
        hit = sum(1 for w in cw if w in page[field])
        s = hit / len(cw) if cw else 0.0
        if s > alt_score:
            alt, alt_score = page, s
    if alt and alt_score >= 0.5:
        return alt, round(alt_score, 3)
    return best, score


def best_page(query, inventory, room_signal=""):
    """Best-matching page for a query, by share of its content words covered.

    Deliberately crude. It is a triage score for a human reading the report,
    not a ranking model, and the report says so: 1.0 means every meaningful
    word in the query appears in some page title, which is the weakest claim
    to coverage anybody can make without impression data.
    """
    cw = content_words(query)
    if not cw:
        return None, 0.0
    best, score = None, -1.0
    for page in inventory:
        hit = sum(1 for w in cw if w in page["words"])
        s = hit / len(cw)
        if s > score or (s == score and best is not None
                         and _tie_break(page, best, room_signal, cw)):
            best, score = page, s
    best, score = _prefer_in_room_zone(inventory, room_signal, best, score, "words", cw)
    return best, round(score, 3)


def classify(score):
    if score >= 0.999:
        return "covered"
    if score >= 0.5:
        return "partial"
    return "gap"


def attribute_room(query, rooms):
    """Which room a query belongs to, longest name first so Guest Bathroom
    wins over Bathroom and Kids Bedroom over Bedroom."""
    low = query.lower()
    for room in sorted(rooms, key=len, reverse=True):
        if room.lower() in low:
            return room
    return ""


def best_by(query, inventory, field, room_signal=""):
    """Best-matching page for a query against one surface of the inventory."""
    cw = content_words(query)
    if not cw:
        return None, 0.0
    best, score = None, -1.0
    for page in inventory:
        hit = sum(1 for w in cw if w in page[field])
        s = hit / len(cw)
        if s > score or (s == score and best is not None
                         and _tie_break(page, best, room_signal, cw, field)):
            best, score = page, s
    best, score = _prefer_in_room_zone(inventory, room_signal, best, score, field, cw)
    return best, round(score, 3)


def score_rows(results, rooms, inventory):
    synonyms = room_synonyms()
    rows = []
    for q in sorted(results):
        row = dict(results[q])
        signal = household_room_signal(q, rooms, synonyms)
        page, score = best_page(q, inventory, signal)
        hpage, hscore = best_by(q, inventory, "head_words", signal)
        row["room"] = attribute_room(q, rooms)
        # WHICH SURFACE WON MUST DECIDE WHICH PAGE IS CREDITED.
        #
        # Found live 2026-11-05: best_page/best_page_title were set from the
        # title surface (`page`) unconditionally, even though matched_on and
        # status were already computed from whichever surface scored higher.
        # Across the live corpus, 1402 rows had a heading surface that beat
        # the title surface outright (not even a tie) and pointed at a
        # DIFFERENT page, 778 of those a different room entirely (e.g.
        # "master bedroom storage" reported `best_page` as a Kids Bedroom
        # zone while the row's own status came from Primary Bedroom's room
        # page). Every consumer of this field (room_guide_candidates.py,
        # room_guide_underperformance.py, keyword_demand_global.py) treats
        # best_page as "the page this query actually routes to", so a silent
        # mismatch there does not just mislabel a report, it can send a
        # later cycle hunting for a synonym fix on the wrong zone, or credit
        # the wrong room with coverage it does not have. On an exact tie
        # between the two surfaces, prefer whichever one matches the query's
        # own room signal, the same preference _tie_break already applies
        # within a single surface, rather than defaulting to title.
        use_heading = hscore > score or (
            hscore == score and signal
            and hpage and hpage.get("room") == signal
            and not (page and page.get("room") == signal))
        winner = hpage if use_heading else page
        row["best_page"] = winner["url"] if winner else ""
        row["best_page_title"] = winner["title"] if winner else ""
        # Title-only, unchanged, so this column stays comparable with the
        # first reading taken before headings were read at all.
        row["coverage"] = score
        row["heading_coverage"] = hscore
        row["heading_page"] = hpage["url"] if hpage else ""
        # The status uses the better surface, because a question answered
        # under its own <h2> is genuinely answered, and names which surface
        # earned it so a reader can discount it if they disagree.
        row["matched_on"] = "heading" if use_heading else "title"
        row["status"] = classify(max(score, hscore))
        # UNMATCHED_WORDS, ADDED 2026-10-31. Found live: two gap rows
        # ("car organisation must haves", "car organizer canadian tire")
        # were handed off three cycles running as "needs a title or
        # heading phrase addition" because the query text itself contains
        # "organizer"/"organisation", which reads as the missing word. It
        # is not: both are in FORMAT_WORDS and never enter content_words()
        # at all, so the word actually missing from the page is "must"/
        # "haves" or "canadian"/"tire", neither of which could be added
        # honestly (generic listicle filler and a named retailer this
        # product has no relationship with). A reader (or a later cycle)
        # seeing only the score has no way to tell a real content gap from
        # this one without re-deriving content_words() by hand. Naming the
        # actual unmatched words closes that gap once, here, rather than
        # once per cycle that reopens the same row.
        cw = content_words(q)
        won_words = (winner or {}).get(
            "head_words" if use_heading else "words", set())
        row["unmatched_words"] = sorted(w for w in cw if w not in won_words)
        rows.append(row)
    return rows


def canary_ok(source, sleep=True):
    """Is this endpoint still answering with real content?

    Called before and after the harvest. An endpoint that has started refusing
    us returns a valid, empty, HTTP 200, which is indistinguishable from a
    genuine zero in any single response. It is distinguishable here, because
    this phrase has completions and always will.
    """
    suggestions, err = SOURCES[source](CANARY)
    if sleep:
        time.sleep(random.uniform(*DELAY))
    if err:
        return False, err
    if not suggestions:
        return False, "canary returned an empty 200: endpoint is refusing us"
    return True, ""


def harvest(sources, seeds, verbose=True, sleep=True):
    rooms = room_names()
    results = {}
    attempts, failures = [], []
    for i, seed in enumerate(seeds, 1):
        for source in sources:
            suggestions, err = SOURCES[source](seed)
            attempts.append({"seed": seed, "source": source,
                             "count": len(suggestions), "error": err,
                             "outcome": ("error" if err else
                                         "empty" if not suggestions else "ok")})
            if err:
                failures.append({"seed": seed, "source": source, "error": err})
                if verbose:
                    print("  [%d/%d] %s ERROR %s: %s"
                          % (i, len(seeds), source, seed, err))
            elif not suggestions:
                # A genuine zero, not a refusal. The canary decides which.
                if verbose:
                    print("  [%d/%d] %s  0  %s  (no completions)"
                          % (i, len(seeds), source, seed))
            else:
                for rank, s in enumerate(suggestions, 1):
                    q = re.sub(r"\s+", " ", s).strip().lower()
                    row = results.setdefault(q, {"query": q, "sources": [],
                                                 "best_rank": rank,
                                                 "seeds": []})
                    if source not in row["sources"]:
                        row["sources"].append(source)
                    row["best_rank"] = min(row["best_rank"], rank)
                    if seed not in row["seeds"]:
                        row["seeds"].append(seed)
                if verbose:
                    print("  [%d/%d] %s %2d  %s"
                          % (i, len(seeds), source, len(suggestions), seed))
            if sleep:
                time.sleep(random.uniform(*DELAY))
    inventory = page_inventory(rooms)
    return (score_rows(results, rooms, inventory), attempts, failures,
            len(inventory))


def outcome_counts(attempts):
    counts = {"ok": 0, "empty": 0, "error": 0}
    for a in attempts:
        counts[a.get("outcome", "error" if a.get("error") else "ok")] += 1
    return counts


def refusal_reason(attempts, canaries):
    """Why this harvest must not be written, or an empty string if it may be.

    Separated from main() so a test can plant each condition and assert the
    refusal, rather than trusting that the three ceilings are wired up.
    """
    for source, (ok, why) in sorted(canaries.items()):
        if not ok:
            return "canary failed on %s: %s" % (source, why)
    counts = outcome_counts(attempts)
    total = sum(counts.values())
    if not total:
        return "no attempts were made at all"
    if counts["error"] / total > MAX_ERROR_RATE:
        return ("error rate %.0f%% is over the %.0f%% ceiling (%d of %d)"
                % (counts["error"] / total * 100, MAX_ERROR_RATE * 100,
                   counts["error"], total))
    if counts["empty"] / total > MAX_EMPTY_RATE:
        return ("empty rate %.0f%% is over the %.0f%% ceiling (%d of %d), "
                "which looks like an endpoint answering 200 with nothing"
                % (counts["empty"] / total * 100, MAX_EMPTY_RATE * 100,
                   counts["empty"], total))
    return ""


def write_outputs(payload):
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report(payload))


def report(payload):
    rows = payload["rows"]
    gaps = [r for r in rows if r["status"] == "gap"]
    partial = [r for r in rows if r["status"] == "partial"]
    covered = [r for r in rows if r["status"] == "covered"]
    lines = []
    w = lines.append
    w("# What people type, and whether we have a page for it\n")
    w("> Generated by `ops/keyword_demand.py`. Do not hand-edit: rerun it.\n")
    w("**Harvested:** %s from %s, %d seeds, %d attempts: %d returned "
      "completions, %d had none, %d errored. Canary: %s.\n"
      % (payload["checked_at"], ", ".join(payload["sources"]),
         payload["seeds"], payload["attempts"],
         payload.get("ok_attempts", 0), payload.get("empty_attempts", 0),
         payload["failed_attempts"],
         ", ".join("%s %s" % (k, "ok" if v["ok"] else "FAILED")
                   for k, v in sorted(payload.get("canaries", {}).items()))
         or "not recorded"))
    # TWO DATES, NOT ONE, AND THEY ARE DIFFERENT FACTS (LRN-0032).
    # When the queries were collected is a fact about the engines. When the
    # statuses were derived is a fact about this site, which changes several
    # times an hour, so a coverage number read without its scoring date is a
    # number about a corpus that no longer exists.
    w("**Scored:** %s against %d page(s)%s. Coverage below describes the "
      "site at THAT moment, not when the queries were harvested. Re-derive "
      "with `python ops/keyword_demand.py --rescore`, which needs no "
      "network.\n"
      % (payload.get("scored_at") or "not recorded, so treat every status "
         "here as of unknown age",
         payload.get("pages_checked", 0),
         (" at commit " + payload["scored_against_commit"])
         if payload.get("scored_against_commit") else ""))
    w("**Queries found:** %d. Checked against %d published page titles: "
      "%d covered, %d partial, %d gap.\n"
      % (len(rows), payload["pages_checked"], len(covered), len(partial),
         len(gaps)))
    w("**This is not search volume.** An autocomplete suggestion proves an "
      "engine predicts the phrase, which means people type it often enough to "
      "be worth predicting. It carries no count, and `rank` orders suggestions "
      "only within the one seed that produced them. Anything here presented "
      "as a monthly volume is a fabrication (CLAUDE.md section 8).\n")
    w("**Coverage is a triage score, not a ranking.** It is the share of a "
      "meaningful query word that appears in the best-matching page title. "
      "`covered` means every word appears somewhere, which is the weakest "
      "claim to coverage available without impression data, and a page can be "
      "`covered` here and invisible on a real result page.\n")
    w("\n---\n")
    w("## Gaps: nothing we publish is titled for these\n")
    w("Showing the top %d of %d, ordered by the best rank the phrase "
      "reached in any one seed suggestion list, so the top of this list is "
      "what an engine predicts first. The full set is in "
      "`keyword-demand.json`.\n" % (min(80, len(gaps)), len(gaps)))
    w("| Rank | Query | Room | Closest page we have | Missing words |")
    w("|---|---|---|---|---|")
    for r in sorted(gaps, key=lambda r: (r["best_rank"], r["query"]))[:80]:
        w("| %d | %s | %s | %s (%.2f) | %s |"
          % (r["best_rank"], r["query"], r["room"] or "-",
             r["best_page_title"] or "-", r["coverage"],
             ", ".join(r.get("unmatched_words", [])) or "-"))
    w("\n## Partial: we are close, and the title does not use their words\n")
    w("Showing the top %d of %d.\n" % (min(60, len(partial)), len(partial)))
    w("| Rank | Query | Our closest title | Coverage |")
    w("|---|---|---|---|")
    for r in sorted(partial, key=lambda r: (-r["coverage"], r["best_rank"]))[:60]:
        w("| %d | %s | %s | %.2f |"
          % (r["best_rank"], r["query"], r["best_page_title"], r["coverage"]))
    w("\n## By room\n")
    w("| Room | Queries | Gap | Partial | Covered |")
    w("|---|---|---|---|---|")
    for room in sorted({r["room"] for r in rows if r["room"]}):
        sub = [r for r in rows if r["room"] == room]
        w("| %s | %d | %d | %d | %d |"
          % (room, len(sub),
             sum(1 for r in sub if r["status"] == "gap"),
             sum(1 for r in sub if r["status"] == "partial"),
             sum(1 for r in sub if r["status"] == "covered")))
    unattributed = [r for r in rows if not r["room"]]
    w("\n%d queries name no room of ours. Those are either a different "
      "subject the engine wandered into, or a room-independent question, and "
      "the second kind is where an article earns its place.\n"
      % len(unattributed))
    if payload["failures"]:
        w("\n## Not checked\n")
        w("| Seed | Source | Why |")
        w("|---|---|---|")
        for f in payload["failures"][:40]:
            w("| %s | %s | %s |" % (f["seed"], f["source"], f["error"]))
    return "\n".join(lines) + "\n"


# The two query clusters GOALS.md's O1 section names by hand, matched here
# by an explicit, reproducible rule rather than re-typed from memory. Found
# 2026-10-02: GOALS.md's own prose citation of these two counts went stale
# the same day it was written (A13/A14 shipped the pages that moved them,
# nobody told this sentence), and a concurrent session was misled by it into
# drafting a handoff for work already done, LRN-0032's "a stored status is a
# snapshot other sessions are changing" recurring against prose instead of
# the JSON file itself. CLUSTER_PATTERNS is the thing gate_goals_keyword_
# cluster_citation_current re-derives against, so this is provable, not
# asserted: "cheap/budget/DIY" as `\b(cheap|budget|diy)\b` reproduces the
# historical "of 99" denominator exactly; a plain substring check for "diy"
# (no word boundary) or an added "small" term would not.
CLUSTER_PATTERNS = {
    "small space": re.compile(r"small space", re.I),
    "cheap/budget/DIY": re.compile(r"\b(cheap|budget|diy)\b", re.I),
}


def cluster_counts(rows, pattern):
    """covered/partial/gap counts among the rows whose query matches pattern.

    Pure: takes rows already loaded from keyword-demand.json (or a rescore),
    never reads a file itself, so gate_goals_keyword_cluster_citation_
    current can prove it against a synthetic payload as well as the real one.
    """
    matched = [r for r in rows if pattern.search(r["query"])]
    counts = {"covered": 0, "partial": 0, "gap": 0}
    for r in matched:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    counts["total"] = len(matched)
    return counts


# The exact phrasing GOALS.md's O1 section uses to cite each cluster's
# coverage, so gate_goals_keyword_cluster_citation_current can check the
# live claim, not just whether the file mentions the cluster at all.
CLUSTER_CITATION_PATTERNS = {
    "small space": re.compile(
        r'"small space"\s+is\s+\*\*(\d+)\s+covered\s*/\s*(\d+)\s+partial'
        r'\s*/\s*(\d+)\s+gap\s+of\s+(\d+)\*\*'),
    "cheap/budget/DIY": re.compile(
        r'"cheap/budget/DIY"\s+is\s+\*\*(\d+)\s+covered\s*/\s*(\d+)\s+'
        r'partial\s*/\s*(\d+)\s+gap\s+of\s+(\d+)\*\*'),
}


def goals_cluster_citation_problems(text, live_counts):
    """Pure so gate_goals_keyword_cluster_citation_current can prove it
    without shelling out.

    live_counts maps a CLUSTER_PATTERNS name to a cluster_counts()-shaped
    dict freshly re-derived from the real keyword-demand.json. Returns one
    problem string per cluster whose cited covered/partial/gap/total in
    GOALS.md disagrees with the live count. A cluster GOALS.md does not
    currently cite in this exact phrasing is skipped, not flagged: a
    legitimate rewording of the sentence is not this function's business,
    only a citation that stayed in place and went stale underneath it,
    which is what happened 2026-10-02 (A13/A14 shipped the pages that moved
    both clusters; the sentence citing their old counts was never updated,
    and a concurrent session read it instead of re-deriving from the JSON).
    """
    problems = []
    for name, pat in CLUSTER_CITATION_PATTERNS.items():
        m = pat.search(text)
        if not m:
            continue
        cited = tuple(int(x) for x in m.groups())
        live = live_counts.get(name)
        if live is None:
            continue
        real = (live["covered"], live["partial"], live["gap"], live["total"])
        if cited != real:
            problems.append(
                "GOALS.md cites the %r cluster as %d covered / %d partial "
                "/ %d gap of %d, but the real keyword-demand.json currently "
                "scores it as %d covered / %d partial / %d gap of %d"
                % (name, cited[0], cited[1], cited[2], cited[3],
                   real[0], real[1], real[2], real[3]))
    return problems


def status():
    if not os.path.exists(OUT_JSON):
        print("No harvest on record. Run: python ops/keyword_demand.py")
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        payload = json.load(fh)
    rows = payload["rows"]
    print("last harvest : %s" % payload["checked_at"])
    print("sources      : %s" % ", ".join(payload["sources"]))
    print("seeds        : %d, %d attempts, %d ok, %d empty, %d errored"
          % (payload["seeds"], payload["attempts"],
             payload.get("ok_attempts", 0), payload.get("empty_attempts", 0),
             payload["failed_attempts"]))
    print("queries      : %d" % len(rows))
    for st in ("gap", "partial", "covered"):
        print("  %-8s   : %d" % (st, sum(1 for r in rows if r["status"] == st)))
    return 0


def head_commit():
    """The commit the corpus was scored against, or an empty string."""
    try:
        r = subprocess.run(["git", "rev-parse", "--short=9", "HEAD"],
                           cwd=ROOT, capture_output=True, text=True,
                           timeout=20)
    except Exception:                                  # noqa: BLE001
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def rescore():
    """Re-derive every status against the corpus as it stands right now.

    LRN-0032, written 2026-10-02 after this cost a wasted investigation and nearly
    cost a duplicate article. A stored `status` is not a property of the query.
    It is the result of scoring that query against the site AS IT WAS when the
    harvest ran, and on this repository the site changes several times an hour
    because more than one session is working on it. Reading the stored file
    said the budget cluster was 121 queries with zero covered; re-scoring the
    identical queries against the corpus as it actually stood returned 29
    covered, because a concurrent session had added a room-by-room budget
    section in the interval.

    This is the cheap half of the tool: pure functions over files already on
    disk, no network, no seeds, nothing to rate-limit. There is no reason to
    read a stale status ever again.
    """
    if not os.path.exists(OUT_JSON):
        print("No harvest on record to re-score. Run: python "
              "ops/keyword_demand.py")
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        payload = json.load(fh)
    before = {}
    for row in payload["rows"]:
        before[row["status"]] = before.get(row["status"], 0) + 1
    results = {r["query"]: {"query": r["query"], "sources": r["sources"],
                            "best_rank": r["best_rank"], "seeds": r["seeds"]}
               for r in payload["rows"]}
    rooms = room_names()
    inventory = page_inventory(rooms)
    payload["rows"] = score_rows(results, rooms, inventory)
    payload["pages_checked"] = len(inventory)
    payload["scored_at"] = (datetime.datetime.now(datetime.timezone.utc)
                            .strftime("%Y-%m-%dT%H:%M:%SZ"))
    payload["scored_against_commit"] = head_commit()
    after = {}
    for row in payload["rows"]:
        after[row["status"]] = after.get(row["status"], 0) + 1
    write_outputs(payload)
    print("re-scored %d quer(ies) against %d page(s) at commit %s"
          % (len(payload["rows"]), len(inventory),
             payload["scored_against_commit"] or "unknown"))
    for st in ("gap", "partial", "covered"):
        print("  %-8s %5d -> %5d" % (st, before.get(st, 0), after.get(st, 0)))
    return 0


def main(argv):
    # A FLAG THIS FILE DOES NOT KNOW MUST NOT START A LIVE HARVEST.
    #
    # Found 2026-10-03 by running it: `--help` was not recognised here, so it
    # matched none of the branches below and fell straight through to the
    # default action, which fetches both autocomplete endpoints for every seed
    # in the corpus and overwrites ops/keyword-demand.json. A reader asking a
    # tool how to use it cannot have meant that, and the same hole made every
    # typo (--statuss, --dry-ryn, --rescor) silently do the most expensive and
    # least reversible thing this file can do rather than say it did not
    # understand. Validate first, act second.
    FLAGS = {
        '--rescore', '--status', '--dry-run', '--source', '--help', '-h',
    }
    if '--help' in argv or '-h' in argv:
        print((__doc__ or '').strip())
        return 0
    unknown = []
    skip = False
    for arg in argv:
        if skip:
            skip = False          # the value belonging to --source
            continue
        if arg == '--source':
            skip = True
            continue
        if arg not in FLAGS:
            unknown.append(arg)
    if unknown:
        print('unknown argument(s): %s' % ', '.join(unknown))
        print('Refusing to harvest, because that is not what you asked for. '
              'Run with --help for what this accepts.')
        return 2
    if '--source' in argv and argv.index('--source') + 1 >= len(argv):
        print('--source needs a value: google, bing or both.')
        return 2
    if '--rescore' in argv:
        return rescore()
    if "--status" in argv:
        return status()
    source = "google"
    if "--source" in argv:
        source = argv[argv.index("--source") + 1]
    sources = ["google", "bing"] if source == "both" else [source]
    for s in sources:
        if s not in SOURCES:
            print("unknown source: %s" % s)
            return 2
    seeds = build_seeds()
    dry = "--dry-run" in argv
    if dry:
        seeds = seeds[:6]
    print("Harvesting %d seeds from %s%s"
          % (len(seeds), ", ".join(sources), " (dry run)" if dry else ""))
    canaries = {}
    for src in sources:
        ok, why = canary_ok(src)
        canaries[src] = (ok, why)
        print("  canary %s: %s" % (src, "ok" if ok else why))
    rows, attempts, failures, pages = harvest(sources, seeds)
    for src in sources:
        ok, why = canary_ok(src)
        if not ok:
            canaries[src] = (ok, why)
        print("  canary %s, after the run: %s" % (src, "ok" if ok else why))
    counts = outcome_counts(attempts)
    print()
    print("%d distinct queries from %d attempts: %d returned completions, "
          "%d had none, %d errored"
          % (len(rows), len(attempts), counts["ok"], counts["empty"],
             counts["error"]))
    reason = refusal_reason(attempts, canaries)
    if reason:
        print("UNCHECKED: %s. Nothing written. A partial harvest must "
              "not overwrite a complete one." % reason)
        return 1
    payload = {
        "checked_at": datetime.datetime.now(datetime.timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": sources,
        "seeds": len(seeds),
        "attempts": len(attempts),
        "ok_attempts": counts["ok"],
        "empty_attempts": counts["empty"],
        "failed_attempts": counts["error"],
        "canaries": {k: {"ok": v[0], "note": v[1]}
                     for k, v in sorted(canaries.items())},
        "pages_checked": pages,
        "failures": failures,
        "rows": rows,
        "scored_against_commit": head_commit(),
    }
    if dry:
        print("dry run: nothing written")
        for r in rows[:15]:
            print("  %-8s %.2f  %s" % (r["status"], r["coverage"], r["query"]))
        return 0
    write_outputs(payload)
    print("wrote %s and %s" % (os.path.relpath(OUT_JSON, ROOT),
                               os.path.relpath(OUT_MD, ROOT)))
    for st in ("gap", "partial", "covered"):
        print("  %-8s: %d" % (st, sum(1 for r in rows if r["status"] == st)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
