#!/usr/bin/env python3
"""Fast, Chromium-free check that ops/NIGHTLY-LOG.md is well formed.

Found 2026-10-20: a cycle appended its entry (and two more after it) to the
tail of this file instead of prepending to the top, exactly the shape
``gate_nightly_log_ordering`` in ``ops/preflight.py`` already exists to catch
(itself written after the identical defect on 2026-09-05, then widened
2026-10-15). CI caught it on push, correctly, but every cloud-sandbox cycle
between the broken push and the next CI read reported a clean local
preflight, because this sandbox's own ``gate_tests`` hangs on a headless
Chromium check and every gate after it, including this one, never runs
locally: ``preflight.py`` never gets far enough to say so. A control nobody
reaches before pushing is not a control.

This script calls the same three cheap, pure-file-parsing gates directly,
skipping every gate that needs a browser, a network call or a Stripe key, so
it finishes in under a second and can run on every push regardless of what
else in this sandbox is unavailable.

Run directly: ``python3 ops/check_nightly_log_fast.py``
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight  # noqa: E402


def main() -> int:
    preflight.FAIL.clear()
    preflight.WARN.clear()
    for gate in (
        preflight.gate_nightly_log_not_oversized,
        preflight.gate_nightly_log_ordering,
        preflight.gate_nightly_log_no_duplicate_entries,
    ):
        try:
            gate()
        except Exception as exc:  # pragma: no cover - defensive, see run_gate
            preflight.fail(gate.__name__, "gate raised %r" % (exc,))

    # Found 2026-10-22: a script that crashed mid-rewrite left this file at
    # zero bytes, and all three gates above passed it, because an empty log
    # has nothing out of order, nothing duplicated and nothing oversized. A
    # log with no entries is not well formed; it is a lost log.
    log = os.path.join(ROOT, "ops", "NIGHTLY-LOG.md")
    try:
        text = open(log, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        text = ""
        preflight.fail("nightly-log-present", "could not read %s: %s"
                       % (log, exc))
    if text and not any(line.startswith("## 20")
                        for line in text.splitlines()):
        preflight.fail("nightly-log-present", "ops/NIGHTLY-LOG.md has no "
                       "dated '## 20..' entries at all; it was emptied or "
                       "overwritten. Restore it from git.")
    elif not text:
        preflight.fail("nightly-log-present", "ops/NIGHTLY-LOG.md is empty "
                       "or missing. Restore it from git.")
    for name, msg in preflight.WARN:
        print(f"  warn {name}: {msg}", file=sys.stderr)

    if preflight.FAIL:
        print("check_nightly_log_fast: FAIL", file=sys.stderr)
        for name, msg in preflight.FAIL:
            print(f"  {name}: {msg}", file=sys.stderr)
        return 1

    print("check_nightly_log_fast: ops/NIGHTLY-LOG.md is well formed "
          "(size, ordering, no duplicate entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
