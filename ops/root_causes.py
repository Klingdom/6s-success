#!/usr/bin/env python3
"""The one root-cause vocabulary shared by the deck, the app and the articles.

PLAN-MICROZONES-DECKS-APP.md item M1: "one name per cause across deck, app,
articles". Before this file, that name existed in exactly one place, the
Kitchen deck's 12 root-cause cards (ops/cardtext/kitchen-deck.json, ids
KC-001..012), and it had never been checked against anything.

The plan's own text claimed "the full list in the product model is
twenty-one." That number does not exist anywhere in this repository.
DECK-SYSTEM.md line 242 reads "21  KF-001..021  three frictions per zone,
each branching to a root cause": 21 FRICTION cards in the Kitchen deck, not
21 root causes. Reading the plan's own citation rather than trusting its
arithmetic found the actual count: 12 causes are in production use
(kitchen-deck.json), and the 28 root-cause articles under site/articles/
evidence 5 more that no Kitchen zone happens to need. Corrected in
PLAN-MICROZONES-DECKS-APP.md; the real total is 17, not padded to a number
nobody measured.

CAUSES[i]["id"] for the first 12 is copied character-for-character from
ops/cardtext/kitchen-deck.json's ROOT CAUSE CARD entries (title, six_s and
confirm_in_30_seconds included) so the frozen vocabulary cannot silently
diverge from the cards already in print. The remaining 5 use a new "RC-"
prefix rather than continuing "KC-", because "KC" already means a Kitchen
card id in three other card types (KF, KA, KZ) and reusing it for causes
with no Kitchen origin would make a future Kitchen-specific id collide with
a whole-product one.

article is the site/articles/ slug whose own text names this exact cause
(quoted in this file's own history, not guessed), or None if no article
maps to it yet.
"""

CAUSES = [
    {
        "id": "KC-001",
        "name": "EXCESS",
        "meaning": "More things are kept here than the zone's job needs.",
        "confirm_30s": "Count what you used in the past month. If the "
                        "honest number is a third of what is stored here, "
                        "the space is not too small.",
        "six_s": "Sort",
        "article": "more-storage-wont-fix-clutter",
    },
    {
        "id": "KC-002",
        "name": "NO ASSIGNED HOME",
        "meaning": "The thing has no single defined destination, so it "
                    "lands wherever the hand opens.",
        "confirm_30s": "Ask where one specific item lives. If two people "
                        "answer differently, or nobody answers, it has no "
                        "home.",
        "six_s": "Straighten",
        "article": "everything-needs-an-assigned-home",
    },
    {
        "id": "KC-003",
        "name": "WRONG LOCATION",
        "meaning": "It is stored somewhere, just not where it is used.",
        "confirm_30s": "Stand where you use it and count the steps to "
                        "where it is kept. More than two is the wrong "
                        "cabinet.",
        "six_s": "Straighten",
        "article": "why-it-lives-in-one-room-but-gets-used-in-another",
    },
    {
        "id": "KC-004",
        "name": "EXCESS MOTION",
        "meaning": "Getting it out means bending, lifting, unstacking, or "
                    "moving something else first: too many steps.",
        "confirm_30s": "Fetch it once and count the movements. More than "
                        "two and the storage is charging you rent every "
                        "time.",
        "six_s": "Straighten",
        "article": "why-you-have-to-dig-for-what-you-need",
    },
    {
        "id": "KC-005",
        "name": "POOR VISIBILITY",
        "meaning": "You own it, but you cannot see it, so you buy it "
                    "again or forget it.",
        "confirm_30s": "Open the door and, without moving anything, name "
                        "what is at the back. If you cannot, that stock "
                        "is invisible.",
        "six_s": "Straighten",
        "article": "why-you-keep-buying-things-you-already-own",
    },
    {
        "id": "KC-006",
        "name": "POOR ACCESSIBILITY",
        "meaning": "The people who use it cannot reach it safely, or at "
                    "all.",
        "confirm_30s": "Have the shortest person who uses this zone "
                        "fetch what they need daily. If they climb, reach "
                        "overhead, or ask for help, the height is wrong.",
        "six_s": "Safety",
        "article": "everyday-things-out-of-reach",
    },
    {
        "id": "KC-007",
        "name": "INSUFFICIENT CAPACITY",
        "meaning": "The right storage exists and genuinely cannot hold "
                    "what belongs in it.",
        "confirm_30s": "Put back only what belongs here. If it still "
                        "will not close, or still stacks four deep, the "
                        "capacity is the problem, not the habit.",
        "six_s": "Sort",
        "article": "zone-too-small-for-what-it-holds",
    },
    {
        "id": "KC-008",
        "name": "MISSING STANDARD",
        "meaning": "Nobody agreed what good looks like, so everybody is "
                    "right.",
        "confirm_30s": "Ask two people what this surface should look "
                        "like at bedtime. Two answers means there is no "
                        "standard to keep.",
        "six_s": "Standardize",
        "article": "why-everyone-in-your-house-disagrees-about-clean",
    },
    {
        "id": "KC-009",
        "name": "MISSING TRIGGER",
        "meaning": "The reset is a good intention with nothing to attach "
                    "it to.",
        "confirm_30s": "Name the moment it happens. If the answer is "
                        "\"when I get round to it\", there is no trigger "
                        "and it will not survive a bad week.",
        "six_s": "Sustain",
        "article": "why-your-house-gets-messy-again",
    },
    {
        "id": "KC-010",
        "name": "SAFETY CONSTRAINT",
        "meaning": "The current arrangement can hurt somebody, and that "
                    "outranks tidy.",
        "confirm_30s": "Look for the four: a blade your hand would meet, "
                        "weight above shoulder height, heat beside "
                        "something that burns, and an unsafe placement "
                        "near a child's reach.",
        "six_s": "Safety",
        "article": "tidy-is-not-the-same-as-safe",
    },
    {
        "id": "KC-011",
        "name": "POOR REPLENISHMENT",
        "meaning": "Consumables run out unnoticed, and stock ages out of "
                    "use unseen.",
        "confirm_30s": "Find the last one of something you use daily. If "
                        "nothing tells you it is the last one, you will "
                        "find out at the worst possible moment.",
        "six_s": "Standardize",
        "article": "why-you-keep-running-out-of-things",
    },
    {
        "id": "KC-012",
        "name": "CONFLICTING USERS",
        "meaning": "Two people run one zone by two designs, so it is "
                    "permanently half of each.",
        "confirm_30s": "Do the shared task together, once. The argument "
                        "that starts is the conflict, and it is a design "
                        "problem, not a character problem.",
        "six_s": "Standardize",
        "article": None,
    },
    {
        "id": "RC-013",
        "name": "UNCLEAR OWNERSHIP",
        "meaning": "Nobody specific is responsible for resetting this "
                    "zone, so upkeep depends on whoever notices first.",
        "confirm_30s": "Ask who resets this zone. If the honest answer is "
                        "\"whoever gets to it\" or two names with no "
                        "agreement, there is no owner.",
        "six_s": "Sustain",
        "article": "why-a-shared-zone-never-stays-reset",
    },
    {
        "id": "RC-014",
        "name": "SENTIMENTAL ATTACHMENT",
        "meaning": "The item is kept for what it represents, not because "
                    "it is used, and the guilt stalls Sort indefinitely.",
        "confirm_30s": "Ask if you would buy this again today for what "
                        "it does. If the answer is no but you still "
                        "cannot decide, the hold is sentimental.",
        "six_s": "Sort",
        "article": "sentimental-items-without-guilt",
    },
    {
        "id": "RC-015",
        "name": "UNRESOLVED DECISION",
        "meaning": "The item is not clutter, it is a decision that has "
                    "not been made, so it is stacked instead of acted on.",
        "confirm_30s": "Pick up one piece. If your first thought is a "
                        "verb (pay, sign, call, decide) rather than a "
                        "place, it needs a decision, not a home.",
        "six_s": "Sort",
        "article": "why-mail-piles-up-by-the-door",
    },
    {
        "id": "RC-016",
        "name": "DIFFICULT TO CLEAN",
        "meaning": "Reaching the surface to clean it costs more effort "
                    "than the rest of the zone combined, so it gets "
                    "skipped.",
        "confirm_30s": "Time how long it actually takes to reach and "
                        "wipe the surface. If it requires moving "
                        "something first, that cost is why it is skipped.",
        "six_s": "Shine",
        "article": "why-the-same-spot-never-gets-clean",
    },
    {
        "id": "RC-017",
        "name": "PERCEPTUAL BLINDNESS",
        "meaning": "The clutter has been visible so long the eye stops "
                    "flagging it as a problem.",
        "confirm_30s": "Ask someone who does not live here to name what "
                        "looks out of place. If they see it instantly and "
                        "you had stopped noticing, this is the cause.",
        "six_s": "Sort",
        "article": "why-you-cant-see-your-own-clutter",
    },
]

BY_ID = {c["id"]: c for c in CAUSES}

VALID_SIX_S = {"Sort", "Straighten", "Shine", "Safety", "Standardize", "Sustain"}


def _self_check():
    """Fail loudly if this file's own data is internally broken."""
    ids = [c["id"] for c in CAUSES]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError("duplicate cause id(s): %s" % dupes)
    for c in CAUSES:
        if c["six_s"] not in VALID_SIX_S:
            raise ValueError("%s: six_s %r is not one of %s"
                              % (c["id"], c["six_s"], sorted(VALID_SIX_S)))
        if not c["meaning"] or not c["confirm_30s"]:
            raise ValueError("%s: meaning and confirm_30s are required"
                              % c["id"])


_self_check()


def unknown_ids_in(obj, found=None):
    """Walk a parsed JSON structure and collect every string matching a
    card-id shape (KC-### or RC-###) that is not in this vocabulary.

    Deliberately pattern-based rather than key-based: a new field name for
    "root cause" (root_cause, root_causes, cause, causes...) should not be
    able to bypass this check by using a key this function has not been
    told about yet.
    """
    import re
    if found is None:
        found = set()
    pattern = re.compile(r"^(KC|RC)-\d+$")
    if isinstance(obj, dict):
        for v in obj.values():
            unknown_ids_in(v, found)
    elif isinstance(obj, list):
        for v in obj:
            unknown_ids_in(v, found)
    elif isinstance(obj, str) and pattern.match(obj) and obj not in BY_ID:
        found.add(obj)
    return found


if __name__ == "__main__":
    print("%d root causes frozen." % len(CAUSES))
    for c in CAUSES:
        art = c["article"] or "(no article yet)"
        print("  %-7s %-24s %-12s %s" % (c["id"], c["name"], c["six_s"], art))
