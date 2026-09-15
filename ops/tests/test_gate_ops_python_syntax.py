#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_ops_python_syntax() catches an ops/*.py file
that does not parse on the interpreter actually running it.

Found 2026-09-15: commit e170c110 landed a nested f-string in
ops/build_zone_pages.py, an f-string delimited with single quotes whose own
ternary expression also used single quotes (loading="{'eager' if eager else
'lazy'}"). That parses on Python 3.12+ (PEP 701) but is a hard SyntaxError on
3.11. Nothing had ever asked whether every ops/*.py file parses at all, so
the failure surfaced as three unrelated gate crashes and six unrelated test
failures instead of one plain "syntax error in build_zone_pages.py" line.

Fixed 2026-09-15, the same night: cases 2 and 4 planted that nested-quote
f-string as the broken file, but it parses on 3.12+, so on CI and on any
3.12+ workstation the gate correctly reported nothing and this test failed,
which failed publish-image for every push to main (first seen on 082d0a73).
The gate parses with the interpreter running it, so a fixture must be broken
on every version to prove the gate works everywhere. The nested-quote case
now runs as a version-aware check: flagged on 3.11, and on 3.12+ asserted
NOT flagged, which documents that this gate cannot see 3.11-only breakage
when run on a newer interpreter.

Run:  python ops/tests/test_gate_ops_python_syntax.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD = "def f(eager):\n    loading = 'eager' if eager else 'lazy'\n    return f'<img loading=\"{loading}\">'\n"

# Broken on every Python version: a missing closing parenthesis.
BROKEN_ANY = "def f(eager:\n    return eager\n"

# The exact real regression: a same-quote nested f-string, valid on 3.12+,
# a SyntaxError on the 3.11 this sandbox and (per the incident) at least one
# operator environment actually run.
BROKEN = "def f(eager):\n    return f'<img loading=\"{'eager' if eager else 'lazy'}\">'\n"


def _run(files):
    """files: {filename: source}. Returns preflight.FAIL after running the
    gate against a temp ops/ directory containing exactly these files."""
    tmp = tempfile.mkdtemp()
    ops_dir = os.path.join(tmp, "ops")
    os.makedirs(ops_dir, exist_ok=True)
    for name, src in files.items():
        io.open(os.path.join(ops_dir, name), "w", encoding="utf-8").write(src)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_ops_python_syntax()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A clean file: no failure.
    r = _run({"clean.py": GOOD})
    if r:
        fails.append("clean file wrongly flagged: %r" % (r,))

    # 2. A file that is a syntax error on every version: caught by name.
    r = _run({"broken.py": BROKEN_ANY})
    if not r or "broken.py" not in r[0][1]:
        fails.append("a universally broken file was not caught by name: %r" % (r,))

    # 2b. The real regression, version aware. The gate parses with the running
    #     interpreter: 3.11 must flag the nested-quote f-string, and 3.12+ must
    #     not, because there it is valid Python.
    r = _run({"nested.py": BROKEN})
    if sys.version_info < (3, 12):
        if not r or "nested.py" not in r[0][1]:
            fails.append("nested-quote f-string not caught on 3.11: %r" % (r,))
    elif r:
        fails.append("nested-quote f-string flagged on a 3.12+ interpreter, "
                     "where it is valid: %r" % (r,))

    # 3. A non-.py file with garbage content must be ignored entirely.
    r = _run({"clean.py": GOOD, "notes.txt": "{{{ not python at all"})
    if r:
        fails.append("a non-.py file was wrongly parsed as Python: %r" % (r,))

    # 4. Multiple files, only one broken: the broken one is named, the
    #    clean one does not also produce a spurious failure.
    r = _run({"clean.py": GOOD, "broken.py": BROKEN_ANY})
    if len(r) != 1 or "broken.py" not in r[0][1]:
        fails.append("mixed clean+broken tree did not name exactly the "
                     "broken file: %r" % (r,))

    # 5. The real, committed ops/ tree: clean (this is the actual fix
    #    verification, on the real repository rather than a fixture).
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_ops_python_syntax()
    if preflight.FAIL:
        fails.append("the real committed ops/ tree failed to parse: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS (6 cases, nested-quote case run for Python %d.%d)" % sys.version_info[:2])
    return 0


if __name__ == "__main__":
    sys.exit(main())
