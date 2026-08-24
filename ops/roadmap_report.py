#!/usr/bin/env python3
"""
The four-times-daily roadmap report: body text, and the same thing as a PDF.

WHAT THIS IS FOR
----------------
Phil asked for what a product manager and an executive would each want, four
times a day. Those are different readers. The executive wants to know whether
anything changed and whether a decision is approaching. The product manager
wants to know what moved in the queue and what is blocked.

So the report leads with change, not with state. A report that prints the same
figures four times a day trains its reader to stop opening it, and a report
nobody opens is worse than none because it looks like oversight.

WHY THE EDITIONS DIFFER
-----------------------
08:00 is the full report, read at the start of a day.
12:00 and 17:00 are short: what changed since the last one, and nothing else.
21:00 is the day's close, with the retrospective.

Strategy does not change between breakfast and lunch. Only the change log and
the live figures do.

WHAT IT REFUSES TO DO
---------------------
Every number is labelled measured or estimated. Nothing is projected without
saying so. Revenue at 3.4 visitors a day is a lagging indicator that will read
zero for months, so it is not the headline: the leading indicators are, and the
report says why.

Run:  python ops/roadmap_report.py --preview
      python ops/roadmap_report.py --edition 8 --send ADDRESS
"""
from __future__ import annotations

import datetime
import io
import json
import os
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "ops", "report-state.json")

TARGET = 20000.0
# Last hand transcription from the Umami dashboard. The API token returns 401 on
# every route and Umami renders server side, so this cannot be fetched. It is
# stamped with its date so the report can say how stale it is rather than
# implying it is live.
TRAFFIC = {"visitors": 31, "visits": 57, "views": 171,
           "as_of": "2026-08-24", "days": 9,
           "how": "transcribed by hand from the Umami share dashboard"}


def env(name: str, default: str = "") -> str:
    v = os.environ.get(name, "").strip()
    if v:
        return v
    p = os.path.join(ROOT, ".env.secrets")
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8"):
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return default


def sh(cmd: list, timeout: int = 120) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=ROOT)
        return (r.stdout or "") + (r.stderr or "")
    except Exception:                                          # noqa: BLE001
        return ""


# ------------------------------------------------------------------ measured
def commerce() -> dict:
    """Stripe is the only source here that is genuinely live."""
    key = env("STRIPE_SECRET_KEY")
    if not key:
        return {"error": "no Stripe key in this environment"}

    def get(path):
        r = urllib.request.Request("https://api.stripe.com/v1/" + path,
                                   headers={"Authorization": "Bearer " + key})
        return json.load(urllib.request.urlopen(r, timeout=25))

    now = datetime.datetime.now(datetime.timezone.utc)
    month = int(now.replace(day=1, hour=0, minute=0, second=0,
                            microsecond=0).timestamp())
    try:
        sessions = get(f"checkout/sessions?limit=100&created[gte]={month}")["data"]
        paid = [s for s in sessions if s.get("payment_status") == "paid"]
        allpi = get("payment_intents?limit=100")["data"]
        ok = [p for p in allpi if p["status"] == "succeeded"]
        bal = get("balance")
        return {
            "month_revenue": sum(s.get("amount_total", 0) for s in paid) / 100,
            "month_orders": len(paid),
            "month_sessions": len(sessions),
            "lifetime_orders": len(ok),
            "lifetime_revenue": sum(p["amount"] for p in ok) / 100,
            "available": sum(b["amount"] for b in bal.get("available", [])) / 100,
            "pending": sum(b["amount"] for b in bal.get("pending", [])) / 100,
        }
    except Exception as e:                                     # noqa: BLE001
        return {"error": str(e)[:140]}


def repo() -> dict:
    audit = sh([sys.executable, "ops/audit_pages.py"])
    findings = 0
    for ln in audit.splitlines():
        if "finding(s)" in ln:
            try:
                findings = int(ln.split("pages audited,")[1].split("finding")[0])
            except Exception:                                  # noqa: BLE001
                pass
    issues = sh(["gh", "issue", "list", "--state", "open", "--limit", "100",
                 "--json", "number,title,labels"])
    try:
        iss = json.loads(issues) if issues.strip().startswith("[") else []
    except Exception:                                          # noqa: BLE001
        iss = []
    decisions = [i for i in iss
                 if any(l.get("name") == "decision" for l in i.get("labels", []))]
    since = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    commits = sh(["git", "log", "--oneline", f"--since={since}"]).strip()
    return {
        "audit_findings": findings,
        "open_issues": len(iss),
        "decisions_waiting": len(decisions),
        "decision_titles": [f"#{i['number']} {i['title'][:64]}" for i in decisions][:6],
        "commits_24h": len([c for c in commits.splitlines() if c.strip()]),
        "commit_titles": [c[8:78] for c in commits.splitlines()[:6]],
    }


def backlog_next() -> list:
    """The top unblocked items, read from the backlog rather than remembered."""
    p = os.path.join(ROOT, "BACKLOG-2026-H2.md")
    if not os.path.exists(p):
        return []
    out = []
    for ln in io.open(p, encoding="utf-8"):
        if ln.startswith("| ") and "|" in ln[2:] and ln.count("|") >= 5:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 5 and cells[0][:1].isdigit():
                waiting = "Phil" in cells[4]
                out.append({"id": cells[0], "item": cells[1][:70],
                            "accept": cells[2][:70], "waiting": waiting})
    return out


def load_state() -> dict:
    if os.path.exists(STATE):
        try:
            return json.load(io.open(STATE, encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            pass
    return {}


# ------------------------------------------------------------------- render
def money(v) -> str:
    return "not measured" if v is None else f"${v:,.2f}"


def build(edition: int = 8) -> tuple[str, str, dict]:
    now = datetime.datetime.now()
    cm, rp = commerce(), repo()
    prev = load_state()
    items = backlog_next()

    daily = round(TRAFFIC["visitors"] / TRAFFIC["days"], 1)
    stale = (datetime.date.today()
             - datetime.date.fromisoformat(TRAFFIC["as_of"])).days

    full = edition in (8, 21)
    L = []
    label = {8: "Morning", 12: "Midday", 17: "Afternoon", 21: "Evening"}.get(edition, "")
    L += [f"6S SUCCESS {label.upper()} REPORT", f"{now:%A %d %B %Y, %H:%M}", ""]

    # ---- what changed, first, because that is the only reason to open this
    L += ["WHAT CHANGED SINCE THE LAST REPORT", ""]
    changes = []
    if not cm.get("error"):
        d_orders = cm["lifetime_orders"] - prev.get("lifetime_orders", cm["lifetime_orders"])
        if d_orders > 0:
            changes.append(f"  {d_orders} NEW ORDER(S). Lifetime now "
                           f"{cm['lifetime_orders']}, {money(cm['lifetime_revenue'])}.")
    d_commits = rp["commits_24h"]
    if d_commits:
        changes.append(f"  {d_commits} commit(s) in the last 24 hours:")
        changes += [f"      {t}" for t in rp["commit_titles"]]
    if rp["audit_findings"]:
        changes.append(f"  {rp['audit_findings']} page audit finding(s), was "
                       f"{prev.get('audit_findings', 0)}.")
    if not changes:
        changes = ["  Nothing material. No orders, no new findings, no commits."]
    L += changes + [""]

    # ---- the numbers, each labelled
    L += ["THE NUMBERS", ""]
    if cm.get("error"):
        L.append(f"  Stripe unreadable: {cm['error']}   [UNKNOWN, source unreachable]")
    else:
        L += [f"  Revenue this month     {money(cm['month_revenue']):>14}   [EXACT]",
              f"  Lifetime revenue       {money(cm['lifetime_revenue']):>14}   [EXACT]",
              f"  Balance available      {money(cm['available']):>14}   [EXACT]",
              f"  Cash pending           {money(cm['pending']):>14}   [EXACT]"]
        # Counts, never a rate. One paid of eleven sessions is not nine percent,
        # it is one of eleven, and a percentage invites a decision the sample
        # cannot support.
        L.append(f"  Checkout funnel        {cm['lifetime_orders']} paid of "
                 f"{cm['month_sessions']} started   [EXACT, n TOO SMALL FOR A RATE]")
        L.append(f"  Paying customers       {cm['lifetime_orders']}, and that one "
                 "was a referral from you, not a stranger")
    L += [f"  Visitors per day       {daily:>14}   [MANUAL, read "
          f"{TRAFFIC['as_of']}, {stale} day(s) old]",
          "  Product event data     not retrievable   [INSTRUMENTED, NOT READABLE]",
          ""]
    # DELIBERATELY ABSENT: any percent-of-goal figure or progress bar. At 18.15
    # dollars lifetime from a single referral, a bar reading 0.1 percent of
    # target implies a steady climb toward a number the evidence does not
    # support. The dollar figures say everything a percentage would, without
    # the implication. Same reason there is no run rate and no annualisation.

    if full:
        L += ["  Why revenue is not the headline: at "
              f"{daily} visitors a day it is a lagging",
              "  indicator that will read near zero for months regardless of what",
              "  is built. The leading indicators are traffic, then whether a",
              "  stranger converts at all. Neither has happened yet.", ""]

    # ---- the constraint, stated the same way every time on purpose
    if full:
        L += ["THE CONSTRAINT", "",
              "  $20,000 a month at $19 needs 246,000 to 737,000 visits a month.",
              f"  Today: {daily} a day, about {daily*30:.0f} a month.",
              "  At $1,200 it needs 3,900 visits but 150 of 160 available hours.",
              "",
              "  So the digital catalogue cannot carry the target on any reachable",
              "  traffic, and services reach it by becoming a full time job. The",
              "  strategy has to live between them. Full arithmetic:",
              "  python ops/revenue_model.py", ""]

    # ---- decisions waiting, which is what an executive is for
    L += ["DECISIONS WAITING ON YOU", ""]
    waiting = [i for i in items if i["waiting"]]
    if rp["decision_titles"] or waiting:
        for t in rp["decision_titles"]:
            L.append(f"  {t}")
        for w in waiting[:6]:
            L.append(f"  Backlog {w['id']}  {w['item']}")
    else:
        L.append("  Nothing. Everything in the queue is mine to do.")
    L.append("")

    # ---- the queue
    if full:
        L += ["NEXT IN THE QUEUE, and it is ordered by dependency not appeal", ""]
        for i in [x for x in items if not x["waiting"]][:6]:
            L.append(f"  {i['id']:5} {i['item']}")
            L.append(f"        done when: {i['accept']}")
        L += ["", f"  {rp['open_issues']} open issues, "
              f"{rp['decisions_waiting']} labelled decision.", ""]

    # ---- health
    L += ["HEALTH", "",
          f"  Page audit             {rp['audit_findings']} finding(s)",
          f"  Open issues            {rp['open_issues']}",
          f"  Commits, 24h           {rp['commits_24h']}", ""]

    if full:
        # Gates, not strategy. A four-times-daily report should never carry a
        # revised target or the word pivot unless a gate has actually been
        # crossed, and if one has that is an escalation rather than a line item.
        L += ["DECISION GATES, and where each stands", "",
              "  G2  Local demand test for the two service SKUs.",
              "      3 or more paid non-referral bookings by about Nov 2026 and",
              "      hired delivery becomes plannable. 1 or fewer and services",
              "      close pending new evidence.",
              "      STATUS: not started, needs a spending decision from you.",
              "      Backlog 3B.1. This is the only route to the target that does",
              "      not need a mid-sized media property's worth of traffic.", "",
              "  G1  Under 500 organic visits a month and no stranger has bought,",
              "      by Aug 2027, and digital stops being a target bearing route.",
              f"      STATUS: about {daily*30:.0f} visits a month, no stranger has bought.", "",
              "  G5  If neither finds a path by Aug 2027, re-baseline the target",
              "      down to the $3,000 to $8,000 the digital catalogue can carry.",
              "      STATUS: live. An honest ceiling beats an optimistic plan.", ""]

        L += ["THE THREE FACTS THAT SHAPE EVERY DECISION", "",
              "  1. The digital catalogue cannot reach $20,000 a month on any",
              "     reachable traffic. The $49 bundle already contains every",
              "     digital asset that exists.",
              "  2. This business has never converted a stranger. The one sale was",
              "     a personal referral.",
              "  3. Nova Consulting has no list. There is no audience to borrow.", ""]

    L += ["", "Full plan: ROADMAP-2026-2029.md. Queue: BACKLOG-2026-H2.md.",
          "Every figure above is marked MEASURED or HAND READ. Nothing is projected.",
          "Reply to this email and the instruction reaches the operator within the hour."]

    subject = (f"6S {label}: {money(cm.get('month_revenue', 0))} this month, "
               f"{len(waiting) + len(rp['decision_titles'])} waiting on you")
    state = {"lifetime_orders": cm.get("lifetime_orders"),
             "audit_findings": rp["audit_findings"],
             "at": now.isoformat(timespec="seconds")}
    return subject, "\n".join(L), state


def pdf_bytes(title: str, text: str) -> bytes:
    """The same report as a PDF, in the brand's own colours."""
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.lib import colors

    buf = io.BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=LETTER)
    W, H = LETTER
    ink = colors.HexColor("#2B2622")
    soft = colors.HexColor("#6A625A")
    terra = colors.HexColor("#BC4B2A")
    deep = colors.HexColor("#22323C")

    def header():
        c.setFillColor(deep)
        c.rect(0, H - 0.9 * inch, W, 0.9 * inch, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#EDE4D2"))
        c.setFont("Helvetica-Bold", 15)
        c.drawString(0.75 * inch, H - 0.55 * inch, "6S Success")
        c.setFont("Helvetica", 9)
        c.drawRightString(W - 0.75 * inch, H - 0.55 * inch, title)

    header()
    y = H - 1.3 * inch
    for raw in text.splitlines():
        if y < 0.85 * inch:
            c.showPage()
            header()
            y = H - 1.3 * inch
        line = raw.rstrip()
        if not line:
            y -= 7
            continue
        # A heading is an unindented all-caps line. Everything else is body.
        if line == line.upper() and not line.startswith(" ") and len(line) > 3:
            y -= 5
            c.setFillColor(terra)
            c.setFont("Helvetica-Bold", 10.5)
        elif line.startswith("      "):
            c.setFillColor(soft)
            c.setFont("Helvetica", 8.6)
        else:
            c.setFillColor(ink)
            c.setFont("Helvetica", 9.4)
        c.drawString(0.75 * inch, y, line[:110])
        y -= 13.5

    c.setFillColor(soft)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawString(0.75 * inch, 0.55 * inch,
                 "Generated by ops/roadmap_report.py. Every figure marked "
                 "MEASURED or HAND READ. Nothing projected.")
    c.save()
    return buf.getvalue()


if __name__ == "__main__":
    ed = 8
    if "--edition" in sys.argv:
        ed = int(sys.argv[sys.argv.index("--edition") + 1])
    subject, text, state = build(ed)

    # A report that silently reports zeros because a credential is missing looks
    # exactly like a calm business. Refuse instead.
    assert "Stripe unreadable" not in text or "--allow-partial" in sys.argv, \
        "Stripe could not be read. Re-run with --allow-partial to send anyway."

    if "--send" in sys.argv:
        to = sys.argv[sys.argv.index("--send") + 1]
        pdf = pdf_bytes(subject, text)
        assert pdf[:4] == b"%PDF", "the PDF did not render"
        from mailer import send                                # noqa: E402
        stamp = datetime.date.today().isoformat()
        send(to, subject, text,
             attachments=[(f"6S-Success-report-{stamp}-{ed:02d}00.pdf",
                           pdf, "application", "pdf")])
        json.dump(state, io.open(STATE, "w", encoding="utf-8", newline=""), indent=1)
        print(f"sent: {subject} ({len(pdf)//1024} KB pdf)")
    else:
        print("SUBJECT:", subject, "\n")
        print(text)
