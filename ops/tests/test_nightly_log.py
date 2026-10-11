#!/usr/bin/env python3
"""
Prove ops/nightly_log.py's prepend_entry() always lands a new entry directly
below the file's three-line header, ahead of every existing entry, the exact
place gate_nightly_log_ordering() requires and the exact place every prior
hand-edit mistake (2026-09-05, 2026-09-18, 2026-09-29, 2026-10-03, 2026-10-10)
missed by writing at the physical end of the file instead.

Run:  python ops/tests/test_nightly_log.py
"""
import datetime as dt
import io
import os
import re
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
    #
    #    Found 2026-10-11: this case's injected title used to hardcode a
    #    literal date ("2026-10-10"). That was the newest date in the real
    #    file the day this test was written, but every later cycle moves
    #    the real file's own top entry to a newer date, and a hardcoded
    #    date that is no longer the newest makes gate_nightly_log_ordering()
    #    correctly fail (the injected entry reads as an older entry placed
    #    above newer ones). Derive a date strictly newer than anything
    #    already in the real file instead, so this case stays valid no
    #    matter which day it runs.
    with tempfile.TemporaryDirectory() as tmp2:
        real_text = io.open(nightly_log.LOG_PATH, encoding="utf-8").read()
        real_dates = re.findall(r"(?m)^## (\d{4}-\d{2}-\d{2})", real_text)
        newest_real = max(dt.date.fromisoformat(d) for d in real_dates)
        test_date = (newest_real + dt.timedelta(days=1)).isoformat()
        copy_path = _write(tmp2, real_text)
        result = nightly_log.prepend_entry(
            copy_path, "%s, test entry (not a real cycle)" % test_date,
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

    # 6. main() writes via a temp file + rename, never truncating the real
    #    path directly, so a crash mid-write cannot leave it empty.
    with tempfile.TemporaryDirectory() as tmp3:
        path3 = _write(tmp3, HEADER + "\n" + EXISTING)
        old_argv, old_log_path = sys.argv, nightly_log.LOG_PATH
        sys.argv = ["nightly_log.py", "--title", "C: third call",
                    "--handoff", "none", "--body", "**Did:** c."]
        nightly_log.LOG_PATH = path3
        try:
            rc = nightly_log.main()
        finally:
            sys.argv, nightly_log.LOG_PATH = old_argv, old_log_path
        if rc != 0:
            fails.append("main() returned nonzero on a valid call: %r" % (rc,))
        if os.path.exists(path3 + ".tmp"):
            fails.append("main() left a .tmp file behind after a successful write")
        final_text = io.open(path3, encoding="utf-8").read()
        if "## C: third call" not in final_text or "**Did:** older work." not in final_text:
            fails.append("main()'s written file is missing content: %r"
                          % (final_text[:300],))

    # 7. Proving the crash-safety property itself: if the temp-file write
    #    fails partway (disk full, kill -9), the real path must come out
    #    byte-identical to before, never truncated.
    with tempfile.TemporaryDirectory() as tmp4:
        path4 = _write(tmp4, HEADER + "\n" + EXISTING)
        before = io.open(path4, encoding="utf-8").read()
        old_argv, old_log_path = sys.argv, nightly_log.LOG_PATH
        sys.argv = ["nightly_log.py", "--title", "D: crash",
                    "--handoff", "none", "--body", "**Did:** d."]
        nightly_log.LOG_PATH = path4
        real_open = io.open

        def failing_open(path, *a, **kw):
            mode = a[0] if a else kw.get("mode", "r")
            if path == path4 + ".tmp" and "w" in mode:
                raise OSError("simulated disk full")
            return real_open(path, *a, **kw)

        io.open = failing_open
        try:
            try:
                nightly_log.main()
                fails.append("main() swallowed a write failure instead of raising")
            except OSError:
                pass
        finally:
            io.open = real_open
            sys.argv, nightly_log.LOG_PATH = old_argv, old_log_path
        after = io.open(path4, encoding="utf-8").read()
        if after != before:
            fails.append("real log file changed even though the write failed "
                          "before the rename: %r" % (after[:300],))
        if os.path.exists(path4 + ".tmp"):
            fails.append("a failed write left a .tmp file behind")

    # 8. format_handoff() turns --handoff's raw value into the canonical
    #    marker line cold_read_handoff_stale_files() parses: 'none' (any
    #    case, blank) collapses to a bare 'none'; a comma-separated list
    #    is wrapped in backticks even if the caller already supplied
    #    some, and bare whitespace is trimmed.
    cases = [
        ("none", "HANDOFF-FILES: none"),
        ("None", "HANDOFF-FILES: none"),
        ("  ", "HANDOFF-FILES: none"),
        ("ops/foo.py", "HANDOFF-FILES: `ops/foo.py`"),
        ("ops/foo.py, ops/bar.py",
         "HANDOFF-FILES: `ops/foo.py`, `ops/bar.py`"),
        ("`ops/foo.py`, `ops/bar.py`",
         "HANDOFF-FILES: `ops/foo.py`, `ops/bar.py`"),
    ]
    for raw, expected in cases:
        got = nightly_log.format_handoff(raw)
        if got != expected:
            fails.append("format_handoff(%r) = %r, expected %r"
                          % (raw, got, expected))

    # 9. --handoff is required: main() must refuse (argparse exits
    #    nonzero) rather than silently writing an entry with no handoff
    #    state at all, the gap this flag exists to close.
    with tempfile.TemporaryDirectory() as tmp5:
        path5 = _write(tmp5, HEADER + "\n" + EXISTING)
        old_argv, old_log_path = sys.argv, nightly_log.LOG_PATH
        sys.argv = ["nightly_log.py", "--title", "E: missing handoff",
                    "--body", "**Did:** e."]
        nightly_log.LOG_PATH = path5
        try:
            try:
                nightly_log.main()
                fails.append("main() accepted a call with no --handoff")
            except SystemExit:
                pass
        finally:
            sys.argv, nightly_log.LOG_PATH = old_argv, old_log_path

    # 10. A successful call's written entry carries the HANDOFF-FILES
    #     line main() derives from --handoff, so a fresh preflight run
    #     reading this file sees the same marker the gate expects.
    with tempfile.TemporaryDirectory() as tmp6:
        path6 = _write(tmp6, HEADER + "\n" + EXISTING)
        old_argv, old_log_path = sys.argv, nightly_log.LOG_PATH
        sys.argv = ["nightly_log.py", "--title", "F: real handoff",
                    "--handoff", "ops/foo.py", "--body", "**Did:** f."]
        nightly_log.LOG_PATH = path6
        try:
            nightly_log.main()
        finally:
            sys.argv, nightly_log.LOG_PATH = old_argv, old_log_path
        final6 = io.open(path6, encoding="utf-8").read()
        if "HANDOFF-FILES: `ops/foo.py`" not in final6:
            fails.append("main()'s written entry is missing the derived "
                          "HANDOFF-FILES line: %r" % (final6[:400],))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: ops/nightly_log.py, 10/10 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
