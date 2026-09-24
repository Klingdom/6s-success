#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_double_encoded_entities() catches a
double-encoded HTML entity ("&amp;#x27;" or "&amp;#39;" where a reader
expects an apostrophe) and does not fire on real, correctly single-escaped
text.

Found 2026-09-24, cold-reading ops/build_cleaning_index.py (0 prior mentions
in ops/NIGHTLY-LOG.md): its strip_tags() stripped tags out of source text
that already carried an HTML entity ("season&#x27;s") without decoding it
first, so the caller's own html.escape() re-encoded the leading "&" a
second time, shipping "season&amp;#x27;s kit" on the live
how-to-clean-anything.html. The same class turned out live in two more
places (ops/build_seo.py's hardcoded image_alt strings, and its
page_image() reading an already-escaped og:description meta attribute back
off a rendered page); see gate_no_double_encoded_entities()'s own docstring
for the full account. All three fixed at the source; this test proves the
gate that now watches for the shape across the whole shipped site.

Run:  python ops/tests/test_gate_no_double_encoded_entities.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight  # noqa: E402


def main() -> int:
    fails = []

    # 1. The real live regression shape: a double-escaped decimal entity.
    r = preflight.check_double_encoded_entities(
        "The shelf of this season&amp;#x27;s kit")
    if r != ["&amp;#x27;"]:
        fails.append("hex double-encoded entity not caught: %r" % (r,))

    # 2. The other real live shape: a double-escaped named entity.
    r = preflight.check_double_encoded_entities(
        "&amp;amp; is not the same as &amp;.")
    if "&amp;amp;" not in r:
        fails.append("named double-encoded entity not caught: %r" % (r,))

    # 3. Correctly single-escaped text (what the fix produces): no finding.
    r = preflight.check_double_encoded_entities(
        "The shelf of this season&#x27;s kit")
    if r:
        fails.append("correctly single-escaped entity wrongly flagged: %r" % (r,))

    # 4. Plain text with a real ampersand, HTML-escaped once, same check:
    #    "Sort & Straighten" -> "Sort &amp; Straighten" must not be flagged.
    #    It has no entity-shaped tail after the escaped "&", so the regex
    #    (which requires "&amp;" followed by "#digits;" or "word;") must not
    #    match it.
    r = preflight.check_double_encoded_entities("Sort &amp; Straighten")
    if r:
        fails.append("plain '&amp;' with no entity tail wrongly flagged: %r" % (r,))

    # 5. No entities at all: no finding, no crash.
    r = preflight.check_double_encoded_entities("Nothing to see here.")
    if r:
        fails.append("plain text wrongly flagged: %r" % (r,))

    # 6. Two distinct double-encoded entities in the same string: both
    #    reported, deduplicated, sorted.
    r = preflight.check_double_encoded_entities(
        "a&amp;#39;b and c&amp;#39;d and e&amp;amp;f")
    if r != ["&amp;#39;", "&amp;amp;"]:
        fails.append("multi-entity string not fully/correctly reported: %r" % (r,))

    # 7. Run the real gate against the actual committed corpus (post-fix):
    #    must come back clean, proving the fix actually landed sitewide,
    #    not just in the one file this defect was first found in.
    preflight.FAIL.clear()
    preflight.WARN.clear()
    preflight.gate_no_double_encoded_entities()
    if preflight.FAIL:
        fails.append("real committed site still carries a double-encoded "
                      "entity: %r" % (preflight.FAIL,))

    # 8. Prove the gate would have caught the exact live regression, planted
    #    against the real committed file, without touching the working tree.
    real = open(os.path.join(ROOT, "site", "how-to-clean-anything.html"),
                encoding="utf-8").read()
    planted = real.replace("this season&#x27;s kit",
                            "this season&amp;#x27;s kit", 1)
    if planted == real:
        fails.append("planted-regression fixture did not match real content; "
                      "test is stale")
    elif not preflight.check_double_encoded_entities(planted):
        fails.append("planted real-file regression not caught")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_no_double_encoded_entities, 8/8 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
