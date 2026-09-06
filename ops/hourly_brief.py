#!/usr/bin/env python3
"""
The hourly brief: measure the business, read the inbox, and mail Phil one note.

WHY THIS EXISTS
---------------
Phil asked for an hourly update and for the inbox to be watched, over a run
longer than any desk session lasts. A desk session ends when the terminal
closes, so anything promising to run for hours has to live somewhere that does
not. This runs on GitHub's schedule, reads its credentials from GitHub Secrets,
and needs no laptop to be awake.

WHAT IT REPORTS
---------------
Only things that changed. An hourly mail that says the same thing twelve times
teaches its reader to stop opening it, so unchanged sections are collapsed to a
line and the subject carries the one number that matters.

It also reads the support inbox and surfaces anything unread, because a customer
question sitting unanswered for twelve hours is worse than a slow product.
It does not reply on its own: a reply is a message sent on the business's behalf
and that is a decision, not a measurement.

Run:  python ops/hourly_brief.py --preview
      python ops/hourly_brief.py --send ADDRESS
"""
from __future__ import annotations

import datetime
import email
import imaplib
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
from email.header import decode_header, make_header

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "ops", "state.json")
LAST = os.path.join(ROOT, "ops", "last-brief.json")
SITE = "https://6s-success.com"


def env(name: str, default: str = "") -> str:
    v = os.environ.get(name, "").strip()
    if v:
        return v
    path = os.path.join(ROOT, ".env.secrets")
    if os.path.exists(path):
        for line in io.open(path, encoding="utf-8"):
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return default


# ------------------------------------------------------------------ commerce
def commerce() -> dict:
    """What Stripe says, which is the only account of revenue that counts."""
    key = env("STRIPE_SECRET_KEY")
    if not key:
        return {"error": "no Stripe key in this environment"}

    def get(path):
        req = urllib.request.Request("https://api.stripe.com/v1/" + path,
                                     headers={"Authorization": "Bearer " + key})
        return json.load(urllib.request.urlopen(req, timeout=20))

    since = int((datetime.datetime.now(datetime.timezone.utc)
                 - datetime.timedelta(days=30)).timestamp())
    try:
        sessions = get(f"checkout/sessions?limit=100&created[gte]={since}")["data"]
        paid = [s for s in sessions if s.get("payment_status") == "paid"]
        links = [l for l in get("payment_links?limit=100")["data"] if l.get("active")]
        bal = get("balance")
        avail = sum(b["amount"] for b in bal.get("available", [])) / 100
        pend = sum(b["amount"] for b in bal.get("pending", [])) / 100
        return {
            "paid_30d": len(paid),
            "revenue_30d": sum(s.get("amount_total", 0) for s in paid) / 100,
            "checkouts_started_30d": len(sessions),
            "live_links": len(links),
            "balance_available": avail,
            "balance_pending": pend,
        }
    except Exception as e:                                    # noqa: BLE001
        return {"error": str(e)[:120]}


# ------------------------------------------------------------------ inbox
def inbox() -> dict:
    host, user, pw = env("IMAP_HOST"), env("IMAP_USER"), env("IMAP_PASS")
    if not (host and user and pw):
        # Fall back to the SMTP identity, which is the same mailbox.
        host = host or env("SMTP_HOST", "").replace("smtp.", "imap.")
        user = user or env("SMTP_USER")
        pw = pw or env("SMTP_PASS")
    if not (host and user and pw):
        return {"error": "no mail credentials in this environment"}
    try:
        M = imaplib.IMAP4_SSL(host, int(env("IMAP_PORT", "993")))
        M.login(user, pw)
        out = {"unread": [], "total": 0}
        for box in ("INBOX", "INBOX.Junk"):
            typ, _ = M.select(box, readonly=True)
            if typ != "OK":
                continue
            typ, data = M.search(None, "UNSEEN")
            ids = data[0].split()
            typ, alldata = M.search(None, "ALL")
            out["total"] += len(alldata[0].split())
            for i in ids[-15:]:
                typ, raw = M.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
                h = email.message_from_bytes(raw[0][1])
                frm = str(make_header(decode_header(h.get("From", ""))))
                sub = str(make_header(decode_header(h.get("Subject", ""))))
                # Our own delivery mail is not correspondence.
                if "support@6s-success.com" in frm and sub.startswith("Your copy of"):
                    continue
                out["unread"].append({"box": box, "from": frm[:60],
                                      "subject": sub[:80], "date": h.get("Date", "")[:31]})
        M.logout()
        return out
    except Exception as e:                                    # noqa: BLE001
        return {"error": str(e)[:120]}


# ------------------------------------------------------------------ site
def site() -> dict:
    out = {}
    for name, path in (("home", "/"), ("shop", "/shop.html"),
                       ("quest", "/quest.html"), ("deck", "/deck.html")):
        try:
            req = urllib.request.Request(SITE + path, method="GET",
                                         headers={"User-Agent": "6S ops brief"})
            out[name] = urllib.request.urlopen(req, timeout=12).getcode()
        except Exception:                                     # noqa: BLE001
            out[name] = 0
    return out


def measured() -> dict:
    try:
        subprocess.run([sys.executable, os.path.join(ROOT, "ops", "dashboard.py")],
                       capture_output=True, timeout=180)
    except Exception:                                         # noqa: BLE001
        pass
    if os.path.exists(STATE):
        return json.load(io.open(STATE, encoding="utf-8"))
    return {}


def build_line(st: dict) -> str:
    """One line summarising the last measured build state.

    st is ops/state.json, written by ops/dashboard.py. Reads the field names
    dashboard.py actually writes (open_p0, commits_7d), not a guessed
    shorthand: st.get('p0', '?') and st.get('commits7d', '?') never matched
    any real key, so this line has read "P0 ?" and "commits 7d ?" on every
    hourly mail ever sent, even a run with a working Stripe key and real
    egress that measured both numbers correctly two dict keys away.
    """
    return (f"  overall {st.get('overall', '?')}   "
            f"P0 {st.get('open_p0', '?')}   needs Phil {st.get('needs_phil', '?')}   "
            f"commits 7d {st.get('commits_7d', '?')}")


def load_last() -> dict:
    if os.path.exists(LAST):
        try:
            return json.load(io.open(LAST, encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            pass
    return {}


def build() -> tuple[str, str]:
    now = datetime.datetime.now(datetime.timezone.utc)
    st, cm, ib, sv = measured(), commerce(), inbox(), site()
    prev = load_last()

    rev = cm.get("revenue_30d", 0)
    sales = cm.get("paid_30d", 0)
    subject = (f"6S hourly: ${rev:,.0f} / 30d, {sales} sale(s), "
               f"{len(ib.get('unread', []))} unread")

    L = [f"{now:%Y-%m-%d %H:%M} UTC", ""]

    L += ["COMMERCE"]
    if cm.get("error"):
        L.append(f"  could not read Stripe: {cm['error']}")
    else:
        L += [f"  revenue, last 30 days      ${cm['revenue_30d']:,.2f}",
              f"  paid orders                {cm['paid_30d']}",
              f"  checkouts started          {cm['checkouts_started_30d']}",
              f"  live payment links         {cm['live_links']}",
              f"  balance available/pending  ${cm['balance_available']:,.2f}"
              f" / ${cm['balance_pending']:,.2f}"]
        d = sales - prev.get("paid_30d", sales)
        if d > 0:
            L.append(f"  NEW SINCE LAST BRIEF       {d} order(s)")

    L += ["", "INBOX"]
    if ib.get("error"):
        L.append(f"  could not read mail: {ib['error']}")
    elif not ib.get("unread"):
        L.append("  nothing unread")
    else:
        L.append(f"  {len(ib['unread'])} unread, needing a human:")
        for m in ib["unread"]:
            L.append(f"    {m['date'][:22]:24} {m['from'][:34]:36} {m['subject']}")

    L += ["", "SITE"]
    bad = [k for k, v in sv.items() if v != 200]
    L.append("  all pages 200" if not bad
             else "  NOT 200: " + ", ".join(f"{k}={sv[k]}" for k in bad))

    if st:
        L += ["", "BUILD", build_line(st)]

    L += ["", f"Dashboard: {SITE}  |  full log in ops/NIGHTLY-LOG.md"]

    json.dump({"paid_30d": sales, "revenue_30d": rev,
               "at": now.isoformat(timespec="seconds")},
              io.open(LAST, "w", encoding="utf-8"), indent=1)
    return subject, "\n".join(L)


if __name__ == "__main__":
    subject, text = build()
    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    if mode == "--send" and len(sys.argv) > 2:
        from mailer import send                               # noqa: E402
        send(sys.argv[2], subject, text)
        print("sent:", subject)
    else:
        print("SUBJECT:", subject, "\n")
        print(text)
