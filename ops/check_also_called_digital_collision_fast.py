#!/usr/bin/env python3
"""Fast, Chromium-free check that no room/zone also-called name collides
with a digital-context query.

Found 2026-11-03: `zone_also_called_html()`'s heading is matched as a
page-unscoped bag of words (see `check_also_called_no_digital_collision()`'s
own docstring in ops/preflight.py), so a name added to fix one gap query can
silently flip an unrelated query anywhere in the corpus if they share a
word. This session added "grilling station" to fix a real coverage gap,
shared the word "station" with the unrelated digital-context query "desktop
charging station organizer," and shipped it: every local preflight run that
cycle used `--skip-tests` to route around this sandbox's documented
Chromium hang, and `gate_also_called_no_digital_collision` lives inside
that skipped suite, not the fast gate path. `publish-image.yml` caught it
correctly, but only after the push, the same "a control nobody reaches
before pushing is not a control" shape `check_nightly_log_fast.py` and
`check_risks_evidence_fast.py` already exist to close for their own gates.

This script calls the same gate directly, skipping `gate_tests` and
everything it blocks, so it finishes in under a second regardless of what
else in this sandbox is unavailable.

Run directly: ``python3 ops/check_also_called_digital_collision_fast.py``
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
        preflight.gate_also_called_no_digital_collision()
    except Exception as exc:  # pragma: no cover - defensive, see run_gate
        preflight.fail("also-called-no-digital-collision", "gate raised %r" % (exc,))

    if preflight.FAIL:
        print("check_also_called_digital_collision_fast: FAIL", file=sys.stderr)
        for name, msg in preflight.FAIL:
            print(f"  {name}: {msg}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Rename the colliding also-called entry (the '<word> zone' "
              "A-series pattern isolates one content word without reusing "
              "one live in an unrelated digital-context query), then push.",
              file=sys.stderr)
        return 1

    print("check_also_called_digital_collision_fast: no also-called name "
          "collides with a digital-context query")
    return 0


if __name__ == "__main__":
    sys.exit(main())
