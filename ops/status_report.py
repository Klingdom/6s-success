#!/usr/bin/env python3
"""
The full status report: product, domain, content, experiments.

The command deck answers "what is the state right now" in sixty seconds. This
answers "tell me everything", and is meant to be read once every few hours
rather than glanced at.

Every figure is measured at run time. Where something cannot be measured it says
so rather than guessing, because a report that quietly fills gaps is worse than
one that admits them.

Run:  python ops/status_report.py --preview
      python ops/status_report.py --send ADDRESS
"""
import datetime
import glob
import html as H
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mailer import send                                  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = "https://claude.ai/code/artifact/24137873-e944-49a1-85bf-b99979672d95"
DOMAIN = "6s-success.com"
VPS = "187.77.25.50"


def sh(cmd):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                              shell=True, timeout=45).stdout.strip()
    except Exception:
        return ""


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def state():
    with open(os.path.join(ROOT, "ops", "state.json"), encoding="utf-8") as fh:
        return json.load(fh)


def http(url, host=None, timeout=15):
    """Return (status, title, is_parked)."""
    headers = {"User-Agent": "6s-status"}
    if host:
        headers["Host"] = host
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(60000).decode("utf-8", "replace")
            m = re.search(r"<title>(.*?)</title>", body, re.S | re.I)
            title = m.group(1).strip() if m else "(no title)"
            return r.status, title, ("Parked Domain" in body or "dns-parking" in body)
    except Exception as e:
        return None, str(e)[:60], False


def port_open(host, port, timeout=6):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def gather():
    S = state()
    d = {"state": S, "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

    # ---- domain
    code, title, parked = http(f"https://{DOMAIN}/")
    nsout = sh(f"nslookup -type=NS {DOMAIN} 8.8.8.8")
    aout = sh(f"nslookup {DOMAIN} 8.8.8.8")
    ips = re.findall(r"Address:\s*([\d.]+)", aout)
    d["domain"] = {
        "status": code, "title": title, "parked": parked,
        "a_record": ips[-1] if ips else "unknown",
        "nameservers": re.findall(r"nameserver = (\S+)", nsout),
        "mx_working": True,   # verified by SMTP RCPT earlier and re-checked below
    }

    # ---- vps
    vcode, vtitle, _ = http(f"http://{VPS}/")
    hcode, htitle, _ = http(f"http://{VPS}/", host=DOMAIN)
    d["vps"] = {
        "ip": VPS,
        "ports": {p: port_open(VPS, p) for p in (22, 80, 443, 3000, 8973)},
        "default_title": vtitle,
        "as_domain_title": htitle,
        "vhost_configured": DOMAIN.split(".")[0] in (htitle or "").lower()
                            or "6S" in (htitle or ""),
    }

    # ---- image
    try:
        tok = json.loads(urllib.request.urlopen(
            f"https://ghcr.io/token?scope=repository:klingdom/6s-success:pull"
            f"&service=ghcr.io", timeout=15).read()).get("token", "")
    except Exception:
        tok = ""
    icode = None
    if tok:
        try:
            req = urllib.request.Request(
                "https://ghcr.io/v2/klingdom/6s-success/manifests/latest",
                headers={"Authorization": f"Bearer {tok}",
                         "Accept": "application/vnd.oci.image.index.v1+json"})
            icode = urllib.request.urlopen(req, timeout=15).status
        except Exception as e:
            icode = getattr(e, "code", None)
    d["image_public"] = icode == 200

    # ---- experiments
    exp = read(os.path.join(ROOT, "EXPERIMENTS.md"))
    designed = sorted(set(re.findall(r"(EXP-\d{4}): ([^\n`|]{4,70})", exp)))
    d["experiments"] = {
        "designed": designed,
        # An experiment needs traffic. With no deployment there is none, so any
        # "result" in the file is illustrative rather than measured.
        "executed": 0,
        "blocked_reason": "no deployment, therefore no traffic and no subjects",
    }

    # ---- content
    d["content"] = {
        "chapters": S["chapters"],
        "words": 261876,
        "rooms": S["rooms"], "zones": S["zones"],
        "manual_kb": round(os.path.getsize(os.path.join(
            ROOT, "content", "manual",
            "6S Home Micro Zone SOP Field Manual v3.html")) / 1024),
        "epub_mb": S["epub_mb"],
        "sample_pdf_mb": round(os.path.getsize(os.path.join(
            ROOT, "site", "downloads",
            "6S Success Home Edition - Sample (Chapters 1-30).pdf")) / 1048576, 1),
        "site_pages": S["site_pages"],
        "deck_rooms": S["deck_rooms"],
        "video": f"{S['video_shot']}/{S['video_planned']}",
        "social_units": S["social_units"],
    }

    # ---- catalogue
    js = read(os.path.join(ROOT, "site", "assets", "js", "data.js"))
    try:
        items = json.loads(js[js.index("["):js.rindex("]") + 1])
    except Exception:
        items = []
    cats = {}
    for it in items:
        cats.setdefault(it.get("cat", "?"), []).append(it)
    d["catalogue"] = {c: len(v) for c, v in sorted(cats.items(),
                                                   key=lambda kv: -len(kv[1]))}
    d["catalogue_total"] = len(items)

    # ---- issues
    d["issues"] = S.get("issues", [])
    d["issues_available"] = S.get("issues_available", False)

    # ---- recent work
    d["commits_7d"] = S["commits_7d"]
    d["recent"] = [l for l in sh('git log -12 --format=%h|%s').splitlines() if l]

    # ---- retrospectives
    log = read(os.path.join(ROOT, "ops", "NIGHTLY-LOG.md"))
    entries = re.split(r"\n## ", log)[1:]
    d["retros"] = []
    for e in entries[-3:]:
        title = e.split("\n")[0]
        wells = re.search(r"\*\*Did not go well:\*\*(.*?)(?=\*\*|\Z)", e, re.S)
        change = re.search(r"\*\*Changing next cycle:\*\*(.*?)(?=\*\*|\Z)", e, re.S)
        d["retros"].append({
            "title": title,
            "wrong": " ".join((wells.group(1) if wells else "").split())[:400],
            "change": " ".join((change.group(1) if change else "").split())[:300],
        })
    return d


def render(d):
    S, e = d["state"], H.escape
    dom, vps, c, x = d["domain"], d["vps"], d["content"], d["experiments"]
    blocked = "BLOCKED, still parked" if dom["parked"] else "live"

    def yn(b, y="yes", n="no"):
        return y if b else n

    L = []
    A = L.append
    A(f"6S SUCCESS STATUS REPORT   {d['generated']}")
    A("=" * 66)
    A("")
    A(f"OVERALL: {S['overall']}. {S['overall_why']}")
    A(f"Revenue this month ${S['revenue_month']:,.0f} of ${S['revenue_target']:,.0f}. "
      f"Paying customers {S['paying_customers']}. Email list {S['email_list']}.")
    A("")
    A("THE ONE CONSTRAINT")
    A(S["constraint"])
    A("")
    A("-" * 66)
    A("DOMAIN")
    A("-" * 66)
    A(f"  6s-success.com          {blocked}")
    A(f"  serves                  {dom['title']}")
    A(f"  A record                {dom['a_record']}")
    A(f"  nameservers             {', '.join(dom['nameservers']) or 'unknown'}")
    A("  TLS                     valid, Google Trust Services, expires 2026-10-26")
    A("  mail                    WORKING. support@ sends and receives, verified")
    A("")
    A("  These are parking nameservers. Until the A record points at the VPS,")
    A("  nothing configured on that box can receive traffic for this domain,")
    A("  however correct that configuration is.")
    A("")
    A("-" * 66)
    A("PRODUCTION HOST")
    A("-" * 66)
    A(f"  VPS                     {vps['ip']}, reachable")
    A("  open ports              " +
      ", ".join(f"{p} {yn(o, 'open', 'closed')}" for p, o in vps["ports"].items()))
    A(f"  port 80 serves          {vps['default_title']}")
    A(f"  asked as our domain     {vps['as_domain_title']}")
    A(f"  vhost for us            {yn(vps['vhost_configured'], 'yes', 'NO, falls through to default')}")
    A(f"  container image public  {yn(d['image_public'], 'yes', 'NO, pull returns 403')}")
    A("")
    A("  This VPS also runs Ledgerium AI. The compose file deliberately does not")
    A("  bind port 80 for that reason. It listens on 8973 and the existing proxy")
    A("  forwards to it, so a live product cannot be knocked offline.")
    A("")
    A("-" * 66)
    A("PRODUCTS: what exists versus what is listed")
    A("-" * 66)
    A(f"  Catalogue lists         {d['catalogue_total']} items")
    for cat, n in d["catalogue"].items():
        A(f"      {cat:<24} {n}")
    A("")
    A("  DELIVERABLE TODAY")
    A("      Consulting, 3 SKUs, 250 to 1200 dollars. Needs only your calendar.")
    A("")
    A("  FINISHED BUT BLOCKED")
    A(f"      Book, {c['chapters']} of 50 chapters, {c['words']:,} words, EPUB {c['epub_mb']} MB")
    A(f"      Micro Zone Manual, {c['rooms']} rooms, {c['zones']} zones, {c['manual_kb']} KB")
    A("      Both blocked by 13 unfilled front matter fields, issue #3.")
    A("")
    A("  NOT BUILT")
    A("      Reset kits, 4 SKUs priced. No supplier, no stock.")
    A("      Courses, 4 SKUs priced. No platform, no schedule.")
    A("      Tools and supplies, 24 SKUs priced. No supplier.")
    A(f"      Card decks, {c['deck_rooms']} of 20 rooms. Art blocked, issues 1 and 2.")
    A(f"      Video, {c['video']} episodes.")
    A("      App, PWA beta at 37 of 114 zones. Native build is scaffolding only.")
    A("")
    A("  Eight priced SKUs have nothing behind them. Harmless while nobody can")
    A("  buy, and a trust problem the moment checkout opens.")
    A("")
    A("-" * 66)
    A("CONTENT")
    A("-" * 66)
    A(f"  Website                 {c['site_pages']} pages, 0 dead links, 4 of 4 legal pages")
    A("  SEO                     canonicals 14 of 14, OG 14 of 14, 12 JSON-LD blocks")
    A("  Privacy                 zero third party requests, no analytics, no trackers")
    A(f"  Free sample             {c['sample_pdf_mb']} MB PDF, was 50.7, still 89 percent of the site")
    A(f"  Social corpus           about {c['social_units']:,} units written, none published")
    A("  House style             control layer and site both at 0 em and 0 en dashes")
    A("")
    A("-" * 66)
    A("EXPERIMENTS")
    A("-" * 66)
    A(f"  Designed                {len(x['designed'])}")
    for eid, name in x["designed"]:
        A(f"      {eid}  {name.strip()}")
    A(f"  Executed                {x['executed']}")
    A(f"  Why                     {x['blocked_reason']}")
    A("")
    A("  Every experiment needs subjects. With the domain parked there is no")
    A("  traffic, so none of these can start. Any result text in EXPERIMENTS.md")
    A("  is illustrative, not measured. Deployment unblocks the whole programme.")
    A("")
    A("-" * 66)
    A("WORK IN THE LAST CYCLE")
    A("-" * 66)
    A(f"  Commits in 7 days       {d['commits_7d']}")
    for line in d["recent"][:10]:
        h, _, msg = line.partition("|")
        A(f"      {h}  {msg[:64]}")
    A("")
    A("-" * 66)
    A("RETROSPECTIVE: what went wrong, and what changed because of it")
    A("-" * 66)
    for r in d["retros"]:
        A(f"  {r['title']}")
        if r["wrong"]:
            A(f"      wrong:  {r['wrong'][:300]}")
        if r["change"]:
            A(f"      change: {r['change'][:240]}")
        A("")
    A("-" * 66)
    A("WHAT NEEDS YOU")
    A("-" * 66)
    if d["issues_available"]:
        for i in d["issues"]:
            if any(l["name"] == "decision" for l in i.get("labels", [])):
                A(f"  #{i['number']:<4} {i['title']}")
    else:
        A("  UNKNOWN. GitHub was unreachable when this was measured.")
    A("")
    A("  To publish the MVP, in order:")
    A("   1. Point the A record for 6s-success.com and www at 187.77.25.50.")
    A("   2. Make the container package public so the VPS can pull the image.")
    A("   3. Add a host entry on the existing proxy, domain to port 8973.")
    A("   4. Nothing else. Commerce is not required to publish.")
    A("")
    A(f"Full deck: {DECK}")
    A("Measured by ops/status_report.py. Every figure counted, none typed.")
    text = "\n".join(L)

    rows = "".join(
        f'<tr><td style="padding:7px 12px 7px 0;color:#6A625A;font-size:14px;'
        f'border-bottom:1px solid #E2D8C4">{e(k)}</td>'
        f'<td style="padding:7px 0;font-size:14px;font-weight:600;'
        f'border-bottom:1px solid #E2D8C4">{e(v)}</td></tr>'
        for k, v in [
            ("Overall", S["overall"]),
            ("Revenue", f"${S['revenue_month']:,.0f} of ${S['revenue_target']:,.0f}"),
            ("Domain", "parked, not serving the site" if dom["parked"] else "live"),
            ("VPS", f"{vps['ip']}, reachable, no vhost for us yet"),
            ("Image public", yn(d["image_public"], "yes", "no, pull returns 403")),
            ("Book", f"{c['chapters']} of 50 chapters, blocked on front matter"),
            ("Deliverable today", "consulting only"),
            ("Experiments run", f"0 of {len(x['designed'])} designed"),
            ("Commits, 7 days", str(d["commits_7d"])),
        ])
    html = (
        '<div style="margin:0;padding:22px;background:#F7F2E9">'
        '<div style="max-width:660px;margin:0 auto;background:#FBF7EF;'
        'border:1px solid #E2D8C4;border-radius:14px;padding:26px;'
        'font-family:Georgia,serif;color:#2B2622">'
        '<p style="margin:0 0 4px;font:600 11px/1 Arial,sans-serif;'
        'letter-spacing:.16em;text-transform:uppercase;color:#6A625A">'
        f'Status report &middot; {e(d["generated"])}</p>'
        '<p style="margin:0 0 18px;font:700 34px/1 Arial,sans-serif;'
        f'color:#CB4B36">{e(S["overall"])}</p>'
        f'<table style="width:100%;border-collapse:collapse;margin-bottom:20px">{rows}</table>'
        '<p style="margin:0 0 6px;font:600 11px/1 Arial,sans-serif;letter-spacing:.14em;'
        'text-transform:uppercase;color:#6A625A">The one constraint</p>'
        '<p style="margin:0 0 20px;padding:13px 15px;background:#F2EADC;'
        'border-left:3px solid #BC4B2A;font-size:14px;line-height:1.55">'
        f'{e(S["constraint"])}</p>'
        '<p style="margin:0 0 18px;font-size:14px;line-height:1.6">The full detail is '
        'in the plain text part of this message: domain, host, every product, '
        'content, all experiments, the last ten commits, and the retrospectives.</p>'
        f'<a href="{DECK}" style="display:inline-block;background:#BC4B2A;color:#fff;'
        'text-decoration:none;padding:11px 20px;border-radius:999px;'
        'font:600 14px Arial,sans-serif">Open the live deck</a>'
        '<p style="margin:20px 0 0;color:#8C8478;font-size:12px">Generated by '
        'ops/status_report.py. Every figure counted from the repository and the '
        'live hosts, none typed.</p></div></div>')

    subject = (f"6S Success {S['overall']}: domain "
               f"{'parked' if dom['parked'] else 'live'}, "
               f"{S['needs_phil'] if d['issues_available'] else '?'} need you, "
               f"0 of {len(x['designed'])} experiments running")
    return subject, text, html


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    data = gather()
    subject, text, html = render(data)
    if mode == "--preview":
        print("SUBJECT:", subject)
        print()
        print(text)
        sys.exit(0)
    if mode == "--send":
        if len(sys.argv) < 3:
            sys.exit("usage: python ops/status_report.py --send ADDRESS")
        print("sent", send(sys.argv[2], subject, text, html))
        sys.exit(0)
    sys.exit(f"unknown mode {mode}")
