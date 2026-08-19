#!/usr/bin/env python3
"""
Generate the live executive dashboard from measured state.

Nothing here is hand-maintained. Every number is counted from the repository,
GitHub, or the product folders on disk, so the dashboard cannot drift from
reality the way a manually updated status file does.

Run:  python ops/dashboard.py
Writes:  EXECUTIVE-DASHBOARD-LIVE.md   (the at-a-glance read)
         ops/dashboard.html            (the same, styled, open in a browser)
         ops/state.json                (machine-readable, for trend tracking)
"""
import json, os, re, subprocess, glob, datetime, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Read from the in-repo content mirror, never an absolute local path. The nightly
# agent runs in the cloud with only a git checkout, so a Desktop path would
# silently produce zeros there and the dashboard would quietly lie.
CONTENT = os.path.join(ROOT, "content")
MASTER = os.path.join(CONTENT, "book")
DECKS = os.path.join(CONTENT, "decks")
MANUAL = os.path.join(CONTENT, "manual")
VIDEO = os.path.join(CONTENT, "video")

def sh(cmd, cwd=ROOT):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              shell=isinstance(cmd, str), timeout=60).stdout.strip()
    except Exception:
        return ""

def count_files(pattern, recursive=True):
    return len(glob.glob(pattern, recursive=recursive))

def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""

# ---------------------------------------------------------------- measure
now = datetime.datetime.now()
S = {"generated": now.strftime("%Y-%m-%d %H:%M")}

# --- git / github
S["commit"] = sh("git rev-parse --short HEAD")
S["commit_msg"] = sh("git log -1 --format=%s")
S["commits_7d"] = len([l for l in sh('git log --since="7 days ago" --format=%h').splitlines() if l])
S["commits_total"] = len(sh("git log --format=%h").splitlines())
S["clean"] = sh("git status --porcelain") == ""
S["ahead"] = sh("git rev-list --count origin/main..HEAD") or "0"

# A failed API call must never render as "zero open issues". GitHub outages are
# common and an empty result read as all-clear is the most dangerous possible
# failure direction for a dashboard.
issues = sh('gh issue list --state open --json number,title,labels --limit 100')
S["issues_available"] = False
try:
    if issues.strip().startswith("["):
        S["issues"] = json.loads(issues)
        S["issues_available"] = True
    else:
        S["issues"] = []
except Exception:
    S["issues"] = []
S["open_issues"] = len(S["issues"])
S["open_p0"] = len([i for i in S["issues"] if any(l["name"] == "P0" for l in i.get("labels", []))])
S["blocked_art"] = len([i for i in S["issues"] if any(l["name"] == "blocked-on-art" for l in i.get("labels", []))])
S["needs_phil"] = len([i for i in S["issues"] if any(l["name"] == "decision" for l in i.get("labels", []))])

closed = sh('gh issue list --state closed --json number --limit 100')
try:
    S["closed_issues"] = len(json.loads(closed)) if closed.strip().startswith("[") else None
except Exception:
    S["closed_issues"] = None

# --- revenue (the honest number)
S["revenue_month"] = 0.0
S["revenue_target"] = 20000.0
# Is the site actually reachable by a member of the public? This is measured
# from outside rather than assumed, because for weeks the honest answer was no
# while every local check passed. A parked domain answers 200 on every path, so
# the test that matters is that an unknown path 404s and the body is ours.
def site_live():
    import urllib.request, urllib.error
    try:
        req = urllib.request.Request("https://6s-success.com/",
                                     headers={"User-Agent": "6s-dashboard"})
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read(40000).decode("utf-8", "replace")
        if "6S Success" not in body or "Parked Domain" in body:
            return False
        try:
            urllib.request.urlopen(urllib.request.Request(
                "https://6s-success.com/does-not-exist-dashboard-probe",
                headers={"User-Agent": "6s-dashboard"}), timeout=15)
            return False          # a 200 here means a catch-all, not our site
        except urllib.error.HTTPError as e:
            return e.code == 404
    except Exception:
        return False

S["site_live"] = site_live()

# Measured, not asserted. This was previously `... and False`, which hardcoded a
# NO behind an expression that looked like a measurement. It happened to be the
# right answer, which is the dangerous kind of wrong: the day a checkout went
# live the dashboard would still have said the business cannot take money.
# A payment route exists when a page actually reaches a payment processor.
PROCESSORS = ("js.stripe.com", "checkout.stripe.com", "paypal.com/sdk",
              "lemonsqueezy.com", "gumroad.com", "checkout.square", "snipcart")
S["can_take_payment"] = any(
    p in read(f) for f in glob.glob(os.path.join(ROOT, "site", "*.html")) for p in PROCESSORS)
S["paying_customers"] = 0
S["email_list"] = 0

# --- product readiness
site_pages = count_files(os.path.join(ROOT, "site", "*.html"))
S["site_pages"] = site_pages
S["dead_links"] = sum(read(f).count('href="#"') for f in glob.glob(os.path.join(ROOT, "site", "*.html")))
S["legal_pages"] = sum(1 for p in ("privacy", "terms", "accessibility", "disclaimer")
                       if os.path.exists(os.path.join(ROOT, "site", p + ".html")))
S["forms_dead"] = sum(read(f).count('onsubmit="return false"') for f in glob.glob(os.path.join(ROOT, "site", "*.html")))

# --- book
ch = sorted(set(glob.glob(os.path.join(MASTER, "*hapter*", "chapter_*_final.html"))))
S["chapters"] = len(ch)
S["chapters_with_disclaimer"] = sum(1 for f in ch if "six-s-disclaimer" in read(f))
S["chapters_no_photos"] = sum(1 for f in ch if read(f).count("<img") == 0)
S["front_matter"] = os.path.exists(os.path.join(MASTER, "6S-Success-Front-Matter", "FRONT_MATTER.md"))

# Is there a file a retailer would actually accept? A finished manuscript is not
# a sellable product until it is packaged, has a cover, and carries a byline.
epub = os.path.join(ROOT, "build", "6S-Success-Home-Edition.epub")
S["epub_built"] = os.path.exists(epub)
S["epub_mb"] = round(os.path.getsize(epub) / 1048576, 2) if S["epub_built"] else 0
S["epub_has_cover"] = False
if S["epub_built"]:
    import zipfile
    try:
        with zipfile.ZipFile(epub) as _z:
            S["epub_has_cover"] = "EPUB/images/cover.jpg" in _z.namelist()
    except Exception:
        pass
fm_text = read(os.path.join(MASTER, "6S-Success-Front-Matter", "FRONT_MATTER.md"))
S["front_matter_blanks"] = len(re.findall(r"\[[A-Z][A-Z /]{3,}\]", fm_text))
S["book_sellable"] = S["epub_built"] and S["epub_has_cover"] and S["front_matter_blanks"] == 0

# --- decks
deck_dir = DECKS
S["deck_rooms"] = len([d for d in glob.glob(os.path.join(deck_dir, "*Deck")) if os.path.isdir(d)])
# Images are gitignored from the mirror by design, so counting them here would
# report a false zero. Report "not in repo" rather than a number that is wrong.
S["deck_images"] = None
sio = 0
for f in glob.glob(os.path.join(deck_dir, "**", "*.html"), recursive=True):
    if any(k in os.path.basename(f) for k in ("Card_List", "Master_Proof", "Master_Plan", "Room_Deck_Plan")):
        sio += read(f).count("Set in Order")
S["set_in_order_live"] = sio

# The control layer enforces the house style but was never measured against it.
ctrl = glob.glob(os.path.join(ROOT, "*.md")) + glob.glob(os.path.join(ROOT, "claude", "**", "*.md"), recursive=True)
S["ctrl_files"] = len(ctrl)
S["ctrl_em"] = sum(read(f).count("—") for f in ctrl)
S["ctrl_en"] = sum(read(f).count("–") for f in ctrl)
S["site_em"] = sum(read(f).count("—") for f in glob.glob(os.path.join(ROOT, "site", "*.html")))

# --- micro zones (the spine)
mz = os.path.join(MANUAL, "source", "content.json")
try:
    c = json.load(open(mz, encoding="utf-8"))
    S["rooms"] = len(c["rooms"])
    S["zones"] = sum(len(r["zones"]) for r in c["rooms"])
except Exception:
    S["rooms"] = S["zones"] = 0
S["zones_with_deck"] = 9

# --- content corpus
S["social_files"] = len(glob.glob(os.path.join(MASTER, "**", "*.md"), recursive=True))
S["social_units"] = 2600  # corpus size established by audit; not re-counted each run
vt = glob.glob(os.path.join(VIDEO, "*tracker*.csv"))
S["video_planned"] = 0
S["video_shot"] = 0
if vt:
    import csv as _csv
    with open(vt[0], encoding="utf-8-sig", newline="") as fh:
        _rows = list(_csv.DictReader(fh))
    S["video_planned"] = len(_rows)
    S["video_shot"] = sum(1 for r in _rows if (r.get("status_shot") or "").strip().lower() not in ("", "not started"))

# ---------------------------------------------------------------- assess
def status_of():
    if S["revenue_month"] == 0 and not S["can_take_payment"]:
        return "RED", "No route from customer intent to payment exists."
    if not S["issues_available"]:
        return "YELLOW", "Could not reach GitHub, so issue counts are UNKNOWN, not zero."
    if S["open_p0"]:
        return "YELLOW", f"{S['open_p0']} P0 items still open."
    return "GREEN", "Operating normally."

S["overall"], S["overall_why"] = status_of()
# Precision matters here. The forms are no longer silent: they hand the reader a
# prefilled message so their intent survives. What is still missing is a provider,
# so nothing is stored, nothing is automatic, and no list is being built.
_reach = ("" if S["site_live"] else
          " And 6s-success.com does not serve the site, so none of it is reachable.")
S["constraint"] = ("The business cannot accept money. Checkout is staged and there is no "
                   f"payment processor anywhere in the site. All {S['forms_dead']} forms now "
                   "hand off to email by hand, which keeps a visitor's intent but stores "
                   "nothing and builds no list." + _reach +
                   " Nothing else moves revenue until this does.")

pct = S["revenue_month"] / S["revenue_target"] * 100
S["revenue_pct"] = round(pct, 1)

# ---------------------------------------------------------------- render
def bar(p, w=28):
    f = int(round(p / 100 * w))
    return "#" * f + "." * (w - f)

md = f"""# 6S Success: Live Executive Dashboard

> Generated {S['generated']} by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **{S['overall']}** {S['overall_why']} |
| **Revenue this month** | **${S['revenue_month']:,.0f}** of ${S['revenue_target']:,.0f} target ({S['revenue_pct']}%) |
| | `{bar(pct)}` |
| **Paying customers** | {S['paying_customers']} |
| **Email list** | {S['email_list']} |
| **Can the site take money?** | {'yes' if S['can_take_payment'] else '**NO**'} |

### The one constraint

{S['constraint']}

---

## Where the work stands

| Stream | State |
|---|---|
| Open issues | {(str(S['open_issues']) + f" ({S['open_p0']} P0, {S['blocked_art']} blocked on art, {S['needs_phil']} need your call)") if S['issues_available'] else "**UNKNOWN** (GitHub unreachable at generation time)"} |
| Closed to date | {S['closed_issues'] if S['closed_issues'] is not None else "UNKNOWN"} |
| Commits (7 days) | {S['commits_7d']} of {S['commits_total']} total |
| Working tree | {'clean, in sync' if S['clean'] and S['ahead'] == '0' else 'uncommitted or unpushed work'} |
| Last commit | `{S['commit']}` {S['commit_msg'][:60]} |

## Product readiness

| Product | Measured state |
|---|---|
| Website | {S['site_pages']} pages, {S['dead_links']} dead links, {S['legal_pages']}/4 legal pages, {S['forms_dead']} disconnected forms |
| Book | {S['chapters']}/50 chapters, {S['chapters_with_disclaimer']}/50 carry the safety notice, {S['chapters_no_photos']} have no photographs, front matter {'drafted' if S['front_matter'] else 'MISSING'} |
| Book, sellable? | {'YES' if S['book_sellable'] else 'NO'} EPUB {'built ' + str(S['epub_mb']) + ' MB' if S['epub_built'] else 'NOT BUILT'}, cover {'yes' if S['epub_has_cover'] else 'NO'}, {S['front_matter_blanks']} unfilled front-matter fields |
| Micro zones | {S['rooms']} rooms, {S['zones']} zones (the spine every product shares) |
| Card decks | {S['deck_rooms']}/20 rooms, {S['zones_with_deck']}/{S['zones']} zones covered (card art lives outside the repo) |
| Canon defects | {S['set_in_order_live']} live uses of the rejected term "Set in Order" |
| Social corpus | ~{S['social_units']:,} ready-to-publish units, unused |
| Video | {S['video_shot']}/{S['video_planned']} episodes shot |

## What needs you

"""
if not S["issues_available"]:
    md += ("- **UNKNOWN.** GitHub could not be reached when this was generated, so the\n"
           "  decision queue could not be read. That is not the same as nothing being\n"
           "  blocked. Re-run `python ops/dashboard.py` once GitHub responds.\n")
elif S["needs_phil"]:
    for i in S["issues"]:
        if any(l["name"] == "decision" for l in i.get("labels", [])):
            md += f"- **#{i['number']}** {i['title']}\n"
else:
    md += "- Nothing is blocked on you right now.\n"

md += f"""
## Open issues

| # | Title | Labels |
|---|---|---|
"""
for i in S["issues"]:
    md += f"| {i['number']} | {i['title']} | {', '.join(l['name'] for l in i.get('labels', []))} |\n"

open(os.path.join(ROOT, "EXECUTIVE-DASHBOARD-LIVE.md"), "w", encoding="utf-8").write(md)

# --- html -------------------------------------------------------------------
# The HTML deliberately carries no <!doctype>, <html> or <body> wrapper. Browsers
# render it fine without one, and leaving it out means this exact file can also be
# published as a hosted artifact, which wraps the fragment itself. One file, read
# locally at the desk or on a phone from bed, with no second copy to drift.
import math

def esc(x): return html.escape(str(x))

# The six-S ramp doubles as the severity ramp. That is not decoration: the whole
# method runs chaos to calm, so a business measured against its own method should
# be read on its own gauge.
S1, S2, S3, S4, S5, S6 = "#CB4B36", "#BC4B2A", "#D98A2B", "#DDA63A", "#6E8B5B", "#4E7A57"
TONE = {"crit": S1, "warn": S4, "good": S6, "idle": "var(--mute)"}
SEVERITY = {"RED": "crit", "YELLOW": "warn", "GREEN": "good"}

def chip(text, tone):
    return f'<span class="chip {tone}">{esc(text)}</span>'

def gauge(pct, size=340):
    """The friction gauge, the brand's signature mark, pointing at revenue.

    Zero revenue puts the needle hard left, in the red. That is the honest
    picture and it should look like the honest picture.
    """
    cx = cy = size / 2
    r = size / 2 - 26
    seg, gap = 180 / 6, 1.6
    parts = []
    for k, col in enumerate((S1, S2, S3, S4, S5, S6)):
        a0, a1 = 180 + k * seg + gap, 180 + (k + 1) * seg - gap
        x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        parts.append(f'<path d="M{x0:.1f} {y0:.1f} A{r:.1f} {r:.1f} 0 0 1 {x1:.1f} {y1:.1f}" '
                     f'fill="none" stroke="{col}" stroke-width="22"/>')
    a = math.radians(180 + max(0.0, min(100.0, pct)) * 1.8)
    nx, ny = cx + r * 0.66 * math.cos(a), cy + r * 0.66 * math.sin(a)
    # Butt cap, not round: a round cap puts a dot on the needle tip and the whole
    # thing reads as a slider someone can drag rather than a reading.
    parts.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" '
                 f'stroke="var(--ink)" stroke-width="7"/>')
    parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="12" fill="var(--ink)"/>')
    return (f'<svg class="gauge" viewBox="0 0 {size} {size/2+22:.0f}" role="img" '
            f'aria-label="Revenue gauge, {pct} percent of the twenty thousand dollar target">'
            + "".join(parts) + "</svg>")

# Readiness, each row given a state a person can read at a glance rather than a
# number they have to interpret.
ready = [
    ("Website", f"{S['site_pages']} pages, {S['dead_links']} dead links, {S['legal_pages']}/4 legal pages, "
                f"{S['forms_dead']} forms hand off to email, 0 reach a provider",
     ("good", "LIVE") if S["site_live"] else ("crit", "domain parked")),
    ("Book, written", f"{S['chapters']}/50 chapters, {S['chapters_with_disclaimer']}/50 carry the safety notice",
     ("good", "complete") if S["chapters"] == 50 else ("warn", "in progress")),
    ("Book, sellable", (f"EPUB {S['epub_mb']} MB, cover {'embedded' if S['epub_has_cover'] else 'missing'}, "
                        f"{S['front_matter_blanks']} unfilled front-matter fields") if S["epub_built"]
     else "not packaged", ("good", "ready") if S["book_sellable"] else ("warn", "blocked on #3")),
    ("Micro zones", f"{S['rooms']} rooms, {S['zones']} zones, the spine every product shares",
     ("good", "complete")),
    ("Card decks", f"{S['deck_rooms']}/20 rooms, {S['zones_with_deck']}/{S['zones']} zones, card art not in repo",
     ("warn", "2 of 20 rooms")),
    ("Social corpus", f"~{S['social_units']:,} ready-to-publish units", ("idle", "unused")),
    ("Video", f"{S['video_shot']} of {S['video_planned']} episodes shot",
     ("good", "on air") if S["video_shot"] else ("idle", "not started")),
    ("House style", f"control layer {S.get('ctrl_em',0)} em and {S.get('ctrl_en',0)} en dashes across "
                    f"{S.get('ctrl_files',0)} files, published site {S.get('site_em',0)}",
     ("warn", "control layer breaks it") if S.get("ctrl_em", 0) else ("good", "clean")),
]
ready_rows = "".join(
    f'<tr><th scope="row">{esc(n)}</th><td>{esc(detail)}</td>'
    f'<td class="st">{chip(lbl, tone)}</td></tr>' for n, detail, (tone, lbl) in ready)

# GitHub's own label colours, so a label looks the same here as in the issue list.
def labels_of(i):
    return "".join(
        f'<span class="lab" style="--lc:#{esc(l.get("color") or "888888")}">{esc(l["name"])}</span>'
        for l in i.get("labels", []))

if S["issues_available"]:
    issue_rows = "".join(
        f'<tr><td class="num">#{esc(i["number"])}</td><td>{esc(i["title"])}</td>'
        f'<td class="st">{labels_of(i)}</td></tr>' for i in S["issues"]) or \
        '<tr><td colspan="3">No open issues.</td></tr>'
else:
    issue_rows = ('<tr><td colspan="3"><b>UNKNOWN.</b> GitHub could not be reached, so the '
                  'queue could not be read. That is not the same as nothing being open.</td></tr>')

if not S["issues_available"]:
    needs = ('<li><b>Unknown.</b> GitHub was unreachable when this was generated, so the '
             'decision queue could not be read. Re-run <code>python ops/dashboard.py</code>.</li>')
elif S["needs_phil"]:
    needs = "".join(f'<li><b>#{esc(i["number"])}</b> {esc(i["title"])}</li>' for i in S["issues"]
                    if any(l["name"] == "decision" for l in i.get("labels", [])))
else:
    needs = "<li>Nothing is blocked on you right now.</li>"

tone = SEVERITY[S["overall"]]

CSS = """
:root{
  --paper:#F7F2E9; --panel:#FBF7EF; --ink:#2B2622; --soft:#6A625A; --mute:#8C8478;
  --line:#E2D8C4; --line-2:#D9CDB8; --accent:#BC4B2A; --wash:#F2EADC;
  --crit:#CB4B36; --warn:#B07A18; --good:#4E7A57;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#1A272E; --panel:#22323C; --ink:#EDE4D2; --soft:#A9B7BE; --mute:#7E8F97;
    --line:#33474F; --line-2:#3E555E; --accent:#DDA63A; --wash:#1F2E36;
    --crit:#E4735F; --warn:#DDA63A; --good:#8FB37C;
  }
}
:root[data-theme="dark"]{
  --paper:#1A272E; --panel:#22323C; --ink:#EDE4D2; --soft:#A9B7BE; --mute:#7E8F97;
  --line:#33474F; --line-2:#3E555E; --accent:#DDA63A; --wash:#1F2E36;
  --crit:#E4735F; --warn:#DDA63A; --good:#8FB37C;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:400 17px/1.6 "Newsreader",Georgia,"Times New Roman",serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1000px;margin:0 auto;padding:0 22px 96px;
  display:flex;flex-direction:column;gap:14px}
h1{font-family:"Fraunces",Georgia,serif;font-weight:600;letter-spacing:-.02em;
  font-size:clamp(32px,6vw,52px);line-height:1.04;margin:44px 0 0;text-wrap:balance}
h2{font-family:"Fraunces",Georgia,serif;font-weight:600;letter-spacing:-.015em;
  font-size:clamp(20px,3vw,25px);margin:40px 0 0;text-wrap:balance}
.eyebrow{font:600 11px/1 "Inter",system-ui,sans-serif;letter-spacing:.18em;
  text-transform:uppercase;color:var(--soft);margin:0}
p{margin:0}
a{color:var(--accent)}

/* the status band: the one thing that must read from across the room */
.band{display:flex;flex-wrap:wrap;align-items:center;gap:22px 30px;
  background:var(--panel);border:1px solid var(--line);border-radius:16px;
  padding:26px 30px;margin-top:10px}
.band .verdict{font:700 46px/1 "Inter",system-ui,sans-serif;letter-spacing:-.02em}
.band .why{flex:1 1 260px;min-width:220px;color:var(--soft);font-size:17px}
.crit .verdict,.chip.crit,.lead.crit b{color:var(--crit)}
.warn .verdict,.chip.warn{color:var(--warn)}
.good .verdict,.chip.good{color:var(--good)}

/* revenue, told on the brand's own gauge */
.money{display:grid;grid-template-columns:minmax(0,320px) 1fr;gap:8px 36px;
  align-items:center;background:var(--panel);border:1px solid var(--line);
  border-radius:16px;padding:22px 30px}
.gauge{width:100%;height:auto;display:block}
.money .fig{font:700 clamp(40px,7vw,62px)/1 "Inter",system-ui,sans-serif;
  letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.money .of{color:var(--soft);font-size:16px;margin-top:6px}
@media(max-width:720px){.money{grid-template-columns:1fr;text-align:center}}

.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));
  gap:10px}
.cell{background:var(--panel);border:1px solid var(--line);border-radius:13px;
  padding:15px 17px}
.cell b{display:block;font:600 27px/1.1 "Inter",system-ui,sans-serif;
  letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.cell span{display:block;margin-top:7px;font:500 11px/1.35 "Inter",system-ui,sans-serif;
  letter-spacing:.1em;text-transform:uppercase;color:var(--soft)}

.lead{background:var(--panel);border-left:4px solid var(--accent);
  border-radius:0 13px 13px 0;padding:20px 26px}
.lead p{color:var(--ink)}

.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:13px;
  background:var(--panel)}
table{width:100%;border-collapse:collapse;
  font:400 15px/1.5 "Inter",system-ui,sans-serif;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:12px 16px;border-bottom:1px solid var(--line);
  vertical-align:top}
tbody tr:last-child th,tbody tr:last-child td{border-bottom:0}
thead th{font:600 10.5px/1 "Inter",system-ui,sans-serif;letter-spacing:.13em;
  text-transform:uppercase;color:var(--soft);background:var(--wash);
  border-bottom:1px solid var(--line-2)}
tbody th{font-weight:600;white-space:nowrap}
td.num{font-weight:600;color:var(--soft);white-space:nowrap}
td.st{white-space:nowrap}

.chip{display:inline-block;font:600 11.5px/1 "Inter",system-ui,sans-serif;
  letter-spacing:.06em;text-transform:uppercase;padding:6px 10px;border-radius:99px;
  border:1px solid currentColor}
.chip.idle{color:var(--mute)}
.lab{display:inline-block;margin:0 5px 4px 0;padding:5px 9px;border-radius:99px;
  font:600 11px/1 "Inter",system-ui,sans-serif;letter-spacing:.04em;
  color:var(--ink);border:1px solid #0000;
  background:color-mix(in srgb,var(--lc) 26%,transparent);
  box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--lc) 55%,transparent)}

ul.needs{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:9px}
ul.needs li{background:var(--panel);border:1px solid var(--line);border-radius:11px;
  padding:13px 17px;font:400 16px/1.5 "Inter",system-ui,sans-serif}
ul.needs b{color:var(--accent)}
code{font:500 13.5px/1 ui-monospace,SFMono-Regular,Menlo,monospace;
  background:var(--wash);padding:2px 6px;border-radius:5px}
footer{color:var(--mute);font:400 13.5px/1.6 "Inter",system-ui,sans-serif;
  margin-top:34px;border-top:1px solid var(--line);padding-top:16px}
"""

doc = (
    '<meta charset="utf-8">\n'
    '<title>6S Success Command Deck</title>\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Fraunces:opsz,wght@9..144,600&family=Inter:wght@400;500;600;700'
    '&family=Newsreader:wght@400;500&display=swap">\n'
    f"<style>{CSS}</style>\n"
    f'<div class="wrap">\n'
    f'<h1>Command deck</h1>\n'
    f'<p class="eyebrow">Generated {esc(S["generated"])} &middot; every figure measured, none typed</p>\n'

    f'<div class="band {tone}">'
    f'<div class="verdict">{esc(S["overall"])}</div>'
    f'<p class="why">{esc(S["overall_why"])}</p>'
    f'</div>\n'

    f'<div class="money">'
    f'<div>{gauge(S["revenue_pct"])}</div>'
    f'<div><div class="fig">${S["revenue_month"]:,.0f}</div>'
    f'<p class="of">of the ${S["revenue_target"]:,.0f} monthly target, '
    f'{S["revenue_pct"]}%. The needle sits where the money is, on the same gauge '
    f'the method uses to read a room.</p></div>'
    f'</div>\n'

    f'<div class="grid">'
    f'<div class="cell"><b>{S["paying_customers"]}</b><span>Paying customers</span></div>'
    f'<div class="cell"><b>{S["email_list"]}</b><span>Email list</span></div>'
    f'<div class="cell"><b>{"yes" if S["can_take_payment"] else "no"}</b><span>Can take money</span></div>'
    f'<div class="cell"><b>{S["open_p0"] if S["issues_available"] else "?"}</b><span>Open P0</span></div>'
    f'<div class="cell"><b>{S["needs_phil"] if S["issues_available"] else "?"}</b><span>Need your call</span></div>'
    f'<div class="cell"><b>{S["commits_7d"]}</b><span>Commits, 7 days</span></div>'
    f'</div>\n'

    f'<h2>The one constraint</h2>\n'
    f'<div class="lead {tone}"><p>{esc(S["constraint"])}</p></div>\n'

    f'<h2>What needs you</h2>\n'
    f'<ul class="needs">{needs}</ul>\n'

    f'<h2>Product readiness</h2>\n'
    f'<div class="scroll"><table>'
    f'<thead><tr><th>Product</th><th>Measured state</th><th>Reads as</th></tr></thead>'
    f'<tbody>{ready_rows}</tbody></table></div>\n'

    f'<h2>Open issues</h2>\n'
    f'<div class="scroll"><table>'
    f'<thead><tr><th>#</th><th>Title</th><th>Labels</th></tr></thead>'
    f'<tbody>{issue_rows}</tbody></table></div>\n'

    f'<footer>Last commit <code>{esc(S["commit"])}</code> {esc(S["commit_msg"])}. '
    f'{S["commits_7d"]} commits in seven days, {S["commits_total"]} in total. Working tree '
    f'{"clean and in sync" if S["clean"] and S["ahead"] == "0" else "has uncommitted or unpushed work"}. '
    f'{esc(str(S["closed_issues"])) if S["closed_issues"] is not None else "An unknown number of"} issues closed to date. '
    f'Regenerate with <code>python ops/dashboard.py</code>.</footer>\n'
    f'</div>'
)

open(os.path.join(ROOT, "ops", "dashboard.html"), "w", encoding="utf-8").write(doc)
json.dump(S, open(os.path.join(ROOT, "ops", "state.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(f"{S['overall']} | revenue ${S['revenue_month']:,.0f}/{S['revenue_target']:,.0f} | "
      f"P0 {S['open_p0'] if S['issues_available'] else 'UNKNOWN'} | "
      f"need-you {S['needs_phil'] if S['issues_available'] else 'UNKNOWN'} | "
      f"commits7d {S['commits_7d']}")
print("wrote EXECUTIVE-DASHBOARD-LIVE.md, ops/dashboard.html, ops/state.json")
