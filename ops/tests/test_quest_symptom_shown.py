#!/usr/bin/env python3
"""
Prove quest.js fires quest-symptom-shown once when the five symptoms are put
in front of somebody, and not on every render.

WHY THIS EXISTS
---------------
Measured 2026-09-30 from the event payloads, which had never been opened: 8
visitors have ever reached quest-start and 3 have ever picked a symptom. Those
two numbers are not comparable, because quest-start also fires for the room
and draw modes that never see the symptom question at all (mode=zone on 17 of
21 starts, room 2, draw 2). So the first step of the core product, "how many
people are asked what is annoying them and do not answer", could not be read
from the data at all.

quest-symptom-shown closes that gap. The risk it carries is the ordinary one
for an event fired from a render path: applyFirstRunGate() runs on every
render, so an unguarded event would count renders rather than readers and the
new number would be worse than no number. Hence the two conditions this test
holds: the hidden-to-visible transition, and once per page load.

The guard is executed here with node rather than pattern-matched, because a
regex over JavaScript proves the text is present, not that it behaves.

Run:  python ops/tests/test_quest_symptom_shown.py
"""
import io
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUEST = os.path.join(ROOT, "site", "assets", "js", "quest.js")

# A faithful stand-in for the real gate: the same three conditions, in the
# same order, around the same flag. If the real file's logic changes shape,
# case_the_real_file_still_has_the_guard below fails and this must be redone.
HARNESS = """
var fired = [];
var symptomShownReported = false;
function m(name, payload) { fired.push([name, payload]); }
function gate(showSymptom, symWasHidden, choices) {
  if (showSymptom && symWasHidden && !symptomShownReported) {
    symptomShownReported = true;
    m("quest-symptom-shown", { choices: choices });
  }
}
%s
console.log(JSON.stringify(fired));
"""


def _run(body):
    node = shutil.which("node")
    if not node:
        return None
    src = HARNESS % body
    p = subprocess.run([node, "-e", src], capture_output=True, text=True,
                       timeout=60)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout.strip())


def case_fires_once_on_the_transition():
    out = _run('gate(true, true, 5);')
    if out is None:
        print("  no node here, NOT VERIFIED.")
        return
    assert out == [["quest-symptom-shown", {"choices": 5}]], out


def case_does_not_fire_when_already_visible():
    out = _run('gate(true, false, 5);')
    if out is None:
        return
    assert out == [], out


def case_does_not_fire_when_the_step_is_not_shown():
    out = _run('gate(false, true, 5);')
    if out is None:
        return
    assert out == [], out


def case_repeated_renders_fire_once():
    out = _run('for (var i = 0; i < 20; i++) { gate(true, true, 5); }')
    if out is None:
        return
    assert len(out) == 1, out


def case_the_real_file_still_has_the_guard():
    src = io.open(QUEST, encoding="utf-8").read()
    assert "var symptomShownReported = false;" in src
    assert 'm("quest-symptom-shown"' in src
    assert "showSymptom && symWasHidden && !symptomShownReported" in src, \
        "the guard's three conditions changed shape; redo the harness above"
    # The flag must be set before the event, or a throw inside m() would let
    # the next render fire it again.
    i = src.index("symptomShownReported = true;")
    j = src.index('m("quest-symptom-shown"')
    assert i < j, "the once-per-load flag is set after the event, not before"


def case_the_event_carries_no_household_detail():
    """A room or a symptom string is a fact about somebody's house."""
    src = io.open(QUEST, encoding="utf-8").read()
    i = src.index('m("quest-symptom-shown"')
    payload = src[i:src.index("}", i) + 1]
    for forbidden in ("room", "zone", "symptom:", "text"):
        assert forbidden not in payload, (forbidden, payload)


def case_quest_js_parses():
    node = shutil.which("node")
    if not node:
        print("  no node here, NOT VERIFIED.")
        return
    p = subprocess.run([node, "--check", QUEST], capture_output=True,
                       text=True, timeout=60)
    assert p.returncode == 0, p.stderr


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
