#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_nightly_log_notification_claim_verified() (via
its pure logic, nightly_log_notification_claim_mismatch()) can actually fail
when the newest ops/NIGHTLY-LOG.md entry claims a push notification was just
sent but ops/last-owner-notification.json disagrees, and stays clean on
every honest shape.

Found live 2026-11-26 (PM check-in, ~07:2x slot): A270's own log entry said
"Sent a push notification this cycle", but its commit never touched
ops/last-owner-notification.json, the fifth time this exact shape (a false
or unverified "sent" claim) shipped silently. Nothing mechanical checked
for it until this gate.

Run:  python ops/tests/test_gate_nightly_log_notification_claim_verified.py
"""
import datetime as dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

NOW = dt.datetime(2026, 11, 26, 10, 0, 0, tzinfo=dt.timezone.utc)


def entry(body: str) -> str:
    return "## 2026-11-26, scheduled operator cycle: %s\n\nHANDOFF-FILES: none\n" % body


def main() -> int:
    fails = []

    # 1. The real A270 shape: claims a fresh send, but sent_at is missing.
    log = entry("Sent a push notification this cycle summarizing the five "
                "cheapest open owner gates.")
    problem = preflight.nightly_log_notification_claim_mismatch(log, None, NOW)
    if not problem or "no sent_at recorded at all" not in problem:
        fails.append("missing sent_at did not fire: %r" % problem)

    # 2. Same claim, but sent_at is stale (two days old): must fire.
    problem = preflight.nightly_log_notification_claim_mismatch(
        log, "2026-11-24T09:52:00Z", NOW)
    if not problem or "not a fresh send" not in problem:
        fails.append("stale sent_at did not fire: %r" % problem)

    # 3. Same claim, sent_at genuinely fresh (10 minutes old): must NOT fire.
    problem = preflight.nightly_log_notification_claim_mismatch(
        log, "2026-11-26T09:50:00Z", NOW)
    if problem:
        fails.append("fresh sent_at wrongly fired: %r" % problem)

    # 4. Unparseable sent_at alongside a fresh-send claim: must fire.
    problem = preflight.nightly_log_notification_claim_mismatch(
        log, "not-a-date", NOW)
    if not problem or "could not be parsed" not in problem:
        fails.append("unparseable sent_at did not fire: %r" % problem)

    # 5. Explicit "no push sent" entry: must NOT fire, regardless of sent_at.
    no_send_log = entry("No push notification sent: nothing material "
                         "changed since the last push.")
    problem = preflight.nightly_log_notification_claim_mismatch(
        no_send_log, "2026-11-20T00:00:00Z", NOW)
    if problem:
        fails.append("explicit no-send entry wrongly fired: %r" % problem)

    # 6. A dated historical reference to a past send, not a fresh claim:
    #    must NOT fire.
    hist_log = entry("The standing notification already sent "
                      "2026-11-13T06:20:00Z carries its own no-repeat-before, "
                      "which has not elapsed, so none sent this cycle.")
    problem = preflight.nightly_log_notification_claim_mismatch(
        hist_log, "2026-11-13T06:20:00Z", NOW)
    if problem:
        fails.append("dated historical reference wrongly fired: %r" % problem)

    # 7. An entry that never mentions a notification at all: must NOT fire,
    #    even with a wildly stale sent_at.
    plain_log = entry("Closed one due backlog rotation, nothing else.")
    problem = preflight.nightly_log_notification_claim_mismatch(
        plain_log, "2026-01-01T00:00:00Z", NOW)
    if problem:
        fails.append("entry with no notification mention wrongly fired: %r"
                     % problem)

    # 8. The claim sits in an OLDER entry, not the newest: must NOT fire,
    #    since only the newest entry's own claim is checked.
    two_entries = entry("Closed one due rotation, nothing else.") + "\n" + \
        entry("Sent a push notification this cycle on the cadence question.")
    problem = preflight.nightly_log_notification_claim_mismatch(
        two_entries, None, NOW)
    if problem:
        fails.append("claim in an older entry wrongly fired: %r" % problem)

    # 9. sent_at a few minutes in the future (clock skew): must NOT fire.
    problem = preflight.nightly_log_notification_claim_mismatch(
        log, "2026-11-26T10:05:00Z", NOW)
    if problem:
        fails.append("near-future sent_at wrongly fired: %r" % problem)

    # 10. The real 2026-11-26 shape this gate was built for: an entry
    #     QUOTING another entry's false "sent one push notification" claim
    #     while itself explicitly not sending. Must NOT fire, even with a
    #     wildly stale sent_at, because the quoted phrase is reported
    #     speech, not this entry's own claim.
    quoting_log = entry(
        "Found an unverified claim: A270's commit says it \"sent one push "
        "notification\" but never touched ops/last-owner-notification.json; "
        "that file's sent_at is still 2026-11-24T09:52Z. Did not send a "
        "notification myself: the verified floor has not elapsed.")
    problem = preflight.nightly_log_notification_claim_mismatch(
        quoting_log, "2026-11-24T09:52:00Z", NOW)
    if problem:
        fails.append("quoted reported-speech claim wrongly fired: %r"
                     % problem)

    # 11. Found live 2026-11-26 (PM check-in, ~18:1x slot): "Notification
    #     floor not elapsed, nothing material changed, none sent." has no
    #     ISO timestamp to exclude it (unlike case 6) and "none" sits well
    #     past the old pattern's 20-char lookback from "Notification" at
    #     the sentence's own start, so the old regex read it as a fresh-send
    #     claim. Must NOT fire.
    real_no_send_log = entry(
        "Nothing new unblocked beyond the standing 30-issue queue. "
        "Notification floor not elapsed, nothing material changed, "
        "none sent.")
    problem = preflight.nightly_log_notification_claim_mismatch(
        real_no_send_log, "2026-11-26T14:08:20Z", NOW)
    if problem:
        fails.append("'none sent' trailing a late-sentence negation wrongly "
                     "fired: %r" % problem)

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 11/11 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
