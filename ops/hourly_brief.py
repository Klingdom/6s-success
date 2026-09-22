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

import check_live_links as cll                                # noqa: E402
import stripe_brand                                           # noqa: E402
import stripe_catalog as sc                                   # noqa: E402
import stripe_dedupe                                          # noqa: E402

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
        # Revenue is read from CHARGES, not checkout sessions. A Payment Link
        # session is created when somebody opens the link and expires whether
        # or not they pay; on this account every session reads "unpaid" even
        # for the one real sale (ch_3U722U6OlZmKL8mF1Hooe, $19, 2026-08-21).
        # dashboard.py was fixed for this on 2026-09-10; this reader was not,
        # so the four-hourly email said "$0 / 30d, 0 sale(s)" for the whole
        # window that sale sat inside. Found 2026-09-14 against the live API.
        sessions = get(f"checkout/sessions?limit=100&created[gte]={since}")["data"]
        charges = get(f"charges?limit=100&created[gte]={since}")["data"]
        # Lifetime alongside the 30-day window. The one real sale (2026-08-21)
        # leaves the trailing window on 2026-09-20, after which "$0 / 30d"
        # alone reads like a broken instrument rather than a quiet month.
        ever = get("charges?limit=100")["data"]
        paid = [c for c in charges
                if c.get("status") == "succeeded" and c.get("paid")
                and not c.get("refunded")
                and (c.get("amount_refunded") or 0)
                < (c.get("amount_captured") or c.get("amount") or 0)]
        links = [l for l in get("payment_links?limit=100")["data"] if l.get("active")]
        bal = get("balance")
        avail = sum(b["amount"] for b in bal.get("available", [])) / 100
        pend = sum(b["amount"] for b in bal.get("pending", [])) / 100
        return {
            "paid_30d": len(paid),
            "revenue_30d": sum((c.get("amount_captured") or c.get("amount") or 0)
                               - (c.get("amount_refunded") or 0)
                               for c in paid) / 100,
            "checkouts_started_30d": len(sessions),
            "revenue_lifetime": sum((c.get("amount_captured") or c.get("amount") or 0)
                                    - (c.get("amount_refunded") or 0)
                                    for c in ever
                                    if c.get("status") == "succeeded" and c.get("paid")) / 100,
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


def deploy_staleness_summary(st: dict) -> tuple[bool, list[str]]:
    """Whether production is confirmed behind the repository, from the one
    signal this job can read without a VPS deploy key: ops/dashboard.py's
    own carried-forward deploy_verdict in ops/state.json.

    Written 2026-09-17. Production sat behind the repository by 95 commits
    for a stretch that included two customer-facing trust fixes, while
    ops/state.json read deploy_verdict: stale and the dashboard's own text
    said "Redeploy the site" the whole time (ops/NIGHTLY-LOG.md, 2026-09-17:
    "the instrument worked and the loop did not"). The watcher was real;
    nothing routed its line to a reader who could act on it. This is that
    routing, the same shape payment_link_summary() already gives a dead
    Stripe link: surfaced in the one automated, credentialed mail Phil
    actually reads, not only in a dashboard file nobody was pointed back to.

    This job holds no deploy key, so the ask stays a message, not a fix: a
    session with VPS access still has to run ops/deploy.py or Phil still has
    to click Redeploy. problem is True only for a genuinely confirmed
    mismatch (deploy_verdict == "stale"), never for "unknown", which can be
    perfectly ordinary (nothing with VPS access has run recently) and must
    not read as an outage it was never evidence for, CLAUDE.md 0.4.
    """
    verdict = st.get("deploy_verdict")
    checked = st.get("deploy_verified_at") or "an unknown time"
    if verdict == "stale":
        carried = (" (last CONFIRMED current at that time, not measured "
                   "this run)" if st.get("deploy_carried") else "")
        return True, [f"  BEHIND  production does not match the repository. "
                      f"Last confirmed matching: {checked}{carried}. Needs a "
                      f"Redeploy click, or a session with VPS access running "
                      f"ops/deploy.py."]
    if verdict == "current":
        return False, [f"  OK  production matches the repository "
                       f"(confirmed {checked})"]
    return False, [f"  UNCHECKED  deploy state not measured this run "
                   f"(verdict: {verdict or 'none recorded'})"]


def payment_link_summary(links: dict) -> tuple[bool, list[str]]:
    """Turn check_live_links.check()'s result into (problem, lines).

    Written 2026-09-09. check_live_links.py was built specifically to catch
    the 2026-08-30 outage shape (a deactivated Stripe link still answers HTTP
    200, so a status check cannot tell it apart from a working one), and it
    has run inside every preflight cycle since. But it needs a Stripe
    credential AND real internet access to the live site, and this operator
    sandbox has never held either, so its dead/unknown branch has never fired
    against production for real. The one job that DOES hold both -
    hourly-brief.yml, which already carries STRIPE_SECRET_KEY and already
    proves real egress to 6s-success.com by running ops/indexnow.py in the
    same job - never called it either. This file's own SITE section only
    checks HTTP status, the exact blind spot check_live_links.py's docstring
    names, and COMMERCE's "live payment links" line is a raw count of active
    links in the account, not a check that the live buttons point at them.
    So the one automated, credentialed, hourly job Phil actually reads could
    have sat through a repeat of the exact outage this codebase is built
    around and reported "all pages 200" the entire time.

    problem is True only for a verdict backed by real evidence from the live
    site (a confirmed-dead link, or a slug the live site serves that this
    Stripe account does not recognise at all, which check_live_links.py's own
    main() treats as worse than deactivated). "unknown" with no slugs found
    means the check could not run at all (no credential, or the site could
    not be reached) and must read as unchecked, never as ok and never as an
    outage: CLAUDE.md 0.4, unknown is not a default in either direction.
    """
    verdict = links.get("verdict")
    if verdict == "ok":
        n = len(links.get("slugs", {}))
        return False, [f"  OK  {n} link(s) checked on "
                       f"{links.get('checked_pages', 0)} live page(s), all active"]
    if verdict == "dead":
        dead = links.get("dead", [])
        lines = [f"  OUTAGE  {len(dead)} payment link(s) on the live site are "
                 f"DEACTIVATED in Stripe. A buy click reaches a dead link."]
        for slug, pages in dead[:6]:
            lines.append(f"    {slug}  on {', '.join(pages)}")
        return True, lines
    if verdict == "unknown" and links.get("slugs"):
        unk = links.get("unknown", [])
        lines = [f"  OUTAGE  {len(unk)} payment link(s) on the live site do "
                 f"not exist in this Stripe account at all, worse than "
                 f"deactivated."]
        for slug, pages in unk[:6]:
            lines.append(f"    {slug}  on {', '.join(pages)}")
        return True, lines
    return False, [f"  UNCHECKED  {links.get('note') or 'could not verify live payment links'}"]


def price_claims_summary() -> tuple[bool, list[str]]:
    """Run stripe_catalog.price_claim_gaps() here, the one job that already
    carries STRIPE_SECRET_KEY and real egress.

    Written 2026-09-15. gate_stripe_price_claims in preflight.py has read
    "UNCHECKED, not clean" in every sandbox this project has ever run in,
    the same credential gap payment_link_summary()'s own docstring names for
    check_live_links.py, and for the same reason: this operator sandbox has
    never held a Stripe key. Nothing wired the check into the one job that
    does, even after the sibling check was wired in on 2026-09-09.
    """
    try:
        bad = sc.price_claim_gaps()
    except (Exception, SystemExit) as e:                        # noqa: BLE001
        return False, [f"  UNCHECKED  could not read Stripe product "
                       f"descriptions ({type(e).__name__})"]
    if not bad:
        return False, ["  OK  every dollar figure in an active product "
                       "description matches a catalogue price or a bundle sum"]
    lines = [f"  FABRICATED PRICE  {len(bad)} figure(s) in Stripe product "
             f"descriptions match no catalogue price and no sum of catalogue "
             f"prices:"]
    for name, v in bad[:6]:
        lines.append(f"    {name}  claims ${v:,.2f}")
    return True, lines


def duplicate_sku_summary() -> tuple[bool, list[str]]:
    """Same reasoning as price_claims_summary(): stripe_dedupe.duplicates()
    describes the live account and has only ever run from this sandbox,
    which has never held a credential.
    """
    try:
        dupes = stripe_dedupe.duplicates()
    except (Exception, SystemExit) as e:                        # noqa: BLE001
        return False, [f"  UNCHECKED  could not check for duplicate Stripe "
                       f"products ({type(e).__name__})"]
    if not dupes:
        return False, ["  OK  every SKU resolves to exactly one active "
                       "Stripe product"]
    lines = [f"  DUPLICATE PRODUCTS  {len(dupes)} SKU(s) have more than one "
             f"active Stripe product, so a live link can be charging a price "
             f"nobody approved:"]
    for skusym, prods in list(dupes.items())[:6]:
        lines.append(f"    {skusym}  {len(prods)} active product(s)")
    return True, lines


def brand_summary() -> tuple[bool, list[str]]:
    """Same reasoning again: stripe_brand.check() is issue #21's own
    Ledgerium-identity check and has never run against the live account
    from a credentialed environment before.
    """
    try:
        r = stripe_brand.check()
    except (Exception, SystemExit) as e:                        # noqa: BLE001
        return False, [f"  UNCHECKED  could not check the Stripe account's "
                       f"public business identity ({type(e).__name__})"]
    if not r["gaps"]:
        return False, ["  OK  business name, url, support email and "
                       "description all match 6S Success"]
    lines = [f"  IDENTITY GAP  {len(r['gaps'])} business-identity gap(s) on "
             f"the live Stripe account:"]
    for gap, where in r["gaps"][:6]:
        lines.append(f"    {gap}")
    return True, lines


def link_retirement_summary(st: dict) -> tuple[bool, list[str]]:
    """Surface ops/stripe_catalog.py's own record of a refused link
    retirement (REVIEW-COMMERCE-2026-09-07.md C17).

    st is state.json, already written by the measured() call above (which
    runs ops/dashboard.py, and dashboard.py's own S dict, dumped whole,
    already carries link_retirement_refused from
    ops/link-retirement-refused.json). Reading it here rather than the file
    directly keeps one source of truth: dashboard.py already decided what
    counts as current, this just renders it.

    Unlike price_claims_summary()/duplicate_sku_summary()/brand_summary(),
    this makes no live Stripe call and so is never UNCHECKED: an absent or
    empty list means no --apply run has ever refused a retirement, or the
    last one that did has since gone clean, either way genuinely OK.
    """
    refused = st.get("link_retirement_refused") or []
    if not refused:
        return False, ["  OK  no payment link retirement has been refused "
                       "(or none has cleared since the last check)"]
    when = st.get("link_retirement_refused_at") or "an unknown time"
    lines = [f"  STILL CHARGING A RETIRED PRICE  {len(refused)} payment "
             f"link(s) could not be retired as of {when}, and are still "
             f"live at the old price:"]
    for r in refused[:6]:
        lines.append(f"    {r.get('sku', '?')}  {r.get('reason', '')}")
    lines.append("    Fix: deploy the live site (if it is just behind), or "
                 "restore Stripe access, then rerun "
                 "STRIPE_ALLOW_LIVE=1 python ops/stripe_catalog.py --apply.")
    return True, lines


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

    open_p0 and needs_phil are not missing when GitHub was unreachable that
    run, they are 0: dashboard.py sets issues_available False and both
    counts to 0 in the same breath, so a plain .get(..., '?') never sees the
    '?' fallback and this line would read "P0 0   needs Phil 0", a false
    all-clear on the one field CLAUDE.md 0.4 says must never default to
    passing. Checked explicitly instead.
    """
    if st.get("issues_available") is False:
        p0, phil = "unknown (GitHub unreachable)", "unknown (GitHub unreachable)"
    else:
        p0, phil = st.get("open_p0", "?"), st.get("needs_phil", "?")
    return (f"  overall {st.get('overall', '?')}   "
            f"P0 {p0}   needs Phil {phil}   "
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
    try:
        links = cll.check()
    except Exception as e:                                    # noqa: BLE001
        links = {"verdict": "unknown", "note": f"check_live_links crashed: {e}"}
    link_problem, link_lines = payment_link_summary(links)
    price_problem, price_lines = price_claims_summary()
    dupe_problem, dupe_lines = duplicate_sku_summary()
    brand_problem, brand_lines = brand_summary()
    deploy_problem, deploy_lines = deploy_staleness_summary(st)
    retire_problem, retire_lines = link_retirement_summary(st)
    prev = load_last()

    rev = cm.get("revenue_30d", 0)
    sales = cm.get("paid_30d", 0)
    life = cm.get("revenue_lifetime")
    subject = (f"{'OUTAGE - PAYMENT LINK DEAD - ' if link_problem else ''}"
               f"{'FABRICATED PRICE ON CHECKOUT - ' if price_problem else ''}"
               f"{'DUPLICATE STRIPE PRODUCT - ' if dupe_problem else ''}"
               f"{'PRODUCTION BEHIND REPOSITORY - ' if deploy_problem else ''}"
               f"{'LINK STILL CHARGES RETIRED PRICE - ' if retire_problem else ''}"
               f"6S hourly: ${rev:,.0f} / 30d"
               f"{f' (${life:,.0f} lifetime)' if life is not None else ''}, "
               f"{sales} sale(s), "
               f"{len(ib.get('unread', []))} unread")

    L = [f"{now:%Y-%m-%d %H:%M} UTC", ""]

    L += ["COMMERCE"]
    if cm.get("error"):
        L.append(f"  could not read Stripe: {cm['error']}")
    else:
        L += [f"  revenue, last 30 days      ${cm['revenue_30d']:,.2f}",
              f"  revenue, lifetime          ${cm.get('revenue_lifetime', 0):,.2f}",
              f"  paid orders                {cm['paid_30d']}",
              f"  checkout pages opened      {cm['checkouts_started_30d']}"
              " (not orders; includes our own checks)",
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
    L.append("  (a deactivated Stripe link still answers 200; see PAYMENT "
             "LINKS below for the check that can tell)")

    L += ["", "PAYMENT LINKS (live site, not the repository)"]
    L += link_lines

    L += ["", "STRIPE ACCOUNT (live, not the repository)"]
    L += price_lines
    L += dupe_lines
    L += brand_lines
    L += retire_lines

    if st:
        L += ["", "BUILD", build_line(st)]

    L += ["", "DEPLOY (production vs. repository)"]
    L += deploy_lines

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
