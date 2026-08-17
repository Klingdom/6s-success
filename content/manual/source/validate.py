# -*- coding: utf-8 -*-
"""Validation gates for The Micro Zone Manual v3."""
import json, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))     # content/manual/source
MANUAL_DIR = os.path.dirname(HERE)                    # content/manual
DOC = os.path.join(MANUAL_DIR, "6S Home Micro Zone SOP Field Manual v3.html")

data = json.load(io.open(os.path.join(HERE, "content.json"), encoding="utf-8"))
rooms = data["rooms"] if isinstance(data, dict) else data
doc = io.open(DOC, encoding="utf-8").read()
# strip every stylesheet, not just an unattributed one: the print stylesheet is
# injected as <style id="print-edition">, and its CSS percentages were being read
# by the invented-statistics gate as body copy.
body = re.sub(r"<style[^>]*>.*?</style>", "", doc, flags=re.S)
text = re.sub(r"<[^>]+>", " ", body)

fails, warns = [], []
def gate(ok, label, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + (("  " + detail) if detail else ""))
    if not ok:
        fails.append(label + " " + detail)

print("\n=== GATE 1: dashes ===")
n_em = text.count("—")
gate(n_em == 0, "zero em dashes", "found %d" % n_em)
# House style tightened after the brief was frozen: en dashes are now zero as
# well, including inside number ranges. Session times read 30-45 min, hyphenated.
n_en = text.count("–")
gate(n_en == 0, "zero en dashes", "found %d" % n_en)

print("\n=== GATE 2: six-S canon ===")
S = ["Sort", "Straighten", "Shine", "Safety", "Standardize", "Sustain"]
# every enumerated run of S-names must have Safety 4th
runs = re.findall(r"(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)"
                  r"(?:\s*(?:,|and|&|·|>|→|/)\s*"
                  r"(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)){3,}", text)
bad_runs = []
for r in runs:
    seq = re.findall(r"Sort|Straighten|Shine|Safety|Standardize|Sustain", r)
    if len(seq) >= 5 and seq[:6] != S[:len(seq)]:
        bad_runs.append(r.strip())
gate(not bad_runs, "Safety is the 4th S in every list", "bad: %s" % bad_runs[:3])
gate("Safety" in text, "Safety present")
# per-card ordering from JSON
order_bad = [ (r["room"], z["zone"]) for r in rooms for z in r.get("zones", [])
              if list((z.get("passes") or {}).keys()) and
              [k for k in ["sort","straighten","shine","safety","standardize","sustain"]
               if k in (z.get("passes") or {})] != ["sort","straighten","shine","safety","standardize","sustain"] ]
gate(not order_bad, "all 6 passes present and ordered in every card", "bad: %s" % order_bad[:3])

print("\n=== GATE 3: completeness ===")
gate(len(rooms) == 20, "20 rooms", "got %d" % len(rooms))
nz = sum(len(r.get("zones") or []) for r in rooms)
gate(nz == 114, "114 zones", "got %d" % nz)
REQ = ["zone","session","time_note","purpose","done_looks_like","passes","the_call","watch_for","leave_behind"]
missing = [(r["room"], z.get("zone"), k) for r in rooms for z in r.get("zones", [])
           for k in REQ if not z.get(k)]
gate(not missing, "every zone has all required elements", "missing %d: %s" % (len(missing), missing[:4]))
notips = [r["room"] for r in rooms if len(r.get("tips") or []) != 3]
gate(not notips, "every room has 3 tips", "bad: %s" % notips)

print("\n=== GATE 3b: deepened Shine (How to clean it) ===")
zones_all = [(r["room"], z) for r in rooms for z in r.get("zones", [])]
no_sd = [(rm, z["zone"]) for rm, z in zones_all if not z.get("shine_detail")]
gate(not no_sd, "every zone has a How-to-clean block", "missing %d: %s" % (len(no_sd), no_sd[:5]))
SDREQ = ["shine_summary", "surfaces", "products_used", "inspect_as_you_clean"]
sd_miss = [(rm, z["zone"], k) for rm, z in zones_all if z.get("shine_detail")
           for k in SDREQ if not (z["shine_detail"].get(k))]
gate(not sd_miss, "clean block has all fields", "missing %d: %s" % (len(sd_miss), sd_miss[:5]))
thin = [(rm, z["zone"], len(z.get("shine_detail", {}).get("surfaces") or []))
        for rm, z in zones_all if z.get("shine_detail")
        and len(z["shine_detail"].get("surfaces") or []) < 3]
gate(not thin, "every zone cleans >=3 surfaces", "thin: %s" % thin[:5])
noinspect = [(rm, z["zone"]) for rm, z in zones_all if z.get("shine_detail")
             and len(z["shine_detail"].get("inspect_as_you_clean") or []) < 2]
gate(not noinspect, "every zone has >=2 inspect points", "bad: %s" % noinspect[:5])
# every surface has a method
nomethod = [(rm, z["zone"]) for rm, z in zones_all if z.get("shine_detail")
            for s in (z["shine_detail"].get("surfaces") or []) if not s.get("method")]
gate(not nomethod, "every surface has a method", "bad: %s" % nomethod[:5])
# Shine-vs-Safety separation: inspect lines must NOTICE, not instruct a fix.
# "anchor"/"strap"/"secure" are excluded: in this corpus they are nouns (an anti-tip
# strap, a wall anchor) that the reader is told to FLAG, not verbs. An imperative fix
# is caught only when the verb is not immediately softened by a notice/flag cue.
FIXVERB = re.compile(r"\b(fix it|repair it|replace it|reinstall|tighten it|"
                     r"unplug it|childproof|screw it back|bolt it back)\b", re.I)
NOTICE = re.compile(r"\b(flag|note|notice|noticed|look|check|watch|worth|sign|the one that)\b", re.I)
leaky = [(rm, z["zone"], i[:60]) for rm, z in zones_all if z.get("shine_detail")
         for i in (z["shine_detail"].get("inspect_as_you_clean") or [])
         if FIXVERB.search(i) and not NOTICE.search(i)]
gate(not leaky, "inspect points flag, do not fix (Shine != Safety)",
     "fix-instructions in %d: %s" % (len(leaky), leaky[:5]))

print("\n=== GATE 4: banned vocabulary ===")
BANNED = ["workcell","throughput","production capacity","fire lane","ergonomic",
          "lean practice","SOP","optimize","optimise","leverage","KPI","cadence","real estate"]
hits = collections.Counter()
low = text.lower()
for b in BANNED:
    c = len(re.findall(r"\b" + re.escape(b.lower()) + r"\b", low))
    if c: hits[b] = c
gate(not hits, "no banned vocabulary", "found %s" % dict(hits))

print("\n=== GATE 5: false precision ===")
splits = re.findall(r"(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)\s*:?\s*\d+\s*(?:′|min\b)", text)
gate(not splits, "no per-step minute splits", "found %s" % splits[:3])
totals = re.findall(r"\b\d+\s*h\s*\d*\s*m\b|\b\d{2,}\s*hours\b", text)
gate(not totals, "no whole-house time total", "found %s" % totals[:3])
stats = re.findall(r"\b\d{1,3}\s?%|\bstudies show\b|\bresearch shows\b", low)
gate(not stats, "no invented statistics", "found %s" % stats[:3])
sess_ok = all(re.match(r"^\d+-\d+ min$", (z.get("session") or "")) for r in rooms for z in r.get("zones", []))
gate(sess_ok, "all session times are ranges")

print("\n=== GATE 6: HTML structure ===")
for tag in ["section","article","div","ul","li","dl","nav","main","p","h2","h3"]:
    o = len(re.findall(r"<%s[\s>]" % tag, doc)); c = len(re.findall(r"</%s>" % tag, doc))
    if o != c: fails.append("unbalanced <%s> %d/%d" % (tag, o, c))
    print("  %-8s open %-4d close %-4d %s" % (tag, o, c, "OK" if o == c else "MISMATCH"))
try:
    from html.parser import HTMLParser
    class P(HTMLParser):
        def error(self, m): raise ValueError(m)
    p = P(); p.feed(doc); p.close()
    gate(True, "HTML parses")
except Exception as e:
    gate(False, "HTML parses", str(e))
ids = re.findall(r'id="([^"]+)"', doc)
dupes = [i for i, c in collections.Counter(ids).items() if c > 1]
gate(not dupes, "no duplicate ids", "dupes: %s" % dupes[:5])
anchors = set(re.findall(r'href="#([^"]+)"', doc))
gate(anchors <= set(ids), "all toc anchors resolve", "dangling: %s" % list(anchors - set(ids))[:5])

print("\n=== GATE 7: boilerplate ===")
sents = collections.Counter()
where = collections.defaultdict(list)
for r in rooms:
    for z in r.get("zones", []):
        blob = " ".join([z.get("purpose",""), z.get("done_looks_like",""),
                         (z.get("the_call") or {}).get("text",""),
                         (z.get("leave_behind") or {}).get("standard",""),
                         (z.get("leave_behind") or {}).get("trigger","")]
                        + list((z.get("passes") or {}).values())
                        + [w.get("text","") for w in (z.get("watch_for") or [])])
        for s in re.split(r"(?<=[.!?])\s+", blob):
            s = s.strip()
            if len(s.split()) >= 6:
                sents[s] += 1
                where[s].append("%s/%s" % (r["room"], z.get("zone")))
# The brief freezes four canon lines and instructs agents to quote them verbatim,
# so their recurrence is intended, not boilerplate. Everything else must be unique.
CANON = [
    "A standard is the best way you know today, written down.",
    "An audit checks the home, not the household. What it finds is always a system to fix, never a person to blame.",
    "You do not finish 6S. You keep it.",
    "Find it, and fix it now.",
]
def is_canon(s):
    t = s.strip().strip('"“”‘’\'')
    return any(t == c or t == c.rstrip(".") for c in CANON)

rep = [(s, c) for s, c in sents.items() if c > 1 and not is_canon(s)]
canon_hits = sum(c for s, c in sents.items() if c > 1 and is_canon(s))
print("  note: %d canon-line quotations (intended, whitelisted)" % canon_hits)
gate(not rep, "no sentence repeated across zones", "repeats: %d" % len(rep))
for s, c in rep[:5]:
    print("      x%d  %.90s\n           %s" % (c, s, where[s][:4]))

# near-duplicate check on 'done looks like'
generic = [w for w in ["tidy","organized","organised","clutter-free","clutter free","streamlined","neat and"]
           if w in " ".join((z.get("done_looks_like") or "").lower() for r in rooms for z in r.get("zones", []))]
gate(not generic, "no generic done-states", "found %s" % generic)

print("\n" + "=" * 58)
if fails:
    print("FAILED %d gate(s):" % len(fails))
    for f in fails: print("  - " + f)
    sys.exit(1)
print("ALL GATES PASSED  |  %d rooms, %d zones, %d KB" % (len(rooms), nz, len(doc) // 1024))
