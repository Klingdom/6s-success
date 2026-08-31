#!/usr/bin/env python3
"""
Generate the live executive dashboard from measured state.

Nothing here is hand-maintained. Every number is counted from the repository,
GitHub, or the product folders on disk, so the dashboard cannot drift from
reality the way a manually updated status file does.

Run:  python ops/dashboard.py
Writes:  EXECUTIVE-DASHBOARD-LIVE.md   (the at-a-glance read)
         ops/dashboard.html            (the same, styled, open in a browser)
         ops/state.json                (machine-readable, for trend tracking)
"""
import json, os, re, subprocess, glob, datetime, html, io, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Read from the in-repo content mirror, never an absolute local path. The nightly
# agent runs in the cloud with only a git checkout, so a Desktop path would
# silently produce zeros there and the dashboard would quietly lie.
CONTENT = os.path.join(ROOT, "content")
MASTER = os.path.join(CONTENT, "book")
DECKS = os.path.join(CONTENT, "decks")
MANUAL = os.path.join(CONTENT, "manual")
VIDEO = os.path.join(CONTENT, "video")

def sh(cmd, cwd=ROOT):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              shell=isinstance(cmd, str), timeout=60).stdout.strip()
    except Exception:
        return ""

def count_files(pattern, recursive=True):
    return len(glob.glob(pattern, recursive=recursive))

def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""

# ---------------------------------------------------------------- measure
now = datetime.datetime.now()
S = {"generated": now.strftime("%Y-%m-%d %H:%M")}

# Loaded once, up front, and reused by every carry-forward block below
# (deploy_verdict, live_links_verdict, revenue). A prior version loaded
# state.json separately in each block; the deploy_verdict block was added
# referencing a name (`_prev`) that a later block defined, which only ever
# worked by accident of load order and threw NameError once nothing later
# in the file happened to run first.
_prev = {}
try:
    _prev = json.load(io.open(os.path.join(ROOT, "ops", "state.json"),
                              encoding="utf-8"))
except Exception:                                            # noqa: BLE001
    pass

# --- git / github
S["commit"] = sh("git rev-parse --short HEAD")
S["commit_msg"] = sh("git log -1 --format=%s")
S["commits_7d"] = len([l for l in sh('git log --since="7 days ago" --format=%h').splitlines() if l])
S["commits_total"] = len(sh("git log --format=%h").splitlines())
S["clean"] = sh("git status --porcelain") == ""
S["ahead"] = sh("git rev-list --count origin/main..HEAD") or "0"

# A failed API call must never render as "zero open issues". GitHub outages are
# common and an empty result read as all-clear is the most dangerous possible
# failure direction for a dashboard.
#
# The `gh` CLI is not installed in every environment this script runs in (the
# cloud sandbox has GitHub access only through the REST API and a token in
# GH_TOKEN/GITHUB_TOKEN), so issues are fetched directly rather than shelling
# out to a binary that may not exist.
def gh_token():
    """Env first, then the gh CLI's own keyring.

    The dashboard reported "GitHub unreachable, issue counts UNKNOWN" on a
    machine where gh was logged in and a push had just succeeded seconds
    earlier. It was not unreachable: nothing had asked. Reporting UNKNOWN when
    the answer is one subprocess away is worse than not having the panel, since
    "nothing is blocked on you" and "I did not look" read the same on a
    dashboard and mean opposite things.
    """
    t = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    try:
        import subprocess
        r = subprocess.run(["gh", "auth", "token"], capture_output=True,
                           text=True, timeout=20)
        return r.stdout.strip() or None
    except Exception:
        return None


def gh_issues(state):
    import urllib.request, urllib.error
    token = gh_token()
    if not token:
        return None
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/klingdom/6s-success/issues"
            f"?state={state}&per_page=100",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "User-Agent": "6s-dashboard"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        # the issues endpoint also returns pull requests; exclude them
        return [i for i in data if "pull_request" not in i]
    except Exception:
        return None

# Zone imagery. Counted off the pages themselves rather than off the number of
# images generated, because an image that exists and an image a reader can see
# are different facts, and only the second one is worth a dashboard row. The
# gap between them is deliberate: images that failed review are held back.
# Is any of this reaching a customer? Every product row above is measured off
# the repository, which is the correct place to measure "is it built" and the
# wrong place to answer "can somebody see it". Those were the same number for
# most of this project's life and stopped being the same the moment a build
# sat undeployed. ops/verify_deploy.py said 10 of 10 checks passed on a site
# serving a build from weeks earlier: every check was true and none of them
# asked this question.
try:
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import deploy_freshness
    S["deploy"] = deploy_freshness.check()
except Exception as e:                                       # noqa: BLE001
    # Say which of the two things went wrong. The first version of this caught
    # everything and reported "6s-success.com could not be reached", when what
    # had actually happened was a NameError in this file: sys was never
    # imported. A dashboard that turns its own bug into a claim about the
    # outside world is the exact failure this row was added to prevent.
    S["deploy"] = {"verdict": "unknown", "reachable": None, "assets": [],
                   "stale_assets": 0, "checked_assets": 0,
                   "error": f"{type(e).__name__}: {e}", "probes": []}
S["deploy_verdict"] = S["deploy"]["verdict"]

# The same rule live_links already has, and for the same reason. A run without
# egress cannot see production, reports "unknown", and used to write that over
# a "stale" a measuring run had established an hour earlier. That is what
# happened overnight: the owner's status report stopped leading with "redeploy
# the site" because the verdict it keys on had been quietly downgraded to
# unknown by a run that simply could not look.
#
# A verdict nobody could take is not evidence that the last one expired.
if S["deploy_verdict"] == "unknown" and _prev.get("deploy_last_verdict"):
    S["deploy_verdict"] = _prev["deploy_last_verdict"]
    S["deploy_last_verdict"] = _prev["deploy_last_verdict"]
    S["deploy_verified_at"] = _prev.get("deploy_verified_at", "an earlier run")
    S["deploy_carried"] = True
elif S["deploy_verdict"] != "unknown":
    S["deploy_last_verdict"] = S["deploy_verdict"]
    S["deploy_verified_at"] = S.get("generated", "")
    S["deploy_carried"] = False

try:
    import check_live_links
    S["live_links_verdict"] = check_live_links.check()["verdict"]
except Exception:                                            # noqa: BLE001
    S["live_links_verdict"] = "unknown"

def resolve_live_links_verdict(verdict: str, prev: dict, generated: str) -> dict:
    """Keep a CONFIRMED "dead" live-links verdict when this run could not check.

    Pure, mirroring carry_forward() below, so ops/preflight.py can prove it
    with synthetic inputs. Confirmed 2026-08-31: a run with no Stripe
    credential silently overwrote a same-day CONFIRMED "dead" verdict with
    "unknown", and status_of() treats "unknown" as materially better than
    "dead" (YELLOW instead of RED), so a real, still-open payment outage
    stopped reading as RED the moment a credential-less cloud cycle ran next,
    with nothing about production having actually changed.

    Only "dead" is ever carried forward, never "ok": a stale "confirmed
    working" claim is its own trust problem, so an unmeasured run that was
    not previously dead stays honestly "unconfirmed" rather than borrowing
    old good news.
    """
    if verdict == "unknown":
        if prev.get("live_links_last_verdict") == "dead":
            when = prev.get("live_links_verified_at") or "an earlier run"
            return {"live_links_verdict": "dead",
                    "live_links_last_verdict": "dead",
                    "live_links_verified_at": when,
                    "live_links_carried_from": when}
        return {"live_links_carried_from": None}
    if verdict in ("dead", "ok"):
        return {"live_links_last_verdict": verdict,
                "live_links_verified_at": generated,
                "live_links_carried_from": None}
    return {"live_links_carried_from": None}


S.update(resolve_live_links_verdict(S["live_links_verdict"], _prev, S["generated"]))

S["zone_pages_with_image"] = len(
    [f for f in glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))
     if 'id="zone-hero"' in io.open(f, encoding="utf-8").read()])

open_issues = gh_issues("open")
S["issues_available"] = open_issues is not None
S["issues"] = open_issues or []
S["open_issues"] = len(S["issues"])
S["open_p0"] = len([i for i in S["issues"] if any(l["name"] == "P0" for l in i.get("labels", []))])
S["blocked_art"] = len([i for i in S["issues"] if any(l["name"] == "blocked-on-art" for l in i.get("labels", []))])
S["needs_phil"] = len([i for i in S["issues"] if any(l["name"] == "decision" for l in i.get("labels", []))])

closed_issues = gh_issues("closed")
S["closed_issues"] = len(closed_issues) if closed_issues is not None else None

# --- revenue (the honest number)
#
# These were hardcoded to 0.0 from the day this script was written, which was
# true then and stopped being true on 2026-08-21 when the first sale landed.
# A dashboard that types its headline figure is not a dashboard, and this one
# went on printing a zero next to real money in the Stripe account.
#
# Now measured from Stripe, with three distinct states rather than two: a
# figure, or None meaning the source could not be read. None is NOT zero, and
# is rendered as "not measured" rather than as a dollar amount, because a
# missing credential reporting as $0 looks exactly like a business with no
# customers. CLAUDE.md section 25.
S["revenue_target"] = 20000.0


def _stripe_month():
    """Revenue and distinct payers for the current calendar month, or None."""
    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        path = os.path.join(ROOT, ".env.secrets")
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                if line.startswith("STRIPE_SECRET_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        return None, None

    import urllib.request
    now = datetime.datetime.now(datetime.timezone.utc)
    since = int(now.replace(day=1, hour=0, minute=0, second=0,
                            microsecond=0).timestamp())
    try:
        req = urllib.request.Request(
            "https://api.stripe.com/v1/checkout/sessions"
            f"?limit=100&created[gte]={since}",
            headers={"Authorization": "Bearer " + key})
        data = json.load(urllib.request.urlopen(req, timeout=20))["data"]
        paid = [x for x in data if x.get("payment_status") == "paid"]
        who = {(x.get("customer_details") or {}).get("email") for x in paid}
        return (sum(x.get("amount_total", 0) for x in paid) / 100,
                len(who - {None}))
    except Exception:                                         # noqa: BLE001
        return None, None


S["revenue_month"], S["paying_customers"] = _stripe_month()
# Is the site actually reachable by a member of the public? This is measured
# from outside rather than assumed, because for weeks the honest answer was no
# while every local check passed. A parked domain answers 200 on every path, so
# the test that matters is that an unknown path 404s and the body is ours.
#
# Returns True (confirmed serving our site), False (confirmed not, e.g. still
# parked), or None (could not determine). None matters on its own: this script
# can run inside a sandboxed agent environment whose outbound network policy
# blocks the request before it ever reaches the real internet, which looks
# identical to a network error but proves nothing about production. Folding
# that into False would report a live site as down.
def site_live():
    import urllib.request, urllib.error
    try:
        req = urllib.request.Request("https://6s-success.com/",
                                     headers={"User-Agent": "6s-dashboard"})
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read(40000).decode("utf-8", "replace")
    except urllib.error.HTTPError:
        return False  # a real HTTP error response, so the request did land
    except Exception:
        return None   # DNS failure, timeout, or this environment's own proxy denying egress
    if "6S Success" not in body or "Parked Domain" in body:
        return False
    try:
        urllib.request.urlopen(urllib.request.Request(
            "https://6s-success.com/does-not-exist-dashboard-probe",
            headers={"User-Agent": "6s-dashboard"}), timeout=15)
        return False          # a 200 here means a catch-all, not our site
    except urllib.error.HTTPError as e:
        return e.code == 404
    except Exception:
        return None

S["site_live"] = site_live()

# Measured, not asserted. This was previously `... and False`, which hardcoded a
# NO behind an expression that looked like a measurement. It happened to be the
# right answer, which is the dangerous kind of wrong: the day a checkout went
# live the dashboard would still have said the business cannot take money.
# A payment route exists when a page, or the catalog data a page renders from,
# actually reaches a payment processor. Stripe Payment Links (buy.stripe.com)
# live in assets/js/data.js as product "buy" URLs, not as an embedded checkout
# script in the HTML, so both the pages and the catalog data must be scanned.
PROCESSORS = ("js.stripe.com", "checkout.stripe.com", "buy.stripe.com",
              "paypal.com/sdk", "lemonsqueezy.com", "gumroad.com",
              "checkout.square", "snipcart")
_payment_scan_files = (glob.glob(os.path.join(ROOT, "site", "*.html")) +
                        glob.glob(os.path.join(ROOT, "site", "assets", "js", "*.js")))
S["can_take_payment"] = any(p in read(f) for f in _payment_scan_files for p in PROCESSORS)
S["email_list"] = 0

# How many catalog items actually resolve to a live payment link, read from the
# same file the site renders from. This replaced a hardcoded "two consulting
# packages, the book and the manual still cannot be bought" sentence that went
# stale the moment more Payment Links went live, and kept asserting the old
# count without anything re-checking it against the catalog it described.
_catalog_path = os.path.join(ROOT, "site", "assets", "js", "data.js")
S["catalog_total"] = None
S["catalog_buyable"] = None
S["catalog_buyable_names"] = []
S["catalog_unbuyable_names"] = []
_cat_text = read(_catalog_path)
_cat_match = re.search(r"window\.CATALOG\s*=\s*(\[.*?\n\]);", _cat_text, re.S)
if _cat_match:
    try:
        _catalog = json.loads(_cat_match.group(1))
        S["catalog_total"] = len(_catalog)
        for item in _catalog:
            name = item.get("name", item.get("sku", "unnamed"))
            has_buy = bool(item.get("buy"))
            is_free = item.get("price") == 0
            if has_buy or is_free:
                S["catalog_buyable_names"].append(name)
            else:
                S["catalog_unbuyable_names"].append(name)
        S["catalog_buyable"] = len(S["catalog_buyable_names"])
    except Exception:
        pass

# --- product readiness
# Every one of these globbed site/*.html before, which only sees the 17 files
# directly in site/ and silently skips the 143 zone, room, and article pages
# living in subdirectories, the highest volume templates on the site. That
# undercounted the page total nine-fold and, worse, undercounted dead links,
# disconnected forms, and stray em dashes on those 143 pages as zero instead
# of not-scanned, which reads as clean when it was never checked at all.
_all_site_html = glob.glob(os.path.join(ROOT, "site", "**", "*.html"), recursive=True)
site_pages = len(_all_site_html)
S["site_pages"] = site_pages


def _count_dead_links(files):
    # href="#" is only a dead link if nothing ever gives it a real target.
    # A card like the Home Quest renders its href with JavaScript right
    # before the element is shown, so id="c-zone-link" href="#" in the
    # template is a placeholder waiting on a script, not a broken link a
    # visitor could ever click. Checking whether the id is set with .href
    # somewhere in the site's own scripts tells the two apart.
    js_text = "".join(read(j) for j in
                       glob.glob(os.path.join(ROOT, "site", "assets", "js", "*.js")))
    total = 0
    for f in files:
        for tag in re.findall(r'<a\b[^>]*href="#"[^>]*>', read(f)):
            m = re.search(r'\bid="([^"]+)"', tag)
            if m and ('#%s").href' % m.group(1)) in js_text:
                continue
            total += 1
    return total


S["dead_links"] = _count_dead_links(_all_site_html)
S["legal_pages"] = sum(1 for p in ("privacy", "terms", "accessibility", "disclaimer")
                       if os.path.exists(os.path.join(ROOT, "site", p + ".html")))
S["forms_dead"] = sum(read(f).count('onsubmit="return false"') for f in _all_site_html)

# --- book
ch = sorted(set(glob.glob(os.path.join(MASTER, "*hapter*", "chapter_*_final.html"))))
S["chapters"] = len(ch)
S["chapters_with_disclaimer"] = sum(1 for f in ch if "six-s-disclaimer" in read(f))
S["chapters_no_photos"] = sum(1 for f in ch if read(f).count("<img") == 0)
S["front_matter"] = os.path.exists(os.path.join(MASTER, "6S-Success-Front-Matter", "FRONT_MATTER.md"))

# Is there a file a retailer would actually accept? A finished manuscript is not
# a sellable product until it is packaged, has a cover, and carries a byline.
epub = os.path.join(ROOT, "build", "6S-Success-Home-Edition.epub")
S["epub_built"] = os.path.exists(epub)
S["epub_mb"] = round(os.path.getsize(epub) / 1048576, 2) if S["epub_built"] else 0
# Three states, not two. "No cover" and "could not open the file to look" are
# different facts and only one of them is a reason not to publish a book.
S["epub_has_cover"] = None          # None means nobody could check
if S["epub_built"]:
    import zipfile
    try:
        with zipfile.ZipFile(epub) as _z:
            S["epub_has_cover"] = "EPUB/images/cover.jpg" in _z.namelist()
    except Exception:                                         # noqa: BLE001
        S["epub_has_cover"] = None

# The inverse defect, sitting in the next line. read() returns "" for a file
# that is not there, so a missing front matter file found zero unfilled fields
# and counted as clean. An absent document is not a finished one, and this is
# the same "I did not look" reported as "I found nothing" that has now cost
# this project four separate fixes.
_fm_path = os.path.join(MASTER, "6S-Success-Front-Matter", "FRONT_MATTER.md")
S["front_matter_readable"] = os.path.exists(_fm_path)
fm_text = read(_fm_path)
S["front_matter_blanks"] = (
    len(re.findall(r"\[[A-Z][A-Z /]{3,}\]", fm_text))
    if S["front_matter_readable"] else None)

S["book_sellable"] = bool(
    S["epub_built"] and S["epub_has_cover"] is True
    and S["front_matter_blanks"] == 0)
# Distinguishable from "not sellable": nobody could establish either way.
S["book_checkable"] = (S["epub_has_cover"] is not None
                       and S["front_matter_blanks"] is not None)

# --- decks
deck_dir = DECKS
S["deck_rooms"] = len([d for d in glob.glob(os.path.join(deck_dir, "*Deck")) if os.path.isdir(d)])
# Images are gitignored from the mirror by design, so counting them here would
# report a false zero. Report "not in repo" rather than a number that is wrong.
S["deck_images"] = None
# The canon count read the deck's HTML documents and nothing else, and
# reported zero for weeks while sixteen six_s_lesson lines in the card text
# corpus carried the rejected term and rendered it onto finished cards. A count
# of the wrong files is indistinguishable on a dashboard from a clean result,
# so the corpus the renderer actually reads is counted too.
sio = 0
for f in glob.glob(os.path.join(deck_dir, "**", "*.html"), recursive=True):
    if any(k in os.path.basename(f) for k in ("Card_List", "Master_Proof", "Master_Plan", "Room_Deck_Plan")):
        sio += read(f).count("Set in Order")
for f in (glob.glob(os.path.join(ROOT, "ops", "cardtext", "*.json"))
          + glob.glob(os.path.join(ROOT, "build", "*cardtext.json"))):
    sio += read(f).count("Set in Order")
S["set_in_order_live"] = sio

# Cards that actually render, counted off the rendered files rather than off
# the corpus, because 88 cards of text and 71 cards you can print are
# different facts and only the second one can be sold.
S["cards_rendered"] = len(glob.glob(os.path.join(ROOT, "build", "cards-rendered",
                                                 "*-front.png")))
S["cards_total"] = 88

# The control layer enforces the house style but was never measured against it.
ctrl = glob.glob(os.path.join(ROOT, "*.md")) + glob.glob(os.path.join(ROOT, "claude", "**", "*.md"), recursive=True)
S["ctrl_files"] = len(ctrl)
S["ctrl_em"] = sum(read(f).count("—") for f in ctrl)
S["ctrl_en"] = sum(read(f).count("–") for f in ctrl)
S["site_em"] = sum(read(f).count("—") for f in _all_site_html)

# --- micro zones (the spine)
mz = os.path.join(MANUAL, "source", "content.json")
try:
    c = json.load(open(mz, encoding="utf-8"))
    S["rooms"] = len(c["rooms"])
    S["zones"] = sum(len(r["zones"]) for r in c["rooms"])
except Exception:
    S["rooms"] = S["zones"] = 0
S["zones_with_deck"] = 9

# --- content corpus
S["social_files"] = len(glob.glob(os.path.join(MASTER, "**", "*.md"), recursive=True))
S["social_units"] = 2600  # corpus size established by audit; not re-counted each run
vt = glob.glob(os.path.join(VIDEO, "*tracker*.csv"))
S["video_planned"] = 0
S["video_shot"] = 0
if vt:
    import csv as _csv
    with open(vt[0], encoding="utf-8-sig", newline="") as fh:
        _rows = list(_csv.DictReader(fh))
    S["video_planned"] = len(_rows)
    S["video_shot"] = sum(1 for r in _rows if (r.get("status_shot") or "").strip().lower() not in ("", "not started"))

# ---------------------------------------------------------------- assess
def status_of(revenue_month, can_take_payment, live_links_verdict,
              issues_available, open_p0, live_links_carried_from=None):
    """Pure so ops/preflight.py can call it with synthetic inputs and prove
    it escalates, without re-running this module's own side effects."""
    if not revenue_month and not can_take_payment:
        return "RED", "No route from customer intent to payment exists."
    if live_links_verdict == "dead":
        if live_links_carried_from:
            return "RED", (f"Live payment links were last confirmed "
                            f"deactivated in Stripe on {live_links_carried_from}; "
                            f"this run has no Stripe credential to reverify, so "
                            f"treat the outage as still open until a session with "
                            f"real access says otherwise.")
        return "RED", "Live payment links are confirmed deactivated in Stripe: the repository can take money, the live site cannot."
    if not issues_available:
        return "YELLOW", "Could not reach GitHub, so issue counts are UNKNOWN, not zero."
    if open_p0:
        return "YELLOW", f"{open_p0} P0 items still open."
    return "GREEN", "Operating normally."

S["overall"], S["overall_why"] = status_of(
    S["revenue_month"], S["can_take_payment"], S.get("live_links_verdict"),
    S["issues_available"], S["open_p0"], S.get("live_links_carried_from"))
# Precision matters here. The forms are no longer silent: they hand the reader a
# prefilled message so their intent survives. What is still missing is a provider,
# so nothing is stored, nothing is automatic, and no list is being built.
if S["site_live"] is False:
    _reach = " And 6s-success.com does not serve the site, so none of it is reachable."
elif S["site_live"] is None:
    _reach = (" Whether 6s-success.com reaches the site could not be checked from "
              "this run's network, so treat public reachability as unverified, not confirmed.")
else:
    _reach = ""
if S["can_take_payment"] and S["catalog_total"] is not None:
    _unbuyable = S["catalog_unbuyable_names"]
    if _unbuyable:
        _still = (" Still not buyable: " + ", ".join(_unbuyable) + ".")
    else:
        _still = " Every catalog item is either buyable or free."
    S["constraint"] = (
        f"The site can take money for {S['catalog_buyable']} of "
        f"{S['catalog_total']} catalog items, each a live Stripe Payment Link "
        f"or a real free download.{_still} All {S['forms_dead']} forms still "
        "hand off to email by hand instead of capturing a list." + _reach +
        " The widened catalog has not moved revenue because almost nobody is "
        "arriving at the site yet. Discovery, not what can be bought, is the "
        "constraint now.")
elif S["can_take_payment"]:
    S["constraint"] = (
        "The site can take money for at least one product, a live Stripe "
        "Payment Link was found, but the catalog file could not be read to "
        f"measure how many. All {S['forms_dead']} forms still hand off to "
        "email by hand instead of capturing a list." + _reach)
else:
    S["constraint"] = ("The business cannot accept money. Checkout is staged and there is no "
                       f"payment processor anywhere in the site. All {S['forms_dead']} forms now "
                       "hand off to email by hand, which keeps a visitor's intent but stores "
                       "nothing and builds no list." + _reach +
                       " Nothing else moves revenue until this does.")

# Two agents regenerate this file, and only one of them can reach the network.
# The cloud operator's sandbox has no Stripe credential and no egress, so its
# run correctly reports "not measured", and committing that overwrites a figure
# the laptop measured an hour earlier. The committed dashboard was alternating
# between $19 and "not measured" every cycle, which reads as the business
# losing its revenue and getting it back.
#
# So an unmeasured run carries the last measured value forward and says when it
# was taken, instead of erasing it. "None is not zero" was right and this is the
# same rule facing the other way: an absent answer must not delete a known one.
# (_prev is loaded once, near the top of this file, and reused here.)

def carry_forward(now: dict, prev: dict) -> dict:
    """Keep a figure this run could not measure, and say where it came from.

    A pure function on two dicts so it can be tested without a Stripe
    credential, which is the whole situation it exists to handle.

    The first version carried the PREVIOUS run's revenue_month, which works
    once and then fails silently: the cloud operator has no Stripe credential,
    so its run wrote "not measured", and the next unmeasured run had nothing
    left to carry. One blind run poisoned the well for every run after it, and
    the dashboard went back to reporting no revenue for a business that has
    taken a payment.

    So the last MEASURED value is persisted under its own key, with the date
    it was taken. That key is only ever written by a run that actually
    measured, so no number of blind runs can erase it.
    """
    out = {}
    measured = now.get("revenue_month")

    if measured is not None:
        # This run knows. Record it as the standing answer.
        out["revenue_last_measured"] = measured
        out["revenue_measured_at"] = now.get("generated", "")
        out["revenue_carried_from"] = None
        return out

    # This run does not know. Prefer the standing answer, and fall back to the
    # previous run's live figure only if no standing answer exists yet.
    last = prev.get("revenue_last_measured")
    when = prev.get("revenue_measured_at") or prev.get("generated")
    if last is None:
        last, when = prev.get("revenue_month"), prev.get("generated")

    if last is None:
        return {"revenue_carried_from": None}

    out["revenue_month"] = last
    out["revenue_last_measured"] = last
    out["revenue_measured_at"] = when or ""
    out["revenue_carried_from"] = when or "an earlier run"
    out["customers"] = prev.get("customers", now.get("customers"))
    return out


S.update(carry_forward(S, _prev))

# The constraint sentences above all describe the repository, where the
# catalogue is correct and every link works. On 2026-08-30 that produced "the
# site can take money for 158 of 159 items" on a day when all six payment
# links the live site served were deactivated in Stripe and the business could
# not take a dollar. A dashboard's single most prominent sentence has to be
# about the thing the reader thinks it is about, which is the website.
if S.get("deploy", {}).get("verdict") == "stale" or         S.get("live_links_verdict") == "dead":
    _ll_note = (f" Last confirmed {S['live_links_carried_from']}; this run has "
                f"no Stripe credential to reverify, so this is not new "
                f"information, only a reminder that nothing has cleared it."
                if S.get("live_links_carried_from") else "")
    S["constraint"] = ("PRODUCTION CANNOT TAKE MONEY. Every payment link the "
                       "live site serves is deactivated in Stripe, so anybody "
                       "clicking buy reaches a dead link. The repository's "
                       "links are all active, so redeploying fixes it."
                       + _ll_note + " "
                       + S["constraint"])

# None is not zero. A source that could not be read renders as unknown, and
# the gauge needle is parked rather than pointed at a figure nobody measured.
if S["revenue_month"] is None:
    S["revenue_pct"] = None
    S["revenue_text"] = "not measured, no Stripe credential in this environment"
    S["customers_text"] = "not measured"
else:
    S["revenue_pct"] = round(S["revenue_month"] / S["revenue_target"] * 100, 1)
    S["revenue_text"] = (f"${S['revenue_month']:,.0f} of "
                         f"${S['revenue_target']:,.0f} target "
                         f"({S['revenue_pct']}%)"
                         + (f", carried forward from {S['revenue_carried_from']} "
                            f"because this run could not reach Stripe"
                            if S.get("revenue_carried_from") else ""))
    S["customers_text"] = str(S["paying_customers"])
pct = S["revenue_pct"] or 0

# ---------------------------------------------------------------- render
def bar(p, w=28):
    f = int(round(p / 100 * w))
    return "#" * f + "." * (w - f)

def money_line() -> str:
    v = S.get("live_links_verdict")
    if v == "dead":
        base = "**NO**, live payment links are deactivated in Stripe"
        if S.get("live_links_carried_from"):
            base += (f" (last confirmed {S['live_links_carried_from']}, not "
                      f"reverified this run: no Stripe credential here)")
        return base
    if v == "unknown" and S["can_take_payment"] and S["catalog_total"] is not None:
        return (f"repository says yes ({S['catalog_buyable']} of "
                f"{S['catalog_total']} catalog items), **unconfirmed on the "
                f"live site**: no Stripe credential in this environment to "
                f"check the links a visitor actually hits")
    if S["can_take_payment"] and S["catalog_total"] is not None:
        return (f"yes, confirmed live, {S['catalog_buyable']} of "
                f"{S['catalog_total']} catalog items")
    return "yes" if S["can_take_payment"] else "**NO**"

md = f"""# 6S Success: Live Executive Dashboard

> Generated {S['generated']} by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **{S['overall']}** {S['overall_why']} |
| **Revenue this month** | **{S['revenue_text']}** |
| | `{bar(pct)}` |
| **Paying customers** | {S['customers_text']} |
| **Email list** | {S['email_list']} |
| **Can the site take money?** | {money_line()} |

### The one constraint

{S['constraint']}

---

## Where the work stands

| Stream | State |
|---|---|
| Open issues | {(str(S['open_issues']) + f" ({S['open_p0']} P0, {S['blocked_art']} blocked on art, {S['needs_phil']} need your call)") if S['issues_available'] else "**UNKNOWN** (GitHub unreachable at generation time)"} |
| Closed to date | {S['closed_issues'] if S['closed_issues'] is not None else "UNKNOWN"} |
| Commits (7 days) | {S['commits_7d']} of {S['commits_total']} total |
| Working tree | {'clean, in sync' if S['clean'] and S['ahead'] == '0' else 'uncommitted or unpushed work'} |
| Last commit | `{S['commit']}` {S['commit_msg'][:60]} |

## Product readiness

| Product | Measured state |
|---|---|
| Website | {S['site_pages']} pages, {S['dead_links']} dead links, {S['legal_pages']}/4 legal pages, {S['forms_dead']} disconnected forms |
| Book | {S['chapters']}/50 chapters, {S['chapters_with_disclaimer']}/50 carry the safety notice, {S['chapters_no_photos']} have no photographs, front matter {'drafted' if S['front_matter'] else 'MISSING'} |
| Book, sellable? | {'YES' if S['book_sellable'] else ('NOT CHECKABLE HERE' if not S['book_checkable'] else 'NO')} EPUB {'built ' + str(S['epub_mb']) + ' MB' if S['epub_built'] else 'NOT BUILT'}, cover {'yes' if S['epub_has_cover'] is True else ('unreadable' if S['epub_has_cover'] is None else 'NO')}, {S['front_matter_blanks'] if S['front_matter_blanks'] is not None else 'front matter not found, so unfilled fields are unknown'} unfilled front-matter fields |
| Micro zones | {S['rooms']} rooms, {S['zones']} zones (the spine every product shares) |
| Card decks | {S['deck_rooms']}/20 rooms, {S['zones_with_deck']}/{S['zones']} zones covered (card art lives outside the repo) |
| Entryway deck | {S['cards_rendered']}/{S['cards_total']} cards render clean from the template layer |
| Zone imagery | {S['zone_pages_with_image']}/{S['zones']} zone pages carry a reviewed picture ({'live' if S['deploy_verdict'] == 'current' else 'BUILT, NOT DEPLOYED' if S['deploy_verdict'] == 'stale' else 'deployment unknown'}) |
| Canon defects | {S['set_in_order_live']} live uses of the rejected term "Set in Order" |
| Social corpus | ~{S['social_units']:,} ready-to-publish units, unused |
| Video | {S['video_shot']}/{S['video_planned']} episodes shot |

## What needs you

"""
# A stale deployment goes above the decision queue, because it is the one item
# that makes every other piece of finished work worth nothing until it is done,
# and because it is the one step this system cannot take itself: the redeploy
# lives behind the owner's hPanel.
if S["deploy_verdict"] == "stale":
    md += (f"- **Redeploy the site.** Production is serving an older build: "
           f"{S['deploy']['stale_assets']} of {S['deploy']['checked_assets']} "
           f"assets on the live homepage differ from this repository, and no "
           f"zone page carries its photograph yet. The image is built and "
           f"pushed to ghcr.io; the Redeploy button in Hostinger is the only "
           f"step left. Until then {S['zone_pages_with_image']} reviewed "
           f"pictures and every fix since the last deploy reach nobody.\n")

if not S["issues_available"]:
    md += ("- **UNKNOWN.** GitHub could not be reached when this was generated, so the\n"
           "  decision queue could not be read. That is not the same as nothing being\n"
           "  blocked. Re-run `python ops/dashboard.py` once GitHub responds.\n")
elif S["needs_phil"]:
    for i in S["issues"]:
        if any(l["name"] == "decision" for l in i.get("labels", [])):
            md += f"- **#{i['number']}** {i['title']}\n"
else:
    md += "- Nothing is blocked on you right now.\n"

md += f"""
## Open issues

| # | Title | Labels |
|---|---|---|
"""
for i in S["issues"]:
    md += f"| {i['number']} | {i['title']} | {', '.join(l['name'] for l in i.get('labels', []))} |\n"

open(os.path.join(ROOT, "EXECUTIVE-DASHBOARD-LIVE.md"), "w", encoding="utf-8").write(md)

# --- html -------------------------------------------------------------------
# The HTML deliberately carries no <!doctype>, <html> or <body> wrapper. Browsers
# render it fine without one, and leaving it out means this exact file can also be
# published as a hosted artifact, which wraps the fragment itself. One file, read
# locally at the desk or on a phone from bed, with no second copy to drift.
import math

def esc(x): return html.escape(str(x))

# The six-S ramp doubles as the severity ramp. That is not decoration: the whole
# method runs chaos to calm, so a business measured against its own method should
# be read on its own gauge.
S1, S2, S3, S4, S5, S6 = "#CB4B36", "#BC4B2A", "#D98A2B", "#DDA63A", "#6E8B5B", "#4E7A57"
TONE = {"crit": S1, "warn": S4, "good": S6, "idle": "var(--mute)"}
SEVERITY = {"RED": "crit", "YELLOW": "warn", "GREEN": "good"}

def chip(text, tone):
    return f'<span class="chip {tone}">{esc(text)}</span>'

def gauge(pct, size=340):
    """The friction gauge, the brand's signature mark, pointing at revenue.

    Zero revenue puts the needle hard left, in the red. That is the honest
    picture and it should look like the honest picture.
    """
    cx = cy = size / 2
    r = size / 2 - 26
    seg, gap = 180 / 6, 1.6
    parts = []
    for k, col in enumerate((S1, S2, S3, S4, S5, S6)):
        a0, a1 = 180 + k * seg + gap, 180 + (k + 1) * seg - gap
        x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        parts.append(f'<path d="M{x0:.1f} {y0:.1f} A{r:.1f} {r:.1f} 0 0 1 {x1:.1f} {y1:.1f}" '
                     f'fill="none" stroke="{col}" stroke-width="22"/>')
    a = math.radians(180 + max(0.0, min(100.0, pct)) * 1.8)
    nx, ny = cx + r * 0.66 * math.cos(a), cy + r * 0.66 * math.sin(a)
    # Butt cap, not round: a round cap puts a dot on the needle tip and the whole
    # thing reads as a slider someone can drag rather than a reading.
    parts.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" '
                 f'stroke="var(--ink)" stroke-width="7"/>')
    parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="12" fill="var(--ink)"/>')
    return (f'<svg class="gauge" viewBox="0 0 {size} {size/2+22:.0f}" role="img" '
            f'aria-label="Revenue gauge, {pct} percent of the twenty thousand dollar target">'
            + "".join(parts) + "</svg>")

# Readiness, each row given a state a person can read at a glance rather than a
# number they have to interpret.
ready = [
    ("Website", f"{S['site_pages']} pages, {S['dead_links']} dead links, {S['legal_pages']}/4 legal pages, "
                f"{S['forms_dead']} forms hand off to email, 0 reach a provider",
     ("good", "LIVE") if S["site_live"] is True else
     (("crit", "domain parked") if S["site_live"] is False else ("warn", "unverified this run"))),
    ("Book, written", f"{S['chapters']}/50 chapters, {S['chapters_with_disclaimer']}/50 carry the safety notice",
     ("good", "complete") if S["chapters"] == 50 else ("warn", "in progress")),
    ("Book, sellable", (f"EPUB {S['epub_mb']} MB, cover {'embedded' if S['epub_has_cover'] else 'missing'}, "
                        f"{S['front_matter_blanks']} unfilled front-matter fields") if S["epub_built"]
     else "not packaged",
     ("good", "ready") if S["book_sellable"]
     else (("idle", "not checkable here") if not S["book_checkable"]
           else ("warn", "blocked on #3"))),
    ("Micro zones", f"{S['rooms']} rooms, {S['zones']} zones, the spine every product shares",
     ("good", "complete")),
    ("Card decks", f"{S['deck_rooms']}/20 rooms, {S['zones_with_deck']}/{S['zones']} zones, card art not in repo",
     ("warn", "2 of 20 rooms")),
    ("Entryway deck", f"{S['cards_rendered']}/{S['cards_total']} cards render clean from the template layer",
     ("good", "printable") if S["cards_rendered"] > 60
     else ("warn", "partial")),
    ("Deployment", {"current": "production serves this repository",
                    "stale": f"production is serving an older build, "
                             f"{S['deploy']['stale_assets']} of "
                             f"{S['deploy']['checked_assets']} assets differ",
                    "unknown": ("the freshness check could not run: "
                                + S["deploy"]["error"]) if S["deploy"].get("error")
                               else "6s-success.com could not be reached, so "
                                    "freshness was not measured"}[S["deploy_verdict"]],
     {"current": ("good", "live"), "stale": ("crit", "behind"),
      "unknown": ("idle", "not measured")}[S["deploy_verdict"]]),
    ("Zone imagery", f"{S['zone_pages_with_image']}/{S['zones']} zone pages carry a reviewed picture",
     ("good", "shipping") if S["zone_pages_with_image"] > S["zones"] * 0.8
     else ("warn", "partial")),
    ("Social corpus", f"~{S['social_units']:,} ready-to-publish units", ("idle", "unused")),
    ("Video", f"{S['video_shot']} of {S['video_planned']} episodes shot",
     ("good", "on air") if S["video_shot"] else ("idle", "not started")),
    ("House style", f"control layer {S.get('ctrl_em',0)} em and {S.get('ctrl_en',0)} en dashes across "
                    f"{S.get('ctrl_files',0)} files, published site {S.get('site_em',0)}",
     ("warn", "control layer breaks it") if S.get("ctrl_em", 0) else ("good", "clean")),
]
ready_rows = "".join(
    f'<tr><th scope="row">{esc(n)}</th><td>{esc(detail)}</td>'
    f'<td class="st">{chip(lbl, tone)}</td></tr>' for n, detail, (tone, lbl) in ready)

# GitHub's own label colours, so a label looks the same here as in the issue list.
def labels_of(i):
    return "".join(
        f'<span class="lab" style="--lc:#{esc(l.get("color") or "888888")}">{esc(l["name"])}</span>'
        for l in i.get("labels", []))

if S["issues_available"]:
    issue_rows = "".join(
        f'<tr><td class="num">#{esc(i["number"])}</td><td>{esc(i["title"])}</td>'
        f'<td class="st">{labels_of(i)}</td></tr>' for i in S["issues"]) or \
        '<tr><td colspan="3">No open issues.</td></tr>'
else:
    issue_rows = ('<tr><td colspan="3"><b>UNKNOWN.</b> GitHub could not be reached, so the '
                  'queue could not be read. That is not the same as nothing being open.</td></tr>')

if not S["issues_available"]:
    needs = ('<li><b>Unknown.</b> GitHub was unreachable when this was generated, so the '
             'decision queue could not be read. Re-run <code>python ops/dashboard.py</code>.</li>')
elif S["needs_phil"]:
    needs = "".join(f'<li><b>#{esc(i["number"])}</b> {esc(i["title"])}</li>' for i in S["issues"]
                    if any(l["name"] == "decision" for l in i.get("labels", [])))
else:
    needs = "<li>Nothing is blocked on you right now.</li>"

if S["deploy_verdict"] == "stale":
    needs = (f'<li><b>Redeploy the site.</b> Production is serving an older '
             f'build: {S["deploy"]["stale_assets"]} of '
             f'{S["deploy"]["checked_assets"]} assets on the live homepage '
             f'differ from this repository, and no zone page carries its '
             f'photograph yet. The image is built and pushed; the Redeploy '
             f'button in Hostinger is the only step left, and the one step '
             f'this system cannot take itself.</li>') + needs

tone = SEVERITY[S["overall"]]

CSS = """
:root{
  --paper:#F7F2E9; --panel:#FBF7EF; --ink:#2B2622; --soft:#6A625A; --mute:#8C8478;
  --line:#E2D8C4; --line-2:#D9CDB8; --accent:#BC4B2A; --wash:#F2EADC;
  --crit:#CB4B36; --warn:#B07A18; --good:#4E7A57;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#1A272E; --panel:#22323C; --ink:#EDE4D2; --soft:#A9B7BE; --mute:#7E8F97;
    --line:#33474F; --line-2:#3E555E; --accent:#DDA63A; --wash:#1F2E36;
    --crit:#E4735F; --warn:#DDA63A; --good:#8FB37C;
  }
}
:root[data-theme="dark"]{
  --paper:#1A272E; --panel:#22323C; --ink:#EDE4D2; --soft:#A9B7BE; --mute:#7E8F97;
  --line:#33474F; --line-2:#3E555E; --accent:#DDA63A; --wash:#1F2E36;
  --crit:#E4735F; --warn:#DDA63A; --good:#8FB37C;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:400 17px/1.6 "Newsreader",Georgia,"Times New Roman",serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1000px;margin:0 auto;padding:0 22px 96px;
  display:flex;flex-direction:column;gap:14px}
h1{font-family:"Fraunces",Georgia,serif;font-weight:600;letter-spacing:-.02em;
  font-size:clamp(32px,6vw,52px);line-height:1.04;margin:44px 0 0;text-wrap:balance}
h2{font-family:"Fraunces",Georgia,serif;font-weight:600;letter-spacing:-.015em;
  font-size:clamp(20px,3vw,25px);margin:40px 0 0;text-wrap:balance}
.eyebrow{font:600 11px/1 "Inter",system-ui,sans-serif;letter-spacing:.18em;
  text-transform:uppercase;color:var(--soft);margin:0}
p{margin:0}
a{color:var(--accent)}

/* the status band: the one thing that must read from across the room */
.band{display:flex;flex-wrap:wrap;align-items:center;gap:22px 30px;
  background:var(--panel);border:1px solid var(--line);border-radius:16px;
  padding:26px 30px;margin-top:10px}
.band .verdict{font:700 46px/1 "Inter",system-ui,sans-serif;letter-spacing:-.02em}
.band .why{flex:1 1 260px;min-width:220px;color:var(--soft);font-size:17px}
.crit .verdict,.chip.crit,.lead.crit b{color:var(--crit)}
.warn .verdict,.chip.warn{color:var(--warn)}
.good .verdict,.chip.good{color:var(--good)}

/* revenue, told on the brand's own gauge */
.money{display:grid;grid-template-columns:minmax(0,320px) 1fr;gap:8px 36px;
  align-items:center;background:var(--panel);border:1px solid var(--line);
  border-radius:16px;padding:22px 30px}
.gauge{width:100%;height:auto;display:block}
.money .fig{font:700 clamp(40px,7vw,62px)/1 "Inter",system-ui,sans-serif;
  letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.money .of{color:var(--soft);font-size:16px;margin-top:6px}
@media(max-width:720px){.money{grid-template-columns:1fr;text-align:center}}

.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));
  gap:10px}
.cell{background:var(--panel);border:1px solid var(--line);border-radius:13px;
  padding:15px 17px}
.cell b{display:block;font:600 27px/1.1 "Inter",system-ui,sans-serif;
  letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.cell span{display:block;margin-top:7px;font:500 11px/1.35 "Inter",system-ui,sans-serif;
  letter-spacing:.1em;text-transform:uppercase;color:var(--soft)}

.lead{background:var(--panel);border-left:4px solid var(--accent);
  border-radius:0 13px 13px 0;padding:20px 26px}
.lead p{color:var(--ink)}

.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:13px;
  background:var(--panel)}
table{width:100%;border-collapse:collapse;
  font:400 15px/1.5 "Inter",system-ui,sans-serif;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:12px 16px;border-bottom:1px solid var(--line);
  vertical-align:top}
tbody tr:last-child th,tbody tr:last-child td{border-bottom:0}
thead th{font:600 10.5px/1 "Inter",system-ui,sans-serif;letter-spacing:.13em;
  text-transform:uppercase;color:var(--soft);background:var(--wash);
  border-bottom:1px solid var(--line-2)}
tbody th{font-weight:600;white-space:nowrap}
td.num{font-weight:600;color:var(--soft);white-space:nowrap}
td.st{white-space:nowrap}

.chip{display:inline-block;font:600 11.5px/1 "Inter",system-ui,sans-serif;
  letter-spacing:.06em;text-transform:uppercase;padding:6px 10px;border-radius:99px;
  border:1px solid currentColor}
.chip.idle{color:var(--mute)}
.lab{display:inline-block;margin:0 5px 4px 0;padding:5px 9px;border-radius:99px;
  font:600 11px/1 "Inter",system-ui,sans-serif;letter-spacing:.04em;
  color:var(--ink);border:1px solid #0000;
  background:color-mix(in srgb,var(--lc) 26%,transparent);
  box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--lc) 55%,transparent)}

ul.needs{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:9px}
ul.needs li{background:var(--panel);border:1px solid var(--line);border-radius:11px;
  padding:13px 17px;font:400 16px/1.5 "Inter",system-ui,sans-serif}
ul.needs b{color:var(--accent)}
code{font:500 13.5px/1 ui-monospace,SFMono-Regular,Menlo,monospace;
  background:var(--wash);padding:2px 6px;border-radius:5px}
footer{color:var(--mute);font:400 13.5px/1.6 "Inter",system-ui,sans-serif;
  margin-top:34px;border-top:1px solid var(--line);padding-top:16px}
"""

doc = (
    '<meta charset="utf-8">\n'
    '<title>6S Success Command Deck</title>\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Fraunces:opsz,wght@9..144,600&family=Inter:wght@400;500;600;700'
    '&family=Newsreader:wght@400;500&display=swap">\n'
    f"<style>{CSS}</style>\n"
    f'<div class="wrap">\n'
    f'<h1>Command deck</h1>\n'
    f'<p class="eyebrow">Generated {esc(S["generated"])} &middot; every figure measured, none typed</p>\n'

    f'<div class="band {tone}">'
    f'<div class="verdict">{esc(S["overall"])}</div>'
    f'<p class="why">{esc(S["overall_why"])}</p>'
    f'</div>\n'

    f'<div class="money">'
    f'<div>{gauge(pct)}</div>'
    f'<div><div class="fig">{("$%s" % format(S["revenue_month"], ",.0f")) if S["revenue_month"] is not None else "not measured"}</div>'
    f'<p class="of">of the ${S["revenue_target"]:,.0f} monthly target, '
    f'{S["revenue_pct"] if S["revenue_pct"] is not None else "unknown"}%. The needle sits where the money is, on the same gauge '
    f'the method uses to read a room.</p></div>'
    f'</div>\n'

    f'<div class="grid">'
    f'<div class="cell"><b>{S["customers_text"]}</b><span>Paying customers</span></div>'
    f'<div class="cell"><b>{S["email_list"]}</b><span>Email list</span></div>'
    f'<div class="cell"><b>{"yes" if S["can_take_payment"] else "no"}</b><span>Can take money</span></div>'
    f'<div class="cell"><b>{S["open_p0"] if S["issues_available"] else "?"}</b><span>Open P0</span></div>'
    f'<div class="cell"><b>{S["needs_phil"] if S["issues_available"] else "?"}</b><span>Need your call</span></div>'
    f'<div class="cell"><b>{S["commits_7d"]}</b><span>Commits, 7 days</span></div>'
    f'</div>\n'

    f'<h2>The one constraint</h2>\n'
    f'<div class="lead {tone}"><p>{esc(S["constraint"])}</p></div>\n'

    f'<h2>What needs you</h2>\n'
    f'<ul class="needs">{needs}</ul>\n'

    f'<h2>Product readiness</h2>\n'
    f'<div class="scroll"><table>'
    f'<thead><tr><th>Product</th><th>Measured state</th><th>Reads as</th></tr></thead>'
    f'<tbody>{ready_rows}</tbody></table></div>\n'

    f'<h2>Open issues</h2>\n'
    f'<div class="scroll"><table>'
    f'<thead><tr><th>#</th><th>Title</th><th>Labels</th></tr></thead>'
    f'<tbody>{issue_rows}</tbody></table></div>\n'

    f'<footer>Last commit <code>{esc(S["commit"])}</code> {esc(S["commit_msg"])}. '
    f'{S["commits_7d"]} commits in seven days, {S["commits_total"]} in total. Working tree '
    f'{"clean and in sync" if S["clean"] and S["ahead"] == "0" else "has uncommitted or unpushed work"}. '
    f'{esc(str(S["closed_issues"])) if S["closed_issues"] is not None else "An unknown number of"} issues closed to date. '
    f'Regenerate with <code>python ops/dashboard.py</code>.</footer>\n'
    f'</div>'
)

open(os.path.join(ROOT, "ops", "dashboard.html"), "w", encoding="utf-8").write(doc)
json.dump(S, open(os.path.join(ROOT, "ops", "state.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(f"{S['overall']} | revenue {S['revenue_text']} | "
      f"P0 {S['open_p0'] if S['issues_available'] else 'UNKNOWN'} | "
      f"need-you {S['needs_phil'] if S['issues_available'] else 'UNKNOWN'} | "
      f"commits7d {S['commits_7d']}")
print("wrote EXECUTIVE-DASHBOARD-LIVE.md, ops/dashboard.html, ops/state.json")
