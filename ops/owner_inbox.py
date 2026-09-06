"""Is the owner waiting on us right now?

Written 2026-09-01, after Phil said he had seen nothing in five days and was
disappointed. The inbox showed why: four messages from him, unread, going back
to 27 August. Among them "fix stripe issues immediately", "you can do all this,
investigate and try everything before you come to me", and "nope, you do it
all". Each one was an instruction. None of them reached a cycle, while hundreds
of commits landed on work he had not asked for.

An autonomous system is supposed to let the owner manage by exception. An
exception he raises that nothing ever reads is not a system, it is a monologue.

Read only. It never marks anything read, because marking a message read is a
claim that it was acted on, and that claim belongs to the cycle that acted.

    python ops/owner_inbox.py
"""
from __future__ import annotations

import email
import imaplib
import io
import os
import re
import sys
from email.header import decode_header

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")


def _env() -> dict:
    env = {}
    if os.path.exists(SECRETS):
        s = io.open(SECRETS, encoding="utf-8", errors="replace").read()
        env = {k: v.strip() for k, v in re.findall(r"^([A-Z_]+)=(.*)$", s, re.M)}
    for k in ("IMAP_HOST", "IMAP_PORT", "IMAP_USER", "IMAP_PASS", "OWNER_EMAIL"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def unread_from_owner():
    """Subjects of unread messages from the owner.

    Returns None when there is no credential to look with, which is different
    from an empty list and must never be reported as "nothing waiting".
    """
    env = _env()
    need = ("IMAP_HOST", "IMAP_PORT", "IMAP_USER", "IMAP_PASS", "OWNER_EMAIL")
    if any(not env.get(k) for k in need):
        return None

    M = imaplib.IMAP4_SSL(env["IMAP_HOST"], int(env["IMAP_PORT"]))
    try:
        M.login(env["IMAP_USER"], env["IMAP_PASS"])
        M.select("INBOX")
        typ, data = M.search(None, "UNSEEN", "FROM", env["OWNER_EMAIL"])
        out = []
        for i in (data[0].split() if data and data[0] else []):
            # BODY.PEEK leaves the message unread. A plain FETCH would mark it
            # read, and this function has no business claiming anything was
            # handled.
            typ, d = M.fetch(i, "(BODY.PEEK[HEADER.FIELDS (SUBJECT DATE)])")
            if not d or not d[0]:
                continue
            msg = email.message_from_bytes(d[0][1])
            subj = decode_header(msg.get("Subject", ""))[0][0]
            if isinstance(subj, bytes):
                subj = subj.decode("utf-8", "replace")
            out.append("%s | %s" % (msg.get("Date", "")[:22], subj))
        return out
    finally:
        try:
            M.logout()
        except Exception:                                       # noqa: BLE001
            pass


def unread_needing_action():
    """Unread mail from third parties that plausibly needs a decision.

    unread_from_owner() searches FROM the owner only, so everything else in the
    mailbox is invisible to it, and "nothing unread from the owner" reads to
    every later run as "nothing to do".

    That cost eight days on 2026-09-06. Impact declined the 6S Success partner
    account on 29 August and the mail sat unread the whole time, while
    ops/affiliate-accounts.json said the application was pending OUR
    verification click and OWNER-ACTIONS.md asked Phil to go and make it. An
    earlier pass had even recorded the subject line, "Application Update", and
    treated it as something waiting on us, because it read the subject and never
    opened the message. Five programmes route through Impact and all five were
    shut, not pending.

    Deliberately keyword-driven and narrow: affiliate networks, payment,
    domain, and anything a person wrote by hand. A digest that lists everything
    is a digest nobody reads, which is the failure this is here to fix.

    Returns None when there is no credential, which is different from an empty
    list and must never be reported as nothing waiting. Uses BODY.PEEK: reading
    a message here is not the same as acting on it, and marking it read would
    claim otherwise.
    """
    env = _env()
    need = ("IMAP_HOST", "IMAP_PORT", "IMAP_USER", "IMAP_PASS")
    if any(not env.get(k) for k in need):
        return None
    interesting = re.compile(
        r"impact|commission\s*junction|cj\.com|rakuten|awin|shareasale|"
        r"amazon\s*associates|affiliate|partner|application|declin|approv|"
        r"stripe|dispute|chargeback|refund|payout|domain|registrar|invoice|"
        r"order|refus|suspend|violat", re.I)
    M = imaplib.IMAP4_SSL(env["IMAP_HOST"], int(env["IMAP_PORT"]))
    try:
        M.login(env["IMAP_USER"], env["IMAP_PASS"])
        M.select("INBOX")
        typ, data = M.search(None, "UNSEEN")
        out = []
        for i in (data[0].split() if data and data[0] else []):
            typ, d = M.fetch(i, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])")
            if not d or not d[0]:
                continue
            msg = email.message_from_bytes(d[0][1])
            def h(k):
                v = decode_header(msg.get(k, ""))[0][0]
                return v.decode("utf-8", "replace") if isinstance(v, bytes) else (v or "")
            frm, subj = h("From"), h("Subject")
            # Our own delivery receipts are not somebody asking us for anything.
            if "support@6s-success.com" in frm.lower() and "your copy of" in subj.lower():
                continue
            if interesting.search(frm + " " + subj):
                out.append("%s | %s | %s" % (msg.get("Date", "")[:22], frm[:40], subj))
        return out
    finally:
        try:
            M.logout()
        except Exception:                                       # noqa: BLE001
            pass


def main() -> int:
    p = unread_from_owner()
    if p is None:
        print("  no mail credential here, so the inbox was NOT checked.")
        print("  Unchecked is not empty.")
        return 0
    if not p:
        print("  nothing unread from the owner")
    else:
        print("  %d unread message(s) from the owner. These outrank everything "
              "else:" % len(p))
        for s in p:
            print("    %s" % s)

    # And the rest of the mailbox. Reporting only the owner's mail made
    # "nothing unread from the owner" read as "nothing to do", which is how an
    # affiliate network's decline sat unopened for eight days while our own
    # records said the application was waiting on us.
    third = unread_needing_action()
    if third is None:
        print("  third-party mail NOT checked (no credential). Unchecked is "
              "not empty.")
    elif third:
        print("  %d unread message(s) from third parties that may need a "
              "decision:" % len(third))
        for s in third:
            print("    %s" % s)
        print("  A subject line is not the message. Open them: 'Application "
              "Update' was a decline.")
    else:
        print("  nothing unread from a third party that looks actionable")
    return 1 if (p or third) else 0




def ack() -> int:
    """Mark the owner's unread messages read, meaning they were acted on.

    Deliberately a separate command from reading. Marking a message read is a
    claim that a cycle handled it, so it belongs to whoever handled it and must
    never be a side effect of looking.
    """
    env = _env()
    M = imaplib.IMAP4_SSL(env["IMAP_HOST"], int(env["IMAP_PORT"]))
    try:
        M.login(env["IMAP_USER"], env["IMAP_PASS"])
        M.select("INBOX")
        typ, data = M.search(None, "UNSEEN", "FROM", env["OWNER_EMAIL"])
        ids = data[0].split() if data and data[0] else []
        for i in ids:
            M.store(i, "+FLAGS", "\\Seen")
        print("  acknowledged %d message(s) as acted on" % len(ids))
        return 0
    finally:
        try:
            M.logout()
        except Exception:                                       # noqa: BLE001
            pass


if __name__ == "__main__":
    sys.exit(ack() if "--ack" in sys.argv else main())
