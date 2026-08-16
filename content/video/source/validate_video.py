# -*- coding: utf-8 -*-
"""Validation gates for The 6S Micro Zone Reset production plan."""
import json, io, re, sys, collections

import os
SCRATCH = os.path.dirname(os.path.abspath(__file__))
DOC = r"C:\Users\philk\Desktop\6S-Video-Production-Plan\6S Micro Zone Reset - YouTube Production Plan.html"

data = json.load(io.open(SCRATCH + r"\video.json", encoding="utf-8"))
rooms = data["rooms"] if isinstance(data, dict) else data
doc = io.open(DOC, encoding="utf-8").read()
body = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", doc, flags=re.S)
text = re.sub(r"<[^>]+>", " ", body)

fails = []
def gate(ok, label, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + (("  " + detail) if detail else ""))
    if not ok:
        fails.append(label + " " + detail)

vids = [(r["room"], v) for r in rooms for v in (r.get("videos") or [])]

def allstr(v):
    """Every string in one video record."""
    out = []
    def walk(x):
        if isinstance(x, str): out.append(x)
        elif isinstance(x, list):
            for i in x: walk(i)
        elif isinstance(x, dict):
            for i in x.values(): walk(i)
    walk(v)
    return out

print("\n=== GATE 1: em dashes ===")
gate(text.count("—") == 0, "zero em dashes", "found %d" % text.count("—"))
bad_en = [m.group(0) for m in re.finditer(r".{0,12}–.{0,12}", text)
          if not re.search(r"\d\s*–\s*\d|\d\s*–\s*\d+\s*(min|s)\b", m.group(0))]
gate(not bad_en, "en dashes only in ranges", "found %d: %s" % (len(bad_en), bad_en[:3]))

print("\n=== GATE 2: six-S canon ===")
S = ["Sort","Straighten","Shine","Safety","Standardize","Sustain"]
bad = [(rm, v.get("zone"), [s.get("step") for s in (v.get("segments") or [])])
       for rm, v in vids if [s.get("step") for s in (v.get("segments") or [])] != S]
gate(not bad, "every video has 6 segments in canonical order", "bad %d: %s" % (len(bad), bad[:2]))
runs = re.findall(r"(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)"
                  r"(?:\s*(?:,|and|&|·|>|→|/)\s*(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)){3,}", text)
badruns = []
for r in runs:
    seq = re.findall(r"Sort|Straighten|Shine|Safety|Standardize|Sustain", r)
    if len(seq) >= 5 and seq[:6] != S[:len(seq)]:
        badruns.append(r.strip())
gate(not badruns, "Safety is the 4th S in prose lists", "bad: %s" % badruns[:2])

print("\n=== GATE 3: completeness ===")
gate(len(rooms) == 20, "20 rooms", "got %d" % len(rooms))
gate(len(vids) == 114, "114 videos", "got %d" % len(vids))
REQ = ["zone","title","runtime","thumbnail_text","cold_open_problem","segments","close",
       "shot_list","description_hook","tags"]
miss = [(rm, v.get("zone"), k) for rm, v in vids for k in REQ if not v.get(k)]
gate(not miss, "all video fields present", "missing %d: %s" % (len(miss), miss[:4]))
segmiss = [(rm, v.get("zone"), s.get("step"), k)
           for rm, v in vids for s in (v.get("segments") or [])
           for k in ["covers","beats","shots","on_screen_text","short"] if not s.get(k)]
gate(not segmiss, "all segment fields present", "missing %d: %s" % (len(segmiss), segmiss[:3]))
shorts = [s for rm, v in vids for s in (v.get("segments") or [])]
gate(len(shorts) == 684, "684 Shorts", "got %d" % len(shorts))
shmiss = [(rm, v.get("zone"), s.get("step"))
          for rm, v in vids for s in (v.get("segments") or [])
          for k in ["hook","standalone_note","target_length"] if not (s.get("short") or {}).get(k)]
gate(not shmiss, "every Short has hook, standalone note, length", "missing %d: %s" % (len(shmiss), shmiss[:3]))

print("\n=== GATE 4: headless constraint ===")
# a presenter, a face, or a body above the wrists must never appear
# Patterns target a PERSON on camera. "cloth turned to camera" (hands) and
# "a box landing on your head and shoulders" (the viewer's body, described) are
# legitimate headless content, so bare "to camera" / "head and shoulders" are not
# flagged. Only a presenter framing is.
# Target a PERSON framed on camera. Bare words like "presenter"/"host" are NOT
# flagged: in this dataset they appear as "no presenter on camera" and "meals
# hosted here". A violation is a presenter/host performing an on-camera ACTION,
# or an explicit on-camera framing. "cloth turned to camera" (hands) and "a box
# landing on your head and shoulders" (the viewer's body, described) stay clean.
PRESENTER = [r"\btalking head\b", r"\bpiece to camera\b", r"\bon.camera host\b",
             r"\b(?:presenter|host|narrator|actor|model)\s+(?:appears|walks|stands|sits|turns|smiles|faces|gestures|points|enters|holds up|demonstrates)\b",
             r"\bface(?:s)? the camera\b", r"\bsmiles? (?:at|into) (?:the )?camera\b",
             r"\bselfie\b", r"\bvlog style\b", r"\bwaist.up\b",
             r"\bhead(?:\s|-)and(?:\s|-)shoulders? (?:shot|framing|angle)\b",
             r"\bfull body shot\b",
             r"\bpresent(?:s|ing)? to camera\b", r"\bspeaks? to (?:the )?camera\b"]
hits = []
for rm, v in vids:
    blob = " ".join(allstr(v)).lower()
    for p in PRESENTER:
        if re.search(p, blob):
            hits.append((rm, v.get("zone"), p))
gate(not hits, "no presenter on camera", "found %d: %s" % (len(hits), hits[:4]))
# unshootable one-person gear
GEAR = [r"\bcrane shot\b", r"\bdrone\b", r"\bjib\b", r"\bdolly track\b", r"\bsteadicam\b",
        r"\bgimbal operator\b", r"\bsecond camera operator\b", r"\bcamera crew\b", r"\bstudio lighting rig\b"]
ghits = []
for rm, v in vids:
    blob = " ".join(allstr(v)).lower()
    for p in GEAR:
        if re.search(p, blob):
            ghits.append((rm, v.get("zone"), p))
gate(not ghits, "no gear beyond a one-person shoot", "found %d: %s" % (len(ghits), ghits[:4]))

print("\n=== GATE 5: outline discipline ===")
BANNED = ["workcell","throughput","production capacity","fire lane","ergonomic",
          "lean practice","SOP","optimize","optimise","leverage","KPI","cadence"]
low = text.lower()
bv = {b: len(re.findall(r"\b"+re.escape(b)+r"\b", low)) for b in BANNED}
bv = {k: c for k, c in bv.items() if c}
gate(not bv, "no banned vocabulary", "found %s" % bv)
# fake timecodes: the plan deliberately avoids invented precision
tc = re.findall(r"\b\d{1,2}:\d{2}\b", text)
gate(not tc, "no fake timecodes", "found %s" % tc[:5])
stats = re.findall(r"\b\d{1,3}\s?%|\bstudies show\b|\bresearch shows\b", low)
gate(not stats, "no invented statistics", "found %s" % stats[:3])
# clickbait in titles
CLICK = [r"\bYOU WON'T BELIEVE\b", r"\bSHOCKING\b", r"\bthis one weird\b", r"\bhack that\b",
         r"!!!", r"\bINSANE\b", r"\bnobody tells you\b", r"\bgone wrong\b"]
ch = [(rm, v.get("title")) for rm, v in vids for p in CLICK if re.search(p, v.get("title",""), re.I)]
gate(not ch, "no clickbait titles", "found %s" % ch[:3])
caps = [(rm, v.get("title")) for rm, v in vids
        if len(re.findall(r"\b[A-Z]{4,}\b", v.get("title",""))) > 1]
gate(not caps, "no shouted titles", "found %s" % caps[:3])

print("\n=== GATE 6: HTML structure ===")
for tag in ["section","article","div","ul","li","details","summary","nav","main","p","h2","h3"]:
    o = len(re.findall(r"<%s[\s>]" % tag, doc)); c = len(re.findall(r"</%s>" % tag, doc))
    if o != c: fails.append("unbalanced <%s> %d/%d" % (tag, o, c))
    print("  %-9s open %-4d close %-4d %s" % (tag, o, c, "OK" if o == c else "MISMATCH"))
ids = re.findall(r'id="([^"]+)"', doc)
dupes = [i for i, c in collections.Counter(ids).items() if c > 1]
gate(not dupes, "no duplicate ids", "dupes: %s" % dupes[:5])
anchors = set(re.findall(r'href="#([^"]+)"', doc)) - {""}
gate(anchors <= set(ids), "all anchors resolve", "dangling: %s" % list(anchors - set(ids))[:5])
for f in ["id=\"filter\"", "id=\"roomjump\"", "id=\"count\"", "id=\"nores\"", "id=\"expand\""]:
    if f not in doc: fails.append("nav control missing: " + f)
gate(all(f in doc for f in ["id=\"filter\"","id=\"roomjump\"","id=\"expand\""]), "nav controls present")

print("\n=== GATE 7: per-zone specificity ===")
sents = collections.Counter(); where = collections.defaultdict(list)
for rm, v in vids:
    for s in [v.get("cold_open_problem",""), v.get("description_hook","")] + \
             [b for sg in (v.get("segments") or []) for b in (sg.get("beats") or [])]:
        s = (s or "").strip()
        if len(s.split()) >= 6:
            sents[s] += 1; where[s].append("%s/%s" % (rm, v.get("zone")))
rep = [(s, c) for s, c in sents.items() if c > 1]
gate(not rep, "no beat repeated across videos", "repeats: %d" % len(rep))
for s, c in rep[:5]:
    print("      x%d  %.86s\n           %s" % (c, s, where[s][:3]))
dup_titles = [t for t, c in collections.Counter(v.get("title","") for rm, v in vids).items() if c > 1]
gate(not dup_titles, "no duplicate titles", "dupes: %s" % dup_titles[:3])

print("\n" + "=" * 58)
if fails:
    print("FAILED %d gate(s):" % len(fails))
    for f in fails: print("  - " + f)
    sys.exit(1)
print("ALL GATES PASSED  |  %d rooms, %d videos, %d Shorts, %d KB"
      % (len(rooms), len(vids), len(shorts), len(doc)//1024))
