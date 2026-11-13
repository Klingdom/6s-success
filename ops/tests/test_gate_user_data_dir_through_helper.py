"""A headless-Chromium caller must get its --user-data-dir decision from
ops/browser.py's isolated_profile(exe), never build the flag text itself.

Found and fixed 2026-11-13, this operator: eight independent call sites
(ops/browser.py's own probe, six other generator files, and eighteen test
files) each built an explicit "--user-data-dir=" + <some tempdir> by hand,
by copy-paste, and every one of them hung outright on this sandbox's own
Chromium (confirmed directly: 5 clean runs with the flag omitted, 3 straight
hangs the moment it was passed, file:// and http://, fresh directory or
reused). isolated_profile() is now the one place that decides whether a
binary needs the flag at all, so a future call site that goes around it can
reintroduce the identical sandbox-wide hang, the exact shape that cost three
consecutive nightly log entries (A87, A122, A125) before anyone checked the
browser itself rather than the test files it kept failing.
"""
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import preflight as pf                                          # noqa: E402


def main():
    fails = []

    # 1. The real repository, today, must be clean: every remaining
    #    occurrence of the literal flag text is in the short, named
    #    allowlist (ops/browser.py's own helper, the two bespoke
    #    shared-profile test files, and the deliberately untouched Etsy
    #    PDF pipeline plus its mirroring test).
    real_bad = pf.user_data_dir_bypasses_helper(
        os.path.join(os.path.dirname(HERE)))
    if real_bad:
        fails.append("the real repository already has an unguarded "
                     "--user-data-dir outside the allowlist: %r" % real_bad)

    # 2. Plant a fake file that builds the flag by hand, the exact old
    #    pattern, in a throwaway ops/ directory. The gate must name it.
    with tempfile.TemporaryDirectory() as tmp:
        ops_dir = os.path.join(tmp, "ops")
        tests_dir = os.path.join(ops_dir, "tests")
        os.makedirs(tests_dir)
        bad_file = os.path.join(ops_dir, "build_something_new.py")
        io.open(bad_file, "w", encoding="utf-8").write(
            'import subprocess, tempfile\n'
            'def shot(exe):\n'
            '    with tempfile.TemporaryDirectory() as prof:\n'
            '        subprocess.run([exe, "--user-data-dir=" + prof])\n')
        hit = pf.user_data_dir_bypasses_helper(ops_dir)
        want = os.path.relpath(bad_file, tmp)
        if want not in set(hit):
            fails.append("a hand-built --user-data-dir in a fresh file "
                         "must be named by the gate; got %r, wanted %r in "
                         "it" % (hit, want))

        # 3. The same file, fixed to route through isolated_profile()
        #    instead, must go quiet.
        io.open(bad_file, "w", encoding="utf-8").write(
            'import subprocess\n'
            'import browser as B\n'
            'def shot(exe):\n'
            '    flags, cleanup = B.isolated_profile(exe)\n'
            '    try:\n'
            '        subprocess.run([exe] + flags)\n'
            '    finally:\n'
            '        cleanup()\n')
        hit_after = pf.user_data_dir_bypasses_helper(ops_dir)
        if hit_after:
            fails.append("a file routed through isolated_profile() must "
                         "not be flagged; got %r" % hit_after)

        # 4. A single-quoted variant of the same mistake must also be caught
        #    (the real defect used both f-strings and %-formatting, which
        #    can land the flag behind either quote style).
        io.open(bad_file, "w", encoding="utf-8").write(
            "import subprocess\n"
            "def shot(exe, prof):\n"
            "    subprocess.run([exe, '--user-data-dir=%s' % prof])\n")
        hit_single = pf.user_data_dir_bypasses_helper(ops_dir)
        if want not in set(hit_single):
            fails.append("a single-quoted hand-built --user-data-dir must "
                         "also be named; got %r" % hit_single)

        # 5. A file in the real allowlist (by its real relative path) must
        #    stay silent even though it carries the literal text, proving
        #    the allowlist is checked by path, not absence of the string.
        os.remove(bad_file)
        browser_py = os.path.join(ops_dir, "browser.py")
        io.open(browser_py, "w", encoding="utf-8").write(
            'FLAG = "--user-data-dir=" + "x"\n')
        hit_allowlisted = pf.user_data_dir_bypasses_helper(ops_dir)
        if hit_allowlisted:
            fails.append("ops/browser.py itself must stay exempt even "
                         "though it legitimately names the flag; got %r"
                         % hit_allowlisted)

    if fails:
        for f in fails:
            print("  FAIL " + f)
        return 1
    print("  OK: a hand-built --user-data-dir is named by path, a fix "
          "through isolated_profile() goes quiet, both quoting styles are "
          "caught, and the real allowlist holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
