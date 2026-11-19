#!/usr/bin/env python3
"""Fast, Chromium-free check that every room-also-called name is a phrase
someone actually typed in the demand harvest.

Found 2026-11-19: ops/room-also-called.json's "names"/"signal_names" are
held to that rule by ops/tests/test_room_also_called.py, but that test
lives inside the slow, full ops/tests/*.py suite (gate_tests), which this
sandbox's documented Chromium hang forces every local preflight run to
skip with --skip-tests. Three names ("childrens bedroom", "groceries",
"stairway landing") lost their grounding the same day keyword-demand.yml
was narrowed to --source google (each one's evidence turned out to be
Bing-only), and no local, reachable check caught it before a push; only
the full CI run did, after the push had already landed
(checks.yml run 44547908641). This script calls the same gate directly,
skipping gate_tests and everything it blocks, so it finishes in under a
second regardless of what else in this sandbox is unavailable.

Run directly: ``python3 ops/check_room_also_called_evidence_fast.py``
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight  # noqa: E402


def main() -> int:
    preflight.FAIL.clear()
    preflight.WARN.clear()
    try:
        preflight.gate_room_also_called_evidence()
    except Exception as exc:  # pragma: no cover - defensive, see run_gate
        preflight.fail("room-also-called-evidence", "gate raised %r" % (exc,))

    if preflight.FAIL:
        print("check_room_also_called_evidence_fast: FAIL", file=sys.stderr)
        for name, msg in preflight.FAIL:
            print(f"  {name}: {msg}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Remove the ungrounded name (or re-earn its evidence), then "
              "push. See ops/room-also-called.json's own inline notes for "
              "the pattern.", file=sys.stderr)
        return 1

    print("check_room_also_called_evidence_fast: every room-also-called "
          "name is evidenced by the demand harvest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
