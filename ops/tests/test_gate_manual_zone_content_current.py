#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_manual_zone_content_current() catches the
Micro Zone Manual's own zone text (purpose, done_looks_like) drifting from
content/manual/source/content.json.

Real shape: LEARNINGS.md LRN-0019 (2026-09-26). A typo in content.json's
Kitchen Cooking Zone `purpose` field reached 21 generated artifacts once
their generators reran, but content/manual/6S Home Micro Zone SOP Field
Manual v3.html is hand-authored HTML that nothing in ops/ re-derives from
content.json, so a future corpus correction can silently fail to reach it.
No gate existed to catch that until this one. This test never touches the
real, large content.json or the real Manual file: a small fixture pair
stands in for the real shape (one room, one zone, one matching or
mismatching <article>).

Run:  python ops/tests/test_gate_manual_zone_content_current.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CONTENT_REL = os.path.join("content", "manual", "source", "content.json")
MANUAL_REL = os.path.join(
    "content", "manual", "6S Home Micro Zone SOP Field Manual v3.html")

PURPOSE = "The spot where pockets empty on the way in and refill on the way out."
DONE = "One tray holding keys and sunglasses, bare surface on both sides of the tray."


def _content_json():
    return {
        "rooms": [{
            "room": "Entryway",
            "zones": [{
                "zone": "Landing Zone",
                "purpose": PURPOSE,
                "done_looks_like": DONE,
            }],
        }],
    }


def _manual_html(purpose=PURPOSE, done=DONE, zone_id="entryway--landing-zone",
                  include_article=True):
    if not include_article:
        return "<html><body>no zones here</body></html>\n"
    return (
        '<html><body>\n'
        '<article class="zone" id="%s">\n'
        '<div class="zhead"><h3>Landing Zone</h3></div>\n'
        '<p class="zpurpose">%s</p>\n'
        '<div class="done"><div class="lbl">Done looks like</div>'
        '<p>%s</p></div>\n'
        '</article>\n'
        '</body></html>\n' % (zone_id, purpose, done)
    )


def _fixture(tmp_base, name, content=None, manual=None):
    """A fresh fixture directory with just the two files this gate reads."""
    tmp = os.path.join(tmp_base, name)
    os.makedirs(os.path.join(tmp, "content", "manual", "source"), exist_ok=True)
    io.open(os.path.join(tmp, CONTENT_REL), "w", encoding="utf-8").write(
        json.dumps(content if content is not None else _content_json()))
    io.open(os.path.join(tmp, MANUAL_REL), "w", encoding="utf-8").write(
        manual if manual is not None else _manual_html())
    return tmp


def _run_gate(tmp):
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_manual_zone_content_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    import tempfile
    import shutil

    tmp_base = tempfile.mkdtemp()
    fails = []
    try:
        # 1. The real, current shape: purpose and done_looks_like both match.
        tmp = _fixture(tmp_base, "clean")
        r, w = _run_gate(tmp)
        if r or w:
            fails.append("a genuinely matching Manual was wrongly flagged: "
                         "FAIL=%r WARN=%r" % (r, w))

        # 2. The real LRN-0019 shape: content.json's purpose changed (a
        #    correction landed) and the Manual's own text was never updated.
        tmp = _fixture(tmp_base, "purpose-drift",
                       manual=_manual_html(purpose="A stale, uncorrected sentence."))
        r, w = _run_gate(tmp)
        if not r or "entryway--landing-zone.purpose" not in r[0][1]:
            fails.append("a real purpose mismatch was not caught by name: %r" % (r,))

        # 3. Same shape, the other field LRN-0019 named: done_looks_like.
        tmp = _fixture(tmp_base, "done-drift",
                       manual=_manual_html(done="A stale done-looks-like sentence."))
        r, w = _run_gate(tmp)
        if not r or "entryway--landing-zone.done_looks_like" not in r[0][1]:
            fails.append("a real done_looks_like mismatch was not caught by "
                         "name: %r" % (r,))

        # 4. A zone exists in content.json with no matching <article> in the
        #    Manual at all (a new zone, or an id that drifted out of sync
        #    with ops/build_zone_pages.py's own room--zone slug convention).
        tmp = _fixture(tmp_base, "missing-article",
                       manual=_manual_html(include_article=False))
        r, w = _run_gate(tmp)
        if not r or "entryway--landing-zone" not in r[0][1]:
            fails.append("a zone missing from the Manual entirely was not "
                         "caught by name: %r" % (r,))

        # 5. A zone id that no longer matches the slug convention (a rename
        #    on one side only) is the same missing-article shape, by a
        #    different real cause.
        tmp = _fixture(tmp_base, "renamed-id",
                       manual=_manual_html(zone_id="entryway--landing-zone-v2"))
        r, w = _run_gate(tmp)
        if not r or "entryway--landing-zone" not in r[0][1]:
            fails.append("a renamed zone id was not caught by name: %r" % (r,))

        # 6. Neither file exists yet: nothing to check, not a failure.
        tmp = os.path.join(tmp_base, "neither-file")
        os.makedirs(tmp)
        r, w = _run_gate(tmp)
        if r or w:
            fails.append("an environment with neither file present was not "
                         "silently skipped: FAIL=%r WARN=%r" % (r, w))

        # 7. A blank field in the corpus (nothing authored yet) must never
        #    be compared as if it were a real mismatch.
        blank_content = _content_json()
        blank_content["rooms"][0]["zones"][0]["purpose"] = ""
        tmp = _fixture(tmp_base, "blank-field", content=blank_content,
                       manual=_manual_html())
        r, w = _run_gate(tmp)
        if r or w:
            fails.append("a blank content.json field was wrongly compared "
                         "as a mismatch: FAIL=%r WARN=%r" % (r, w))
    finally:
        shutil.rmtree(tmp_base, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_manual_zone_content_current, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
