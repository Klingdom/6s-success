#!/usr/bin/env python3
"""
Prove verify_deploy.py's honesty check (#6) can actually fail.

Found 2026-09-07: the check read `"does not send email yet" not in contact`,
a phrase contact.html stopped carrying once its disclaimer was reworded to
"Our mail pipe is not connected yet" (checked directly against the served
page, not assumed). Neither phrase existed anywhere in the repository, so the
check was vacuous: a phrase that is never present is always "not in" the
page, so the check passed no matter what the live page actually said,
including a hypothetical regression that falsely claimed a message was sent.

This never runs against a real deploy in this sandbox (no egress to
6s-success.com), so the only way to exercise the check at all is to stub
verify_deploy.get() and drive main() directly.

Run:  python ops/tests/test_verify_deploy.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import verify_deploy as V                                      # noqa: E402

HONEST = ("<p>Our mail pipe is not connected yet, so this button prepares "
          "your message rather than sending it.</p>")
DISHONEST_SENT = "<p>Your message has been sent. Thanks for writing in.</p>"
NONSENSE_MARKER = "6s-check"


def run(contact_body):
    """Run main() against a fake server, returning the two check verdicts
    this file cares about (false-claim, discloses-unconnected), in order."""
    real_get = V.get
    real_results = list(V.results)
    V.results.clear()

    def fake_get(url, timeout=20):
        if NONSENSE_MARKER in url:
            return 404, ""
        if url.rstrip("/").endswith("/contact"):
            return 200, contact_body
        if url == "https://example.test" or url.endswith("/"):
            return 200, "6S Success home"
        return 200, "ok"

    try:
        V.get = fake_get
        V.main("https://example.test")
        # Checks 10 and 11 (1-indexed in the file's own numbering): the two
        # added/rewritten for the honesty check.
        return V.results[-2], V.results[-1]
    finally:
        V.get = real_get
        V.results.clear()
        V.results.extend(real_results)


def main() -> int:
    fails = []

    false_claim_ok, discloses_ok = run(HONEST)
    if not false_claim_ok:
        fails.append("honest current copy must not trip the false-claim check")
    if not discloses_ok:
        fails.append("honest current copy must satisfy the disclosure check")

    false_claim_ok, discloses_ok = run(DISHONEST_SENT)
    if false_claim_ok:
        fails.append("a page falsely claiming the message was sent must fail "
                      "the false-claim check, not pass it")

    # The exact regression this file exists to close: the old phrase, gone,
    # proves nothing about the live page either way, so the check must not
    # pass on its absence alone. A page carrying neither the honest
    # disclosure nor a false claim (e.g. a stale build with no disclaimer at
    # all) must fail the disclosure check.
    false_claim_ok, discloses_ok = run("<p>Send us a message any time.</p>")
    if discloses_ok:
        fails.append("a page with no disclosure at all must fail the "
                      "disclosure check, not pass by default")

    for f in fails:
        print(f"  FAIL  {f}")
    total = 3
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
