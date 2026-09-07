"""Schema check for the optional `diagnosis` block on a content.json zone.

PLAN-MICROZONES-DECKS-APP.md item M2: "the corpus is the single source; the
book, pages, app and deck all build from it." Before this file, root cause
was mapped for 0 of 114 zones (measured in the plan, section 0) and nothing
enforced a shape for the field once authoring started.

WHAT A ZONE MAY CARRY

    "diagnosis": {
        "frictions": [
            {
                "symptom": "The counter is never clear.",
                "branches": [
                    {"answer": "Things get set down on the way past",
                     "cause": "KC-002"},
                    {"answer": "There is more kitchen than the counter can hold",
                     "cause": "KC-001"}
                ]
            },
            ...  # 3 or more frictions
        ],
        "first_15": {"action": "...", "victory": "..."}
    }

THE SHAPE, AND WHY IT IS NOT FLATTER

The obvious first draft gives each friction a single `cause`. The real data
this has to hold, `ops/cardtext/kitchen-deck.json`'s FRICTION CARDs, does not
fit that: one symptom ("the counter is never clear") branches to two or three
different possible causes depending on what is actually true in that reader's
kitchen (KF-001 alone branches to KC-002, KC-001 and KC-008). M3 is required
to reuse those 21 cards character-for-character, so the schema has to be able
to hold what they actually say. This also matches M2's own acceptance text,
which says "a BRANCH naming an unknown cause", not "a friction naming one".

`start_pass` is deliberately not a field here. Every root cause in
ops/root_causes.py already carries the pass it belongs to (`six_s`), and a
reader who picks a branch is choosing a cause, which already determines the
pass: storing a second copy of that fact in content.json would be one more
place for it to silently drift from the vocabulary that actually owns it.
Look it up with `root_causes.BY_ID[cause]["six_s"]` wherever "which pass to
start at" needs to be shown (M4).

`cause` (on every branch) must be an id from ops/root_causes.py, the one
vocabulary M1 froze. `first_15.victory` must describe an observable end
state, not repeat the instruction itself.

THE VICTORY CHECK, AND WHY IT IS NOT A STATE-VERB WHITELIST

The first version of this file required a state verb (holds, sits, shows...)
to be present. Checked against the 9 real 15-minute ACTION CARD victory
conditions already live in ops/cardtext/kitchen-deck.json before any content
was authored against it, that version rejected 4 of the 9, including "Dry
basin, two tools standing, nothing lying in water": true, observable, and
already shipped, but it names no verb from any fixed list a regex could
anticipate. Natural prose describing a scene is too varied for a whitelist.

What actually distinguishes this corpus's instructions from its victory
conditions is not word choice, it is mood: every `first_15.action` and every
ACTION CARD step opens with a bare imperative ("Tip the tray...", "Take
everything off..."), and no real victory condition does. So the check here
is the cheap, robust version of that same signal: fail only when the
sentence's own first word is one of the imperative verbs this corpus's
instructions are actually written with (IMPERATIVE_FIRST_WORD, built from
every ACTION CARD step in ops/cardtext/kitchen-deck.json). This is a
heuristic, not a parser, and it is deliberately permissive: it will not
catch every possible instruction-shaped victory, but proven against the
real, already-shipped corpus it accepts all 9 real cases and still rejects
the plan's own example, "Tip the tray onto the table."

Zones without a `diagnosis` key are untouched by this check, so authoring can
proceed zone by zone (M3, M6) without every unfinished zone failing the gate.

    python ops/diagnosis.py path/to/content.json    report only, exit 1 on problems
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import root_causes                                             # noqa: E402

# Built from every ACTION CARD step's opening word in
# ops/cardtext/kitchen-deck.json: the corpus's own real vocabulary for
# giving an instruction, not a guessed list of "action verbs" in general.
IMPERATIVE_FIRST_WORD = {
    "assign", "band", "bring", "cap", "check", "clean", "clear", "close",
    "count", "degrease", "design", "discard", "divide", "empty", "fit",
    "give", "hang", "heat", "label", "let", "lift", "measure", "mop",
    "mount", "move", "note", "photograph", "pick", "place", "press", "pull",
    "put", "remove", "return", "send", "separate", "set", "sheath", "sort",
    "stack", "stand", "start", "sweep", "take", "tape", "test", "tip",
    "toss", "turn", "unplug", "vacuum", "wash", "wipe", "write",
}

FIRST_WORD = re.compile(r"[A-Za-z']+")


def victory_is_observable(text: str) -> bool:
    """A victory line must describe a state a reader can look at and confirm,
    not repeat the instruction as if it were the outcome. See the module
    docstring: this checks mood (is the sentence an imperative?), not word
    choice, because the real corpus describes end states in too many
    different words for a fixed vocabulary to recognise them all.
    """
    if not text:
        return False
    m = FIRST_WORD.match(text.strip())
    if not m:
        return False
    return m.group(0).lower() not in IMPERATIVE_FIRST_WORD


def check_zone_diagnosis(zone: dict, valid_cause_ids=None) -> list[str]:
    """Return a list of problems with zone["diagnosis"], or [] if absent or
    fine. `valid_cause_ids` defaults to ops/root_causes.py's frozen set so a
    caller can substitute a synthetic set in a test without touching the
    real vocabulary.
    """
    diag = zone.get("diagnosis")
    if not diag:
        return []
    valid_cause_ids = (root_causes.BY_ID.keys() if valid_cause_ids is None
                       else valid_cause_ids)
    name = zone.get("zone", "?")
    problems = []

    frictions = diag.get("frictions") or []
    if len(frictions) < 3:
        problems.append("%s: diagnosis.frictions has %d, needs >= 3"
                         % (name, len(frictions)))
    for i, f in enumerate(frictions):
        if not f.get("symptom"):
            problems.append("%s: friction[%d] missing 'symptom'" % (name, i))
        branches = f.get("branches") or []
        if not branches:
            problems.append("%s: friction[%d] has no branches" % (name, i))
        for j, b in enumerate(branches):
            if not b.get("answer"):
                problems.append("%s: friction[%d] branch[%d] missing 'answer'"
                                 % (name, i, j))
            cause = b.get("cause")
            if not cause:
                problems.append("%s: friction[%d] branch[%d] missing 'cause'"
                                 % (name, i, j))
            elif cause not in valid_cause_ids:
                problems.append(
                    "%s: friction[%d] branch[%d] cause %r is not a known "
                    "root cause" % (name, i, j, cause))

    first_15 = diag.get("first_15")
    if not first_15 or not first_15.get("action"):
        problems.append("%s: diagnosis.first_15 missing an action" % name)
    if not first_15 or not first_15.get("victory"):
        problems.append("%s: diagnosis.first_15 missing a victory" % name)
    elif not victory_is_observable(first_15["victory"]):
        problems.append("%s: diagnosis.first_15.victory is not observable "
                         "(reads as an instruction, not an end state): %r"
                         % (name, first_15["victory"]))

    return problems


def check_all(rooms, valid_cause_ids=None) -> list[str]:
    problems = []
    for r in rooms:
        for z in r.get("zones", []):
            problems.extend(check_zone_diagnosis(z, valid_cause_ids))
    return problems


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python ops/diagnosis.py path/to/content.json")
        return 2
    data = json.load(io.open(sys.argv[1], encoding="utf-8"))
    rooms = data["rooms"] if isinstance(data, dict) else data
    problems = check_all(rooms)
    covered = sum(1 for r in rooms for z in r.get("zones", []) if z.get("diagnosis"))
    total = sum(len(r.get("zones", [])) for r in rooms)
    print("  diagnosis present on %d of %d zones" % (covered, total))
    if problems:
        print("  FAIL %d problem(s):" % len(problems))
        for p in problems[:20]:
            print("    - " + p)
        return 1
    print("  every zone carrying a diagnosis block passes schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
