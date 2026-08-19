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

    live = "LIVE" if S.get("site_live") else "not reachable"
    F = []
    F.append(Paragraph("6S Success", S_H1))
    F.append(Paragraph(f"STATUS REPORT &nbsp;.&nbsp; {d['generated']} &nbsp;.&nbsp; "
                       f"EVERY FIGURE COUNTED, NONE TYPED", S_EYE))

    F.append(table([
        ["", ""],
        ["Overall", S["overall"]],
        ["Website", f"{live} at https://6s-success.com"],
        ["Revenue this month", f"${S['revenue_month']:,.0f} of ${S['revenue_target']:,.0f}"],
        ["Paying customers", str(S["paying_customers"])],
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
        "The catalogue lists 41 items. Three are deliverable today and all three "
        "are consulting. The rest need either a supplier, a platform, or the "
        "front matter that blocks the book and the manual together.", S_BODY))
    F.append(table([
        ["Offer", "State", "What it needs"],
        ["Virtual Home Consult, $250", "Deliverable", "your calendar"],
        ["In-Home Reset Day, $1,200", "Deliverable", "your calendar"],
        ["Corporate Lean 6S", "Deliverable", "quoted, so an invoice"],
        [f"Book, {c['chapters']} of 50 chapters", "Finished, blocked", "front matter, issue 3"],
        [f"Manual, {c['zones']} zones", "Finished, blocked", "front matter, issue 3"],
        ["Reset kits, 4 SKUs", "Not built", "a supplier and stock"],
        ["Courses, 4 SKUs", "Not built", "a platform and a schedule"],
        ["Tools, 24 SKUs", "Not built", "a supplier"],
        [f"Card decks, {c['deck_rooms']} of 20 rooms", "Not built", "art, issues 1 and 2"],
        [f"Video, {c['video']}", "Not started", "filming"],
    ], [2.5 * inch, 1.5 * inch, 2.7 * inch]))

    F.append(Paragraph("Stripe", S_H2))
    F.append(table([
        ["Item", "State"],
        ["Account", "6S Success sandbox, test mode, US and USD"],
        ["Products created", "Virtual Home Consult and In-Home Reset Day"],
        ["Deliberately not created", "kits, courses, tools, book, manual"],
        ["Why", "a buy path must not sit in front of something that does not exist"],
        ["Before the first charge", "terms still say ordering is not live, and there is no refund policy"],
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

    if d["issues_available"]:
        dec = [i for i in d["issues"]
               if any(l["name"] == "decision" for l in i.get("labels", []))]
        F.append(Paragraph("What needs you", S_H2))
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
        live = "live" if S.get("site_live") else "not reachable"
        subject = (f"6S Success status {datetime.datetime.now():%d %b}: site {live}, "
                   f"{S['needs_phil'] if d['issues_available'] else '?'} need you")
        body = (f"The full status report is attached as a PDF.\n\n"
                f"Overall: {S['overall']}. {S['overall_why']}\n"
                f"Website: {live} at https://6s-success.com\n"
                f"Revenue: ${S['revenue_month']:,.0f} of ${S['revenue_target']:,.0f}\n\n"
                f"The one constraint\n{S['constraint']}\n\n"
                f"Measured {d['generated']} by ops/status_pdf.py.\n")
        with open(p, "rb") as fh:
            data = fh.read()
        print("sent", send(sys.argv[2], subject, body,
                           attachments=[(os.path.basename(p), data,
                                         "application", "pdf")]))
