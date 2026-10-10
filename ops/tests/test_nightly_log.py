#!/usr/bin/env python3
"""
Prove ops/nightly_log.py's prepend_entry() always lands a new entry directly
below the file's three-line header, ahead of every existing entry, the exact
place gate_nightly_log_ordering() requires and the exact place every prior
hand-edit mistake (2026-09-05, 2026-09-18, 2026-09-29, 2026-10-03, 2026-10-10)
missed by writing at the physical end of the file instead.

Run:  python ops/tests/test_nightly_log.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import nightly_log                                             # noqa: E402
import preflight                                                # noqa: E402

HEADER = "# Nightly log\n\nOne entry per unattended pass, newest first. Written to be read half awake.\n"
EXISTING = "## 2026-10-09, scheduled operator cycle (older)\n\n**Did:** older work.\n\nPushed to main.\n"


def _write(tmp, text):
    path = os.path.join(tmp, "NIGHTLY-LOG.md")
    io.open(path, "w", encoding="utf-8").write(text)
    return path


def main() -> int:
    fails = []

    with tempfile.TemporaryDirectory() as tmp:
        # 1. Prepending to a file with one existing entry puts the new
        #    entry first, ahead of the existing one, both intact.
        path = _write(tmp, HEADER + "\n" + EXISTING)
        new_text = nightly_log.prepend_entry(
            path, "2026-10-10, PM check-in (test)", "**Did:** new work.")
        new_pos = new_text.find("## 2026-10-10, PM check-in (test)")
        old_pos = new_text.find("## 2026-10-09, scheduled operator cycle (older)")
        if new_pos == -1 or old_pos == -1 or new_pos > old_pos:
            fails.append("new entry did not land ahead of the existing one: %r"
                          % (new_text[:300],))
        if "**Did:** older work." not in new_text:
            fails.append("existing entry body lost during prepend")

        # 2. A leading '## ' in --title is stripped, not doubled.
        new_text2 = nightly_log.prepend_entry(
            path, "## 2026-10-10, already-hashed title", "**Did:** x.")
        if "## ## " in new_text2:
            fails.append("leading '## ' in title was doubled")

        # 3. Prepending twice, in order, leaves both newest-first: the
        #    second call's entry must land above the first call's.
        step1 = nightly_log.prepend_entry(path, "A: first call", "**Did:** a.")
        _write(tmp, step1)
        step2 = nightly_log.prepend_entry(path, "B: second call", "**Did:** b.")
        pos_b = step2.find("## B: second call")
        pos_a = step2.find("## A: first call")
        if pos_b == -1 or pos_a == -1 or pos_b > pos_a:
            fails.append("second prepend did not land above the first: %r"
                          % (step2[:400],))

        # 4. A malformed header (not matching the real file's three-line
        #    shape) must refuse rather than guess where to insert.
        bad = "# Something else\n\nnot the real header\n\n" + EXISTING
        path_bad = _write(tmp, bad)
        try:
            nightly_log.prepend_entry(path_bad, "T", "B")
            fails.append("malformed header was silently accepted")
        except ValueError:
            pass

    # 5. Using the tool on a copy of the REAL committed file must satisfy
    #    the real gate it exists to stop violating.
    with tempfile.TemporaryDirectory() as tmp2:
        real_text = io.open(nightly_log.LOG_PATH, encoding="utf-8").read()
        copy_path = _write(tmp2, real_text)
        result = nightly_log.prepend_entry(
            copy_path, "2026-10-10, test entry (not a real cycle)",
            "**Did:** exercised the tool against a copy of the real file.")
        io.open(copy_path, "w", encoding="utf-8").write(result)
        ops_dir = os.path.join(tmp2, "ops")
        os.makedirs(ops_dir, exist_ok=True)
        os.rename(copy_path, os.path.join(ops_dir, "NIGHTLY-LOG.md"))
        old_root = preflight.ROOT
        preflight.ROOT = tmp2
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_nightly_log_ordering()
            if preflight.FAIL:
                fails.append("tool's own output failed the real gate: %r"
                              % (preflight.FAIL,))
        finally:
            preflight.ROOT = old_root

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: ops/nightly_log.py, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
