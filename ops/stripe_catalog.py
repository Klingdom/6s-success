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

import datetime
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
REFUSALS_PATH = os.path.join(ROOT, "ops", "link-retirement-refused.json")

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
    # A list here, not a string: ops/stripe_fulfil.py's own DELIVERY["BK-BUNDLE"]
    # sends all three files (the same list, same order) and refuses to ship if
    # any one is missing. deliverable() below must refuse to sell the link on
    # the same condition, or a missing EPUB/manual would still read
    # "deliverable" here while an order silently stalled at fulfilment time.
    "BK-BUNDLE": dict(kind="digital",
                      deliverable=["build/6S-Success-Home-Edition.epub",
                                   "content/manual/micro-zone-manual-publishable.html",
                                   "build/6S-Whole-House-Print-Pack.html"]),
    "PACK-HOUSE": dict(kind="digital",
                       deliverable="build/6S-Whole-House-Print-Pack.html"),
    "MZ-MANUAL": dict(kind="digital",
                      deliverable="content/manual/micro-zone-manual-publishable.html"),
    "CN-VIRTUAL": dict(kind="service"),
    "CN-INHOME": dict(kind="service"),
}

# The 149 generated packs are added rather than typed. They are computed by
# ops/generated_products.py from the same content that builds the files, so
# the list here cannot drift from the list on disk or the list in the shop.
# Anything that module excludes, for example the entryway packs the free deck
# already covers, never reaches Stripe at all.
def _add_generated() -> int:
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    from generated_products import products
    keep, _dropped = products()
    for p in keep:
        SELLABLE[p["sku"]] = dict(kind="digital", deliverable=p["deliverable"])
    return len(keep)


_GENERATED = _add_generated()

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


_KEY: str | None = None


def key() -> str:
    """Lazy on purpose: importing this module for SELLABLE (a local dict, no
    network) must not require live credentials. Only an actual API call
    should, and only then.
    """
    global _KEY
    if _KEY is None:
        _KEY = secret_key()
    return _KEY


def live() -> bool:
    return key().startswith("sk_live_")


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
                                 headers={"Authorization": "Bearer " + key()})
    try:
        return json.load(urllib.request.urlopen(req, timeout=20))
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


def price_claim_gaps() -> list[tuple[str, float]]:
    """Every dollar figure in an active Stripe product description must be
    either a catalogue price or the exact sum of a bundle's components.

    Extracted from preflight.py's gate_stripe_price_claims so the same check
    can run inside ops/hourly_brief.py, the one credentialed job that can
    actually reach this account, rather than only from a sandbox that never
    holds a Stripe key. Raises via list_all()/secret_key() when there is no
    credential, the convention every other Stripe reader here uses; callers
    that want a soft failure catch that themselves.
    """
    import re as _re
    prods = [p for p in list_all("products") if p.get("active")]
    prices = {round(float(i.get("price") or 0), 2) for i in catalogue().values()}
    sums = {round(sum(c), 2) for c in
            [[a, b, c2] for a in prices for b in prices for c2 in prices]} if len(prices) < 40 else set()
    bad = []
    for p in prods:
        for amt in _re.findall(r"\$([0-9]+(?:\.[0-9]{2})?)", p.get("description") or ""):
            v = float(amt)
            if v not in prices and v not in sums:
                bad.append((p.get("name", "")[:36], v))
    return bad


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
        # A bundle SKU names a list of files (must all exist to ship, matching
        # stripe_fulfil.py's own all-or-nothing DELIVERY check); every other
        # SKU names one file as a plain string.
        paths = [path] if isinstance(path, str) else path
        missing = [p for p in paths if not os.path.exists(os.path.join(ROOT, p))]
        if missing:
            return False, f"file not built: {missing[0]}"
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


def skus_stuck_on_inactive_link() -> list[str]:
    """Deliverable SKUs whose only Stripe payment-link match is inactive.

    find_by_sku() below deliberately falls back to an inactive match when no
    active one exists, which is correct for retirement bookkeeping (it needs
    to see a retired link to replace it). The cost is that ensure_link()
    treats that fallback as "found" and never builds a new, real link: once a
    SKU is in this state it stays in it until someone edits Stripe by hand.
    2026-09-26 found one way to reach this state (ensure_link()'s
    orphan-adoption loop tagging a retired link by price with no active
    check, now fixed); this function is the live check for whether it, or
    anything else, has already left a SKU here.
    """
    cat = catalogue()
    stuck = []
    for sku, spec in SELLABLE.items():
        item = cat.get(sku)
        if not item:
            continue
        ok, _why = deliverable(sku, item, spec)
        if not ok:
            continue
        found = find_by_sku("payment_links", sku)
        if found and not found.get("active", True):
            stuck.append(sku)
    return stuck


# ---------------------------------------------------------------- sync
def find_by_sku(kind: str, sku: str, adopt_names: list[str] | None = None) -> dict | None:
    """Stripe has no lookup by metadata, so scan. The catalogue is tiny.

    adopt_name exists because the first two products were created by hand,
    before this script, and carry no sku metadata. Without adopting them by
    name the first --apply would have created a second Virtual Home Consult and
    a second In-Home Reset Day, leaving two live payment links each at the same
    price and no way to tell which one a customer used.
    """
    objs = list_all(kind)

    # A deactivated object is not the one to reuse. This scan used to return
    # whichever matched first, and after 155 duplicate links were deactivated
    # it started handing back dead ones: ensure_link then reported a retired
    # URL as the product's link. The site was spared only because
    # sync_site_links filters on active separately, which is luck, not design.
    for want_active in (True, False):
        for obj in objs:
            if (obj.get("metadata") or {}).get("sku") != sku:
                continue
            if obj.get("active", True) is want_active:
                return obj
    for candidate in (adopt_names or []):
        for obj in objs:
            if obj.get("name") == candidate and not (obj.get("metadata") or {}).get("sku"):
                return obj
    return None


# Listings are fetched once per kind per run. Without this, find_by_sku
# paginated the entire account for every one of 155 SKUs, which turned a
# minute of work into hundreds of round trips and timed the run out before it
# reached sync_site_links. The site then kept stale buy links while Stripe held
# correct ones, which is the drift this whole file exists to prevent.
_CACHE: dict = {}


def list_all(kind: str, params: dict | None = None) -> list:
    """Every object of a kind, not the first hundred of them.

    Stripe caps a page at 100. Every lookup in this file used to take page one
    and treat it as the whole account, which was invisible while the account
    held six products and actively destructive the moment it held more.

    It caused two failures in one run. The idempotency check stopped finding
    products that existed, so a second --apply created a duplicate payment
    link for all 155 SKUs. And sync_site_links concluded that everything past
    page one had been retired, so it stripped the buy button from the book,
    the bundle, the manual, the print pack and both consults: every product
    the business actually sells.

    The docstring on find() below warned about precisely this outcome, in
    those words, and the code under it took one page anyway.
    """
    key = (kind, tuple(sorted((params or {}).items())))
    if key in _CACHE:
        return _CACHE[key]

    out, after = [], None
    while True:
        q = dict(params or {})
        q["limit"] = 100
        if after:
            q["starting_after"] = after
        page = call("GET", kind, q)
        out += page["data"]
        if not page.get("has_more") or not page["data"]:
            break
        after = page["data"][-1]["id"]

    _CACHE[key] = out
    return out


def invalidate(kind: str) -> None:
    """Forget cached listings for a kind after writing one.

    Without this the cache would hand back a view of the account from before
    the write, and the next lookup would decide the object it just created
    does not exist and create it again.
    """
    for k in [k for k in _CACHE if k[0] == kind]:
        del _CACHE[k]


def product_name(item: dict) -> str:
    """The exact Stripe product name ensure_product() sends for a catalogue
    item, pulled out so a name collision can be checked from the catalogue
    alone, with no Stripe credential and no live call.
    """
    name = item["name"]
    if item.get("variant"):
        name = f"{name} ({item['variant']})"
    return name


def duplicate_product_names(cat: dict[str, dict] | None = None) -> dict[str, list[str]]:
    """SKUs that would resolve to the same Stripe product name.

    REVIEW-QA-2026-09-07.md found six live $4 zone packs sharing a bare
    Stripe name ("Dresser Drawers Pack") with the room that disambiguates
    them ("Primary Bedroom", "Kids Bedroom") dropped, three real name
    collisions on the storefront's own line-item text. product_name() above
    already builds the full, disambiguated name from the catalogue; this
    only needs grouping and reporting, no Stripe account to check against.
    """
    cat = cat if cat is not None else catalogue()
    by_name: dict[str, list[str]] = {}
    for sku, item in cat.items():
        by_name.setdefault(product_name(item), []).append(sku)
    return {name: skus for name, skus in by_name.items() if len(skus) > 1}


def ensure_product(sku: str, item: dict, spec: dict, apply_it: bool) -> str | None:
    name = product_name(item)
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
    pid = call("POST", "products", payload)["id"]
    invalidate("products")
    return pid


def ensure_price(product_id: str, sku: str, amount: int, apply_it: bool) -> str | None:
    """Prices are immutable in Stripe. A changed amount means a new price and
    the old one deactivated, never an edit, so history stays truthful."""
    existing = [p for p in list_all("prices", {"product": product_id})
                if p["active"]]
    for p in existing:
        if p["unit_amount"] == amount and p["currency"] == "usd":
            return p["id"]
    if not apply_it:
        return None
    for p in existing:
        call("POST", f"prices/{p['id']}", {"active": False})
    pid = call("POST", "prices", {
        "product": product_id, "currency": "usd", "unit_amount": amount,
        "metadata": {"sku": sku},
    })["id"]
    invalidate("prices")
    return pid


def link_charges(link_id: str, price_id: str) -> bool:
    """Does this payment link actually sell the price we think it does?

    A payment link's line items are immutable in Stripe. A price change
    creates a NEW price and deactivates the old one, but the existing link
    goes on charging the old amount forever, and nothing about the link says
    so: the URL, the sku metadata and the active flag are all unchanged.

    Without this check, dropping the book from $18 to $9.99 updated the site,
    the catalogue and the structured data, left the link charging $18, and
    reported success. A customer would have read $9.99 and been charged 80
    percent more. That is the worst class of defect this file can produce.
    """
    for it in call("GET", f"payment_links/{link_id}/line_items",
                   {"limit": 10})["data"]:
        if (it.get("price") or {}).get("id") == price_id:
            return True
    return False


_LIVE_SLUGS: set | None = None
_LIVE_READ = False


def _live_slugs():
    """What the live site serves, read once per run."""
    global _LIVE_SLUGS, _LIVE_READ
    if not _LIVE_READ:
        _LIVE_READ = True
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import check_live_links
            _LIVE_SLUGS = check_live_links.live_slugs()
        except Exception:                                       # noqa: BLE001
            _LIVE_SLUGS = None
    return _LIVE_SLUGS


REFUSED_RETIREMENTS: list[dict] = []


def ensure_link(sku: str, price_id: str, spec: dict, apply_it: bool) -> str | None:
    found = find_by_sku("payment_links", sku)

    # A link selling the wrong price is worse than no link, so it is retired
    # and rebuilt rather than reused. Stripe gives no way to edit it in place.
    if found and price_id and not link_charges(found["id"], price_id):
        if not apply_it:
            print(f"  {sku:16} link charges the WRONG price, would be replaced")
            return None
        # Ask the live site before retiring anything. The repository is not
        # production: whenever a deploy lags, the live pages still point at
        # this link, and deactivating it takes the buy button down for real
        # customers. That is not a hypothetical, it is what caused the eight
        # day outage that began with this exact branch on the book price.
        slug = (found.get("url") or "").rsplit("/", 1)[-1]
        serving = _live_slugs()
        if serving is None:
            reason = ("the live site could not be read, so whether a "
                      "customer is using it is unknown. Unknown is not unused.")
            print(f"  {sku:16} REFUSING to retire the link: {reason}")
            # A designed-in refusal, not a crash: the tool did exactly what
            # it should, but the only trace used to be this print, gone the
            # moment the terminal closed. Persisted so a later, separate
            # process (the dashboard, the hourly brief) can see the window
            # this run left open: the old link is still live, still charging
            # a retired price, and nobody has been told since.
            REFUSED_RETIREMENTS.append({"sku": sku, "reason": reason})
            return None
        if slug in serving:
            reason = ("the live site is still serving it. Deploy first, "
                      "then rerun. Retiring it now would take a live buy "
                      "button down.")
            print(f"  {sku:16} REFUSING to retire the link: {reason}")
            REFUSED_RETIREMENTS.append({"sku": sku, "reason": reason})
            return None
        print(f"  {sku:16} REPLACING link: it still charges a retired price")
        call("POST", f"payment_links/{found['id']}", {"active": "false"})
        invalidate("payment_links")
        found = None
    if not found:
        # A payment link has no name to adopt by, so match on the price it
        # already sells. Same reason as products: the hand made links predate
        # this script and would otherwise be duplicated.
        for l in list_all("payment_links"):
            if (l.get("metadata") or {}).get("sku"):
                continue
            # A retired link matching by price is still retired. Adopting one
            # here would tag a dead link with this SKU's metadata and hand a
            # customer a "This link is no longer active" page as the buy
            # button, silently, since the URL, active flag and price all look
            # unrelated to this SKU until read this closely.
            if not l.get("active", True):
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
    link = call("POST", "payment_links", payload)
    invalidate("payment_links")
    return link["url"]


def persist_refusals(refused: list[dict] | None = None,
                      path: str | None = None) -> None:
    """Write this run's link-retirement refusals where a later, separate
    process can see them.

    Pure enough to test directly: takes the list rather than reading the
    module global, so ops/preflight.py and ops/tests can prove the dashboard
    and the brief actually surface a REFUSED entry without a Stripe
    credential, by constructing one by hand (REVIEW-COMMERCE-2026-09-07.md
    C17's own acceptance: "a simulated refusal surfaces on the dashboard and
    in the brief").

    Always a full overwrite, never appended: a clean --apply run with
    nothing refused has to clear a stale entry from the last run that did
    refuse, or the dashboard would show a RED row forever after the one
    real cause was already fixed.
    """
    payload = {
        "generated": datetime.datetime.now(datetime.timezone.utc)
                     .isoformat(timespec="seconds"),
        "refused": refused if refused is not None else REFUSED_RETIREMENTS,
    }
    io.open(path or REFUSALS_PATH, "w", encoding="utf-8", newline="").write(
        json.dumps(payload, indent=1, ensure_ascii=False) + "\n")


def sync_site_links(apply_it):
    """Point the site's buy buttons at the live payment links.

    Doing this by hand is how the shop ends up offering a link Stripe has
    retired, or hiding one it has. The site follows Stripe, in one direction,
    so there is only ever one answer to what is buyable.
    """
    # Stripe caps a page at 100 and this used to take the first page as the
    # whole truth. That was harmless while the account held six links. The
    # moment it held more than a hundred, every link that fell off page one
    # looked to this function like a product Stripe had retired, and it
    # stripped the buy button from the site. It did exactly that to the book,
    # the bundle, the manual, the print pack and both consults: the six things
    # that actually sell. Paginate, or the shop quietly loses its checkout the
    # first time the catalogue grows.
    live = {}
    for l in list_all("payment_links"):
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
            # This is the destructive branch and it has been wrong before, so
            # it says so loudly rather than scrolling past in a comma list.
            i.pop("buy")
            changed.append(i["sku"] + " (link removed)")
            print(f"  REMOVING the buy link for {i['sku']}: no active payment "
                  f"link in Stripe carries that sku")

    if changed and apply_it:
        header = "/* Auto-generated catalog. window.CATALOG consumed by shop.js/home. */"
        out = header + chr(10) + "window.CATALOG = " + json.dumps(
            arr, indent=1, ensure_ascii=False) + ";" + chr(10)
        io.open(path, "w", encoding="utf-8", newline="").write(out)
    print("  site buy links: " + (", ".join(changed) if changed else "already in sync"))
    return len(changed)


def main(apply_it: bool) -> int:
    if apply_it and live() and os.environ.get("STRIPE_ALLOW_LIVE") != "1":
        sys.exit("Refusing to write to a LIVE account without STRIPE_ALLOW_LIVE=1")

    cat = catalogue()
    print(f"  mode: {'LIVE' if live() else 'test'}   "
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

    # Structured data is generated from the same catalogue the page renders, so
    # it has to be rebuilt whenever a link or a price moves. Doing it here means
    # a schema that quietly claims last week's price cannot happen.
    if apply_it:
        import subprocess
        subprocess.run([sys.executable,
                        os.path.join(ROOT, "ops", "build_product_schema.py")],
                       check=True)
        # Only a real --apply run can populate REFUSED_RETIREMENTS (the
        # refusal branches in ensure_link() are unreachable on a dry run),
        # so only a real --apply run gets to clear a stale one either.
        persist_refusals()
        if REFUSED_RETIREMENTS:
            print(f"\n  {len(REFUSED_RETIREMENTS)} link retirement(s) "
                  f"REFUSED this run, recorded in "
                  f"{os.path.relpath(REFUSALS_PATH, ROOT)} for the "
                  f"dashboard and the hourly brief.")
    if not apply_it:
        print("\n  Dry run. Re-run with --apply and STRIPE_ALLOW_LIVE=1 to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
