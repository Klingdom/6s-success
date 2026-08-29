#!/usr/bin/env python3
"""
Read the support inbox, act on what is actionable, and file the rest.

WHY THIS EXISTS
---------------
Until now mail was counted, not read. The hourly brief reported "3 unread" for
days while a message from the owner asking for a status update sat there
unopened. A metric about unread mail is not the same as reading the mail, and
the gap cost four days.

Worse, the loop was one directional. Phil could be emailed and his replies went
nowhere: nothing parsed them, nothing acted, nothing even noticed they had
arrived. He asked for a two way channel, so this is the inbound half.

WHAT IT DOES AND DOES NOT DECIDE
--------------------------------
It classifies and it extracts. It does not answer customers on its own.

A reply from Phil is an instruction from the owner and gets turned into a work
item. A customer email gets summarised and surfaced with a drafted reply, but
the reply is NOT sent: a message to a customer is a message sent on the
business's behalf, and the standing rule is that those are surfaced for a human
rather than fired automatically. Automated support mail that gets something
wrong costs more than slow support mail that gets it right.

The one exception is a delivery failure, where the customer has paid and the
correct action is unambiguous, and even that is only flagged, not fixed.

WHAT IT WRITES
--------------
ops/inbox-state.json, an append-only record of what has been seen and what was
extracted, so the same message is not re-actioned every hour. Messages are
matched by Message-ID, not by subject, because subjects repeat.

Run:  python ops/inbox_agent.py --check          read and classify, change nothing
      python ops/inbox_agent.py --apply          also write the state file
"""
from __future__ import annotations

import email
import imaplib
import io
import json
import os
import re
import sys
from email.header import decode_header, make_header

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "ops", "inbox-state.json")

OWNER_DOMAINS = ("gmail.com",)
OWNER_HINTS = ("philkling", "phil kling")

# Mail this business sends itself. Counting a delivery receipt as a customer
# enquiry is how an inbox agent invents work that does not exist.
OURS = ("support@6s-success.com",)
OUR_SUBJECTS = ("Your copy of", "6S hourly", "3 LinkedIn drafts", "6S Success:")


def env(name: str, default: str = "") -> str:
    v = os.environ.get(name, "").strip()
    if v:
        return v
    p = os.path.join(ROOT, ".env.secrets")
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8"):
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return default


def load_state() -> dict:
    if os.path.exists(STATE):
        try:
            return json.load(io.open(STATE, encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            pass
    return {"seen": [], "items": []}


def body_of(msg) -> str:
    for part in (msg.walk() if msg.is_multipart() else [msg]):
        if part.get_content_type() == "text/plain":
            try:
                return part.get_payload(decode=True).decode("utf-8", "replace")
            except Exception:                                 # noqa: BLE001
                continue
    for part in (msg.walk() if msg.is_multipart() else [msg]):
        if part.get_content_type() == "text/html":
            raw = part.get_payload(decode=True).decode("utf-8", "replace")
            return re.sub(r"<[^>]+>", " ", raw)
    return ""


def strip_quoted(text: str) -> str:
    """Just what they wrote, not the thread underneath it.

    Without this, every reply from Phil carries the entire brief he was replying
    to, and a classifier reading that decides the reply is about whatever the
    brief was about rather than what he actually said.
    """
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith(">"):
            break
        if re.match(r"^On .+ wrote:$", s):
            break
        if s in ("--", "-- ", "Sent from my iPhone"):
            break
        lines.append(ln)
    return "\n".join(lines).strip()


def classify(frm: str, subject: str, text: str, extra: dict | None = None) -> dict:
    low = (frm or "").lower()
    is_owner = any(h in low for h in OWNER_HINTS) or any(
        low.endswith("@" + d) or ("@" + d) in low for d in OWNER_DOMAINS)
    is_ours = any(o in low for o in OURS) or any(
        subject.startswith(s) for s in OUR_SUBJECTS)

    # AN AFFILIATE DECISION, which nothing recognised before.
    #
    # Applications are pending at CJ, Rakuten and Impact, and every one of
    # them decides by email. Without this, a Rakuten approval arrives, gets
    # classified as automated mail, and sits unread while the link layer goes
    # on refusing to emit links because nothing told it the programme was
    # approved. That is a silent stall of exactly the kind worth catching.
    NETWORKS = ("rakuten", "linkshare", "cj.com", "commissionjunction",
                "conversant", "impact.com", "impactradius", "awin",
                "shareasale", "pepperjam", "partnerize", "flexoffers")
    BRANDS = ("etsy", "office depot", "officemax", "target", "walmart",
              "home depot", "lowes", "lowe's", "ace hardware",
              "container store", "wayfair", "amazon associates")
    blob = f"{low} {subject} {text[:1500]}".lower()
    if any(n in low for n in NETWORKS) or (
            any(b in blob for b in BRANDS)
            and re.search(r"applicat|approv|declin|accept|reject|welcome to|"
                          r"partnership|publisher", blob)):
        verdict = ("declined" if re.search(r"declin|reject|not qualif|"
                                      r"do not qualify", blob)
                   else "approved" if re.search(r"approv|accepted|"
                                                r"welcome to", blob)
                   else "pending")
        who = (next((b for b in BRANDS if b in blob), None)
               or next((n for n in NETWORKS if n in low), "an affiliate network"))
        return {"kind": "affiliate", "action": "work-item",
                "why": (f"an affiliate programme message about {who}, reading "
                        f"as {verdict}. Record it in "
                        f"ops/affiliate-accounts.json and, if approved, set "
                        f"the publisher id so links can be built."),
                "extracted": {"programme": who, "verdict": verdict}}

    if is_ours and not is_owner:
        return {"kind": "self", "action": "ignore",
                "why": "mail this business sent itself"}

    if is_owner:
        # An instruction from the owner. Pull out anything that looks like a
        # concrete answer, because most of what blocks work is one value.
        found = {}
        for pat, key in (
            (r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", "uuid"),
            (r"(https?://[^\s>]+)", "url"),
            (r"\b(sk_live_[A-Za-z0-9]+|sk_test_[A-Za-z0-9]+)\b", "SECRET"),
        ):
            m = re.search(pat, text)
            if m:
                found[key] = m.group(1)
        # A secret pasted into email must never be written to a state file that
        # lives in a public repository.
        if "SECRET" in found:
            found["SECRET"] = "[REDACTED, present in the email, do not store]"
        return {"kind": "owner", "action": "work-item",
                "why": "an instruction or answer from the owner",
                "extracted": found}

    # Bulk and automated mail. Classifying a marketing blast or another
    # service's confirmation as a customer enquiry generates a queue of replies
    # nobody should send, and a queue full of noise is a queue that stops being
    # read. Detected from the headers senders are obliged to set, not from
    # guessing at the subject line.
    # Presence of the header is the signal, not its contents. The first version
    # of this searched for the header NAME inside the joined header VALUES,
    # which of course never matched, and every marketing blast queued as a
    # customer awaiting a reply. Found by reading the headers of a message it
    # had misfiled rather than by rereading the condition.
    ex = extra or {}
    vals = " ".join(str(v) for v in ex.values()).lower()
    if (ex.get("lu") or ex.get("lid")
            or "bulk" in vals or "auto-generated" in vals or "auto-replied" in vals
            or "noreply" in low or "no-reply" in low or "donotreply" in low):
        return {"kind": "bulk", "action": "ignore",
                "why": "automated or bulk mail, no reply is expected or wanted"}

    low_t = (text or "").lower()
    if any(w in low_t for w in ("did not receive", "never arrived", "no email",
                                "did not get", "missing file", "cannot download")):
        return {"kind": "delivery-problem", "action": "flag-urgent",
                "why": "a paying customer may not have received what they bought"}

    if any(w in low_t for w in ("refund", "charge", "invoice", "receipt", "payment")):
        return {"kind": "billing", "action": "draft-for-human",
                "why": "money is involved, a person decides"}

    return {"kind": "customer", "action": "draft-for-human",
            "why": "a message to a customer is sent on the business's behalf"}


def main() -> int:
    apply = "--apply" in sys.argv
    host = env("IMAP_HOST") or env("SMTP_HOST").replace("smtp.", "imap.")
    user = env("IMAP_USER") or env("SMTP_USER")
    pw = env("IMAP_PASS") or env("SMTP_PASS")
    if not (host and user and pw):
        print("  no mail credentials in this environment")
        return 1

    state = load_state()
    seen = set(state.get("seen", []))

    M = imaplib.IMAP4_SSL(host, int(env("IMAP_PORT", "993")))
    M.login(user, pw)

    fresh, counts = [], {}
    for box in ("INBOX", "INBOX.Junk"):
        typ, _ = M.select(box, readonly=True)
        if typ != "OK":
            continue
        typ, data = M.search(None, "ALL")
        for i in data[0].split():
            typ, raw = M.fetch(i, "(BODY.PEEK[])")
            if not raw or not raw[0]:
                continue
            msg = email.message_from_bytes(raw[0][1])
            mid = msg.get("Message-ID", "") or f"{box}:{i.decode()}"
            if mid in seen:
                continue
            frm = str(make_header(decode_header(msg.get("From", ""))))
            sub = str(make_header(decode_header(msg.get("Subject", ""))))
            text = strip_quoted(body_of(msg))
            c = classify(frm, sub, text, {
                "lu": msg.get("List-Unsubscribe", ""),
                "prec": msg.get("Precedence", ""),
                "auto": msg.get("Auto-Submitted", ""),
                "lid": msg.get("List-Id", ""),
            })
            counts[c["kind"]] = counts.get(c["kind"], 0) + 1
            fresh.append({"id": mid, "box": box, "from": frm[:70],
                          "subject": sub[:90], "date": msg.get("Date", "")[:31],
                          "excerpt": " ".join(text.split())[:400], **c})
    M.logout()

    if not fresh:
        print("  nothing new since the last run")
        return 0

    print(f"  {len(fresh)} new message(s): "
          + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) + "\n")

    order = {"delivery-problem": 0, "owner": 1, "billing": 2, "customer": 3, "self": 4}
    for m in sorted(fresh, key=lambda x: order.get(x["kind"], 9)):
        if m["kind"] in ("self", "bulk"):
            continue
        print(f"  [{m['kind'].upper()}] {m['date'][:22]}  {m['from']}")
        print(f"    {m['subject']}")
        print(f"    action: {m['action']}, because {m['why']}")
        if m.get("extracted"):
            for k, v in m["extracted"].items():
                print(f"    found {k}: {v}")
        print(f"    said: {m['excerpt'][:220]}")
        print()

    actionable = [m for m in fresh if m["action"] in ("work-item", "flag-urgent")]
    print(f"  {len(actionable)} need action now, "
          f"{sum(1 for m in fresh if m['action'] == 'draft-for-human')} need a human reply.")

    if apply:
        state["seen"] = list(seen | {m["id"] for m in fresh})
        state["items"] = (state.get("items", []) + [
            {k: v for k, v in m.items() if k != "excerpt"} for m in actionable])[-200:]
        json.dump(state, io.open(STATE, "w", encoding="utf-8", newline=""), indent=1)
        print(f"  state written, {len(state['seen'])} messages now known")
    else:
        print("  --check only, nothing written. Re-run with --apply to record.")

    # A state file in a public repository must never carry a pasted credential.
    if apply:
        blob = io.open(STATE, encoding="utf-8").read()
        assert not re.search(r"sk_live_[A-Za-z0-9]{6}|sk_test_[A-Za-z0-9]{6}", blob), \
            "a secret reached the state file, which is committed. Remove it."
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
