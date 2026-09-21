#!/usr/bin/env python3
"""
Build the free B2B artefact: the 6S Zone Scoring Sheet and Layered Audit
Template, a blank printable a facilities/EHS/ops buyer can use before they
ever talk to us.

WHY THIS EXISTS
---------------
REVIEW-COMMERCE-2026-09-07.md section 4.2 item 2: "The one B2B artefact we
can honestly give away: the zone scoring sheet and the layered audit
template. The engagement's first deliverable is a scored 6S baseline per
zone. That instrument can be published as a blank template with the scoring
definitions. It requires no client result, so nothing about it is
fabricated, and it is the artefact an EHS or ops manager will actually
keep."

It is BLANK. No filled-in example, no client's zone, no score anybody
actually gave a real area, because we have never run this engagement for a
client and a worked example would have to invent one. corporate.html
already says so about itself and this file inherits the same constraint.

WHY IT CAN SHIP TODAY
---------------------
No illustration, no printer, no supplier, no email gate. It is a page a
buyer opens and prints, the same shape as build_standards.py's free
Standards Pack and build_zone_map_pack.py's free Micro Zone Map, and it
follows build_zone_map_pack.py's pattern of writing the SAME bytes to
build/ and to site/downloads/ from one main(), rather than
build_standards.py's older shape (a build/ copy and a hand-copied
site/downloads/ copy that can drift, the exact gap gate_standards_pack_
current exists to catch). One generator, one write, nothing to forget to
copy.

WHAT MUST NEVER DRIFT FROM corporate.html
------------------------------------------
The layered-audit cadence described here (team leader daily or per shift,
supervisor weekly, manager monthly, same scoring sheet each time) is the
same claim build_corporate.py's COMPONENTS makes in its "Audit and
sustain" component. main() asserts the anchor sentence is still live on
the shipped page, so this artefact and the page it is linked from cannot
quietly disagree about what the audit actually is.

OWNERSHIP
---------
This file owns build/6S-Zone-Scoring-and-Audit-Template.html and
site/downloads/6S-Zone-Scoring-and-Audit-Template.html completely.
Registered in preflight's GENERATOR_OWNERSHIP_CHAIN and in
ops/check_pack_pages.py's PRINTABLES list, the one check that can see a
printable document paginate wrong.

Run:  python ops/build_corporate_asset.py
"""
from __future__ import annotations

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

CORPORATE_HTML = os.path.join(ROOT, "site", "corporate.html")
OUT_BUILD = os.path.join(ROOT, "build", "6S-Zone-Scoring-and-Audit-Template.html")
OUT_SITE = os.path.join(ROOT, "site", "downloads",
                         "6S-Zone-Scoring-and-Audit-Template.html")
URL = "https://6s-success.com/downloads/6S-Zone-Scoring-and-Audit-Template.html"

TITLE = "The 6S Zone Scoring Sheet and Layered Audit Template"

# The anchor sentence this artefact must never disagree with. Verbatim from
# build_corporate.py's COMPONENTS, "Audit and sustain". Checked against the
# LIVE shipped page in main(), not against the source constant, so a future
# edit to either file that breaks the agreement is caught where a customer
# would actually see the mismatch.
AUDIT_ANCHOR = ("the team leader checks daily or per shift, the "
                "supervisor weekly, the manager monthly")

# The five passes this sheet scores per zone. Sustain is not a sixth row
# here: it is the layered audit itself, the second sheet, not a one-time
# score alongside the other five.
PASSES = ["Sort", "Straighten", "Shine", "Safety", "Standardize"]

RUBRIC = [
    (1, "Not started, or unsafe as found."),
    (2, "Started, but holds only when one specific person remembers."),
    (3, "Workable most days; a stranger could not tell what right looks "
        "like without asking."),
    (4, "Holds under normal conditions; the standard is posted where the "
        "work happens."),
    (5, "Holds without reminding; a stranger could follow it from what "
        "they see alone."),
]

TIERS = [
    ("Team leader", "Daily, or once per shift"),
    ("Supervisor", "Weekly"),
    ("Manager", "Monthly"),
]

AUDIT_ROWS = 16
SCORE_ROWS_PER_SHEET = 6


def esc(t) -> str:
    return (str(t or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


CSS = """
@page { size: letter; margin: 0.55in; }
*{box-sizing:border-box}
body{margin:0;background:#EFE7D6;color:#2B2622;
  font-family:"Newsreader",Georgia,serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.intro{max-width:7.3in;margin:0 auto;padding:40px 24px 8px}
.intro h1{font-family:"Fraunces",Georgia,serif;font-size:32px;margin:0 0 10px;
  letter-spacing:-.015em;line-height:1.1}
.intro p{color:#584f46;margin:0 0 11px;font-size:15px;line-height:1.6;max-width:74ch}
.intro .k{font-size:12.5px;color:#666058;font-family:"Inter",Arial,sans-serif}

.sheet{width:7.4in;margin:0 auto 26px;background:#FBF7EF;border:1px solid #E2D8C4;
  border-top:6px solid #BC4B2A;padding:0.42in 0.44in 0.34in}
.sheet.audit{border-top-color:#4E7A57}
.shead{display:flex;justify-content:space-between;align-items:baseline;
  border-bottom:1px solid #E2D8C4;padding-bottom:9px;margin-bottom:14px}
.shead h2{font-family:"Fraunces",Georgia,serif;font-size:20pt;margin:0;
  letter-spacing:-.015em;line-height:1.05}
.shead .n{font-family:"Inter",Arial,sans-serif;font-size:7.4pt;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:#666058;white-space:nowrap;
  padding-left:14px}
.lede{font-size:9.6pt;line-height:1.5;color:#584f46;margin:0 0 16px;max-width:70ch}

.fields{display:flex;flex-wrap:wrap;gap:0 26px;margin:0 0 18px;
  font-family:"Inter",Arial,sans-serif;font-size:8.6pt;letter-spacing:.04em;
  text-transform:uppercase;color:#666058;font-weight:700}
.fields span{display:inline-flex;align-items:flex-end;gap:6px;padding-bottom:5px}
.fields i{display:inline-block;width:150px;border-bottom:1px solid #C9BFA9;
  height:13px}

.twrap{width:100%}
table{width:100%;border-collapse:collapse;font-size:9.6pt}
th{font-family:"Inter",Arial,sans-serif;font-size:7.4pt;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:#666058;
  text-align:left;padding:6px 8px;border-bottom:1px solid #C9BFA9}
td{padding:9px 8px;border-bottom:1px solid #E2D8C4;vertical-align:top}
tr:last-child td{border-bottom:1px solid #C9BFA9}
.pass{font-weight:700;color:#2B2622;white-space:nowrap}
.dots{white-space:nowrap;font-family:"Inter",Arial,sans-serif;
  letter-spacing:.16em;color:#584f46}
.blank{color:#C9BFA9}

.rubric{margin-top:16px;padding-top:14px;border-top:1px solid #E2D8C4}
.rubric h3{font-family:"Inter",Arial,sans-serif;font-size:8pt;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:#5A714A;margin:0 0 8px}
.rubric ol{margin:0;padding:0 0 0 0;list-style:none}
.rubric li{display:flex;gap:10px;font-size:9pt;line-height:1.44;
  color:#584f46;margin:0 0 5px}
.rubric b{flex:0 0 16px;color:#BC4B2A;font-weight:700}

.tiers{display:flex;gap:18px;margin:0 0 16px;flex-wrap:wrap}
.tier{flex:1 1 180px;border:1px solid #E2D8C4;border-radius:6px;
  padding:10px 12px;background:#F7F2E9}
.tier b{display:block;font-family:"Inter",Arial,sans-serif;font-size:8pt;
  letter-spacing:.08em;text-transform:uppercase;color:#466E4E;margin-bottom:3px}
.tier span{font-size:9.4pt;color:#584f46}

.sig{margin-top:18px;padding-top:13px;border-top:1px solid #E2D8C4;
  display:flex;gap:16px;align-items:flex-end;
  font-family:"Inter",Arial,sans-serif;font-size:6.8pt;
  letter-spacing:.09em;text-transform:uppercase;color:#666058;font-weight:700}
.sig i{flex:1;border-bottom:1px solid #C9BFA9;height:15px;display:block;
  margin-bottom:-1px}
.sig .brand{flex:0 0 auto;letter-spacing:.05em}

/* Screen: this is opened on a phone before anyone prints it. At a fixed
   7.4in the sheet is 710px, wider than a 390px viewport, so let width be
   the screen below paper width and stop measuring type in points. The
   @page/print rules below are untouched. */
@media screen and (max-width:760px){
  body{overflow-x:hidden}
  .sheet{width:auto;max-width:100%;margin:0 12px 20px;padding:22px 18px 20px}
  .shead{flex-wrap:wrap;gap:4px}
  .shead h2{font-size:21px}
  .shead .n{padding-left:0}
  .lede{font-size:14.5px}
  /* The table itself scrolls sideways rather than forcing the whole page
     to, the same fix build_standards.py needed for its own fixed-width
     sheet: found live at 390px, four columns of a scoring table do not
     fit a phone and letting them push the page wide put the intro's own
     text off-screen too, not just the table. */
  .twrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
  table{font-size:12.5px;min-width:540px}
  th{font-size:10px}
  .fields{font-size:11px}
  .fields i{width:110px}
  .rubric li{font-size:12.5px}
  .tier span{font-size:13px}
  .sig{font-size:10.5px;flex-wrap:wrap}
  .intro{padding:28px 18px 4px}
  .intro h1{font-size:26px}
}
@media print{
  body{background:#fff}
  .intro{display:none}
  .sheet{margin:0;border:0;page-break-after:always;break-after:page}
  .sheet:last-child{page-break-after:auto;break-after:auto}
}
"""


def score_row(pass_name: str) -> str:
    dots = " &middot; ".join(str(n) for n in range(1, 6))
    return ('<tr><td class="pass">%s</td>'
            '<td class="dots">%s</td>'
            '<td class="blank">&nbsp;</td>'
            '<td class="blank">&nbsp;</td></tr>'
            % (esc(pass_name), dots))


def scoring_sheet(idx: int, total: int) -> str:
    rows = "".join(score_row(p) for p in PASSES)
    rubric = "".join(
        '<li><b>%d</b>%s</li>' % (n, esc(text)) for n, text in RUBRIC)
    return (
        '<section class="sheet">'
        '<div class="shead"><h2>Zone Scoring Sheet</h2>'
        '<span class="n">sheet %d of %d</span></div>' % (idx, total) +
        '<p class="lede">One zone per sheet. Score what you actually see '
        'today, not what the standard says should be there. Photocopy this '
        'page for every zone in the baseline.</p>' +
        '<div class="fields">'
        '<span>Site or area <i></i></span>'
        '<span>Zone <i></i></span>'
        '<span>Date <i></i></span>'
        '<span>Scored by <i></i></span>'
        '</div>' +
        '<div class="twrap"><table><thead><tr><th>Pass</th>'
        '<th>Circle a score</th>'
        '<th>What you saw</th><th>Action if below a 4</th></tr></thead>'
        '<tbody>' + rows + '</tbody></table></div>' +
        '<div class="rubric"><h3>What the score means</h3>'
        '<ol>' + rubric + '</ol></div>' +
        '<div class="sig">Reviewed with <i></i> Next score due <i></i>'
        '<span class="brand">6S Success &middot; Nova Consulting</span></div>'
        '</section>')


def audit_log() -> str:
    tiers = "".join(
        '<div class="tier"><b>%s</b><span>%s</span></div>' % (esc(n), esc(c))
        for n, c in TIERS)
    rows = "".join(
        '<tr><td class="blank">&nbsp;</td><td class="blank">&nbsp;</td>'
        '<td class="blank">&nbsp;</td><td class="blank">&nbsp;</td>'
        '<td class="blank">&nbsp;</td></tr>' for _ in range(AUDIT_ROWS))
    return (
        '<section class="sheet audit">'
        '<div class="shead"><h2>Layered Audit Log</h2>'
        '<span class="n">one area</span></div>' +
        '<p class="lede">The same scoring sheet the baseline used, checked '
        'again on a cadence, by three different people, so the trend line '
        'is comparable to day one instead of a fresh opinion each time.</p>' +
        '<div class="tiers">' + tiers + '</div>' +
        '<div class="twrap"><table><thead><tr><th>Date</th><th>Zone</th>'
        '<th>Checked by (tier)</th><th>Score</th><th>Notes</th></tr></thead>'
        '<tbody>' + rows + '</tbody></table></div>' +
        '<div class="sig">Area <i></i> Sponsor <i></i>'
        '<span class="brand">6S Success &middot; Nova Consulting</span></div>'
        '</section>')


def build() -> str:
    intro = (
        '<div class="intro">'
        '<h1>%s</h1>' % TITLE +
        '<p>The first deliverable of a Corporate Lean 6S engagement is a '
        'scored 6S baseline for every zone in the area. This is that '
        'instrument, blank: the same sheet used at the baseline and again '
        'by the layered audit afterwards, so a later score means something '
        'against the first one.</p>' +
        '<p>There is no filled-in example on this page. No corporate '
        'engagement has been sold through 6S Success, so a worked example '
        'would have to invent a client and a score, and we do not do '
        'that.</p>' +
        '<p>Print the Zone Scoring Sheet once per zone in your baseline, '
        'and the Layered Audit Log once per area, and reuse both on paper '
        'as many times as the audit runs.</p>' +
        '<p class="k">6S Success &middot; Nova Consulting &middot; '
        '6s-success.com &middot; free, no email required.</p>' +
        '</div>')

    sheets = "".join(scoring_sheet(i, SCORE_ROWS_PER_SHEET)
                      for i in range(1, SCORE_ROWS_PER_SHEET + 1))
    body = sheets + audit_log()

    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, '
            'initial-scale=1">'
            '<title>%s</title>' % esc(TITLE) +
            '<meta name="robots" content="noindex, follow">'
            '<link rel="canonical" href="%s">' % URL +
            '<style>%s</style></head><body>' % CSS + intro +
            '<main>' + body + '</main>' +
            '</body></html>')


def main() -> int:
    html = build()

    os.makedirs(os.path.dirname(OUT_BUILD), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_SITE), exist_ok=True)
    for path in (OUT_BUILD, OUT_SITE):
        io.open(path, "w", encoding="utf-8", newline="\n").write(html)

    # No dollar figure, anywhere. This is a free artefact and it stays one.
    money = re.findall(r"\$\s?\d", html)
    assert not money, "a price appeared on the free scoring/audit artefact"

    # No client claim of any kind: this repeats build_corporate.py's own
    # rule 1, because a worked example or a result would be exactly as
    # fabricated here as on the page it is linked from.
    banned = ["case study", "testimonial", "client said", "results for",
              "% improvement", "reduced by"]
    low = html.lower()
    for phrase in banned:
        assert phrase not in low, \
            "the free artefact carries a claim it should not: %r" % phrase

    # The layered-audit cadence here must still be the one corporate.html
    # actually promises, checked against the LIVE shipped page.
    if os.path.exists(CORPORATE_HTML):
        live = io.open(CORPORATE_HTML, encoding="utf-8").read()
        assert AUDIT_ANCHOR in live, (
            "corporate.html no longer states the audit cadence this "
            "artefact assumes (%r); the two would disagree about what the "
            "layered audit is" % AUDIT_ANCHOR)

    print("  wrote build/6S-Zone-Scoring-and-Audit-Template.html")
    print("  wrote site/downloads/6S-Zone-Scoring-and-Audit-Template.html")
    print("  %d scoring sheets, %d audit log rows, no price, no client claim"
          % (SCORE_ROWS_PER_SHEET, AUDIT_ROWS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
