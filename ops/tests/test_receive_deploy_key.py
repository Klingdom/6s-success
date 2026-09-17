#!/usr/bin/env python3
"""
Prove ops/receive_deploy_key.py's dedupe() and existing() are correct, and
that existing() cannot mistake "gh api failed" for "no keys installed yet".

This file installs real read-only SSH deploy keys onto the live GitHub
repository and had no test file at all. Found 2026-09-17, reading the file
cold. existing() parsed `gh api repos/.../keys` stdout without checking
`proc.returncode`; a broken `gh` auth or a network failure returns an empty,
non-erroring-looking stdout, which existing() would have read as "the repo
has zero deploy keys" rather than "unknown". Under --install that reads every
mailbox key as new even if it is already installed. Fixed to raise on a
non-zero returncode instead of silently returning an empty set, and main()
now reports UNCHECKED and refuses to proceed rather than acting on a guess.

Run:  python ops/tests/test_receive_deploy_key.py
"""
import os
import sys
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import receive_deploy_key as rdk                                  # noqa: E402


def _completed(returncode=0, stdout="", stderr=""):
    class _R:
        pass
    r = _R()
    r.returncode = returncode
    r.stdout = stdout
    r.stderr = stderr
    return r


def main() -> int:
    fails = []

    # 1. dedupe() keeps the first sighting of a given key material and drops
    #    later duplicates, whatever subject/sender they arrived under.
    key_a = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI0000000000000000000000000000000000000 vps"
    key_a_again = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI0000000000000000000000000000000000000 vps-resend"
    key_b = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI1111111111111111111111111111111111111 vps2"
    found = [("s1", "f1", key_a), ("s2", "f2", key_a_again), ("s3", "f3", key_b)]
    unique = rdk.dedupe(found)
    if [u[2] for u in unique] != [key_a, key_b]:
        fails.append("dedupe() did not keep first sighting and drop the "
                      "repeated key material: got %r" % ([u[2] for u in unique],))

    # 2. dedupe() with no duplicates returns everything, order preserved.
    found2 = [("s1", "f1", key_a), ("s2", "f2", key_b)]
    if len(rdk.dedupe(found2)) != 2:
        fails.append("dedupe() dropped a key that was not actually a duplicate")

    # 3. existing(): a clean gh api call returns the key material set.
    ok_stdout = (
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI0000000000000000000000000000000000000 old\n"
        "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC22222222222222222222222 other\n"
    )
    with mock.patch.object(rdk.subprocess, "run",
                           return_value=_completed(0, ok_stdout, "")):
        have = rdk.existing()
    expect = {"AAAAC3NzaC1lZDI1NTE5AAAAI0000000000000000000000000000000000000",
              "AAAAB3NzaC1yc2EAAAADAQABAAABgQC22222222222222222222222"}
    if have != expect:
        fails.append("existing() did not parse a clean gh api response "
                      "correctly: got %r" % (have,))

    # 4. existing(): the real regression. gh api fails (bad auth, no
    #    network) with empty stdout and a non-zero returncode. This must
    #    raise, never silently read as "zero keys installed".
    with mock.patch.object(rdk.subprocess, "run",
                           return_value=_completed(1, "", "gh: authentication required")):
        try:
            rdk.existing()
            fails.append("existing() returned normally on a failed gh api "
                          "call instead of raising; a broken auth would "
                          "have read as 'no keys installed yet'")
        except RuntimeError as exc:
            if "authentication required" not in str(exc):
                fails.append("existing()'s error did not carry the real "
                              "gh stderr: %r" % (str(exc),))

    # 5. existing(): a failure with genuinely empty stderr still raises,
    #    naming the returncode rather than producing a blank, useless error.
    with mock.patch.object(rdk.subprocess, "run",
                           return_value=_completed(2, "", "")):
        try:
            rdk.existing()
            fails.append("existing() did not raise on returncode=2 with "
                          "empty stderr")
        except RuntimeError as exc:
            if "2" not in str(exc):
                fails.append("existing()'s error did not name the exit "
                              "code when stderr was empty: %r" % (str(exc),))

    # 6. main() must not report a check as "not yet installed" or attempt
    #    an install when existing() cannot be trusted; it must say UNCHECKED
    #    and stop.
    with mock.patch.object(rdk, "harvest", return_value=[("s", "f", key_a)]), \
         mock.patch.object(rdk, "existing",
                            side_effect=RuntimeError("could not read the repo's "
                                                      "existing deploy keys: boom")):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = rdk.main("--check")
        out = buf.getvalue()
    if rc == 0:
        fails.append("main() returned success while the existing-keys check "
                      "was unchecked")
    if "UNCHECKED" not in out:
        fails.append("main() did not report UNCHECKED when existing() failed: "
                      "%r" % out)
    if "not yet installed" in out:
        fails.append("main() claimed a key state it could not have known "
                      "while existing() was failing")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: dedupe(), existing() success/failure, main() UNCHECKED "
          "refusal all correct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
