"""Single source of truth for the opening direct answer on the six
"specific problem" articles D12 (REVIEW-DISCOVERY-2026-09-07.md section 2)
names as the only six articles with a nameable query behind them.

Each article is hand-maintained under site/articles/ (no generator owns
this directory's content; see ops/build_articles.py, which only ever wrote
the two generic "why" article templates, article_one/article_two).
gate_specific_article_direct_answer in ops/preflight.py re-derives the
expected opening <p class="lede"> from this dict and diffs it byte for byte
against the real shipped HTML, the same pattern
ops.build_zone_pages.direct_answer()/gate_zone_direct_answer_current
already uses for all 114 zone pages, so this hand-authored surface gets the
same drift protection a generator-owned one gets automatically.

D1's own reasoning, applied here: "the first 60 words under the H1 should
answer the question the title asks... it is what AI Overviews, Copilot and
ChatGPT extract." Before this fix, each of these six opened with a
narrative hook (real, true, not fabricated) and only stated the actual
answer in a second block below it, a <p class="notice"> the hook pushed
out of the first-60-words window. Each entry below is the same real answer
that block already stated, tightened to lead the page instead of follow
it; nothing here is a new claim, only a reordering of one already
published. The former hook paragraph moves to the second paragraph on the
page, unchanged in substance, so the narrative is not lost, it is no
longer first.
"""

DIRECT_ANSWERS = {
    "why-you-always-lose-your-keys": (
        "Your keys do not have one fixed spot they always go, so where "
        "they land depends on whatever your hands were doing when you "
        "walked in. Give them exactly one home, in the exact spot your "
        "hand opens on the way through the door, hold nothing else in "
        "it, and attach the drop to a motion you already make, like "
        "taking off your coat."
    ),
    "how-to-organize-a-junk-drawer": (
        "A kitchen is allowed one drawer of small useful things, but it "
        "needs a name and a written list, not an amnesty. Decide what "
        "belongs there, then hold everything in it to that list. "
        "Anything you cannot name a use for goes into a dated box "
        "instead, and it leaves unopened if nothing is pulled from it "
        "by season's end."
    ),
    "why-mail-piles-up-by-the-door": (
        "A mail pile is not a filing problem, it is a stack of "
        "undecided paper. Give every piece a verdict before it goes "
        "back on the surface: act, file, or recycle, then hold act mail "
        "to a fourteen day deadline written in the corner. Once a piece "
        "passes its date, it stops being paperwork and becomes a "
        "decision: do it, or recycle it."
    ),
    "why-the-medicine-cabinet-never-gets-cleared-out": (
        "A medicine cabinet never signals for review the way a fridge "
        "or a pantry does. Food announces when it has gone off; a "
        "tablet past its date looks exactly the same as the day you "
        "bought it, so nothing prompts a check unless you decide to, "
        "and that decision keeps losing to everything else on your "
        "list. The fix is attaching the check to something that "
        "already happens on its own: the pharmacy trip."
    ),
    "why-you-cant-find-the-right-charger": (
        "A charger drawer has one home for every device instead of one "
        "home per device, so every cable looks the same and nothing "
        "tells you which one is still yours. Give each working device "
        "its own named slot on a power strip, recycle everything left "
        "over, and settle the retired phone's job once instead of "
        "leaving it to occupy a slot indefinitely."
    ),
    "why-you-have-to-dig-for-what-you-need": (
        "Too many steps is its own root cause, separate from no "
        "assigned home and separate from poor accessibility. The item "
        "has a home at a fine height; the problem is what sits between "
        "your hand and the item once you are standing there: a stack "
        "to unload, a drawer to excavate, a box in front of a box. The "
        "fix is reordering what is already there so nothing used often "
        "sits behind something used rarely."
    ),
}
