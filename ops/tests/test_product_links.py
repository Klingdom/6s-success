#!/usr/bin/env python3
"""
Tests for the retailer link layer.

None of these touch the network. What is worth testing here is not whether
Target is up, it is whether this tool can tell the difference between a
verified link, a wrong one, and a look that never happened, because that is
the distinction the whole thing exists to make and the one that was wrong
twice while it was being written.

Run:  python ops/tests/test_product_links.py
"""
import csv
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import product_links as P                                      # noqa: E402
import affiliate as A                                          # noqa: E402

OK = []


def check(name, cond):
    OK.append((name, bool(cond)))
    print(f"  {'ok  ' if cond else 'FAIL'}  {name}")


def rows():
    with io.open(P.CATALOGUE, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def test_every_product_has_a_spec():
    ids = {r["Product ID"] for r in rows()}
    check("every catalogue product has a link spec",
          not (ids - set(P.SPEC)))
    check("no spec points at a product that does not exist",
          not (set(P.SPEC) - ids))


def test_every_spec_names_a_readable_merchant():
    bad = [k for k, v in P.SPEC.items() if v["m"] not in P.MERCHANTS]
    check("no spec names a merchant this machine cannot read", not bad)


def test_no_affiliate_code_is_ever_built_into_a_url():
    """No programme is approved, so no URL may carry a tag."""
    bad = [r["Product ID"] for r in rows()
           if "tag=" in (r.get("Affiliate URL") or "")
           or "ascsubtag" in (r.get("Affiliate URL") or "")]
    check("no catalogue URL carries an affiliate tag", not bad)


def test_matcher_requires_a_whole_word():
    """The first version substring-matched and certified the wrong product."""
    check("'washer' does not match 'dishwasher'",
          not P.matches("clean-people-dishwasher-detergent-tablets", "washer"))
    check("'can' does not match 'candle'",
          not P.matches("white-candle-holder-set", "can"))
    check("'can' matches a real can", P.matches("3-tier-can-organizer", "can"))
    check("plurals still match", P.matches("microfiber-dust-cloths-6pk",
                                           "cloth"))
    check("a hyphenated keyword matches across words",
          P.matches("3m-safety-glasses-clear", "safety-glass"))


def test_judge_states():
    slugs = "".join(f'href="/p/microfiber-cloth-{i}/-/A-{i}"' for i in range(6))
    state, hits, n, _ = P.judge("target", slugs, ["microfiber"])
    check("enough matches reads ok", state == "ok" and hits == 6)

    one = 'href="/p/microfiber-cloth-1/-/A-1"href="/p/juice-box/-/A-2"'
    state, hits, _, _ = P.judge("target", one, ["microfiber"])
    check("one match is weak, not ok", state == "weak")

    none = 'href="/p/juice-box/-/A-2"href="/p/coffee-pods/-/A-3"'
    state, _, _, _ = P.judge("target", none, ["microfiber"])
    check("no match is dead", state == "dead")


def test_a_blocked_page_is_unchecked_not_dead():
    """The rule that cost the most elsewhere in this repository.

    Home Depot answers a burst with a 2KB page titled "Error Page". It has
    zero product slugs, so a size-blind reader scores it "nothing matched"
    and publishes a verdict it never earned.
    """
    real = P.render.__doc__ or ""
    check("render() documents that it returns unchecked, not dead",
          "unchecked" in real.lower())
    check("a small body is treated as not-looked-at",
          P.MIN_RESULTS_BYTES > 10000)
    check("known challenge titles include Home Depot's error page",
          "error page" in P.BLOCKED_TITLES)


def test_published_rows_carry_a_reason():
    """CLAUDE.md section 48. A recommendation with no stated reason is the
    thing the section forbids, so it is a test, not a style note."""
    bad = [r["Product ID"] for r in rows()
           if (r.get("Link Status") or "").lower().startswith("verified")
           and not (r.get("Why Recommended") or "").strip()]
    check("every published product says why it is recommended", not bad)


def test_published_rows_have_a_url_and_a_merchant():
    bad = [r["Product ID"] for r in rows()
           if (r.get("Link Status") or "").lower().startswith("verified")
           and not ((r.get("Affiliate URL") or "").startswith("https://")
                    and (r.get("Merchant") or "").strip())]
    check("every verified row has both a URL and a merchant", not bad)


def test_unverified_rows_publish_nothing():
    bad = [r["Product ID"] for r in rows()
           if not (r.get("Link Status") or "").lower().startswith("verified")
           and A.retailer_link(r)[1] in ("tracked", "plain")]
    check("a row that is not verified never renders a link", not bad)


def test_a_link_to_an_undisclosed_host_is_withheld():
    """site/privacy.html is the permission list, not a formality."""
    fake = {"Affiliate URL": "https://www.example-shop.com/s?q=bin",
            "Link Status": "Verified search", "Merchant": "example"}
    href, kind, _ = A.retailer_link(fake)
    check("a host privacy.html does not name is withheld",
          kind == "withheld" and not href)


def test_evidence_exists_for_every_verified_row():
    ev = P.load_evidence()
    bad = [r["Product ID"] for r in rows()
           if (r.get("Link Status") or "").lower().startswith("verified")
           and not isinstance(ev.get(r["Product ID"]), dict)]
    check("every verified row has auditable evidence behind it", not bad)


def test_the_checker_scope_is_not_chosen_by_the_status_it_writes():
    """The regression the coordinator found on 2026-09-04.

    check() used to select only rows already marked verified, then print
    "UNCHECKED 0" as if that were the whole catalogue. A row whose status says
    it could not be verified is the one that most needs looking at, and it was
    the one guaranteed to be skipped.
    """
    rows = [
        {"Product ID": "DOUBTED", "Affiliate URL": "https://example.com/s?q=x",
         "Link Status": "Search URL, unverifiable here (retailer blocks bots)"},
        {"Product ID": "GOOD", "Affiliate URL": "https://example.com/s?q=y",
         "Link Status": "Verified search"},
        {"Product ID": "NOLINK", "Affiliate URL": "",
         "Link Status": "Too weak to publish"},
    ]
    got = [r["Product ID"] for r in P.checkable(rows)]
    check("a doubted row is still checked", "DOUBTED" in got)
    check("a verified row is still checked", "GOOD" in got)
    check("a row with no URL is not a link to check", "NOLINK" not in got)


def test_no_row_claims_evidence_its_status_denies():
    bad = [r["Product ID"] for r in rows()
           if "when rendered" in (r.get("Notes") or "")
           and not (r.get("Link Status") or "").lower().startswith("verified")]
    check("no row carries rendered evidence with a status that denies it",
          not bad)


if __name__ == "__main__":
    for fn in list(globals()):
        if fn.startswith("test_"):
            globals()[fn]()
    failed = [n for n, ok in OK if not ok]
    print(f"\n  {len(OK) - len(failed)} passed, {len(failed)} failed")
    raise SystemExit(1 if failed else 0)
