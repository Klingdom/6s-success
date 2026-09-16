#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_invest_page_catalog_current() catches a stale
or invented catalogue/storefront number on site/invest.html, and passes
clean on the real file.

Found 2026-09-16, this operator, cold-reading site/invest.html, the
hand-authored investor pitch page. Its traction section claimed "a
41-item catalog and a working cart, deploy-ready." Neither was true:
site/assets/js/data.js holds 159 items, and the cart was removed entirely
on 2026-09-08 (A6, BACKLOG-2026-09-07.md). Every other hard number on the
page (123 products, 7 families, 88/72%% all-room, 33 core) was checked
directly against content/manual/source/products.json and found correct.
This test proves the new gate can fail on each of the two defect shapes
found, on a drifted "N-product catalog" mention, and on a drifted moat
sentence, then passes on the corrected file and the real committed one.

Run:  python ops/tests/test_gate_invest_page_catalog_current.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


CLEAN = (
    '<div class="n">123</div><div class="l">Products, 7 families, fully '
    'specified</div>'
    '<p>Of our 123 fully-specified product types, <b>88 (72%) apply to '
    'every room</b>, anchored by <b>33 core products</b> that appear in '
    'nearly every kit.</p>'
    '<li><b>A 123-product catalog</b>, 7 families, each mapped to zones.</li>'
    '<li><b>A live storefront</b>, a dockerized web app with a 159-item '
    'catalog and one-click Stripe checkout on every product, '
    'deploy-ready.</li>'
    '<li>123-product catalog</li>'
)


def main() -> int:
    fails = []

    # 1. Clean: every number matches the real catalogue.
    problems = preflight.check_invest_page_numbers(
        CLEAN, 123, 7, 88, 72, 33, 159)
    if problems:
        fails.append("the real, matching numbers were wrongly flagged: %s" %
                     problems)

    # 2. The actual defect found live: a stale item count plus a claimed
    #    cart that no longer exists.
    stale = CLEAN.replace(
        'a dockerized web app with a 159-item catalog and one-click Stripe '
        'checkout on every product, deploy-ready.',
        'a dockerized web app with a 41-item catalog and a working cart, '
        'deploy-ready.')
    problems = preflight.check_invest_page_numbers(
        stale, 123, 7, 88, 72, 33, 159)
    if not any("41-item" in p or "159" in p for p in problems):
        fails.append("stale item count NOT caught: %s" % problems)
    if not any("cart" in p for p in problems):
        fails.append("false cart claim NOT caught: %s" % problems)

    # 3. A drifted "N-product catalog" mention (bill of materials grew).
    drifted_bom = CLEAN.replace("123-product catalog", "150-product catalog")
    problems = preflight.check_invest_page_numbers(
        drifted_bom, 123, 7, 88, 72, 33, 159)
    if not problems:
        fails.append("drifted N-product catalog mention NOT caught")

    # 4. A drifted moat-section percentage (as if the all-room share moved).
    drifted_moat = CLEAN.replace(
        "88 (72%) apply to every room", "88 (60%) apply to every room")
    problems = preflight.check_invest_page_numbers(
        drifted_moat, 123, 7, 88, 72, 33, 159)
    if not problems:
        fails.append("drifted moat-section percentage NOT caught")

    # 5. A missing storefront sentence entirely (page rewritten, gate must
    #    say so rather than pass silently).
    no_storefront = CLEAN.replace(
        'a dockerized web app with a 159-item catalog and one-click Stripe '
        'checkout on every product, deploy-ready.', 'a modern web app.')
    problems = preflight.check_invest_page_numbers(
        no_storefront, 123, 7, 88, 72, 33, 159)
    if not problems:
        fails.append("missing storefront sentence NOT caught")

    # 6. The real committed file, against the real source files, end to end.
    page = os.path.join(ROOT, "site", "invest.html")
    products_path = os.path.join(ROOT, "content", "manual", "source",
                                  "products.json")
    data_js_path = os.path.join(ROOT, "site", "assets", "js", "data.js")
    if os.path.exists(page) and os.path.exists(products_path) and \
            os.path.exists(data_js_path):
        master = json.load(io.open(products_path, encoding="utf-8"))["master"]
        js = io.open(data_js_path, encoding="utf-8").read()
        catalog = json.loads(js[js.index("["):js.rindex("]") + 1])
        active = [p for p in master if p.get("Active")]
        bom_total = len(active)
        bom_families = len({p.get("Product Family") for p in active})
        bom_allroom = sum(1 for p in active
                           if p.get("Applicable Rooms") == "All")
        bom_pct = round(100 * bom_allroom / bom_total) if bom_total else 0
        bom_core = sum(1 for p in active
                        if p.get("Required Level") == "Core")
        text = preflight._visible_html(page)
        problems = preflight.check_invest_page_numbers(
            text, bom_total, bom_families, bom_allroom, bom_pct, bom_core,
            len(catalog))
        if problems:
            fails.append("the real committed file failed against the real "
                         "source files: %s" % problems)
    else:
        fails.append("real invest.html, products.json or data.js missing; "
                     "end-to-end case not exercised")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("ok  all invest-page catalogue cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
