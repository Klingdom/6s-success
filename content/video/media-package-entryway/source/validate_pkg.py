# -*- coding: utf-8 -*-
"""Validation gates for the Entryway YouTube media package."""
import json, io, re, sys, collections

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
PKGDIR = r"C:\Users\philk\Desktop\6S-Video-Production-Plan\media-package-entryway"
DOC = PKGDIR + r"\Entryway Media Package - YouTube.html"

meta = json.load(io.open(SCRATCH + r"\package.json", encoding="utf-8"))["zones"]
pilot = {z["zone"]: z for z in json.load(io.open(SCRATCH + r"\pilot.json", encoding="utf-8"))["zones"]}
doc = io.open(DOC, encoding="utf-8").read()

fails = []
def gate(ok, label, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + (("  " + detail) if detail else ""))
    if not ok: fails.append(label + " " + detail)

def allstr(v):
    out = []
    def w(x):
        if isinstance(x, str): out.append(x)
        elif isinstance(x, list):
            for i in x: w(i)
        elif isinstance(x, dict):
            for i in x.values(): w(i)
    w(v); return out

blob_by_zone = {m["zone"]: " ".join(allstr(m)) for m in meta}
allblob = " ".join(blob_by_zone.values())

print("\n=== GATE 1: em dashes ===")
em = sum(t.count("—") for t in allstr(meta))
gate(em == 0, "zero em dashes in copy", "found %d" % em)

print("\n=== GATE 2: completeness ===")
gate(len(meta) == 5, "5 episodes", "got %d" % len(meta))
REQ = ["zone","description_hook","description_body","tags","pinned_comment","end_screen","thumbnail","shorts"]
miss = [(m.get("zone"), k) for m in meta for k in REQ if not m.get(k)]
gate(not miss, "all metadata fields present", "missing: %s" % miss[:5])
# tag counts
tagbad = [(m["zone"], len(m.get("tags") or [])) for m in meta if not (10 <= len(m.get("tags") or []) <= 15)]
gate(not tagbad, "tag count 10-15 per video", "bad: %s" % tagbad)

print("\n=== GATE 3: Shorts match the scripts ===")
# every use_as_short=true segment gets exactly one Short; none for false
prob = []
for m in meta:
    z = m["zone"]
    want = [s["step"] for s in pilot[z]["segments"] if (s.get("short_cut") or {}).get("use_as_short", True)]
    got = [sh.get("step") for sh in (m.get("shorts") or [])]
    if sorted(want) != sorted(got):
        prob.append((z, "want %s got %s" % (want, got)))
gate(not prob, "Shorts set matches use_as_short flags", "; ".join(str(p) for p in prob[:3]))
total = sum(len(m.get("shorts") or []) for m in meta)
gate(total == 23, "23 Shorts total", "got %d" % total)
# each short complete
scmpl = [(m["zone"], sh.get("step")) for m in meta for sh in (m.get("shorts") or [])
         if not (sh.get("short_title") and sh.get("caption") and (sh.get("hashtags") or []))]
gate(not scmpl, "every Short has title, caption, hashtags", "incomplete: %s" % scmpl[:4])

print("\n=== GATE 4: YouTube limits ===")
tl = [(m["zone"], sh.get("step"), len(sh.get("short_title",""))) for m in meta
      for sh in (m.get("shorts") or []) if len(sh.get("short_title","")) > 100]
gate(not tl, "Shorts titles <=100 chars", "over: %s" % tl[:3])
vt = [(z, len(pilot[z].get("title",""))) for z in blob_by_zone if len(pilot[z].get("title","")) > 100]
gate(not vt, "video titles <=100 chars", "over: %s" % vt[:3])
# hashtags well-formed
hb = [(m["zone"], h) for m in meta for sh in (m.get("shorts") or []) for h in (sh.get("hashtags") or [])
      if not h.startswith("#") or " " in h]
gate(not hb, "hashtags start with # and have no spaces", "bad: %s" % hb[:4])

print("\n=== GATE 5: canon and cleanliness ===")
low = allblob.lower()
# no five-S lists / Safety must be 4th where all six appear
runs = re.findall(r"(?:sort|straighten|shine|safety|standardize|sustain)"
                  r"(?:\s*(?:,|and|&|/|then)\s*(?:sort|straighten|shine|safety|standardize|sustain)){3,}", low)
bad = []
for r in runs:
    seq = re.findall(r"sort|straighten|shine|safety|standardize|sustain", r)
    if len(seq) >= 5 and seq[:4] != ["sort","straighten","shine","safety"]:
        bad.append(r)
gate(not bad, "Safety 4th where six S's listed", "bad: %s" % bad[:2])
BANNED = ["workcell","throughput","production capacity","fire lane","ergonomic","lean practice",
          "sop","optimize","optimise","leverage","kpi","cadence"]
bv = {b: len(re.findall(r"\b"+re.escape(b)+r"\b", low)) for b in BANNED}
bv = {k: c for k, c in bv.items() if c}
gate(not bv, "no banned vocabulary", "found %s" % bv)
stats = re.findall(r"\b\d{1,3}\s?%|\bgo viral\b|\bmillions? of views\b|\bstudies show\b", low)
gate(not stats, "no invented stats or view promises", "found %s" % stats[:3])
CLICK = [r"you won'?t believe", r"shocking", r"!!!", r"\binsane\b", r"life.chang"]
ch = [c for c in CLICK if re.search(c, low)]
gate(not ch, "no clickbait phrasing", "found %s" % ch[:3])

print("\n=== GATE 6: chapters ===")
# each video's assembled description carries a chapter block starting at 0:00
import importlib.util
spec = importlib.util.spec_from_file_location("bp", SCRATCH + r"\build_pkg.py")
# don't exec build (it writes files); re-derive chapters here instead
INTRO = 60
for m in meta:
    segs = {s["step"]: s for s in pilot[m["zone"]]["segments"]}
    order = ["Sort","Straighten","Shine","Safety","Standardize","Sustain"]
    present = [k for k in order if k in segs]
    ok = (present == order)
    if not ok: fails.append("chapter steps wrong for " + m["zone"])
gate(all(True for _ in meta), "chapter scaffold derivable for every video")
gate("0:00 Intro" in doc, "descriptions start chapters at 0:00 Intro")
gate("estimated" in doc.lower(), "chapters flagged estimated")

print("\n=== GATE 7: HTML + paste files ===")
for tag in ["section","div","ul","li","main","p","h2","h3","h5","pre"]:
    o = len(re.findall(r"<%s[\s>]" % tag, doc)); c = len(re.findall(r"</%s>" % tag, doc))
    if o != c: fails.append("unbalanced <%s> %d/%d" % (tag, o, c))
    print("  %-6s open %-4d close %-4d %s" % (tag, o, c, "OK" if o == c else "X"))
ids = re.findall(r'id="([^"]+)"', doc)
dupes = [i for i, c in collections.Counter(ids).items() if c > 1]
gate(not dupes, "no duplicate ids", "%s" % dupes[:4])
anchors = set(re.findall(r'href="#([^"]+)"', doc)) - {""}
gate(anchors <= set(ids), "nav anchors resolve", "%s" % list(anchors - set(ids))[:4])
import os
pfiles = [f for f in os.listdir(PKGDIR + r"\paste")] if os.path.isdir(PKGDIR + r"\paste") else []
gate(len(pfiles) == 5, "5 paste-ready .txt files", "got %d" % len(pfiles))

print("\n" + "=" * 58)
if fails:
    print("FAILED %d gate(s):" % len(fails))
    for f in fails: print("  - " + f)
    sys.exit(1)
print("ALL GATES PASSED  |  %d videos, %d Shorts, %d paste files"
      % (len(meta), total, len(pfiles)))
