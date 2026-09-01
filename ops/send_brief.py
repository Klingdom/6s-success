#!/usr/bin/env python3
"""
Email the command deck as the morning brief.

Phil debriefs each morning. Until now the deck was a link he had to go and open.
This delivers it instead, to the mailbox he already reads, so the five minute
read starts in his inbox.

Everything here comes from ops/state.json, which ops/dashboard.py writes from
measured state. Nothing is typed and nothing is inferred. If dashboard.py has
not run, this refuses rather than sending a stale picture.

Usage:
    python ops/send_brief.py --preview          write the html to a file, send nothing
    python ops/send_brief.py --send ADDRESS     send it
"""
import datetime
import html as H
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mailer import send, load                      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "ops", "state.json")
DECK_URL = "https://claude.ai/code/artifact/24137873-e944-49a1-85bf-b99979672d95"

TONE = {"RED": "#CB4B36", "YELLOW": "#B07A18", "GREEN": "#4E7A57"}


def state():
    if not os.path.exists(STATE):
        raise SystemExit("ops/state.json missing. Run python ops/dashboard.py first.")
    with open(STATE, encoding="utf-8") as fh:
        s = json.load(fh)
    # A brief built from yesterday's measurements is worse than no brief, because
    # it looks current. Refuse rather than mislead.
    stamp = datetime.datetime.strptime(s["generated"], "%Y-%m-%d %H:%M")
    age = (datetime.datetime.now() - stamp).total_seconds() / 3600
    if age > 12:
        raise SystemExit(f"ops/state.json is {age:.0f} hours old. "
                         "Run python ops/dashboard.py first.")
    return s


def build(s):
    """Return (subject, text, html). Plain text is written first and on purpose:
    it is what a watch and a locked phone screen show."""
    money = "can take payment" if s["can_take_payment"] else "cannot take payment"
    subject = (f"6S Success: {s['overall']}, {s['revenue_text']}, "
               f"{s['needs_phil']} need you")

    decisions = [i for i in s.get("issues", [])
                 if any(l["name"] == "decision" for l in i.get("labels", []))]

    lines = [
        f"{s['overall']}. {s['overall_why']}",
        "",
        f"Revenue this month  {s['revenue_text']}",
        f"Paying customers    {s['customers_text']}",
        f"Email list          {s['email_list']}",
        f"The site            {money}",
        "",
        "THE ONE CONSTRAINT",
        s["constraint"],
        "",
    ]
    if s["issues_available"]:
        lines.append(f"NEEDS YOU ({len(decisions)})")
        lines += [f"  #{i['number']}  {i['title']}" for i in decisions] or ["  nothing"]
    else:
        lines.append("NEEDS YOU: unknown, GitHub was unreachable when this was measured.")
    lines += [
        "",
        "WHERE THE WORK STANDS",
        f"  Book      {s['chapters']}/50 chapters, sellable: "
        f"{'yes' if s['book_sellable'] else 'no'}",
        f"  Zones     {s['rooms']} rooms, {s['zones']} micro zones",
        f"  Commits   {s['commits_7d']} in seven days",
        "",
        f"Full deck: {DECK_URL}",
        f"Measured {s['generated']}. Every figure counted, none typed.",
    ]
    text = "\n".join(lines)

    e = H.escape
    rows = "".join(
        f'<tr><td style="padding:9px 0;border-bottom:1px solid #E2D8C4;'
        f'color:#6A625A;font-size:14px">{e(k)}</td>'
        f'<td style="padding:9px 0;border-bottom:1px solid #E2D8C4;text-align:right;'
        f'font-weight:600;font-size:14px">{e(v)}</td></tr>'
        for k, v in [
            ("Revenue this month", s["revenue_text"]),
            ("Paying customers", s["customers_text"]),
            ("Email list", str(s["email_list"])),
            ("The site", money),
            ("Book sellable", "yes" if s["book_sellable"] else "no"),
            ("Commits, 7 days", str(s["commits_7d"])),
        ])
    if s["issues_available"]:
        needs = "".join(
            f'<li style="margin:0 0 8px"><b style="color:#BC4B2A">#{i["number"]}</b> '
            f'{e(i["title"])}</li>' for i in decisions) or "<li>Nothing today.</li>"
    else:
        needs = ("<li>Unknown. GitHub was unreachable when this was measured, "
                 "which is not the same as nothing.</li>")
    colour = TONE[s["overall"]]

    html = f"""<div style="margin:0;padding:24px;background:#F7F2E9">
<div style="max-width:560px;margin:0 auto;background:#FBF7EF;border:1px solid #E2D8C4;
border-radius:14px;padding:28px;font-family:Georgia,'Times New Roman',serif;color:#2B2622">
  <p style="margin:0 0 4px;font:600 11px/1 Arial,sans-serif;letter-spacing:.16em;
     text-transform:uppercase;color:#6A625A">Morning brief &middot; {e(s['generated'])}</p>
  <p style="margin:0 0 2px;font:700 40px/1 Arial,sans-serif;color:{colour}">{e(s['overall'])}</p>
  <p style="margin:0 0 22px;color:#6A625A;font-size:15px">{e(s['overall_why'])}</p>

  <table style="width:100%;border-collapse:collapse;margin-bottom:22px">{rows}</table>

  <p style="margin:0 0 6px;font:600 11px/1 Arial,sans-serif;letter-spacing:.14em;
     text-transform:uppercase;color:#6A625A">The one constraint</p>
  <p style="margin:0 0 22px;padding:14px 16px;background:#F2EADC;border-left:3px solid #BC4B2A;
     font-size:14.5px;line-height:1.55">{e(s['constraint'])}</p>

  <p style="margin:0 0 6px;font:600 11px/1 Arial,sans-serif;letter-spacing:.14em;
     text-transform:uppercase;color:#6A625A">Needs you</p>
  <ul style="margin:0 0 24px;padding-left:18px;font-size:14.5px;line-height:1.5">{needs}</ul>

  <a href="{DECK_URL}" style="display:inline-block;background:#BC4B2A;color:#fff;
     text-decoration:none;padding:11px 20px;border-radius:999px;
     font:600 14px Arial,sans-serif">Open the full deck</a>

  <p style="margin:22px 0 0;color:#8C8478;font-size:12px;line-height:1.5">
    Generated by ops/dashboard.py and sent by ops/send_brief.py.
    Every figure is counted from the repository, never typed.</p>
</div></div>"""
    return subject, text, html


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    s = state()
    subject, text, html = build(s)
    if mode == "--preview":
        out = os.path.join(ROOT, "ops", "brief-preview.html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(html)
        print("subject:", subject)
        print("-" * 60)
        print(text)
        print("-" * 60)
        print("html written to", os.path.relpath(out, ROOT))
        sys.exit(0)
    if mode == "--send":
        # Default to the owner rather than requiring an address. A
        # caller that forgot one used to be a silent misdelivery.
        import mailer as _m
        addr = sys.argv[2] if len(sys.argv) > 2 else _m.owner()
        print("sent", send(addr, subject, text, html))
        sys.exit(0)
    sys.exit(f"unknown mode {mode}")
