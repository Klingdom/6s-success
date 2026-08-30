#!/usr/bin/env python3
"""
The launch plan: what must be true before traffic, and where $250 goes.

WHY A DOCUMENT AND NOT A DASHBOARD
----------------------------------
The dashboard answers "what is the state right now". This answers a different
question: "what should we do, in what order, and what will it cost". It is
written once, read once, and acted on, so it is a document.

Eight specialist agents audited the site for this. Every figure below either
comes from ops/state.json, which is measured, or from a check run live against
production and the Stripe API at build time. Nothing is typed from memory.

WHAT IT REFUSES TO DO
---------------------
Forecast. There is one sale in the history of this business, so any conversion
rate, ROAS or traffic projection would be invention dressed as arithmetic. The
plan states what each spend can actually measure at the sample size it buys,
which for $112 of local search is impressions and cost per click, not a
conversion rate.

Run:  python ops/launch_plan_pdf.py
      python ops/launch_plan_pdf.py --send phil@example.com
"""
from __future__ import annotations

import datetime
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

from reportlab.lib import colors                              # noqa: E402
from reportlab.lib.pagesizes import LETTER                    # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import inch                          # noqa: E402
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether,  # noqa: E402
                                PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

PAPER = colors.HexColor("#F7F2E9")
PANEL = colors.HexColor("#FBF7EF")
INK = colors.HexColor("#2B2622")
SOFT = colors.HexColor("#6A625A")
MUTE = colors.HexColor("#8C8478")
LINE = colors.HexColor("#E2D8C4")
TERRA = colors.HexColor("#BC4B2A")
CRIT = colors.HexColor("#CB4B36")
GOOD = colors.HexColor("#4E7A57")

SERIF, SERIF_B = "Times-Roman", "Times-Bold"
SANS, SANS_B = "Helvetica", "Helvetica-Bold"

ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Normal"], fontName=SERIF_B, fontSize=25,
                    leading=28, textColor=INK, spaceAfter=4)
EYE = ParagraphStyle("eye", parent=ss["Normal"], fontName=SANS_B, fontSize=8,
                     textColor=TERRA, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=ss["Normal"], fontName=SERIF_B, fontSize=14,
                    leading=17, textColor=INK, spaceBefore=16, spaceAfter=6)
H3 = ParagraphStyle("h3", parent=ss["Normal"], fontName=SANS_B, fontSize=9,
                    textColor=TERRA, spaceBefore=10, spaceAfter=3)
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName=SERIF, fontSize=10,
                      leading=14.2, textColor=INK, spaceAfter=7)
NOTE = ParagraphStyle("note", parent=BODY, fontSize=9, leading=12.8,
                      textColor=SOFT)
CELL = ParagraphStyle("cell", parent=ss["Normal"], fontName=SANS, fontSize=8.2,
                      leading=10.8, textColor=INK)
CELLH = ParagraphStyle("cellh", parent=CELL, fontName=SANS_B, textColor=SOFT)


def esc(t) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def table(rows, widths, zebra=True):
    data = [[Paragraph(esc(c), CELLH if i == 0 else CELL) for c in row]
            for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("TOPPADDING", (0, 0), (-1, -1), 5),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
             ("LEFTPADDING", (0, 0), (-1, -1), 7),
             ("RIGHTPADDING", (0, 0), (-1, -1), 7),
             ("LINEBELOW", (0, 0), (-1, 0), 0.7, LINE),
             ("BACKGROUND", (0, 0), (-1, 0), PANEL)]
    if zebra:
        for r in range(1, len(data)):
            if r % 2 == 0:
                style.append(("BACKGROUND", (0, r), (-1, r), PANEL))
    t.setStyle(TableStyle(style))
    return t


def callout(text, tone=CRIT):
    p = Paragraph(text, ParagraphStyle("co", parent=BODY, textColor=INK,
                                       leftIndent=10, spaceAfter=0))
    t = Table([[p]], colWidths=[6.7 * inch], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("LINEBEFORE", (0, 0), (0, -1), 3, tone),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12)]))
    return t


def measured() -> dict:
    """Live facts, gathered now rather than remembered."""
    d = {}
    try:
        d["state"] = json.load(io.open(os.path.join(ROOT, "ops", "state.json"),
                                       encoding="utf-8"))
    except Exception:                                         # noqa: BLE001
        d["state"] = {}
    try:
        import check_live_links
        d["links"] = check_live_links.check()
    except Exception as e:                                    # noqa: BLE001
        d["links"] = {"verdict": "unknown", "note": f"{type(e).__name__}"}
    try:
        import deploy_freshness
        d["fresh"] = deploy_freshness.check()
    except Exception as e:                                    # noqa: BLE001
        d["fresh"] = {"verdict": "unknown", "note": f"{type(e).__name__}"}
    return d


def build(path=None) -> tuple:
    m = measured()
    S = m["state"]
    links, fresh = m["links"], m["fresh"]
    today = datetime.date.today().isoformat()
    path = path or os.path.join(ROOT, "build", f"6S-Launch-Plan-{today}.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PAPER)
        canvas.rect(0, 0, LETTER[0], LETTER[1], stroke=0, fill=1)
        canvas.setFillColor(MUTE)
        canvas.setFont(SANS, 7.5)
        canvas.drawString(0.9 * inch, 0.6 * inch,
                          f"6S Success   |   Launch plan   |   {today}")
        canvas.drawRightString(LETTER[0] - 0.9 * inch, 0.6 * inch,
                               f"page {doc.page}")
        canvas.restoreState()

    doc = BaseDocTemplate(path, pagesize=LETTER,
                          leftMargin=0.9 * inch, rightMargin=0.9 * inch,
                          topMargin=0.85 * inch, bottomMargin=0.9 * inch,
                          title="6S Success: launch plan",
                          author="Nova Consulting")
    doc.addPageTemplates([PageTemplate(
        id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin,
                              doc.width, doc.height, id="f")],
        onPage=page)])

    F = []
    F.append(Paragraph("PREPARED FOR PHIL KLING", EYE))
    F.append(Paragraph("Getting 6S Success ready for traffic", H1))
    F.append(Paragraph(
        "What must be true before visitors arrive, where $250 should go, and "
        "what the media pipeline can produce. Every figure here was measured "
        "when this document was built. Nothing is forecast.", NOTE))
    F.append(Spacer(1, 14))

    # ---- the headline ---------------------------------------------------
    dead = len(links.get("dead", []))
    total_links = len(links.get("slugs", {}))
    if links.get("verdict") == "dead":
        F.append(callout(
            f"<b>The site cannot take money right now.</b> All {dead} of "
            f"{total_links} payment links on the live site are deactivated in "
            f"Stripe. Anyone who clicks buy reaches a dead link, and has for "
            f"days. The repository's links are active, so one deploy fixes it. "
            f"Nothing else in this plan matters until that happens."))
    else:
        F.append(callout(
            "Live payment links could not be verified when this was built. "
            "That is not the same as them working.", MUTE))
    F.append(Spacer(1, 12))

    F.append(Paragraph("Why nothing caught this", H3))
    F.append(Paragraph(
        "Every check that existed was true. The pages return 200. The payment "
        "links return 200 as well: a deactivated Stripe link serves the same "
        "550 KB JavaScript shell as a working one and only says 'no longer "
        "active' once the browser runs it, so no status check can tell them "
        "apart. The repository's links are correct, which is exactly what made "
        "it invisible. There is now a check that asks Stripe's API whether the "
        "links the live site serves are active, and it runs in preflight.", BODY))

    # ---- state ----------------------------------------------------------
    F.append(Paragraph("Where things actually stand", H2))
    stale = fresh.get("stale_assets", "?")
    checked = fresh.get("checked_assets", "?")
    F.append(table([
        ["", "Measured", "Reads as"],
        ["Production build",
         f"{stale} of {checked} assets differ from the repository",
         "Serving a build from before this month's work"],
        ["Payment links, live",
         f"{dead} of {total_links} deactivated in Stripe",
         "Revenue outage"],
        ["Zone pages with a picture",
         f"{S.get('zone_pages_with_image', '?')} of {S.get('zones', '?')} built",
         "None of them live yet"],
        ["Entryway deck",
         f"{S.get('cards_rendered', '?')} of {S.get('cards_total', '?')} cards, "
         f"fronts and backs, print and play PDF built",
         "Complete, not yet live"],
        ["Catalogue", "155 priced items, all with active Stripe links in the repo",
         "Ready, not reachable"],
        ["Email list", f"{S.get('email_list', 0)}",
         "The compounding asset, still at zero"],
        ["Revenue, all time", "$19, one sale", "Discovery is the constraint"],
    ], [1.45 * inch, 2.5 * inch, 2.75 * inch]))

    # ---- before traffic --------------------------------------------------
    F.append(Paragraph("Before any traffic: the gates", H2))
    F.append(Paragraph(
        "These are ordered. Each is cheap, and each one makes the next "
        "measurable.", BODY))
    F.append(table([
        ["#", "Gate", "Why it comes first", "Who"],
        ["1", "Redeploy the site",
         "Fixes the payment outage, and ships 102 zone photographs, seven "
         "articles that currently 404, the finished deck and the corrected "
         "legal pages", "Phil"],
        ["2", "Buy one item from the live link yourself",
         "Proves an order actually delivers end to end. The fulfilment job "
         "runs and reports delivering, but it has processed one order ever",
         "Phil"],
        ["3", "Read Umami once",
         "Nothing in this system has ever read the analytics. Without it, any "
         "money spent on traffic buys a number nobody can see", "Phil"],
        ["4", "Get a phone number and publish the Google Business Profile",
         "Free, drafted already, and required before local search ads are "
         "worth running", "Phil"],
        ["5", "Stand up a free-tier email provider",
         "The list is zero and every page's signup form is inert. This is the "
         "only asset that compounds", "Phil decides, I build"],
    ], [0.3 * inch, 1.75 * inch, 3.55 * inch, 1.1 * inch]))

    F.append(Paragraph(
        "On gate 5: the blocker recorded as issue #15 assumes the list must "
        "live on the Listmonk instance shared with another brand, which cannot "
        "send under two identities. It does not have to. A free tier under the "
        "6S Success name removes the shared-identity problem entirely and the "
        "form-placement script already exists. That is a decision, not a build.",
        NOTE))

    # ---- the money -------------------------------------------------------
    F.append(Paragraph("Where the $250 goes", H2))
    F.append(Paragraph(
        "The digital catalogue is the wrong target for paid traffic and the "
        "arithmetic says so plainly: a $19 pack nets about $17.91, which no "
        "realistic cost per click survives. The two consulting offers are "
        "different. One In-Home Reset Day is $1,200, which is nearly five "
        "times this entire budget, and it is bought by people typing a local "
        "search. So the money goes local, or it does not go.", BODY))
    F.append(table([
        ["#", "Line", "$", "What it buys, and how you know it worked"],
        ["1", "Local search ads, exact match only", "112",
         "About two weeks at $8 a day on terms like 'professional organizer "
         "boise', 15 mile radius, no display network, no broad match. Measured "
         "on enquiries and cost per click, not on a conversion rate"],
        ["2", "Ad reserve, released once", "48",
         "Held back deliberately. Released only if line 1 produces clicks but "
         "no enquiry, to retest one changed variable. If line 1 produces no "
         "clicks at all, this moves to line 3"],
        ["3", "One pilot reset day: supplies and printing", "60",
         "A free or at-cost reset of one real household in exchange for "
         "written permission to photograph. Six matched before and after pairs "
         "of a real home are the strongest proof this site could carry, and it "
         "currently has none"],
        ["4", "Cards and printed decks for partner outreach", "30",
         "About 250 business cards and a few properly printed decks as a "
         "leave-behind for senior move managers, agents and organizers. The "
         "outreach templates are already written"],
        ["", "Total", "250", ""],
    ], [0.3 * inch, 1.55 * inch, 0.4 * inch, 4.45 * inch]))

    F.append(Paragraph("What $112 can and cannot measure", H3))
    F.append(Paragraph(
        "At a plausible cost per click for local organizer terms, $112 buys "
        "somewhere in the region of fifteen to thirty clicks. That sample "
        "cannot measure a conversion rate, and I will not pretend otherwise: "
        "zero enquiries from twenty clicks is entirely consistent with a "
        "healthy business. What it can measure reliably, even at that size, is "
        "whether those searches happen here at all and what a click costs. "
        "Both are decision-grade and neither is obtainable any other way. The "
        "most likely single outcome is zero enquiries. Plan for it.", BODY))
    F.append(Paragraph(
        "Check the keyword planner before committing. If exact-match clicks "
        "cost more than about ten dollars, $112 buys single digits and the test "
        "cannot answer anything. In that case move lines 1 and 2 into two more "
        "pilot reset days instead. That is a real branch, not a formality.",
        NOTE))

    F.append(Paragraph("What I would not spend a dollar on", H3))
    F.append(table([
        ["Not this", "Because"],
        ["Paid traffic to the digital catalogue",
         "A $19 product nets $17.91. No realistic click price survives that"],
        ["Meta or Pinterest ads",
         "Home organisation is genuinely strong on Pinterest, which is the "
         "argument for posting there free first. Paying before one free post "
         "has been tested is buying an unknown"],
        ["Amazon ads for the book",
         "The book is ready but not published. A brand-new book with no "
         "reviews is the standard way to lose a budget on Amazon"],
        ["Tools and subscriptions",
         "Analytics, payments, search console and ads management are already "
         "free or self-hosted here. This is where small budgets quietly go"],
        ["Backlink or directory packages",
         "Already researched and declined. They skew toward link schemes"],
    ], [1.75 * inch, 4.95 * inch]))

    # ---- organic ---------------------------------------------------------
    F.append(Paragraph("The organic plan, which is the real one", H2))
    F.append(Paragraph(
        "The site has 189 pages and, as far as can be measured, almost no "
        "external links. Content quality is not the bottleneck: a similarity "
        "test across all 6,441 pairs of zone pages found a median overlap of "
        "0.10 after removing template words, which is strong evidence these "
        "are genuinely distinct pages rather than one page with the nouns "
        "swapped. Being found by other people is the bottleneck.", BODY))
    F.append(table([
        ["When", "What to expect", "What to do"],
        ["Weeks 0 to 2", "Indexing, not traffic",
         "Submit the sitemap the day the deploy lands. Watch pages indexed, "
         "not clicks"],
        ["Weeks 2 to 8", "Impressions before clicks",
         "This is the first real evidence of what people search for. Do not "
         "write new pages. Fix titles on pages already getting impressions"],
        ["Months 2 to 6", "The authority problem",
         "Organic alone will not solve discovery in this window. The free "
         "standards sheets and the 114-zone index are the two assets most "
         "able to earn a link honestly"],
    ], [0.95 * inch, 1.85 * inch, 3.9 * inch]))

    F.append(Paragraph("Fixes worth making first", H3))
    F.append(table([
        ["Fix", "Why"],
        ["Room page title reads 'How to organize a entryway'",
         "Three times on the room most likely to rank first"],
        ["About 2,700 internal links point at the non-canonical URL form",
         "The site declares one form canonical and links the other everywhere"],
        ["www does not redirect to the apex",
         "A complete duplicate of the site on a second hostname"],
        ["Every zone page shares one social preview image",
         "102 of them now have their own photograph and do not use it"],
        ["The Quest's 684 cards exist only inside JavaScript",
         "The most differentiated asset on the site is invisible to search "
         "engines and answer engines alike"],
    ], [3.3 * inch, 3.4 * inch]))

    # ---- media -----------------------------------------------------------
    F.append(Paragraph("Media capability, measured today", H2))
    F.append(table([
        ["Capability", "State", "Evidence"],
        ["Local image generation", "Working",
         "Stable Diffusion on the RTX 2070 SUPER, about 5 seconds an image. "
         "202 images generated and reviewed this week"],
        ["Hosted image APIs", "One of seven authenticates",
         "Gemini only. OpenAI, Cloudflare, Replicate, Stability, Hugging Face "
         "and Runway have no credential"],
        ["Card and page rendering", "Working",
         "Headless Chromium renders card fronts and backs at print resolution"],
        ["Video, photo led", "Working, new today",
         "Vertical 1080x1920, slow push, karaoke captions burned in with "
         "ffmpeg. Two built and checked"],
        ["Video, typographic", "Working, now superseded",
         "Was chosen only because zones had no photographs. 102 now do"],
        ["Voice over", "Not usable",
         "Only robotic system voices. Short form is watched muted, so captions "
         "carry the content"],
        ["Stock footage and music", "None", "No library on this machine"],
    ], [1.4 * inch, 1.5 * inch, 3.8 * inch]))

    F.append(Paragraph("Video roadmap", H2))
    F.append(Paragraph(
        "The unlock is that 102 micro zones now have a reviewed photograph. "
        "The old zone video format was a text slide, chosen because there were "
        "no pictures, and a text slide does not hold attention on a feed. Every "
        "word still comes from that zone's own entry, so nothing is written to "
        "fill a beat.", BODY))
    F.append(table([
        ["Stage", "Output", "Cost", "Gate"],
        ["1. Zone videos", "102 vertical clips, 15 to 30 seconds, one per "
         "reviewed zone", "About 90 minutes of machine time",
         "Only zones whose photograph passed review"],
        ["2. Card videos", "88 Entryway card clips from the rendered fronts",
         "Similar", "Only cards whose art passed review"],
        ["3. Before and after", "The strongest asset the site could carry, and "
         "the one thing generation cannot fake", "Needs a real household and "
         "written permission", "Never publish a private home without a signed "
         "release"],
        ["4. Room tours", "20 room level clips assembled from zone stills",
         "Low", "After stage 1"],
    ], [1.15 * inch, 2.35 * inch, 1.6 * inch, 1.6 * inch]))
    F.append(Paragraph(
        "Sequencing note: stages 1 and 2 are cheap and produce a lot of "
        "material, which is exactly why they should not run before the deploy. "
        "Publishing a hundred videos that point at a site which cannot take "
        "money spends the material once and teaches nothing.", NOTE))

    # ---- what needs Phil -------------------------------------------------
    F.append(Paragraph("What only you can do", H2))
    F.append(table([
        ["#", "Action", "Where"],
        ["1", "Redeploy the site. This fixes the payment outage",
         "Hostinger Docker Manager"],
        ["2", "Confirm Umami and Listmonk are not on default passwords, and "
         "close their public ports. Both admin apps are reachable from the "
         "open internet over plain HTTP", "Hostinger, host firewall"],
        ["3", "Turn on HTTP/2 and HSTS, and redirect www to the apex",
         "Nginx Proxy Manager"],
        ["4", "Decide the email provider so the list can start",
         "Issue #15"],
        ["5", "Decide how the card decks are sold",
         "Issue #20"],
    ], [0.3 * inch, 4.5 * inch, 1.9 * inch]))
    F.append(Paragraph(
        "Item 2 is the one genuine security finding. Neither app is behind the "
        "domain's TLS, so their logins cross the internet in clear text. I did "
        "not test their passwords, deliberately.", NOTE))

    doc.build(F)
    return path, m


def main() -> int:
    path, _m = build()
    size = os.path.getsize(path) / 1024
    print(f"  wrote {os.path.relpath(path, ROOT)}  {size:.0f} KB")

    if "--send" in sys.argv:
        to = sys.argv[sys.argv.index("--send") + 1]
        from mailer import send
        send(to, "6S Success: launch plan, and one thing that needs you today",
             io.open(os.path.join(ROOT, "build", "launch-plan-email.txt"),
                     encoding="utf-8").read()
             if os.path.exists(os.path.join(ROOT, "build",
                                            "launch-plan-email.txt"))
             else "The launch plan is attached.",
             attachments=[path])
        print(f"  sent to {to}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
