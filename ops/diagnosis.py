"""Schema check for the optional `diagnosis` block on a content.json zone.

PLAN-MICROZONES-DECKS-APP.md item M2: "the corpus is the single source; the
book, pages, app and deck all build from it." Before this file, root cause
was mapped for 0 of 114 zones (measured in the plan, section 0) and nothing
enforced a shape for the field once authoring started.

WHAT A ZONE MAY CARRY

    "diagnosis": {
        "frictions": [
            {"symptom": "...", "cause": "KC-002", "start_pass": "straighten"},
            ...  # 3 or more
        ],
        "first_15": {"action": "...", "victory": "..."}
    }

`cause` must be an id from ops/root_causes.py, the one vocabulary M1 froze.
`start_pass` must be one of the six pass keys content.json already uses.
`first_15.victory` must describe an observable end state, not an instruction:
checked for a state verb (holds, sits, shows, reads, stays...) rather than an
imperative opening the sentence with the action itself.

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

VALID_PASSES = {"sort", "straighten", "shine", "safety", "standardize", "sustain"}

FRICTION_FIELDS = ("symptom", "cause", "start_pass")

STATE_VERB = re.compile(
    r"\b(is|are|holds?|sits?|stands?|shows?|reads?|stays?|remains?|fits?|"
    r"contains?|has|have|closes?|opens?|hangs?|rests?)\b",
    re.IGNORECASE,
)


def victory_is_observable(text: str) -> bool:
    """A victory line must describe a state a reader can look at and confirm,
    not repeat the instruction as if it were the outcome.
    """
    return bool(text) and bool(STATE_VERB.search(text))


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
        for field in FRICTION_FIELDS:
            if not f.get(field):
                problems.append("%s: friction[%d] missing %r" % (name, i, field))
        cause = f.get("cause")
        if cause and cause not in valid_cause_ids:
            problems.append("%s: friction[%d] cause %r is not a known root cause"
                             % (name, i, cause))
        start_pass = f.get("start_pass")
        if start_pass and start_pass not in VALID_PASSES:
            problems.append("%s: friction[%d] start_pass %r not one of %s"
                             % (name, i, start_pass, sorted(VALID_PASSES)))

    first_15 = diag.get("first_15")
    if not first_15 or not first_15.get("action"):
        problems.append("%s: diagnosis.first_15 missing an action" % name)
    if not first_15 or not first_15.get("victory"):
        problems.append("%s: diagnosis.first_15 missing a victory" % name)
    elif not victory_is_observable(first_15["victory"]):
        problems.append("%s: diagnosis.first_15.victory is not observable "
                         "(no verb of state): %r" % (name, first_15["victory"]))

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
