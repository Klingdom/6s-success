#!/usr/bin/env python3
"""
Prove inbox_agent.classify() always recognises the owner first, found
2026-09-11 cold-reading a genuinely untested money/communication file.

The affiliate-programme check used to run before the owner check and never
looked at who the sender was, only at the words in the message. An email
from Phil's own gmail address that merely mentioned a retailer name next to
a word like "approved" (exactly how he would report an affiliate decision
back to the operator, e.g. "got the Amazon Associates approval, welcome to
the program") was classified as kind="affiliate" instead of kind="owner".

That is backwards from both this file's own docstring ("A reply from Phil
is an instruction from the owner") and CLAUDE.md 0.5 / this run's own step
8, which say an owner message outranks everything else picked that cycle.
It also has a live cost beyond ordering: the owner branch extracts a
uuid/url/pasted-secret from the text (with the secret redacted before it
ever reaches the committed state file); the affiliate branch extracts only
a programme name and verdict, so any answer or credential Phil pasted
alongside the affiliate mention would have been silently dropped, and the
message would have sorted after billing and customer mail
(order.get("affiliate", 9)) instead of first.

Run:  python ops/tests/test_inbox_agent.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import inbox_agent as ia                                          # noqa: E402


def main() -> int:
    fails = []

    # The regression itself: an owner email, from a real owner address, that
    # happens to mention an affiliate brand next to an affiliate verb.
    c = ia.classify(
        "Phil Kling <philkling@gmail.com>", "Re: Amazon Associates",
        "Just got the Amazon Associates approval email, welcome to the "
        "program. Go ahead and wire it up.")
    if c["kind"] != "owner":
        fails.append(f"an email from the owner's own address must classify "
                      f"as owner regardless of topic, got kind={c['kind']!r}")

    # A second shape of the same bug: a network name inside the owner's own
    # signature or a pasted URL, not just a brand word.
    c = ia.classify(
        "Phil Kling <philkling@gmail.com>", "rakuten reply",
        "Saw the rakuten note, looks declined, try Amazon instead. "
        "https://example.com/decision")
    if c["kind"] != "owner":
        fails.append(f"a second owner-mentions-a-network case must still "
                      f"classify as owner, got kind={c['kind']!r}")
    if c.get("extracted", {}).get("url") != "https://example.com/decision":
        fails.append("owner classification must still extract a pasted URL "
                      f"when the topic is affiliate-shaped: {c}")

    # Must not regress the real affiliate path: a genuine network sender with
    # no owner signal at all still classifies as affiliate.
    c = ia.classify(
        "noreply@rakuten.com", "Your application has been approved",
        "Congratulations, welcome to the Rakuten Advertising network.")
    if c["kind"] != "affiliate":
        fails.append(f"a real affiliate-network sender must still classify "
                      f"as affiliate, got kind={c['kind']!r}")

    # Must not regress self-mail: business mail to itself, no owner signal.
    c = ia.classify("6S Success <support@6s-success.com>", "6S hourly brief",
                     "numbers here")
    if c["kind"] != "self":
        fails.append(f"mail this business sent itself must still classify "
                      f"as self, got kind={c['kind']!r}")

    # Must not regress delivery-problem detection for an ordinary customer.
    c = ia.classify("buyer@example.com", "help",
                     "I did not receive my download link")
    if c["kind"] != "delivery-problem":
        fails.append(f"a real delivery problem must still classify as "
                      f"delivery-problem, got kind={c['kind']!r}")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("inbox_agent.classify() owner-priority: 5 case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
