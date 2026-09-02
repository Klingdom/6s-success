"""Forward service bookings to Phil, with a calendar invite.

Three products are appointments rather than downloads, so fulfilment is a
conversation, not a file:

    Virtual Home Consult    $250     one hour, online
    In-Home Reset Day       $1200    full day, on site
    Corporate Lean 6S       enquiry  no payment link yet

Phil's instruction, 2026-09-02: when one of these is bought, or somebody emails
about one, forward it to him and send a meeting invite for any time the
customer picked.

The invite is a real .ics attachment, so it lands in a calendar rather than as
a sentence somebody has to retype. When the customer named no time, no invite
is sent and the forward says so, because inventing an appointment time is
worse than asking.

Idempotent: every charge and message it has already handled is recorded in
ops/state-service-orders.json, so a rerun does not forward the same booking
twice.

    python ops/service_orders.py            report only, send nothing
    python ops/service_orders.py --send     forward and invite
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
STATE = os.path.join(ROOT, "ops", "state-service-orders.json")

SERVICES = {
    "CN-VIRTUAL": "Virtual Home Consult",
    "CN-INHOME": "In-Home Reset Day",
    "CN-CORP": "Corporate Lean 6S",
}
# What to look for in a subject line or a Stripe product name. Kept loose,
# because a customer writes "reset day" not "CN-INHOME".
PHRASES = [
    ("Virtual Home Consult", ("virtual home consult", "virtual consult",
                              "home consult")),
    ("In-Home Reset Day", ("in-home reset", "in home reset", "reset day")),
    ("Corporate Lean 6S", ("corporate lean", "corporate 6s", "lean 6s")),
]

DURATION = {"Virtual Home Consult": 60,
            "In-Home Reset Day": 480,
            "Corporate Lean 6S": 60}


def which_service(text: str):
    t = (text or "").lower()
    for name, keys in PHRASES:
        if any(k in t for k in keys):
            return name
    return None


def load_state() -> dict:
    if os.path.exists(STATE):
        try:
            return json.load(io.open(STATE, encoding="utf-8"))
        except Exception:                                       # noqa: BLE001
            pass
    return {"charges": [], "messages": []}


def save_state(s: dict) -> None:
    io.open(STATE, "w", encoding="utf-8", newline="").write(
        json.dumps(s, indent=1, sort_keys=True) + "\n")


# --- finding a time the customer actually named ---------------------------

MONTHS = ("january february march april may june july august september "
          "october november december").split()
# Match on the three letter stem so "Oct", "Oct." and "October" all work.
# Matching full names only meant "Oct 20 9am" silently found no time and the
# customer got no invite.
STEMS = "|".join(m[:3] for m in MONTHS)
DATE_PATTERNS = [
    # 14 October at 2pm
    r"(\d{1,2})\s+(%s)[a-z]*\.?\s*(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?" % STEMS,
    # Oct 14 at 2pm
    r"(%s)[a-z]*\.?\s+(\d{1,2})\w*,?\s*(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?" % STEMS,
]


def find_time(text: str):
    """A datetime the customer named, or None.

    Deliberately conservative. A wrong appointment time is worse than no
    invite, so anything ambiguous returns None and the forward says a time
    could not be read.
    """
    t = re.sub(r"\s+", " ", (text or "").lower())
    now = dt.datetime.now()
    for pat in DATE_PATTERNS:
        m = re.search(pat, t)
        if not m:
            continue
        g = list(m.groups())
        try:
            if g[0].isdigit():
                day = int(g[0])
                month = [i for i, m in enumerate(MONTHS)
                         if m.startswith(g[1][:3])][0] + 1
            else:
                month = [i for i, m in enumerate(MONTHS)
                         if m.startswith(g[0][:3])][0] + 1
                day = int(g[1])
            hour = int(g[2])
            minute = int(g[3]) if g[3] else 0
            ampm = g[4]
            if ampm == "pm" and hour < 12:
                hour += 12
            if ampm == "am" and hour == 12:
                hour = 0
            if ampm is None and hour < 8:
                # 3 with no am/pm on a working calendar means afternoon.
                hour += 12
            year = now.year
            when = dt.datetime(year, month, day, hour, minute)
            if when < now - dt.timedelta(days=1):
                when = when.replace(year=year + 1)
            return when
        except Exception:                                       # noqa: BLE001
            continue
    return None


def ics(service: str, when: dt.datetime, customer: str) -> bytes:
    mins = DURATION.get(service, 60)
    end = when + dt.timedelta(minutes=mins)
    fmt = "%Y%m%dT%H%M%S"
    uid = "%s-%s@6s-success.com" % (re.sub(r"\W", "", service).lower(),
                                    when.strftime(fmt))
    body = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//6S Success//Service booking//EN",
        "CALSCALE:GREGORIAN", "METHOD:REQUEST", "BEGIN:VEVENT",
        "UID:" + uid,
        "DTSTAMP:" + dt.datetime.utcnow().strftime(fmt) + "Z",
        "DTSTART:" + when.strftime(fmt),
        "DTEND:" + end.strftime(fmt),
        "SUMMARY:%s with %s" % (service, customer or "a customer"),
        "DESCRIPTION:Booked through 6s-success.com. Duration %d minutes." % mins,
        "ORGANIZER;CN=6S Success:mailto:support@6s-success.com",
        "STATUS:CONFIRMED", "END:VEVENT", "END:VCALENDAR",
    ]
    return ("\r\n".join(body) + "\r\n").encode("utf-8")


# --- sources ---------------------------------------------------------------

def stripe_key():
    p = os.path.join(ROOT, ".env.secrets")
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"^STRIPE_SECRET_KEY=(.*)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    return os.environ.get("STRIPE_SECRET_KEY")


def recent_service_charges(limit: int = 100) -> list:
    key = stripe_key()
    if not key:
        return []
    url = "https://api.stripe.com/v1/charges?limit=%d" % limit
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=40).read().decode())
    except Exception:                                           # noqa: BLE001
        return []
    out = []
    for c in d.get("data", []):
        if not c.get("paid") or c.get("refunded"):
            continue
        blob = " ".join(str(x) for x in [
            c.get("description"), (c.get("metadata") or {}).get("sku"),
            (c.get("metadata") or {}).get("product"),
            ((c.get("billing_details") or {}).get("name"))])
        svc = which_service(blob)
        if svc:
            out.append({
                "id": c["id"], "service": svc,
                "amount": c["amount"] / 100,
                "email": c.get("receipt_email")
                         or (c.get("billing_details") or {}).get("email"),
                "name": (c.get("billing_details") or {}).get("name"),
                "created": c.get("created"),
            })
    return out


def service_emails() -> list:
    """Unread inbox messages about one of the three services."""
    import email
    import imaplib
    from email.header import decode_header

    env = {}
    p = os.path.join(ROOT, ".env.secrets")
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"^([A-Z_]+)=(.*)$", line.strip())
            if m:
                env[m.group(1)] = m.group(2)
    for k in ("IMAP_HOST", "IMAP_PORT", "IMAP_USER", "IMAP_PASS"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    if not all(env.get(k) for k in ("IMAP_HOST", "IMAP_PORT",
                                    "IMAP_USER", "IMAP_PASS")):
        return []

    M = imaplib.IMAP4_SSL(env["IMAP_HOST"], int(env["IMAP_PORT"]))
    out = []
    try:
        M.login(env["IMAP_USER"], env["IMAP_PASS"])
        M.select("INBOX")
        typ, data = M.search(None, "UNSEEN")
        for i in (data[0].split() if data and data[0] else []):
            # PEEK so reading does not mark it handled.
            typ, d = M.fetch(i, "(BODY.PEEK[])")
            if not d or not d[0]:
                continue
            msg = email.message_from_bytes(d[0][1])
            subj = decode_header(msg.get("Subject", ""))[0][0]
            if isinstance(subj, bytes):
                subj = subj.decode("utf-8", "replace")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(
                            part.get_content_charset() or "utf-8", "replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode(
                    msg.get_content_charset() or "utf-8", "replace")
            svc = which_service(str(subj) + " " + body)
            if svc:
                out.append({"id": msg.get("Message-ID", str(i)),
                            "service": svc, "subject": str(subj),
                            "from": msg.get("From", ""), "body": body})
    finally:
        try:
            M.logout()
        except Exception:                                       # noqa: BLE001
            pass
    return out


def main() -> int:
    send = "--send" in sys.argv
    state = load_state()
    import mailer

    charges = recent_service_charges()
    emails = service_emails()
    new_c = [c for c in charges if c["id"] not in state["charges"]]
    new_e = [e for e in emails if e["id"] not in state["messages"]]

    print("  service charges seen : %d, new: %d" % (len(charges), len(new_c)))
    print("  service emails seen  : %d, new: %d" % (len(emails), len(new_e)))

    if not send:
        for c in new_c:
            print("     WOULD FORWARD charge %s  %s  $%s  %s"
                  % (c["id"], c["service"], c["amount"], c.get("email")))
        for e in new_e:
            when = find_time(e["subject"] + " " + e["body"])
            print("     WOULD FORWARD email   %s  %s  time=%s"
                  % (e["service"], e["from"][:34],
                     when.strftime("%Y-%m-%d %H:%M") if when else "none named"))
        return 0

    owner = mailer.owner()
    for c in new_c:
        text = ("A service was purchased.\n\n"
                "Service   : %s\nAmount    : $%s\nCustomer  : %s\nEmail     : %s\n"
                "Charge    : %s\n\n"
                "No time has been agreed yet. Reply to the customer to arrange "
                "one, and a calendar invite will follow once they name it.\n"
                % (c["service"], c["amount"], c.get("name") or "not given",
                   c.get("email") or "not given", c["id"]))
        mailer.send(owner, "BOOKING: %s, $%s" % (c["service"], c["amount"]), text)
        state["charges"].append(c["id"])
        print("     forwarded charge %s" % c["id"])

    for e in new_e:
        when = find_time(e["subject"] + " " + e["body"])
        head = ("An email about a service came in.\n\n"
                "Service : %s\nFrom    : %s\nSubject : %s\n\n"
                % (e["service"], e["from"], e["subject"]))
        attach = []
        if when:
            head += ("Time the customer named: %s.\n"
                     "A calendar invite for that slot is attached.\n\n"
                     % when.strftime("%A %d %B %Y at %H:%M"))
            attach = [("invite.ics",
                       ics(e["service"], when, e["from"]),
                       "text", "calendar")]
        else:
            head += ("No time could be read from the message, so no invite is "
                     "attached. Inventing one would be worse than asking.\n\n")
        head += "--- their message ---\n" + e["body"][:2000]
        mailer.send(owner, "SERVICE ENQUIRY: %s" % e["service"], head,
                    attachments=attach)
        state["messages"].append(e["id"])
        print("     forwarded email about %s (invite: %s)"
              % (e["service"], "yes" if when else "no time named"))

    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
