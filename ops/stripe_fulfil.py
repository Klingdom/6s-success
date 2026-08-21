#!/usr/bin/env python3
"""
Deliver what people have paid for, and say what still needs a human.

THE PROBLEM THIS SOLVES
-----------------------
Stripe takes the money and then stops. It does not host files and it does not
deliver anything, so between "payment succeeded" and "the customer has the
thing" there has to be code. Stripe's own docs recommend a webhook, and
explicitly warn against relying on the post payment redirect page for
fulfilment, because a customer who closes the tab never loads it.

A webhook needs a public HTTPS endpoint with a secret, which means a service to
run, deploy, monitor and secure. This business sells single figures of digital
items to nobody so far. So this polls instead. Stripe's documentation names a
scheduled check as the recognised alternative, and at this volume it is the
right trade: it reuses the mailer and the scheduled run that already exist, and
adds no new service, no new port, no new secret and nothing else to keep alive.

The cost is latency. A buyer waits up to the polling interval rather than
seconds, so the thank you page has to promise the interval and not "instantly".
When volume makes that unacceptable, replace this with a webhook. That is a
real upgrade path, not a rewrite: the delivery half stays exactly as it is.

NO DATABASE
-----------
The ledger of what has already been sent is `fulfilled_at` in the
PaymentIntent's metadata, so Stripe holds the state. That means this can run
from anywhere, twice at once, or after a total loss of this repository, and it
still cannot send the same order twice. A local file would have been simpler to
write and would have broken the first time it ran from CI instead of the desk.

SAFETY
------
Dry run by default. Sending requires --send. It refuses to deliver anything it
cannot name a file for, refuses without a customer email, and marks the order
fulfilled only after the send has actually returned.

Run:  python ops/stripe_fulfil.py                 what would happen
      python ops/stripe_fulfil.py --send          deliver, for real
      python ops/stripe_fulfil.py --days 30       widen the window
"""
from __future__ import annotations

import datetime
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")
API = "https://api.stripe.com/v1/"
SITE = "https://6s-success.com"

# What each SKU is and what file it ships. Kept beside stripe_catalog.py's
# SELLABLE rather than imported from it, because the two answer different
# questions: that one decides what may be offered, this one decides what gets
# sent. A digital SKU missing here fails loudly instead of silently delivering
# nothing.
DELIVERY = {
    "BK-EB": dict(
        file="build/6S-Success-Home-Edition.epub",
        label="6S Success: Home Edition",
        note="Your copy is attached as an EPUB. It opens in Apple Books, "
             "Google Play Books, Kobo, Calibre, and most e-readers."),
    "BK-BUNDLE": dict(
        file="build/6S-Success-Home-Edition.epub",
        label="6S Success: Home Edition, digital half of your bundle",
        note="The digital edition is attached. The hardcover ships separately "
             "and you will get a note when it is posted."),
    "BK-BUNDLE": dict(
        files=["build/6S-Success-Home-Edition.epub",
               "content/manual/micro-zone-manual-publishable.html",
               "build/6S-Whole-House-Print-Pack.html"],
        label="the Complete Digital Bundle",
        note="All three are attached: the book as an EPUB, the Micro Zone "
             "Manual and the Whole House Print Pack as HTML you can open in any "
             "browser and print. The book is the method, the manual is the "
             "reference, and the pack is what you carry into the room."),
    "PACK-HOUSE": dict(
        file="build/6S-Whole-House-Print-Pack.html",
        label="The Whole House Print Pack",
        note="The pack is attached. Open it in any browser and print it: nine "
             "cards to a US Letter page, 76 pages for the whole house. Card "
             "stock holds up better, but paper works. You do not need to print "
             "it all at once, and the pages are in room order."),
    "MZ-MANUAL": dict(
        file="content/manual/micro-zone-manual-publishable.html",
        label="The Micro Zone Manual",
        note="The manual is attached. Open it in any browser, and use your "
             "browser's print dialog if you want it on paper."),
    "DECK-ENTRY-PDF": dict(
        file="build/entryway-deck-illustrated.pdf",
        label="The Entryway Deck, illustrated edition",
        note="The deck is attached. It prints nine cards to a letter page at "
             "true trading card size, so card stock is worth using."),
}

# Attachments beyond this bounce at a lot of mail providers. Better to refuse
# and be told than to send into a wall and mark the order done.
MAX_ATTACH_MB = 15


def secret_key() -> str:
    env = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if env:
        return env
    if not os.path.exists(SECRETS):
        sys.exit("No STRIPE_SECRET_KEY in the environment and no .env.secrets")
    for line in io.open(SECRETS, encoding="utf-8"):
        if line.startswith("STRIPE_SECRET_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("STRIPE_SECRET_KEY not found")


KEY = secret_key()


def call(method: str, path: str, data: dict | None = None) -> dict:
    url = API + path
    body = None
    if data:
        pairs = []
        for k, v in data.items():
            pairs.append((k, "true" if v is True else "false" if v is False else str(v)))
        flat = urllib.parse.urlencode(pairs).encode()
        if method == "GET":
            url += "?" + flat.decode()
        else:
            body = flat
    req = urllib.request.Request(url, data=body, method=method,
                                 headers={"Authorization": "Bearer " + KEY})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        detail = json.load(e).get("error", {}).get("message", "")
        raise SystemExit(f"Stripe {method} {path} failed: {e.code} {detail}")


def paid_sessions(days: int) -> list[dict]:
    since = int((datetime.datetime.now(datetime.timezone.utc)
                 - datetime.timedelta(days=days)).timestamp())
    out, params = [], {"limit": 100, "created[gte]": since,
                       "expand[]": "data.payment_intent"}
    while True:
        page = call("GET", "checkout/sessions", params)
        out += [s for s in page["data"] if s.get("payment_status") == "paid"]
        if not page.get("has_more"):
            return out
        params = dict(params, starting_after=page["data"][-1]["id"])


def sku_of(session: dict) -> str:
    for src in (session.get("metadata") or {},
                ((session.get("payment_intent") or {}) or {}).get("metadata") or {}):
        if src.get("sku"):
            return src["sku"]
    return ""


def deliver(session: dict, sku: str, spec: dict, send: bool,
            ledger: bool = True) -> str:
    email = ((session.get("customer_details") or {}).get("email") or "").strip()
    if not email:
        return "no customer email on the order, cannot deliver"

    # A bundle is several files in one order, so every product carries a list
    # even when it holds one item. Sending only the first would be delivering
    # part of what somebody paid for.
    files = spec.get("files") or [spec["file"]]
    paths = []
    for rel in files:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            return f"file missing: {rel}"
        paths.append(p)
    size_mb = sum(os.path.getsize(p) for p in paths) / 1048576
    if size_mb > MAX_ATTACH_MB:
        return f"attachments total {size_mb:.1f} MB, over the {MAX_ATTACH_MB} MB limit"

    name = ((session.get("customer_details") or {}).get("name") or "").split(" ")[0]
    hello = f"Hello {name}," if name else "Hello,"
    text = "\n".join([
        hello, "",
        f"Thank you for buying {spec['label']}.",
        "",
        spec["note"],
        "",
        "If the attachment does not arrive or will not open, reply to this "
        "message and a person will sort it out.",
        "",
        "6S Success",
        SITE,
    ])

    if not send:
        return f"WOULD SEND to {email}  ({os.path.basename(path)}, {size_mb:.1f} MB)"

    from mailer import send as send_mail                              # noqa: E402
    TYPES = {"epub": ("application", "epub+zip"),
             "html": ("text", "html"),
             "pdf": ("application", "pdf")}
    attachments = []
    for p in paths:
        ext = os.path.splitext(p)[1].lstrip(".").lower()
        major, minor = TYPES.get(ext, ("application", "octet-stream"))
        # Name each file after itself rather than after the order, so a
        # bundle does not arrive as three attachments with one name.
        nice = os.path.basename(p).replace("6S-", "6S ").replace("-", " ")
        attachments.append((nice, io.open(p, "rb").read(), major, minor))
    send_mail(email, f"Your copy of {spec['label']}", text, None, None, None,
              attachments)

    # Only now, after the send returned, is the order marked done. Marking
    # first would lose an order to any mail failure.
    if not ledger:
        return f"SENT to {email} (self test, no fulfilment record written)"

    pi = session.get("payment_intent")
    pi_id = pi["id"] if isinstance(pi, dict) else pi
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    call("POST", f"payment_intents/{pi_id}", {"metadata[fulfilled_at]": stamp,
                                              "metadata[sku]": sku})
    return f"SENT to {email}"


def selftest(sku, to):
    """Deliver one synthetic order through the real deliver(), to an address we
    control.

    Zero paid orders proves only that the empty case works. The part that will
    actually face a customer, reading the file, encoding the attachment, the
    mailer, the subject and the body, has to be exercised before it is. A real
    purchase would be the honest test, but that needs card details typed into a
    payment form, which is not something to do from here.

    This calls deliver() rather than repeating what it does. An earlier draft
    reimplemented the delivery inline, which would have tested a copy of the
    code and left the real path unproven, which is worse than no test because
    it looks like one.

    ledger=False because there is no PaymentIntent behind a synthetic order and
    inventing one would put a fake row in the record of what has been sold.
    """
    if sku not in DELIVERY:
        sys.exit(sku + " is not a digital product. One of: " + ", ".join(DELIVERY))
    spec = DELIVERY[sku]
    for rel in (spec.get("files") or [spec["file"]]):
        if not os.path.exists(os.path.join(ROOT, rel)):
            sys.exit("Cannot self test " + sku + ": " + rel + " is not built yet.")

    session = {
        "customer_details": {"email": to, "name": "Self Test"},
        "amount_total": 0,
        "metadata": {"sku": sku},
    }
    print("  self test: " + sku + " to " + to)
    print("  files: " + ", ".join(spec.get("files") or [spec["file"]]))
    print("  " + deliver(session, sku, spec, send=True, ledger=False))
    print("  A send that returns proves the sender worked, never that the "
          "recipient got something usable. Go and read it.")
    return 0


def main(send: bool, days: int) -> int:
    sessions = paid_sessions(days)
    print(f"  {len(sessions)} paid order(s) in the last {days} days")
    if not sessions:
        print("  Nothing to deliver. This is the expected state until the first sale.")
        return 0

    done = sent = held = manual = 0
    for s in sessions:
        sku = sku_of(s)
        pi = s.get("payment_intent") or {}
        already = (pi.get("metadata") or {}).get("fulfilled_at") if isinstance(pi, dict) else None
        who = (s.get("customer_details") or {}).get("email", "unknown")
        amount = (s.get("amount_total") or 0) / 100

        if already:
            done += 1
            continue
        if not sku:
            held += 1
            print(f"  {'?':16} ${amount:<9,.2f} {who:32} no sku on the order, "
                  f"cannot tell what was bought")
            continue
        if sku not in DELIVERY:
            manual += 1
            print(f"  {sku:16} ${amount:<9,.2f} {who:32} NEEDS A HUMAN, not a "
                  f"digital product")
            continue
        result = deliver(s, sku, DELIVERY[sku], send)
        if result.startswith("SENT"):
            sent += 1
        elif not result.startswith("WOULD"):
            held += 1
        print(f"  {sku:16} ${amount:<9,.2f} {who:32} {result}")

    print(f"\n  {done} already delivered, {sent} delivered now, "
          f"{manual} need a person, {held} could not be delivered")
    if held:
        print("  Anything that could not be delivered is a paid order with no "
              "goods. Fix it today.")
    if not send:
        print("\n  Dry run. Re-run with --send to actually deliver.")
    return 1 if held else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        i = sys.argv.index("--selftest")
        sku = sys.argv[i + 1] if len(sys.argv) > i + 1 else "BK-EB"
        to = sys.argv[i + 2] if len(sys.argv) > i + 2 else "support@6s-success.com"
        sys.exit(selftest(sku, to))
    if "--selftest" in sys.argv:
        i = sys.argv.index("--selftest")
        sku = sys.argv[i + 1] if len(sys.argv) > i + 1 else "BK-EB"
        to = sys.argv[i + 2] if len(sys.argv) > i + 2 else "support@6s-success.com"
        sys.exit(selftest(sku, to))
    n = 14
    if "--days" in sys.argv:
        n = int(sys.argv[sys.argv.index("--days") + 1])
    sys.exit(main("--send" in sys.argv, n))
