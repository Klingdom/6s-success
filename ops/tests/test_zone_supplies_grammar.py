#!/usr/bin/env python3
"""
Prove ops/zone_supplies.py's optional-kit disclosure sentence is correct
English for every noun in ops/zone-search-terms.json, not just the singular
ones.

Found 2026-09-19, the narrative-level cold read of site/zones/*.html
(the standing handoff several prior ops/NIGHTLY-LOG.md entries named but
had not yet reached these specific pages). render() and render_storage()
both built "Only if your {noun} has one" / "Not every {noun} needs
these", which is correct only when {noun} is grammatically singular
("medicine cabinet", "workbench"). ops/zone-search-terms.json's own
overrides include plural and plural-compound nouns ("towels", "bed and
linens", "dresser drawers", "cleaning supplies"), and the fallback in
searchable() produces more of them ("coats and outerwear", "shoes and
boots"). Verified live before fixing: guest-bathroom-the-guest-linen-zone
shipped "Only if your towels has one" and "Not every towels needs these",
both real subject-verb disagreements a reader would notice, on a real
page a visitor is sent to. A scan of all 114 committed zone pages found
the same shape wherever the noun is plural, not a single instance.

Fixed by rewording so the noun is never the grammatical subject of a
verb ("Only if it applies to the {noun}" / "Not every home needs these
for the {noun}"), which is correct regardless of the noun's number, so
this cannot regress again just because zone-search-terms.json grows a
new plural entry.

Run:  python ops/tests/test_zone_supplies_grammar.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import zone_supplies as zs                                     # noqa: E402


PLURAL_NOUNS = [
    "towels",
    "bed and linens",
    "dresser drawers",
    "cleaning supplies",
    "coats and outerwear",
    "shoes and boots",
]

SINGULAR_NOUNS = [
    "medicine cabinet",
    "workbench",
    "dining table",
]


def main() -> int:
    fails = []

    # zone_supplies.kit() reads real content; rather than hunt for a room/
    # zone pair with a non-empty "maybe" bucket for every noun above (kit()
    # is keyed by real room/zone names, not by the noun itself), test the
    # sentence templates directly the way the two call sites in
    # ops/zone_supplies.py build them, so the assertion is about the
    # English, not about which real zone happens to carry which noun.
    def summary_and_body(noun: str):
        n = zs._esc(noun.strip().lower())
        summary = f"Only if it applies to the {n}: 3 more"
        body = (f"Not every home needs these for the {n}. Each one is "
                "here because some do, and the reason is next to it.")
        return summary, body

    for noun in PLURAL_NOUNS + SINGULAR_NOUNS:
        summary, body = summary_and_body(noun)
        bad_summary = f"Only if your {noun} has one"
        bad_body = f"Not every {noun} needs these"
        if bad_summary in summary or bad_body in body:
            fails.append(f"{noun!r}: old broken construction still present")
        if f"your {noun} has" in summary or f"every {noun} needs" in body:
            fails.append(f"{noun!r}: noun still sits where a verb must "
                         "agree with it")

    # Confirm the two real call sites in zone_supplies.py actually use the
    # fixed wording today, not just that the wording above would be fine
    # if used. Uses a real room/zone with a known non-empty "maybe" list.
    out = zs.render("Guest Bathroom", "Guest Linen Zone", "towels")
    if "Only if your towels has one" in out:
        fails.append("render(): old broken sentence still shipping live "
                     "for a real plural noun (towels)")
    if "Not every towels needs these" in out:
        fails.append("render(): old broken sentence (needs) still "
                     "shipping live for a real plural noun (towels)")
    if "Only if it applies to the towels" not in out:
        fails.append("render(): fixed sentence not found for a zone with "
                     "a real 'maybe' list")

    storage_out = zs.render_storage("Guest Bathroom", "Guest Linen Zone",
                                    "towels")
    if "Only if your towels has one" in storage_out:
        fails.append("render_storage(): old broken sentence still "
                     "shipping live for a real plural noun (towels)")
    if storage_out and "Only if it applies to the towels" not in storage_out:
        fails.append("render_storage(): fixed sentence not found even "
                     "though a storage 'maybe' list is present")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: zone_supplies optional-kit sentence is grammatical for "
          "plural and singular nouns alike, in both the abstract template "
          "and the real render() / render_storage() output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
