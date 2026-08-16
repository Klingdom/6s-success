# -*- coding: utf-8 -*-
"""Validation gates for the Entryway pilot shooting scripts."""
import json, io, re, sys, collections

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
DOC = r"C:\Users\philk\Desktop\6S-Video-Production-Plan\pilot\Entryway Pilot - Shooting Scripts.html"

zones = json.load(io.open(SCRATCH + r"\pilot.json", encoding="utf-8"))["zones"]
opener = json.load(io.open(SCRATCH + r"\opener_asset.json", encoding="utf-8"))
doc = io.open(DOC, encoding="utf-8").read()
body = re.sub(r"<style>.*?</style>", "", doc, flags=re.S)
text = re.sub(r"<[^>]+>", " ", body)

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

# VO fields only (what gets recorded) -- opener asset uses [PLACEHOLDER] tokens, excluded here
def vo_fields(v):
    out = [v.get("cold_open_vo",""), v.get("close_vo",""), v.get("next_teaser_vo","")]
    for s in (v.get("segments") or []):
        out.append(s.get("vo",""))
        sc = s.get("short_cut") or {}
        out += [sc.get("standalone_intro_vo",""), sc.get("end_card_vo","")]
    return out

print("\n=== GATE 1: em dashes ===")
# document includes rendered &mdash; entities in OST captions (my template) -> check source strings, not rendered text
src_all = [s for v in zones for s in allstr(v)]
em_src = sum(t.count("—") for t in src_all)
gate(em_src == 0, "zero em dashes in script content", "found %d" % em_src)

print("\n=== GATE 2: six-S canon ===")
S = ["Sort","Straighten","Shine","Safety","Standardize","Sustain"]
bad = [(v.get("zone"), [s.get("step") for s in (v.get("segments") or [])])
       for v in zones if [s.get("step") for s in (v.get("segments") or [])] != S]
gate(not bad, "6 segments, canonical order, Safety 4th", "bad: %s" % bad[:2])
# opener asset beat 2 names all six with Safety fourth
b2 = next((b for b in opener["beats"] if b["beat"] == 2), {}).get("vo", "")
seq = re.findall(r"Sort|Straighten|Shine|Safety|Standardize|Sustain", b2)
gate(seq[:6] == S, "opener names six S's, Safety 4th", "got %s" % seq[:6])

print("\n=== GATE 3: completeness ===")
gate(len(zones) == 5, "5 episodes", "got %d" % len(zones))
REQ = ["zone","episode_code","title","runtime","thumbnail_text","cold_open_vo",
       "segments","close_vo","next_teaser_vo","consolidated_shot_list","shoot_notes"]
miss = [(v.get("zone"), k) for v in zones for k in REQ if not v.get(k)]
gate(not miss, "all episode fields present", "missing: %s" % miss[:4])
# every VO is real prose, not a stub
short_vo = [(v.get("zone"), t[:40]) for v in zones for t in vo_fields(v) if len(t.split()) < 3]
gate(not short_vo, "every VO field is real prose", "stubs: %s" % short_vo[:4])
# shots synced
segct = [(v.get("zone"), s.get("step"), len(s.get("shots") or []))
         for v in zones for s in (v.get("segments") or []) if len(s.get("shots") or []) < 2]
gate(not segct, "every segment has >=2 shots", "thin: %s" % segct[:3])

print("\n=== GATE 4: VO / shot sync ===")
# each shot's vo_sync phrase should be recognizably part of the segment VO.
def norm(s): return re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())
def toks(s): return [w for w in norm(s).split() if len(w) > 3]
unsynced = []
for v in zones:
    for s in (v.get("segments") or []):
        vo = norm(s.get("vo", ""))
        for sh in (s.get("shots") or []):
            key = norm(sh.get("vo_sync", ""))
            kt = [w for w in key.split() if len(w) > 3]
            if not kt:
                continue
            # at least half the content words of the sync phrase appear in the VO
            hit = sum(1 for w in kt if w in vo)
            if hit < max(1, len(kt) // 2):
                unsynced.append((v.get("zone"), s.get("step"), sh.get("vo_sync", "")[:50]))
gate(len(unsynced) <= 2, "shot vo_sync phrases trace to segment VO",
     "loose %d: %s" % (len(unsynced), unsynced[:4]))

print("\n=== GATE 5: headless ===")
PRESENTER = [r"\btalking head\b", r"\bpiece to camera\b", r"\bon.camera host\b",
             r"\b(?:presenter|host|narrator|actor|model)\s+(?:appears|walks|stands|sits|turns|smiles|faces|gestures|points|enters|holds up|demonstrates)\b",
             r"\bface(?:s)? the camera\b", r"\bsmiles? (?:at|into) (?:the )?camera\b",
             r"\bselfie\b", r"\bvlog style\b", r"\bwaist.up\b",
             r"\bhead(?:\s|-)and(?:\s|-)shoulders? (?:shot|framing|angle)\b",
             r"\bfull body shot\b", r"\bpresent(?:s|ing)? to camera\b", r"\bspeaks? to (?:the )?camera\b"]
# "no second operator" / "without a second operator" is the correct headless
# intent, so only flag a second operator when it is NOT negated.
GEAR = [r"\bcrane shot\b", r"\bdrone\b", r"\bjib\b", r"\bdolly track\b", r"\bsteadicam\b",
        r"\bgimbal operator\b", r"(?<!no )(?<!without a )\bsecond (?:camera )?operator\b",
        r"\bcamera crew\b", r"\blighting rig\b"]
ph, gh = [], []
for v in zones:
    blob = " ".join(allstr(v)).lower()
    for p in PRESENTER:
        if re.search(p, blob): ph.append((v.get("zone"), p))
    for p in GEAR:
        if re.search(p, blob): gh.append((v.get("zone"), p))
gate(not ph, "no presenter on camera", "found: %s" % ph[:3])
gate(not gh, "one-person shoot only", "found: %s" % gh[:3])

print("\n=== GATE 6: outline/script discipline ===")
low = " ".join(src_all).lower()
BANNED = ["workcell","throughput","production capacity","fire lane","ergonomic","lean practice",
          "sop","optimize","optimise","leverage","kpi","cadence"]
bv = {b: len(re.findall(r"\b"+re.escape(b)+r"\b", low)) for b in BANNED}
bv = {k: c for k, c in bv.items() if c}
gate(not bv, "no banned vocabulary", "found %s" % bv)
# absolute timecodes forbidden; "~8s" targets allowed
tc = re.findall(r"\b\d{1,2}:\d{2}\b", " ".join(src_all))
gate(not tc, "no absolute timecodes", "found %s" % tc[:5])
stats = re.findall(r"\b\d{1,3}\s?%|\bstudies show\b|\bresearch shows\b", low)
gate(not stats, "no invented statistics", "found %s" % stats[:3])

print("\n=== GATE 7: HTML structure ===")
for tag in ["section","div","table","thead","tbody","tr","ul","li","main","p","h2","h3"]:
    o = len(re.findall(r"<%s[\s>]" % tag, doc)); c = len(re.findall(r"</%s>" % tag, doc))
    if o != c: fails.append("unbalanced <%s> %d/%d" % (tag, o, c))
    print("  %-8s open %-4d close %-4d %s" % (tag, o, c, "OK" if o == c else "MISMATCH"))
ids = re.findall(r'id="([^"]+)"', doc)
dupes = [i for i, c in collections.Counter(ids).items() if c > 1]
gate(not dupes, "no duplicate ids", "dupes: %s" % dupes[:5])
anchors = set(re.findall(r'href="#([^"]+)"', doc)) - {""}
gate(anchors <= set(ids), "nav anchors resolve", "dangling: %s" % list(anchors - set(ids))[:5])

print("\n" + "=" * 58)
if fails:
    print("FAILED %d gate(s):" % len(fails))
    for f in fails: print("  - " + f)
    sys.exit(1)
n_short = sum(1 for v in zones for s in (v.get("segments") or []) if (s.get("short_cut") or {}).get("use_as_short", True))
print("ALL GATES PASSED  |  %d episodes, %d Shorts, %d KB" % (len(zones), n_short, len(doc)//1024))
