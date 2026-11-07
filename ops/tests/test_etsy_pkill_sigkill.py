#!/usr/bin/env python3
"""
Prove gate_etsy_pdfs_current()'s self-heal Chrome sweep uses SIGKILL, not
pkill's own default SIGTERM.

Found live 2026-11-07, scheduled operator cycle: killed a real orchestrating
preflight.py the routine way an operator ends a stalled run (SIGKILL by
pid), while it held a build_etsy_assets.py child that had already launched
a real Chrome render. Confirmed directly (ps -eo pid,ppid,pgid) that the
whole functional Chrome tree -- the browser process plus its zygote,
gpu-process, utility and renderer children -- shares ONE process group
distinct from build_etsy_assets.py's own, exactly as gate_etsy_pdfs_current's
own docstring already describes ("Chrome runs one session further down").
_reap_lock_children() only ever kills the ONE pgid _run_bounded registered
(build_etsy_assets.py's), so this sweep's `pkill -f <tmp_marker>` is the
only code path that can reach Chrome at all.

A single live trial of the pre-fix SIGTERM-based sweep happened to clean up
the tree, so this is not a reproduction of a sweep that never works; it is a
hardening against the documented reason everywhere else in this file kills a
Chrome tree with SIGKILL specifically (crashpad and a wedged renderer can
both survive a plain SIGTERM/kill), matching house doctrine rather than
leaving the one Chrome-cleanup path on the weaker signal. A render this
sweep tears down is always already-stale and gets restored by
_restore_etsy_all right after, so there is no correctness cost to killing
it harder.

This is a static source check, not a live Chrome spawn: fast, deterministic,
and does not depend on this sandbox shipping a Chromium binary at all.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREFLIGHT = os.path.join(ROOT, "ops", "preflight.py")


def _gate_source() -> str:
    src = open(PREFLIGHT, encoding="utf-8").read()
    m = re.search(r"def gate_etsy_pdfs_current\(\).*?(?=\ndef [a-zA-Z_]+\()",
                  src, re.S)
    assert m, "gate_etsy_pdfs_current() not found in ops/preflight.py"
    return m.group(0)


def _pkill_calls(src: str) -> "list[list[str]]":
    """Every `subprocess.run(["pkill", ...` argument list in `src`, split
    on commas rather than parsed as a Python literal: the list's last
    element is the bare identifier `tmp_marker`, not a string constant,
    which ast.literal_eval() cannot evaluate."""
    calls = []
    for m in re.finditer(r'subprocess\.run\(\[([^\]]*"pkill"[^\]]*)\]', src):
        parts = [p.strip() for p in m.group(1).split(",")]
        calls.append([p.strip('"') if p.startswith('"') else p
                      for p in parts])
    return calls


def test_both_etsy_pkill_sweeps_use_sigkill():
    src = _gate_source()
    calls = _pkill_calls(src)
    assert len(calls) == 2, (
        f"expected 2 pkill sweeps in gate_etsy_pdfs_current (the pre-run "
        f"sweep and the post-TimeoutExpired sweep), found {len(calls)}: "
        f"{calls}. If a sweep was added, removed or merged, update this "
        f"test's expected count rather than silently losing coverage.")
    for call in calls:
        assert "pkill" in call
        assert "-9" in call, (
            f"pkill sweep {call} does not pass -9 (SIGKILL); it would fall "
            f"back to pkill's own default SIGTERM, which this file's own "
            f"doctrine elsewhere (os.killpg(..., signal.SIGKILL) in "
            f"_run_bounded and in build_etsy_assets.py's render()) treats "
            f"as too weak for a Chrome tree: a crashpad handler or a wedged "
            f"renderer can survive it.")
        # -9 must be a real pkill flag here, not swallowed into the
        # tmp_marker path argument by a future refactor.
        assert call.index("-9") < call.index("--"), (
            f"pkill sweep {call}: -9 must appear before the '--' that ends "
            f"flag parsing, or it is not actually read as a signal flag")


def main() -> int:
    test_both_etsy_pkill_sweeps_use_sigkill()
    print("OK: 1/1 case, both pkill sweeps in gate_etsy_pdfs_current use SIGKILL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
