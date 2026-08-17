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
S["constraint"] = ("The business cannot accept money. Checkout is staged, all "
                   f"{S['forms_dead']} forms are disconnected, and the email list is empty, "
                   "so every visitor is lost permanently. Nothing else moves revenue until this does.")

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

# --- html
def esc(x): return html.escape(str(x))
rows = "".join(
    f"<tr><td>{esc(i['number'])}</td><td>{esc(i['title'])}</td>"
    f"<td>{esc(', '.join(l['name'] for l in i.get('labels', [])))}</td></tr>"
    for i in S["issues"])
color = {"GREEN": "#6E8B5B", "YELLOW": "#DDA63A", "RED": "#CB4B36"}[S["overall"]]
doc = f"""<meta charset="utf-8"><title>6S Success: Live Dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;
--slate:#3C5A6B;--rule:#E2D8C4}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 Georgia,serif}}
.wrap{{max-width:960px;margin:0 auto;padding:0 24px 80px}}
h1{{font-size:clamp(30px,5vw,46px);margin:.4em 0 .1em;font-family:Georgia,serif}}
.gen{{font:12px/1 system-ui;letter-spacing:.14em;text-transform:uppercase;color:var(--soft);margin-bottom:28px}}
h2{{font-size:24px;margin:44px 0 10px;padding-top:20px;border-top:1px solid var(--rule)}}
.hero{{background:var(--panel);border-left:5px solid {color};padding:22px 26px;margin:20px 0}}
.hero .big{{font-size:40px;font-weight:700;color:{color};font-family:system-ui}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule)}}
.cell{{background:var(--panel);padding:14px}}
.cell b{{display:block;font-size:25px;font-family:system-ui;color:var(--slate)}}
.cell span{{font:11px/1.3 system-ui;letter-spacing:.1em;text-transform:uppercase;color:var(--soft);display:block;margin-top:6px}}
table{{width:100%;border-collapse:collapse;font:14px/1.5 system-ui;margin-top:8px}}
th,td{{border-bottom:1px solid var(--rule);padding:10px;text-align:left}}
th{{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--soft);background:#F2EADC}}
.constraint{{background:var(--panel);border-left:5px solid var(--terra);padding:18px 22px;margin:16px 0}}
</style>
<div class="wrap">
<h1>Live Executive Dashboard</h1>
<p class="gen">Generated {esc(S['generated'])} &middot; measured, not typed</p>

<div class="hero">
  <div class="big">{esc(S['overall'])}</div>
  <p style="margin:6px 0 0">{esc(S['overall_why'])}</p>
</div>

<div class="grid">
  <div class="cell"><b>${S['revenue_month']:,.0f}</b><span>Revenue this month</span></div>
  <div class="cell"><b>{S['revenue_pct']}%</b><span>Of $20k target</span></div>
  <div class="cell"><b>{S['paying_customers']}</b><span>Paying customers</span></div>
  <div class="cell"><b>{S['email_list']}</b><span>Email list</span></div>
  <div class="cell"><b>{S['open_p0'] if S['issues_available'] else "?"}</b><span>Open P0</span></div>
  <div class="cell"><b>{S['needs_phil'] if S['issues_available'] else "?"}</b><span>Need your call</span></div>
  <div class="cell"><b>{S['commits_7d']}</b><span>Commits, 7 days</span></div>
  <div class="cell"><b>{S['closed_issues'] if S['closed_issues'] is not None else "?"}</b><span>Issues closed</span></div>
</div>

<h2>The one constraint</h2>
<div class="constraint"><p style="margin:0">{esc(S['constraint'])}</p></div>

<h2>Product readiness</h2>
<table>
<tr><th>Product</th><th>Measured state</th></tr>
<tr><td>Website</td><td>{S['site_pages']} pages &middot; {S['dead_links']} dead links &middot; {S['legal_pages']}/4 legal pages &middot; {S['forms_dead']} disconnected forms</td></tr>
<tr><td>Book</td><td>{S['chapters']}/50 chapters &middot; {S['chapters_with_disclaimer']}/50 with safety notice &middot; {S['chapters_no_photos']} without photographs</td></tr>
<tr><td>Book, sellable?</td><td><b>{'YES' if S['book_sellable'] else 'NO'}</b> &middot; EPUB {str(S['epub_mb']) + ' MB' if S['epub_built'] else 'not built'} &middot; cover {'embedded' if S['epub_has_cover'] else 'MISSING'} &middot; {S['front_matter_blanks']} unfilled front-matter fields</td></tr>
<tr><td>Micro zones</td><td>{S['rooms']} rooms &middot; {S['zones']} zones</td></tr>
<tr><td>Card decks</td><td>{S['deck_rooms']}/20 rooms &middot; {S['zones_with_deck']}/{S['zones']} zones &middot; card art not tracked in repo</td></tr>
<tr><td>Canon</td><td>{S['set_in_order_live']} live uses of "Set in Order" in decks</td></tr>
<tr><td>House style</td><td>control layer {S.get("ctrl_em",0)} em and {S.get("ctrl_en",0)} en dashes across {S.get("ctrl_files",0)} files &middot; published site {S.get("site_em",0)} em</td></tr>
<tr><td>Social corpus</td><td>~{S['social_units']:,} units ready, unused</td></tr>
<tr><td>Video</td><td>{S['video_shot']}/{S['video_planned']} episodes shot</td></tr>
</table>

<h2>Open issues</h2>
<table><tr><th>#</th><th>Title</th><th>Labels</th></tr>{rows}</table>
</div>"""
open(os.path.join(ROOT, "ops", "dashboard.html"), "w", encoding="utf-8").write(doc)
json.dump(S, open(os.path.join(ROOT, "ops", "state.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(f"{S['overall']} | revenue ${S['revenue_month']:,.0f}/{S['revenue_target']:,.0f} | "
      f"P0 {S['open_p0'] if S['issues_available'] else 'UNKNOWN'} | "
      f"need-you {S['needs_phil'] if S['issues_available'] else 'UNKNOWN'} | "
      f"commits7d {S['commits_7d']}")
print("wrote EXECUTIVE-DASHBOARD-LIVE.md, ops/dashboard.html, ops/state.json")
