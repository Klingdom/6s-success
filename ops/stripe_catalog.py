#!/usr/bin/env python3
"""
Mirror the sellable catalogue into Stripe: products, prices, payment links.

WHY THIS EXISTS
---------------
The site lists 44 SKUs. Stripe held 2. Anything sold has to exist in both, with
the same price, or the shop is lying about something. This makes Stripe follow
the site rather than the two drifting apart by hand.

WHAT IT WILL AND WILL NOT CREATE
--------------------------------
It creates a Product and a Price for every SKU in SELLABLE below.

It creates a **Payment Link only when the SKU can actually be delivered**, which
is decided by `deliverable()` and not by anybody's optimism. A payment link is a
live invitation to hand over money. Publishing one for a thing that does not
exist is taking money for nothing, which CLAUDE.md section 8 rules out, so an
undeliverable SKU gets its catalogue entry and no link.

Everything is idempotent and keyed on `metadata.sku`. Running it twice changes
nothing. It never deletes: retiring a SKU is a deliberate act, not a side effect
of an edit somewhere else.

FULFILMENT
----------
Stripe does not host or deliver files. Each digital product carries
`metadata.deliverable`, naming the file ops/stripe_fulfil.py sends after payment.
A product marked digital with no deliverable on disk is refused rather than
listed, because the failure would otherwise land on a customer who has paid.

Run:  python ops/stripe_catalog.py --check
      STRIPE_ALLOW_LIVE=1 python ops/stripe_catalog.py --apply
"""
from __future__ import annotations

import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")
SITE = "https://6s-success.com"
API = "https://api.stripe.com/v1/"

# The SKUs Stripe should know about. Deliberately not all 44.
#
# The 24 tools and supplies are excluded: they are retail goods with no supplier
# and no fulfilment, so a Stripe product for each would be 24 pieces of clutter
# describing nothing. Courses, kits and the app are excluded for the same
# reason. They come in when they have a delivery path, not before.
#
#   kind        digital  needs a file to send, and a fulfilment run
#               physical needs a shipping address collected at checkout
#               service  delivered by a person, nothing to ship
#   deliverable path relative to the repo root, for digital only
SELLABLE = {
    "BK-EB": dict(kind="digital",
                  deliverable="build/6S-Success-Home-Edition.epub"),
    "BK-HC": dict(kind="physical"),
    "BK-BUNDLE": dict(kind="physical",
                      deliverable="build/6S-Success-Home-Edition.epub"),
    "PACK-HOUSE": dict(kind="digital",
                       deliverable="build/6S-Whole-House-Print-Pack.html"),
    "MZ-MANUAL": dict(kind="digital",
                      deliverable="content/manual/micro-zone-manual-publishable.html"),
    "DECK-ENTRY-PDF": dict(kind="digital",
                           deliverable="build/entryway-deck-illustrated.pdf"),
    "DECK-ENTRY-BOX": dict(kind="physical"),
    "CN-VIRTUAL": dict(kind="service"),
    "CN-INHOME": dict(kind="service"),
}

# Countries we will actually post a physical item to. Stripe requires an
# explicit list; an empty one silently means "no shipping collected", which
# would take money for a parcel with nowhere to send it.
SHIP_TO = ["US", "CA", "GB", "IE", "AU", "NZ"]


# ---------------------------------------------------------------- plumbing
def secret_key() -> str:
    if not os.path.exists(SECRETS):
        sys.exit(".env.secrets not found. Nothing to authenticate with.")
    for line in io.open(SECRETS, encoding="utf-8"):
        if line.startswith("STRIPE_SECRET_KEY"):
            # .strip() matters: a leading space once made a live key report
            # itself as test mode while operating on the real account.
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("STRIPE_SECRET_KEY not in .env.secrets")


KEY = secret_key()
LIVE = KEY.startswith("sk_live_")


def call(method: str, path: str, data: dict | None = None) -> dict:
    url = API + path
    body = None
    if data:
        flat = urllib.parse.urlencode(flatten(data)).encode()
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


def flatten(d: dict, prefix: str = "") -> list[tuple[str, str]]:
    """Stripe takes bracketed form encoding, not JSON."""
    out: list[tuple[str, str]] = []
    for k, v in d.items():
        key = f"{prefix}[{k}]" if prefix else k
        if isinstance(v, dict):
            out += flatten(v, key)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    out += flatten(item, f"{key}[{i}]")
                else:
                    out.append((f"{key}[{i}]", str(item)))
        elif isinstance(v, bool):
            out.append((key, "true" if v else "false"))
        elif v is not None:
            out.append((key, str(v)))
    return out


def catalogue() -> dict[str, dict]:
    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    arr = json.loads(js[js.index("["):js.rindex("]") + 1])
    return {i["sku"]: i for i in arr}


# ---------------------------------------------------------------- decisions
def deliverable(sku: str, item: dict, spec: dict) -> tuple[bool, str]:
    """Can a customer actually receive this if they pay right now?

    This is the gate on creating a payment link, so it errs towards no. Every
    branch names what is missing, because "not deliverable" with no reason is
    how a blocker survives for a month.
    """
    if item.get("available") is False:
        return False, "listed as In development on the site"
    if spec["kind"] == "physical":
        return False, "no printer or stock, and nothing to post"
    if spec["kind"] == "digital":
        path = spec.get("deliverable")
        if not path:
            return False, "digital with no file named"
        if not os.path.exists(os.path.join(ROOT, path)):
            return False, f"file not built: {path}"
        blockers = front_matter_blockers()
        if blockers and sku in ("BK-EB", "BK-BUNDLE", "MZ-MANUAL"):
            return False, f"front matter unanswered ({blockers} fields), issue 3"
    return True, ""


def front_matter_blockers() -> int:
    p = os.path.join(ROOT, "ops", "front-matter.json")
    if not os.path.exists(p):
        return 0
    answers = json.load(io.open(p, encoding="utf-8"))
    return sum(1 for k, v in answers.items() if not k.startswith("_") and not v)


# ---------------------------------------------------------------- sync
def find_by_sku(kind: str, sku: str, adopt_names: list[str] | None = None) -> dict | None:
    """Stripe has no lookup by metadata, so scan. The catalogue is tiny.

    adopt_name exists because the first two products were created by hand,
    before this script, and carry no sku metadata. Without adopting them by
    name the first --apply would have created a second Virtual Home Consult and
    a second In-Home Reset Day, leaving two live payment links each at the same
    price and no way to tell which one a customer used.
    """
    objs = call("GET", kind, {"limit": 100})["data"]
    for obj in objs:
        if (obj.get("metadata") or {}).get("sku") == sku:
            return obj
    for candidate in (adopt_names or []):
        for obj in objs:
            if obj.get("name") == candidate and not (obj.get("metadata") or {}).get("sku"):
                return obj
    return None


def ensure_product(sku: str, item: dict, spec: dict, apply_it: bool) -> str | None:
    name = item["name"]
    if item.get("variant"):
        name = f"{name} ({item['variant']})"
    payload = {
        "name": name,
        "description": item["blurb"][:350],
        "url": f"{SITE}/shop.html",
        "metadata": {"sku": sku, "kind": spec["kind"],
                     "deliverable": spec.get("deliverable", "")},
        "shippable": spec["kind"] == "physical",
    }
    found = find_by_sku("products", sku, adopt_names=[name, item["name"]])
    if found:
        if not apply_it:
            return found["id"]
        call("POST", f"products/{found['id']}", payload)
        return found["id"]
    if not apply_it:
        return None
    return call("POST", "products", payload)["id"]


def ensure_price(product_id: str, sku: str, amount: int, apply_it: bool) -> str | None:
    """Prices are immutable in Stripe. A changed amount means a new price and
    the old one deactivated, never an edit, so history stays truthful."""
    existing = [p for p in call("GET", "prices",
                                {"limit": 100, "product": product_id})["data"]
                if p["active"]]
    for p in existing:
        if p["unit_amount"] == amount and p["currency"] == "usd":
            return p["id"]
    if not apply_it:
        return None
    for p in existing:
        call("POST", f"prices/{p['id']}", {"active": False})
    return call("POST", "prices", {
        "product": product_id, "currency": "usd", "unit_amount": amount,
        "metadata": {"sku": sku},
    })["id"]


def ensure_link(sku: str, price_id: str, spec: dict, apply_it: bool) -> str | None:
    found = find_by_sku("payment_links", sku)
    if not found:
        # A payment link has no name to adopt by, so match on the price it
        # already sells. Same reason as products: the hand made links predate
        # this script and would otherwise be duplicated.
        for l in call("GET", "payment_links", {"limit": 100})["data"]:
            if (l.get("metadata") or {}).get("sku"):
                continue
            items = call("GET", f"payment_links/{l['id']}/line_items", {"limit": 5})["data"]
            if any(i.get("price", {}).get("id") == price_id for i in items):
                if apply_it:
                    call("POST", f"payment_links/{l['id']}", {"metadata": {"sku": sku}})
                found = l
                break
    if found:
        return found["url"]
    if not apply_it:
        return None
    payload = {
        "line_items": [{"price": price_id, "quantity": 1}],
        "metadata": {"sku": sku},
        # Carried onto the PaymentIntent so the fulfilment run can tell what
        # was bought without looking anything up.
        "payment_intent_data": {"metadata": {"sku": sku}},
        "after_completion": {
            "type": "redirect",
            "redirect": {"url": f"{SITE}/thanks.html?sku={sku}"},
        },
        "allow_promotion_codes": True,
    }
    if spec["kind"] == "physical":
        payload["shipping_address_collection"] = {"allowed_countries": SHIP_TO}
    if spec.get("deliverable"):
        # The address is the only way to deliver a digital product, so it is
        # collected rather than left optional.
        payload["customer_creation"] = "always"
    return call("POST", "payment_links", payload)["url"]


def sync_site_links(apply_it):
    """Point the site's buy buttons at the live payment links.

    Doing this by hand is how the shop ends up offering a link Stripe has
    retired, or hiding one it has. The site follows Stripe, in one direction,
    so there is only ever one answer to what is buyable.
    """
    live = {}
    for l in call("GET", "payment_links", {"limit": 100})["data"]:
        sku = (l.get("metadata") or {}).get("sku")
        if sku and l.get("active"):
            live[sku] = l["url"]

    path = os.path.join(ROOT, "site", "assets", "js", "data.js")
    js = io.open(path, encoding="utf-8").read()
    arr = json.loads(js[js.index("["):js.rindex("]") + 1])

    changed = []
    for i in arr:
        want, have = live.get(i["sku"]), i.get("buy")
        if want and have != want:
            i["buy"] = want
            changed.append(i["sku"])
        elif have and not want:
            # A buy button for something Stripe no longer sells leads nowhere.
            i.pop("buy")
            changed.append(i["sku"] + " (link removed)")

    if changed and apply_it:
        header = "/* Auto-generated catalog. window.CATALOG consumed by shop.js/home. */"
        out = header + chr(10) + "window.CATALOG = " + json.dumps(
            arr, indent=1, ensure_ascii=False) + ";" + chr(10)
        io.open(path, "w", encoding="utf-8", newline="").write(out)
    print("  site buy links: " + (", ".join(changed) if changed else "already in sync"))
    return len(changed)


def main(apply_it: bool) -> int:
    if apply_it and LIVE and os.environ.get("STRIPE_ALLOW_LIVE") != "1":
        sys.exit("Refusing to write to a LIVE account without STRIPE_ALLOW_LIVE=1")

    cat = catalogue()
    print(f"  mode: {'LIVE' if LIVE else 'test'}   "
          f"{'applying' if apply_it else 'dry run, nothing will be written'}")
    fm = front_matter_blockers()
    if fm:
        print(f"  front matter: {fm} fields unanswered, so the book and manual "
              f"cannot be sold (issue 3)")
    print()

    linked, held = [], []
    for sku, spec in SELLABLE.items():
        item = cat.get(sku)
        if not item:
            print(f"  {sku:16} SKIP, not in the site catalogue")
            continue
        amount = int(round((item.get("price") or 0) * 100))
        if amount <= 0:
            print(f"  {sku:16} SKIP, no price")
            continue

        pid = ensure_product(sku, item, spec, apply_it)
        rid = ensure_price(pid, sku, amount, apply_it) if pid else None
        ok, why = deliverable(sku, item, spec)

        state = f"${amount/100:,.2f}"
        if ok:
            # rid is None on a dry run, which means "nothing written yet", not
            # "not deliverable". Conflating the two reported the two live
            # consulting offers as blocked with no reason given.
            url = ensure_link(sku, rid, spec, apply_it) if rid else None
            linked.append((sku, url))
            shown = url or ("(dry run, link would be created)" if not apply_it
                            else "(no price id)")
            print(f"  {sku:16} {state:>10}  LINK  {shown}")
        else:
            held.append((sku, why))
            print(f"  {sku:16} {state:>10}  no link: {why}")

    print(f"\n  {len(linked)} buyable, {len(held)} held back")
    if held:
        print("  Held back because they cannot be delivered, not because Stripe "
              "is not ready:")
        for sku, why in held:
            print(f"    {sku:16} {why}")
    sync_site_links(apply_it)
    if not apply_it:
        print("\n  Dry run. Re-run with --apply and STRIPE_ALLOW_LIVE=1 to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
