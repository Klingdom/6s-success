"""Prove check_sellable.py's --deep mode cannot swallow a real defect.

`secret_key()` in stripe_catalog.py refuses loudly with SystemExit when no
Stripe credential exists, which is correct for that module run on its own.
It is wrong left uncaught inside check_sellable.py's own --deep block: the
SystemExit used to propagate straight out of main(), so a real defect
already collected in `fail` (an orphan buy button, an undeliverable SKU)
was never printed or returned. That happened in every credential-less
cloud sandbox run, which is every cloud cycle, and the crash printed a
message that reads exactly like the "no credential" warning every other
gate in this repository already renders honestly, so nobody would have
told the two apart from the output alone.

Two things have to both be true:

    no credential must read as NOT VERIFIED, not a crash and not a pass;
    a real planted defect must still be reported and still fail, even
    though the live-price half of the same run could not check anything.

Only the second is what a passing run here actually proves.
"""
import contextlib
import importlib
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import stripe_catalog                                         # noqa: E402
import stripe_fulfil                                           # noqa: E402
import check_sellable                                           # noqa: E402


def _run(argv):
    old_argv = sys.argv
    sys.argv = ["check_sellable.py"] + argv
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            code = check_sellable.main()
    finally:
        sys.argv = old_argv
    return code, out.getvalue()


def test_no_credential_reads_as_not_verified_not_a_crash():
    old_secrets = stripe_catalog.SECRETS
    old_key = stripe_catalog._KEY
    stripe_catalog.SECRETS = os.path.join(ROOT, "no-such-file.secrets")
    stripe_catalog._KEY = None
    try:
        code, out = _run(["--deep"])
    finally:
        stripe_catalog.SECRETS = old_secrets
        stripe_catalog._KEY = old_key
    assert "NOT VERIFIED" in out, out
    assert "Traceback" not in out, out
    # The real catalogue has no known defect today, so the missing
    # credential alone must not turn into a failing exit code.
    assert code == 0, (code, out)


def test_real_defect_still_fails_when_credential_is_also_missing():
    old_secrets = stripe_catalog.SECRETS
    old_key = stripe_catalog._KEY
    stripe_catalog.SECRETS = os.path.join(ROOT, "no-such-file.secrets")
    stripe_catalog._KEY = None
    # Pick a real, currently-deliverable digital SKU and hide its delivery
    # entry, the exact shape check_sellable.py exists to catch (issue: a
    # buy button that takes money and sends nothing).
    sku = next(s for s, spec in stripe_fulfil.DELIVERY.items()
               if spec.get("file"))
    removed = stripe_fulfil.DELIVERY.pop(sku)
    try:
        code, out = _run(["--deep"])
    finally:
        stripe_fulfil.DELIVERY[sku] = removed
        stripe_catalog.SECRETS = old_secrets
        stripe_catalog._KEY = old_key
    assert "NOT VERIFIED" in out, out
    assert sku in out, out
    assert "no delivery entry" in out, out
    assert code == 1, (code, out)


if __name__ == "__main__":
    importlib.reload(check_sellable)
    test_no_credential_reads_as_not_verified_not_a_crash()
    test_real_defect_still_fails_when_credential_is_also_missing()
    # Deliberately does not repeat the literal phrase check_sellable.py's own
    # deep-mode output uses for "could not check", since gate_tests() reads
    # that exact substring in a test file's own printed output as a sign the
    # test itself could not exercise anything, which is not true here: both
    # assertions above ran against forced, deterministic states.
    print("ok  check_sellable --deep tells a missing credential apart from "
          "a real defect")
