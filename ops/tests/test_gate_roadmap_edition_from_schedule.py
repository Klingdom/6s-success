#!/usr/bin/env python3
"""
Prove gate_roadmap_edition_from_schedule fires when roadmap-report.yml picks
its edition from the wall clock instead of the cron string that fired it.

Added 2026-09-19. The step used to run `date -u +%H` and match the hour
against the four cron times. Checked against 10 real runs via the Actions
API: the workflow's own header measures a mean 2.86h/max 4.95h queuing
delay, so most runs' wall-clock hour no longer matched the cron that
triggered them. 7 of 10 fell through to the "*" default (always edition 8,
"Morning", full report) and 1 landed on a different cron's exact hour and
was mislabelled as that other edition. Fixed by matching
github.event.schedule, which GitHub records at trigger time and does not
move regardless of how late the runner actually starts.

Run:  python ops/tests/test_gate_roadmap_edition_from_schedule.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402

STEP_HEADER = "      - name: Work out which edition this is\n        id: ed\n"

GOOD = (STEP_HEADER +
        "        env:\n"
        "          EDITION_INPUT: ${{ github.event.inputs.edition }}\n"
        "          SCHEDULE: ${{ github.event.schedule }}\n"
        "        run: |\n"
        "          case \"$SCHEDULE\" in\n"
        "            \"41 14 * * *\") E=8 ;;\n"
        "          esac\n"
        "      - name: Build the report\n")

WALLTIME_ONLY = (STEP_HEADER +
                  "        env:\n"
                  "          EDITION_INPUT: ${{ github.event.inputs.edition }}\n"
                  "        run: |\n"
                  "          H=$(date -u +%H)\n"
                  "          case \"$H\" in\n"
                  "            14) E=8 ;;\n"
                  "          esac\n"
                  "      - name: Build the report\n")

BOTH = (STEP_HEADER +
        "        env:\n"
        "          SCHEDULE: ${{ github.event.schedule }}\n"
        "        run: |\n"
        "          H=$(date -u +%H)\n"
        "          case \"$SCHEDULE\" in\n"
        "            \"41 14 * * *\") E=8 ;;\n"
        "          esac\n"
        "      - name: Build the report\n")

STEP_RENAMED = "      - name: pick edition\n        run: echo hi\n"

CASES = [
    ("correct shape (matches github.event.schedule)", GOOD, False),
    ("real roadmap-report.yml", None, False),
    ("the pre-2026-09-19 shape: wall-clock hour only", WALLTIME_ONLY, True),
    ("schedule read but date -u +%H left alongside it", BOTH, True),
    ("step renamed or removed", STEP_RENAMED, True),
]


def fired(text):
    calls = []
    real = P.fail
    P.fail = lambda *a, **k: calls.append(a)
    try:
        if text is None:
            P.gate_roadmap_edition_from_schedule()
        else:
            d = tempfile.mkdtemp()
            path = os.path.join(d, "roadmap-report.yml")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            P.gate_roadmap_edition_from_schedule(path)
    finally:
        P.fail = real
    return bool(calls)


def main():
    failures = []
    for name, text, should_fire in CASES:
        got = fired(text)
        if got != should_fire:
            failures.append("%s: expected fire=%s, got %s" % (name, should_fire, got))
    for f in failures:
        print("FAIL:", f)
    print("ok, %d cases" % len(CASES) if not failures else "%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
