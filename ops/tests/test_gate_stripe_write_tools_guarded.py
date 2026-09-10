#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_stripe_write_tools_guarded() catches a Stripe
tool that can write on --apply without checking STRIPE_ALLOW_LIVE, the exact
shape ops/stripe_links.py shipped with: it could create a real payment link
against a live secret key with no second look at all, unlike every sibling
Stripe write tool. Found and fixed 2026-09-10.

Run:  python ops/tests/test_gate_stripe_write_tools_guarded.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

UNGUARDED = (
    "def main(apply_it):\n"
    "    live = True\n"
    "    print('Mode: LIVE')\n"
    "    if apply_it:\n"
    "        create_a_real_payment_link()\n"
)

GUARDED = (
    "import os\n"
    "def main(apply_it):\n"
    "    live = True\n"
    "    if live and apply_it and os.environ.get('STRIPE_ALLOW_LIVE') != '1':\n"
    "        return 1\n"
)

READ_ONLY = (
    "def main():\n"
    "    print('just checks the live account, never writes')\n"
)

NOT_A_STRIPE_FILE = UNGUARDED   # same shape, wrong filename prefix


def _run(files: dict):
    """files: {filename: source}. Writes them under a fake ops/, points
    preflight.ROOT at the fake tree, runs the gate, restores real ROOT."""
    tmp = tempfile.mkdtemp()
    try:
        ops_dir = os.path.join(tmp, "ops")
        os.makedirs(ops_dir)
        for name, src in files.items():
            io.open(os.path.join(ops_dir, name), "w", encoding="utf-8").write(src)
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_stripe_write_tools_guarded()
            return list(preflight.FAIL)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def test_unguarded_write_tool_fails():
    fails = _run({"stripe_missing.py": UNGUARDED})
    assert fails, "a stripe_*.py with --apply and no STRIPE_ALLOW_LIVE " \
        "check should fail, and did not"
    assert "stripe_missing.py" in fails[0][1], \
        "the failure should name the offending file: %r" % (fails[0],)


def test_guarded_write_tool_passes():
    fails = _run({"stripe_present.py": GUARDED})
    assert not fails, "a stripe_*.py that checks STRIPE_ALLOW_LIVE should " \
        "pass: %r" % (fails,)


def test_read_only_tool_not_flagged():
    fails = _run({"stripe_check.py": READ_ONLY})
    assert not fails, "a stripe_*.py with no apply_it/--apply write path " \
        "should not be scanned: %r" % (fails,)


def test_non_stripe_file_ignored():
    """Only stripe_*.py is in scope; a same-shape helper elsewhere should
    not be scanned, since it is not a tool that can bill a real customer."""
    fails = _run({"build_something.py": NOT_A_STRIPE_FILE})
    assert not fails, "a non stripe_*.py file should never be scanned: " \
        "%r" % (fails,)


def test_stripe_brand_is_exempt_even_when_unguarded():
    """stripe_brand.py accepts --apply and defines a live-writing upload(),
    but main()'s apply_it branch never calls it (verified by reading the
    real file); the gate's documented exemption must hold even against a
    synthetic file shaped exactly like the unguarded case, since the
    exemption is by filename, not by re-deriving reachability each run."""
    fails = _run({"stripe_brand.py": UNGUARDED})
    assert not fails, "stripe_brand.py should be exempt: %r" % (fails,)


def test_mixed_only_flags_the_offender():
    fails = _run({"stripe_good.py": GUARDED, "stripe_bad.py": UNGUARDED,
                  "stripe_readonly.py": READ_ONLY})
    names = [m for _, m in fails]
    assert len(fails) == 1, "exactly one of the three files is wrong: %r" % (fails,)
    assert "stripe_bad.py" in names[0]
    assert "stripe_good.py" not in names[0]


def test_real_repository_is_clean():
    """The actual fix: run the gate against the real, committed ops/
    directory (not a synthetic fixture) and confirm every Stripe write
    tool now checks STRIPE_ALLOW_LIVE."""
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_stripe_write_tools_guarded()
    fails = list(preflight.FAIL)
    assert not fails, "the real repository should be clean: %r" % (fails,)


TESTS = [test_unguarded_write_tool_fails, test_guarded_write_tool_passes,
         test_read_only_tool_not_flagged, test_non_stripe_file_ignored,
         test_stripe_brand_is_exempt_even_when_unguarded,
         test_mixed_only_flags_the_offender, test_real_repository_is_clean]


def main():
    n = 0
    for t in TESTS:
        t()
        n += 1
    print("  %d of %d cases pass" % (n, len(TESTS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
