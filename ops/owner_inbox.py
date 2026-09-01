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


def main() -> int:
    p = unread_from_owner()
    if p is None:
        print("  no mail credential here, so the inbox was NOT checked.")
        print("  Unchecked is not empty.")
        return 0
    if not p:
        print("  nothing unread from the owner")
        return 0
    print("  %d unread message(s) from the owner. These outrank everything "
          "else:" % len(p))
    for s in p:
        print("    %s" % s)
    return 1




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
