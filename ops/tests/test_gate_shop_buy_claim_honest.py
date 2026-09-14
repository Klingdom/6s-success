"""gate_shop_buy_claim_honest: shop.html must not claim universal instant
checkout while a quote-based product sits in its own grid.

Found 2026-09-14 cold-reading shop.html for content honesty: the hero said
"Everything here can be bought today and delivered today" and "Every priced
item below checks out directly and securely through Stripe", both false for
Corporate Lean 6S (SKU CN-CORP), the one quote-based product in the grid.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import preflight as P  # noqa: E402

# The real pre-fix wording from commit 94e0ce83 (site/shop.html), copied here
# as a literal so this case does not depend on git history depth: CI checks
# out with --depth=1, where that commit's blob is unreachable by SHA.
PRE_FIX_HERO = (
    "Everything here can be bought today and delivered today. The book and "
    "the manual, printable packs for a single micro zone, a whole room, a "
    "situation or a whole area of the house, a free app, a free deck, and "
    "consulting. Nothing is listed that we cannot hand over. "
    "Every priced item below checks out directly and securely through "
    "Stripe. No card details ever touch this site."
)


def _wrap(hero: str, has_quote: bool) -> str:
    grid = '<span class="price">Quote</span>' if has_quote else '<span class="price">$19</span>'
    return f"<html><body>{hero}{grid}</body></html>"


def main() -> int:
    bad = []

    hero = ("Everything here can be bought today and delivered today. "
            "Every priced item below checks out directly and securely "
            "through Stripe.")
    if P.check_shop_buy_claim_honest(_wrap(hero, has_quote=False)) != []:
        bad.append("case 1: no quote product in the grid must never fail, "
                    "whatever the hero says")

    hero = "Everything here can be bought today and delivered today."
    problems = P.check_shop_buy_claim_honest(_wrap(hero, has_quote=True))
    if not any("bought today" in p for p in problems):
        bad.append("case 2: the bare 'bought today' claim with a real "
                    "Quote tile in the grid must be caught")

    hero = "Every priced item below checks out directly and securely through Stripe."
    problems = P.check_shop_buy_claim_honest(_wrap(hero, has_quote=True))
    if not any("no exception named" in p for p in problems):
        bad.append("case 3: the bare Stripe-checkout claim with a real "
                    "Quote tile in the grid must be caught")

    hero = ("Almost everything here can be bought today and delivered today. "
            "Every priced item below checks out directly and securely "
            "through Stripe, except Corporate Lean 6S, which is scoped "
            "first and quoted at a fixed fee before any work starts.")
    if P.check_shop_buy_claim_honest(_wrap(hero, has_quote=True)) != []:
        bad.append("case 4: the fixed wording, naming the exception, must pass")

    problems = P.check_shop_buy_claim_honest(_wrap(PRE_FIX_HERO, has_quote=True))
    if len(problems) != 2:
        bad.append(f"case 5: the real pre-fix wording (commit 94e0ce83) must fail "
                   f"both checks, got {len(problems)}: {problems}")

    live_path = os.path.join(ROOT, "site", "shop.html")
    live_text = io.open(live_path, encoding="utf-8").read()
    if P.check_shop_buy_claim_honest(live_text) != []:
        bad.append("case 6: the real, current site/shop.html must pass clean")

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  6 of 6 cases pass: no-quote-product is always clean, "
              "both bare overclaims are caught with a quote product present, "
              "the actual fixed wording passes, the real pre-fix commit "
              "fails by name, and the real current file is clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
