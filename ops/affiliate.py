#!/usr/bin/env python3
"""
The affiliate link layer: one registry, one builder, and the rules that bind.

WHAT THIS IS FOR
----------------
Phil applies to the programmes. This holds everything else, so that the moment
an approval arrives the only work is pasting one identifier into a file.

Nothing here can be run before an approval exists, and it refuses to invent a
link, because a broken or guessed affiliate URL on a product page is worse
than no link at all: it takes a reader who trusted a recommendation and sends
them nowhere.

WHAT IS AND IS NOT A SECRET
---------------------------
A store tag or publisher id is NOT a secret. It appears in every link the
public clicks, so it lives in ops/affiliate-accounts.json in the repository
where it can be reviewed. What IS secret, an API key for a product feed, goes
in .env.secrets and is read by name, never committed, and never printed.

Passwords, tax identifiers, bank details and recovery codes have no place in
this repository or in any file this reads. They are not needed to build a
link and nothing here asks for them.

THE THREE RULES THAT ARE NOT NEGOTIABLE
---------------------------------------
1. A page carrying affiliate links must carry the disclosure, above them, in
   plain words. That is the FTC position and it is also just honest.
2. No affiliate link may appear in an ebook, a PDF or any downloadable
   document. Amazon's operating agreement prohibits it outright and other
   programmes carry similar terms. The book points at a page; the page carries
   the links.
3. A product is recommended because it fits the job, and the reason is stated.
   CLAUDE.md section 48 rules out dressing up a commission as personalisation,
   and a recommendation nobody can audit is exactly that.

Run:  python ops/affiliate.py --status
      python ops/affiliate.py --check
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(ROOT, "ops", "affiliate-catalogue.csv")
ACCOUNTS = os.path.join(ROOT, "ops", "affiliate-accounts.json")

DISCLOSURE_ID = "affiliate-disclosure"

# The wording. Amazon requires its sentence verbatim, so it is not paraphrased.
DISCLOSURE_HTML = """\
<aside class="disclosure" id="{id}">
  <p><b>How the links on this page work.</b> Some of the links below are
  affiliate links, which means 6S Success may earn a commission if you buy
  through them, at no extra cost to you.</p>
  <p>Every product here is listed because a specific micro zone needs that
  kind of thing, and the reason is written next to it. We recommend a product
  <i>type</i> first. Where a particular item is named it is because it does
  the job, not because it pays more, and nothing is listed that the method
  does not actually call for.</p>
  <p>{amazon}</p>
</aside>"""
AMAZON_SENTENCE = "As an Amazon Associate I earn from qualifying purchases."


def accounts() -> dict:
    """The programmes only. Keys starting with an underscore are notes to a
    human reader living in the same file, not programmes."""
    if not os.path.exists(ACCOUNTS):
        return {}
    raw = json.load(io.open(ACCOUNTS, encoding="utf-8"))
    return {k: v for k, v in raw.items()
            if not k.startswith("_") and isinstance(v, dict)}


def approved() -> dict:
    return {k: v for k, v in accounts().items()
            if v.get("status") == "approved" and v.get("publisher_id")}


def catalogue() -> list:
    if not os.path.exists(CATALOGUE):
        return []
    return list(csv.DictReader(io.open(CATALOGUE, encoding="utf-8-sig")))


def build_link(merchant: str, target: str) -> str | None:
    """A tracked URL, or None when the programme is not approved yet.

    Returning None rather than a bare merchant URL is deliberate. An untracked
    link earns nothing and looks identical to a working one, so the failure
    would be silent and permanent.
    """
    acct = approved().get(merchant)
    if not acct or not target:
        return None

    tmpl = acct.get("deep_link_template")
    if tmpl:
        return tmpl.replace("{url}", urllib.parse.quote(target, safe="")) \
                   .replace("{id}", acct["publisher_id"])

    if merchant == "amazon":
        sep = "&" if "?" in target else "?"
        return f"{target}{sep}tag={acct['publisher_id']}"
    return None


def disclosure(has_amazon: bool) -> str:
    return DISCLOSURE_HTML.format(
        id=DISCLOSURE_ID,
        amazon=AMAZON_SENTENCE if has_amazon else
        "We are not paid by any retailer to feature a product.")


def status() -> int:
    acc, cat = accounts(), catalogue()
    print(f"  catalogue        {len(cat)} products")
    if not acc:
        print(f"  accounts file    not created yet ({os.path.relpath(ACCOUNTS, ROOT)})")
        print(f"\n  No programme is approved, so no link can be built. That is")
        print(f"  the correct state before an application is accepted.")
        return 0

    print(f"  programmes       {len(acc)} tracked\n")
    print(f"    {'programme':22} {'status':12} {'network':14} id")
    for k, v in sorted(acc.items()):
        pid = v.get("publisher_id") or ""
        print(f"    {k:22} {v.get('status','?'):12} "
              f"{v.get('affiliate_network','') or '-':14} {pid or '-'}")

    live = approved()
    linked = sum(1 for r in cat
                 if build_link(r.get("Merchant", ""), r.get("Affiliate URL", "")))
    print(f"\n  approved         {len(live)}")
    print(f"  products linkable {linked} of {len(cat)}")
    return 0


def check() -> int:
    """Refuse to ship anything that breaks the three rules."""
    bad = []

    # Rule 2, the one with a contract behind it. Amazon's operating agreement
    # prohibits links in any offline document, so a link in the book or a PDF
    # is not a style issue, it is a term of the agreement.
    site = os.path.join(ROOT, "site")
    ids = {v.get("publisher_id") for v in accounts().values() if v.get("publisher_id")}
    import glob
    for f in glob.glob(os.path.join(site, "downloads", "*")):
        if not f.lower().endswith((".html", ".pdf", ".epub", ".md")):
            continue
        try:
            s = io.open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for pid in ids:
            if pid and pid in s:
                bad.append(f"{os.path.basename(f)} carries the affiliate id "
                           f"{pid}. No affiliate link may appear in a "
                           f"downloadable document.")
        if re.search(r"[?&]tag=[\w-]+-20\b", s):
            bad.append(f"{os.path.basename(f)} carries an Amazon tag "
                       f"parameter, which the operating agreement prohibits "
                       f"in an offline document.")

    # Rule 1. Any page with a tracked link needs the disclosure above it.
    for f in glob.glob(os.path.join(site, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8", errors="ignore").read()
        has = bool(re.search(r"[?&]tag=[\w-]+-20\b|data-aff=", s))
        if has and DISCLOSURE_ID not in s:
            bad.append(f"{os.path.relpath(f, ROOT)} has affiliate links and no "
                       f"disclosure block")
        if has and DISCLOSURE_ID in s:
            if s.index(DISCLOSURE_ID) > s.rindex("data-aff=") if "data-aff=" in s else False:
                bad.append(f"{os.path.relpath(f, ROOT)} shows the disclosure "
                           f"after the links rather than before them")

    if bad:
        for b in bad:
            print(f"  FAIL  {b}")
        return 1
    print("  affiliate rules: no links in downloads, disclosure present where "
          "links are")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        raise SystemExit(check())
    raise SystemExit(status())
