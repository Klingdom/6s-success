#!/usr/bin/env python3
"""Fast, Chromium-free check that RISKS.md's evidence citations are current.

Found 2026-11-03: RISK-0012's own `forms_dead=NNN` citation went stale the
moment a page-shipping commit landed, at least six separate times in one
day (233 to 234, 234 to 235, 235 to 236, and earlier the same day 232 to
233). `gate_risks_evidence_current` in `ops/preflight.py` already catches
this correctly, and does so leniently (a citation matching the live
working tree passes even when the hourly `ops/state.json` snapshot has not
caught up, since 2026-10-29). The catch always landed in CI, never before
the push, for the exact same reason `check_nightly_log_fast.py` already
documents: this sandbox's own `gate_tests` hangs on a headless Chromium
check and sits before `gate_risks_evidence_current` in `preflight.py`'s own
call order, so nothing after it ever runs here. Each miss meant a full
`checks.yml` and `publish-image.yml` run went red, and because
`publish-image.yml` only re-triggers on a `site/**`/`Dockerfile` push, the
dashboard-only follow-up commit that actually fixed the citation never
re-fired it either: real content (a new room guide, among others) sat
built but unpublished until someone noticed and re-dispatched the workflow
by hand. A control nobody reaches before pushing is not a control.

This script calls the same gate directly, skipping `gate_tests` and
everything it blocks, so it finishes in under a second regardless of what
else in this sandbox is unavailable.

Run directly: ``python3 ops/check_risks_evidence_fast.py``
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
        preflight.gate_risks_evidence_current()
    except Exception as exc:  # pragma: no cover - defensive, see run_gate
        preflight.fail("risks-evidence-current", "gate raised %r" % (exc,))

    if preflight.FAIL:
        print("check_risks_evidence_fast: FAIL", file=sys.stderr)
        for name, msg in preflight.FAIL:
            print(f"  {name}: {msg}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Edit RISKS.md's live evidence line to match (headline-count"
              "-only, no new history line, matching the entry's own "
              "convention), then push.", file=sys.stderr)
        return 1

    print("check_risks_evidence_fast: RISKS.md's evidence citations are "
          "current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
