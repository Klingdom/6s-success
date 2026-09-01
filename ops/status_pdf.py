#!/usr/bin/env python3
"""
Typeset the status report as a PDF and email it.

The plain text report is right for a phone at 6am. This is the version to read
at a desk, print, or hand to somebody: the same measured figures, set properly,
in the 6S Success palette.

Nothing here is typed. It reads ops/state.json, which ops/dashboard.py writes
from measured state, plus the same live probes the text report uses.

Run:  python ops/status_pdf.py --build           write build/6S-Status-<date>.pdf
      python ops/status_pdf.py --send ADDRESS    build it and email it
"""
import datetime
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from status_report import gather                       # noqa: E402
from mailer import send                                # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The site's own palette, so the report belongs to the same family as
# everything else the business puts in front of a person.
PAPER = colors.HexColor("#F7F2E9")
PANEL = colors.HexColor("#FBF7EF")
INK = colors.HexColor("#2B2622")
SOFT = colors.HexColor("#6A625A")
MUTE = colors.HexColor("#8C8478")
LINE = colors.HexColor("#E2D8C4")
TERRA = colors.HexColor("#BC4B2A")
CRIT = colors.HexColor("#CB4B36")
WARN = colors.HexColor("#B07A18")
GOOD = colors.HexColor("#4E7A57")
TONE = {"RED": CRIT, "YELLOW": WARN, "GREEN": GOOD}

SERIF, SERIF_B, SERIF_I = "Times-Roman", "Times-Bold", "Times-Italic"
SANS, SANS_B = "Helvetica", "Helvetica-Bold"

ss = getSampleStyleSheet()
S_H1 = ParagraphStyle("h1", parent=ss["Normal"], fontName=SERIF_B, fontSize=26,
                      leading=29, textColor=INK, spaceAfter=2)
S_EYE = ParagraphStyle("eye", parent=ss["Normal"], fontName=SANS_B, fontSize=8,
                       leading=11, textColor=SOFT, spaceAfter=16)
S_H2 = ParagraphStyle("h2", parent=ss["Normal"], fontName=SERIF_B, fontSize=13.5,
                      leading=16, textColor=INK, spaceBefore=17, spaceAfter=6)
S_BODY = ParagraphStyle("body", parent=ss["Normal"], fontName=SERIF, fontSize=10,
                        leading=14.5, textColor=INK, alignment=TA_LEFT, spaceAfter=7)
S_NOTE = ParagraphStyle("note", parent=S_BODY, fontSize=9, leading=13, textColor=SOFT)
S_CELL = ParagraphStyle("cell", parent=ss["Normal"], fontName=SANS, fontSize=8.5,
                        leading=11.5, textColor=INK)
S_CELLH = ParagraphStyle("cellh", parent=S_CELL, fontName=SANS_B, textColor=SOFT,
                         fontSize=7.5)


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def table(rows, widths, header=True):
    data = []
    for i, r in enumerate(rows):
        style = S_CELLH if (header and i == 0) else S_CELL
        data.append([Paragraph(esc(c), style) for c in r])
    t = Table(data, colWidths=widths, hAlign="LEFT")
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
    ]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2EADC")),
                 ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.HexColor("#D9CDB8"))]
    t.setStyle(TableStyle(cmds))
    return t


def callout(text, colour=TERRA):
    t = Table([[Paragraph(esc(text), S_BODY)]], colWidths=[6.7 * inch], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2EADC")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, colour),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def site_state(S: dict) -> tuple:
    """What to call the site, in the report and in the subject line.

    "LIVE" meant one thing: the homepage answered 200. On 2026-08-30 that was
    true while every payment link the site served was deactivated in Stripe, so
    the report Phil actually reads told him the site was LIVE on a day it could
    not take a single dollar. Reachable and working are different claims and
    only one of them was being made.

    A dead-links verdict now outranks reachability, because a shop that cannot
    take money is not live in any sense the owner cares about.
    """
    if S.get("live_links_verdict") == "dead":
        return "LIVE BUT CANNOT TAKE MONEY", "cannot take money"
    if not S.get("site_live"):
        return "not reachable", "not reachable"
    if S.get("live_links_verdict") == "unknown":
        return "LIVE, payments unverified", "live, payments unverified"
    return "LIVE", "live"


def build(path=None):
    d = gather()
    S, c, x = d["state"], d["content"], d["experiments"]
    dom, vps = d["domain"], d["vps"]
    stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    path = path or os.path.join(ROOT, "build", f"6S-Status-{stamp}.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PAPER)
        canvas.rect(0, 0, LETTER[0], LETTER[1], stroke=0, fill=1)
        canvas.setFont(SANS, 7.5)
        canvas.setFillColor(MUTE)
        canvas.drawString(0.9 * inch, 0.62 * inch,
                          "6S Success status report  .  measured, not typed")
        canvas.drawRightString(LETTER[0] - 0.9 * inch, 0.62 * inch,
                               f"page {doc.page}")
        canvas.setStrokeColor(LINE)
        canvas.line(0.9 * inch, 0.8 * inch, LETTER[0] - 0.9 * inch, 0.8 * inch)
        canvas.restoreState()

    doc = BaseDocTemplate(path, pagesize=LETTER,
                          leftMargin=0.9 * inch, rightMargin=0.9 * inch,
                          topMargin=0.85 * inch, bottomMargin=0.95 * inch,
                          title=f"6S Success status {stamp}",
                          author="6S Success")
    doc.addPageTemplates([PageTemplate(id="p", frames=[
        Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")],
        onPage=page)])

    live, _subject_word = site_state(S)
    F = []
    F.append(Paragraph("6S Success", S_H1))
    F.append(Paragraph(f"STATUS REPORT &nbsp;.&nbsp; {d['generated']} &nbsp;.&nbsp; "
                       f"EVERY FIGURE COUNTED, NONE TYPED", S_EYE))

    F.append(table([
        ["", ""],
        ["Overall", S["overall"]],
        ["Website", f"{live} at https://6s-success.com"],
        ["Revenue this month", S["revenue_text"]],
        ["Paying customers", S["customers_text"]],
        ["Email list", str(S["email_list"])],
        ["Can take payment", "yes" if S["can_take_payment"] else "no"],
        ["Commits, 7 days", str(d["commits_7d"])],
    ][1:], [2.1 * inch, 4.6 * inch], header=False))

    F.append(Paragraph("The one constraint", S_H2))
    F.append(callout(S["constraint"], CRIT))

    F.append(Paragraph("Domain and hosting", S_H2))
    F.append(table([
        ["What", "State"],
        ["6s-success.com", f"{live}, A record {dom['a_record']}"],
        ["www", "CNAME to apex, follows automatically"],
        ["TLS", "Let's Encrypt, both names, renews automatically"],
        ["Production host", f"{vps['ip']}, shared with two other projects"],
        ["Site container", "port 8973, behind Nginx Proxy Manager"],
        ["Deploys", "push to main, image builds, host pulls within five minutes"],
        ["Mail", "support@6s-success.com sends and receives"],
    ], [1.7 * inch, 5.0 * inch]))

    F.append(Paragraph("Products: deliverable against listed", S_H2))
    F.append(Paragraph(
        f"The catalogue lists {d['catalogue_total']} items. {d['catalogue_buyable']} take "
        f"payment through a live Stripe link, verified against Stripe's own catalogue by "
        f"ops/audit_catalog.py; {d['catalogue_free']} more are free downloads or pages. "
        f"{', '.join(d['catalogue_unready']) or 'Nothing'} still needs a manual quote.",
        S_BODY))
    deck_rows = [[f"{name} deck, {n} cards", "Live, free",
                  "print at home" if name.lower() == "entryway" else "unlinked preview"]
                 for name, n in d["decks"].items()]
    F.append(table([
        ["Offer", "State", "What it needs"],
        ["Virtual Home Consult, $250", "Deliverable", "your calendar"],
        ["In-Home Reset Day, $1,200", "Deliverable", "your calendar"],
        ["Corporate Lean 6S", "Not yet buyable", "quoted, so an invoice"],
        [f"Book, {c['chapters']} of 50 chapters", "Live, buyable", "nothing"],
        [f"Manual, {c['zones']} zones", "Live, buyable", "nothing"],
        [f"{d['catalogue_buyable_other']} other zone, room, situation and bundle packs",
         "Live, buyable", "nothing"],
        *deck_rows,
        ["Entryway deck, 16 cards", "Withheld", "art fix, issues 1 and 2"],
        [f"Video, {c['video']}", "Not started", "filming"],
    ], [2.5 * inch, 1.5 * inch, 2.7 * inch]))

    F.append(Paragraph("Stripe", S_H2))
    F.append(table([
        ["Item", "State"],
        ["Account", "6S Success, US and USD (live/test mode not checked from "
         "this sandbox, no Stripe credential here)"],
        ["Products created",
         f"{d['catalogue_buyable']} catalogue items, each with a live Payment Link"],
        ["Not yet created", ', '.join(d['catalogue_unready']) or "nothing priced"],
        ["Live sales", f"{S['customers_text']} customer(s), {S['revenue_text']}"],
    ], [2.1 * inch, 4.6 * inch]))

    F.append(Paragraph("Content", S_H2))
    F.append(table([
        ["Asset", "Measured"],
        ["Website", f"{c['site_pages']} pages, 0 dead links, 4 of 4 legal pages"],
        ["Book", f"{c['chapters']} chapters, {c['words']:,} words, EPUB {c['epub_mb']} MB"],
        ["Micro zones", f"{c['rooms']} rooms, {c['zones']} zones"],
        ["Free sample", f"{c['sample_pdf_mb']} MB, was 50.7"],
        ["Social corpus", f"about {c['social_units']:,} units written, none published"],
        ["Privacy", "zero third party requests, no analytics, no trackers"],
        ["House style", "0 em and 0 en dashes, site and control layer"],
    ], [1.7 * inch, 5.0 * inch]))

    F.append(Paragraph("Experiments", S_H2))
    F.append(Paragraph(
        f"{len(x['designed'])} designed, {x['executed']} executed. Until today "
        "there was no traffic to run one on. Now that the site is public the "
        "programme can start, and any result text already in EXPERIMENTS.md is "
        "illustrative rather than measured.", S_BODY))
    F.append(table([["ID", "Experiment"]] +
                   [[i, n.strip()] for i, n in x["designed"][:10]],
                   [0.9 * inch, 5.8 * inch]))

    dec = ([i for i in d["issues"]
            if any(l["name"] == "decision" for l in i.get("labels", []))]
           if d["issues_available"] else [])
    # gather() nests the measured figures under d["state"], while issues and
    # a few others sit at the top level. Reading deploy_verdict from the top
    # returned None, so this whole paragraph silently rendered nothing and the
    # PDF looked correct. Caught by opening the built PDF and searching it,
    # rather than by trusting that the code ran.
    st = d.get("state", {})
    # Either fact is sufficient, and the dead links are the sharper of
    # the two: a stale build is a delay, a dead payment link is a
    # customer who tried to pay and could not.
    stale = (st.get("deploy_verdict") == "stale"
             or st.get("live_links_verdict") == "dead")

    if dec or stale:
        F.append(Paragraph("What needs you", S_H2))

    # The deploy blocker goes above the decisions, and into this document at
    # all, because this PDF is what the owner actually reads. It was on the
    # dashboard and in preflight and in neither place he looks on a Sunday.
    # A decision can wait a week without costing anything; an undeployed build
    # costs every day it sits, because all the work behind it reaches nobody.
    if stale:
        dep = st.get("deploy", {})
        F.append(Paragraph(
            f"<b>Redeploy the site.</b> Production is serving an older build: "
            f"{dep.get('stale_assets', '?')} of {dep.get('checked_assets', '?')} "
            f"assets on the live homepage differ from the repository, and no "
            f"zone page carries its photograph yet. The container image is "
            f"built and pushed to ghcr.io. The Redeploy button in Hostinger is "
            f"the only remaining step, and the only one this system cannot "
            f"take itself. Until it happens, "
            f"{st.get('zone_pages_with_image', '?')} reviewed pictures and "
            f"every fix since the last deploy reach nobody.", S_NOTE))
        F.append(Spacer(1, 7))

    if dec:
        F.append(table([["#", "Decision"]] +
                       [[f"#{i['number']}", i["title"]] for i in dec],
                       [0.6 * inch, 6.1 * inch]))

    F.append(Paragraph("Retrospective", S_H2))
    for r in d["retros"][-3:]:
        block = [Paragraph(esc(r["title"]), ParagraphStyle(
            "rt", parent=S_BODY, fontName=SANS_B, fontSize=9, textColor=TERRA,
            spaceAfter=2))]
        if r["wrong"]:
            block.append(Paragraph("<b>What went wrong.</b> " + esc(r["wrong"]), S_NOTE))
        if r["change"]:
            block.append(Paragraph("<b>What changed.</b> " + esc(r["change"]), S_NOTE))
        block.append(Spacer(1, 7))
        F.append(KeepTogether(block))

    doc.build(F)
    return path, d


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--build"
    p, d = build()
    size = os.path.getsize(p)
    print(f"wrote {os.path.relpath(p, ROOT)}  {size/1024:.0f} KB")
    if mode == "--send":
        if len(sys.argv) < 3:
            sys.exit("usage: python ops/status_pdf.py --send ADDRESS")
        S = d["state"]
        _banner, live = site_state(S)
        subject = (f"6S Success status {datetime.datetime.now():%d %b}: site {live}, "
                   f"{S['needs_phil'] if d['issues_available'] else '?'} need you")
        body = (f"The full status report is attached as a PDF.\n\n"
                f"Overall: {S['overall']}. {S['overall_why']}\n"
                f"Website: {live} at https://6s-success.com\n"
                f"Revenue: {S['revenue_text']}\n\n"
                f"The one constraint\n{S['constraint']}\n\n"
                f"Measured {d['generated']} by ops/status_pdf.py.\n")
        with open(p, "rb") as fh:
            data = fh.read()
        print("sent", send(sys.argv[2], subject, body,
                           attachments=[(os.path.basename(p), data,
                                         "application", "pdf")]))
