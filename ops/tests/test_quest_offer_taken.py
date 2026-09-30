#!/usr/bin/env python3
"""
Prove quest.js reports the offer being TAKEN, for both pitches, and that the
SKU it reports is the one the button actually points at.

WHY THIS EXISTS
---------------
The quest's one offer appears only when two zones are holding. Measured
2026-09-30: quest-zone-held is 4 events from 3 visitors, and exactly one
visitor has ever held two. quest-offer-shown has existed since the offer did
and has never fired. So the offer is untested rather than failing, and the
number that will decide whether it works is shown-to-taken.

The taken half was only half measured. The paid pitch points at
buy.stripe.com, which measure.js already turns into buy-click. The free pitch
repoints the SAME button at deck.html, which matches none of measure.js's
branches: not stripe, not outbound (it is same-origin), not `downloads/`, not
`contact.html?ref=`. Taking the free offer therefore fired nothing at all, and
would have been indistinguishable from ignoring it.

The trap this test exists for is the SKU. The markup ships
data-sku="PACK-HOUSE" and the free branch repoints the same element, so an
event that read the SKU from anywhere but the live attribute would file a free
download as a click on the $19 pack. quest.js already had that bug once, in
the same three lines, and its own comment records the fix.

Run:  python ops/tests/test_quest_offer_taken.py
"""
import io
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUEST = os.path.join(ROOT, "site", "assets", "js", "quest.js")

HARNESS = """
var fired = [];
function m(name, payload) { fired.push([name, payload]); }
var offerCta = { sku: %s, getAttribute: function (k) {
  return k === "data-sku" ? this.sku : null; } };
function click() {
  m("quest-offer-taken",
    { offer: (offerCta.getAttribute("data-sku") || "").slice(0, 32) });
}
%s
console.log(JSON.stringify(fired));
"""


def _run(sku_js, body):
    node = shutil.which("node")
    if not node:
        return None
    p = subprocess.run([node, "-e", HARNESS % (sku_js, body)],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout.strip())


def case_paid_pitch_reports_the_pack_sku():
    out = _run('"PACK-HOUSE"', "click();")
    if out is None:
        print("  no node here, NOT VERIFIED.")
        return
    assert out == [["quest-offer-taken", {"offer": "PACK-HOUSE"}]], out


def case_free_pitch_reports_the_deck_sku_not_the_pack():
    """The exact bug the code comment records: a free download filed as $19."""
    out = _run('"DECK-ENTRY"', "click();")
    if out is None:
        return
    assert out == [["quest-offer-taken", {"offer": "DECK-ENTRY"}]], out
    assert "PACK-HOUSE" not in json.dumps(out)


def case_a_missing_sku_does_not_throw():
    out = _run("null", "click();")
    if out is None:
        return
    assert out == [["quest-offer-taken", {"offer": ""}]], out


def case_sku_is_length_capped():
    out = _run('"' + "X" * 80 + '"', "click();")
    if out is None:
        return
    assert len(out[0][1]["offer"]) == 32, out


def case_the_real_file_reads_the_live_attribute():
    src = io.open(QUEST, encoding="utf-8").read()
    i = src.index('m("quest-offer-taken"')
    block = src[i:i + 200]
    assert 'offerCta.getAttribute("data-sku")' in block, block
    # It must not hardcode either SKU, which is how the original bug read.
    assert "PACK-HOUSE" not in block, block
    assert "DECK-ENTRY" not in block, block


def case_the_event_carries_no_household_detail():
    src = io.open(QUEST, encoding="utf-8").read()
    i = src.index('m("quest-offer-taken"')
    block = src[i:src.index("}", i) + 1]
    for forbidden in ("room", "zone", "held"):
        assert forbidden not in block, (forbidden, block)


def case_the_sku_moves_with_the_href_in_the_real_file():
    """If the CTA is repointed without its SKU, this event lies."""
    src = io.open(QUEST, encoding="utf-8").read()
    i = src.index('cta.setAttribute("href", spec.href)')
    j = src.index('cta.setAttribute("data-sku", spec.sku)')
    assert i < j, "href is repointed but data-sku is not set after it"


def case_quest_js_parses():
    node = shutil.which("node")
    if not node:
        return
    p = subprocess.run([node, "--check", QUEST], capture_output=True,
                       text=True, timeout=60)
    assert p.returncode == 0, p.stderr


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
