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
import glob
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
  {amazon}
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
    """The disclosure block. The Amazon sentence appears only when it applies.

    The first version printed "We are not paid by any retailer to feature a
    product" whenever there was no Amazon link, which is nine programmes out
    of ten. That sentence sat directly under "6S Success may earn a commission
    if you buy through them", on a page full of paid links. An affirmative
    false denial is worse than a missing disclosure, and it was my own logic
    error rather than an inherited one. There is no else branch now.
    """
    return DISCLOSURE_HTML.format(
        id=DISCLOSURE_ID,
        amazon=f"<p>{AMAZON_SENTENCE}</p>" if has_amazon else "")


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


def _text_of(path: str) -> tuple:
    """Every readable string in a file, whatever its container.

    (text, parsed_ok). A plain text read of an EPUB returns nothing useful:
    measured on this repository's own book, a text read found 0 occurrences of
    "http" and the decompressed entries held 313. So the first version of this
    gate looked at the flagship product and reported it clean.

    Anything that cannot be parsed returns parsed_ok False and the caller
    fails closed, because "I could not look" must never read as "there is
    nothing there".
    """
    low = path.lower()
    try:
        if low.endswith((".epub", ".zip", ".docx", ".xlsx")):
            import zipfile
            out = []
            with zipfile.ZipFile(path) as z:
                for n in z.namelist():
                    if n.endswith("/"):
                        continue
                    try:
                        out.append(z.read(n).decode("utf-8", errors="ignore"))
                    except Exception:                          # noqa: BLE001
                        return "", False
            return "\n".join(out), True

        if low.endswith(".pdf"):
            try:
                import pymupdf
            except ImportError:
                return "", False
            with pymupdf.open(path) as d:
                parts = []
                for i in range(d.page_count):
                    parts.append(d[i].get_text())
                    for lk in d[i].get_links():
                        if lk.get("uri"):
                            parts.append(lk["uri"])
            return "\n".join(parts), True

        return io.open(path, encoding="utf-8", errors="ignore").read(), True
    except Exception:                                          # noqa: BLE001
        return "", False


def delivered_documents() -> list:
    """Every file a paying customer actually receives.

    site/downloads is not that list. What customers get is built by
    .github/workflows/fulfil-orders.yml and mailed by ops/stripe_fulfil.py
    from build/ and content/, and the 149 generated packs are gitignored so
    no human ever reads them. Scanning only site/downloads left the EPUB, the
    Manual, the Print Pack and every generated pack unexamined.

    Found 2026-09-03: audit_visual.py writes a scratch _visual_probe.html
    beside whatever page it is measuring, including ones under
    site/downloads/, and removes it when it finishes. Running this glob while
    that scan is mid-flight elsewhere can catch the probe between its write
    and its cleanup: it is not a real customer deliverable and either reads
    as "unreadable" (a false compliance FAIL) or gets scanned as if it were
    one, neither of which is this file's job to report. Excluded by the one
    basename audit_visual.py itself uses, not by directory, so a real file a
    customer would ever receive is never the one skipped.
    """
    out = set()
    for p in glob.glob(os.path.join(ROOT, "site", "downloads", "*")):
        if os.path.isfile(p) and os.path.basename(p) != "_visual_probe.html":
            out.add(p)

    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import stripe_fulfil
        for spec in stripe_fulfil.DELIVERY.values():
            for rel in ([spec["file"]] if spec.get("file")
                        else spec.get("files", [])):
                p = os.path.join(ROOT, rel)
                if os.path.exists(p):
                    out.add(p)
    except Exception:                                          # noqa: BLE001
        pass

    for p in glob.glob(os.path.join(ROOT, "build", "products", "*")):
        if os.path.isfile(p):
            out.add(p)
    return sorted(out)


def check() -> int:
    """Refuse to ship anything that breaks the three rules."""
    bad = []
    ids = {v.get("publisher_id") for v in accounts().values()
           if v.get("publisher_id")}
    # A tag parameter, a known network redirect host, or one of our own ids.
    AFF = re.compile(r"[?&](?:tag|ascsubtag)=[\w.-]+|"
                     r"(?:goto\.target|goto\.walmart|linksynergy|"
                     r"anrdoezrs|dpbolvw|kqzyfj|tkqlhce|jdoqocy|"
                     r"prf\.hn|sjv\.io|pxf\.io|awin1|shareasale)\.", re.I)

    site = os.path.join(ROOT, "site")

    # Rule 2, the one with a contract behind it. Amazon's operating agreement
    # prohibits affiliate links in any offline document.
    unreadable = []
    for f in delivered_documents():
        if not f.lower().endswith((".html", ".pdf", ".epub", ".md", ".txt")):
            continue
        text, ok = _text_of(f)
        if not ok:
            unreadable.append(os.path.relpath(f, ROOT))
            continue
        hit = AFF.search(text)
        found_id = next((i for i in ids if i and i in text), None)
        if hit or found_id:
            bad.append(f"{os.path.relpath(f, ROOT)} carries "
                       f"{found_id or hit.group(0)[:40]!r}. No affiliate link "
                       f"may appear in a document a customer receives.")
    if unreadable:
        bad.append(f"could not read {len(unreadable)} delivered document(s), "
                   f"so they cannot be cleared: {unreadable[:3]}. Failing "
                   f"closed rather than reporting them clean.")

    # Rule 1. Any page with a tracked link needs the disclosure, above them.
    for f in glob.glob(os.path.join(site, "**", "*.html"), recursive=True):
        if os.path.basename(f) == "_visual_probe.html":
            continue
        s = io.open(f, encoding="utf-8", errors="ignore").read()
        links = [m.start() for m in AFF.finditer(s)]
        links += [m.start() for m in re.finditer(r"data-aff=", s)]
        if not links:
            continue
        rel = os.path.relpath(f, ROOT)
        if DISCLOSURE_ID not in s:
            bad.append(f"{rel} has affiliate links and no disclosure block")
        elif s.index(DISCLOSURE_ID) > min(links):
            bad.append(f"{rel} places the disclosure after the first "
                       f"affiliate link rather than before it")

    if bad:
        for b in bad:
            print(f"  FAIL  {b}")
        return 1
    print(f"  affiliate rules pass: {len(delivered_documents())} delivered "
          f"documents carry no affiliate link, and every page with links "
          f"discloses above them")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        raise SystemExit(check())
    raise SystemExit(status())
