#!/usr/bin/env python3
"""
Prove two real defects in stripe_brand.py, found and fixed 2026-09-06 cold-
reading the money-domain ops/*.py tier.

First: the module's own usage docstring told an operator to run
`python ops/stripe_brand.py --apply`, but the code only ever checked
`"--draw" in sys.argv`. Every sibling Stripe tool (stripe_setup.py,
stripe_catalog.py, stripe_dedupe.py, stripe_links.py) uses --apply as its
write-trigger flag; this was the one outlier. Running the exact command the
docstring recommends silently did nothing (no icon files written, no error),
which only became visible because the script's own printed gap message
separately said "--draw", contradicting its own top-of-file usage line.

Second: `KEY = secret_key()` ran at module import time, which crashes any
import of this module with no Stripe credential present, the exact anti-
pattern stripe_catalog.py's own key() docstring names on purpose
("importing this module... must not require live credentials. Only an
actual API call should"). This also made the first bug untestable, since
merely importing the module for a test needed a live-looking key already
set up.

Third, added 2026-09-07 closing issue #21's own still-open half: the check
only ever read business_profile.url and .support_email. The issue's actual
finding (a product description reading "Ledgerium AI's... workflow
documentation platform" in full, and no gate anywhere to notice if it drifts
back) lived in .name and .product_description, two fields nothing here had
ever looked at. check() now covers both.

Run:  STRIPE_SECRET_KEY=sk_test_x python ops/tests/test_stripe_brand.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_regression_only")

import stripe_brand as sb                                     # noqa: E402


def main() -> int:
    fails = []

    # The module must import with no .env.secrets and no real credential:
    # proves the lazy-key fix. If this file's import above raised SystemExit,
    # this function would never run at all, so reaching here is itself part
    # of the proof.
    if sb._KEY is not None:
        fails.append("key() was called at import time, not lazily")

    # The CLI flag the code actually looks for must match the one the
    # docstring's own Run: section (and the runtime's own gap message)
    # recommend, or the documented command silently no-ops.
    src = open(os.path.join(ROOT, "ops", "stripe_brand.py"), encoding="utf-8").read()
    doc_flag = "--apply" in src.split('"""', 2)[1]
    code_flag_line = [l for l in src.splitlines() if "in sys.argv))" in l]
    if not code_flag_line:
        fails.append("could not find the sys.argv flag check line")
    elif "--apply" not in code_flag_line[0]:
        fails.append(f"docstring documents --apply but code checks: {code_flag_line[0].strip()!r}")
    if not doc_flag:
        fails.append("usage docstring no longer mentions --apply at all")

    # The gap message printed at the end of a dry run must recommend the same
    # flag the code actually reads, not a flag that does nothing.
    if "--apply writes the icon" not in src:
        fails.append("the runtime gap message still points at the wrong flag")

    # A full dry run (apply_it=False) must work against a monkeypatched
    # account with no network and no PIL (draw_mark is never called).
    calls = []

    def fake_call(method, path, pairs=None):
        calls.append((method, path))
        return {"business_profile": {"url": sb.SITE, "support_email": sb.SUPPORT,
                                      "name": sb.NAME,
                                      "product_description": "Sort, Straighten, Shine."},
                "settings": {"branding": {"icon": "file_1", "logo": "file_2",
                                          "primary_color": "#BC4B2A"}}}

    real_call = sb.call
    sb.call = fake_call
    try:
        rc = sb.main(False)
    except Exception as e:
        fails.append(f"dry run with everything correct raised {type(e).__name__}: {e}")
        rc = None
    else:
        if rc != 0:
            fails.append(f"dry run with nothing wrong should return 0, got {rc}")
        if calls != [("GET", "account")]:
            fails.append(f"dry run should make exactly one GET account call, made {calls}")
    finally:
        sb.call = real_call

    # issue #21: the account's business_profile.name and .product_description
    # are two fields the original check never looked at at all, even though
    # the issue's own finding was a product_description reading "Ledgerium
    # AI's... workflow documentation platform" in full. Four cases, each
    # proving check() names the real problem rather than staying silent.
    base_profile = {"url": sb.SITE, "support_email": sb.SUPPORT, "name": sb.NAME,
                     "product_description": "Sort, Straighten, Shine, Safety, "
                                             "Standardize, Sustain."}
    base_branding = {"icon": "file_1", "logo": "file_2", "primary_color": "#BC4B2A"}

    def run_check(profile_overrides):
        prof = dict(base_profile)
        prof.update(profile_overrides)
        sb.call = lambda method, path, pairs=None: {
            "business_profile": prof, "settings": {"branding": base_branding}}
        try:
            return sb.check()["gaps"]
        finally:
            sb.call = real_call

    clean_gaps = run_check({})
    if clean_gaps:
        fails.append(f"a fully correct profile still reported gaps: {clean_gaps}")

    wrong_name_gaps = run_check({"name": "Ledgerium AI"})
    if not any("name" in g[0].lower() for g in wrong_name_gaps):
        fails.append(f"a wrong business name was not caught: {wrong_name_gaps}")

    no_desc_gaps = run_check({"product_description": ""})
    if not any("description" in g[0].lower() for g in no_desc_gaps):
        fails.append(f"a missing product description was not caught: {no_desc_gaps}")

    ledgerium_desc_gaps = run_check(
        {"product_description": "Ledgerium AI's workflow documentation platform."})
    if not any("ledgerium" in g[0].lower() for g in ledgerium_desc_gaps):
        fails.append(f"a Ledgerium-branded description was not caught: {ledgerium_desc_gaps}")

    set_in_order_gaps = run_check(
        {"product_description": "Sort, Set in Order, Shine, Standardize, Sustain."})
    if not any("set in order" in g[0].lower() for g in set_in_order_gaps):
        fails.append(f"the rejected 'Set in Order' term was not caught: {set_in_order_gaps}")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("stripe_brand.py: lazy key + --apply flag consistency + business "
          "identity coverage (issue #21): 9 case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
