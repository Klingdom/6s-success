# -*- coding: utf-8 -*-
"""Validation gates for the rebuilt Product Spec & Store Release Plan."""
import json, io, re, sys, collections

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
DOC = r"C:\Users\philk\Desktop\6S-Home-Reset-Product-Spec\6S Home Reset - Product Specification and Store Release Plan.html"

data = json.load(io.open(SCRATCH + r"\spec.json", encoding="utf-8"))
units = data["units"]
doc = io.open(DOC, encoding="utf-8").read()
body = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", doc, flags=re.S)
text = re.sub(r"<[^>]+>", " ", body)

fails = []
def gate(ok, label, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + (("  " + detail) if detail else ""))
    if not ok: fails.append(label + " " + detail)

def allstr(x, out=None):
    out = [] if out is None else out
    if isinstance(x, str): out.append(x)
    elif isinstance(x, list):
        for i in x: allstr(i, out)
    elif isinstance(x, dict):
        for i in x.values(): allstr(i, out)
    return out

sections = [s for u in units for s in (u.get("sections") or [])]
content = allstr(units)
blob = " ".join(content)

print("\n=== GATE 1: cleanliness ===")
gate(text.count("—") == 0, "zero em dashes (rendered)", "found %d" % text.count("—"))
gate(sum(t.count("—") for t in content) == 0, "zero em dashes (content)")
arts = [a for a in ["�"] if a in blob]
# leftover extraction artifacts: standalone ! % $ # between spaces, or replacement char
leftover = re.findall(r"(?<=\s)[!#](?=\s)|�", blob)
gate(not leftover and not arts, "no leftover extraction artifacts", "found %d" % (len(leftover)+len(arts)))

print("\n=== GATE 2: six-S canon ===")
S = ["Sort","Straighten","Shine","Safety","Standardize","Sustain"]
runs = re.findall(r"(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)"
                  r"(?:\s*(?:,|and|then|/|>|to)\s*(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)){3,}", blob)
bad = []
for r in runs:
    seq = re.findall(r"Sort|Straighten|Shine|Safety|Standardize|Sustain", r)
    if len(seq) >= 5 and seq[:4] != ["Sort","Straighten","Shine","Safety"]:
        bad.append(r[:60])
gate(not bad, "Safety is the 4th S where six listed", "bad: %s" % bad[:2])

print("\n=== GATE 3: completeness ===")
gate(len(units) >= 12, "at least 12 units", "got %d" % len(units))
gate(len(sections) >= 20, "at least 20 sections", "got %d" % len(sections))
n_new = sum(1 for s in sections if s.get("is_new"))
gate(n_new >= 8, "at least 8 new gap sections", "got %d" % n_new)
noblocks = [s.get("title") for s in sections if not (s.get("blocks"))]
gate(not noblocks, "every section has blocks", "empty: %s" % noblocks[:4])
parts = set(s.get("part") for s in sections)
gate({"front","I","II"} <= parts, "front + Part I + Part II all present", "parts: %s" % parts)

print("\n=== GATE 4: block integrity ===")
VALID = {"p","h3","bullets","table","callout","stats","kv"}
badtype = collections.Counter()
tbl_bad = []
for s in sections:
    for b in (s.get("blocks") or []):
        t = b.get("type")
        if t not in VALID:
            badtype[t] += 1
        if t == "table":
            hs = b.get("headers") or []
            for r in (b.get("rows") or []):
                if len(r) != len(hs):
                    tbl_bad.append((s.get("title"), len(hs), len(r)))
gate(not badtype, "all block types valid", "bad: %s" % dict(badtype))
gate(not tbl_bad, "every table row matches header count", "mismatches %d: %s" % (len(tbl_bad), tbl_bad[:4]))

print("\n=== GATE 5: no fabricated figures stated as fact ===")
# any $ price or % rate should be near a hedge word somewhere in its section
HEDGE = re.compile(r"recommend|assumption|illustrative|to validate|estimate|target|propose|"
                   r"confirm|roughly|approximate|indicative|sketch|band", re.I)
risky = []
for s in sections:
    stext = " ".join(allstr(s))
    money_or_rate = re.findall(r"\$\s?\d|\b\d{1,3}\s?%|\bper month\b|\bper year\b|/mo\b", stext)
    if money_or_rate and not HEDGE.search(stext):
        risky.append((s.get("title"), money_or_rate[:3]))
gate(not risky, "price/rate sections carry a validate/assumption hedge",
     "unhedged: %s" % risky[:4])

print("\n=== GATE 6: HTML structure + navigation ===")
for tag in ["section","div","ul","li","table","thead","tbody","tr","nav","main","h2","p","aside"]:
    o = len(re.findall(r"<%s[\s>]" % tag, doc)); c = len(re.findall(r"</%s>" % tag, doc))
    if o != c: fails.append("unbalanced <%s> %d/%d" % (tag, o, c))
    print("  %-8s open %-4d close %-4d %s" % (tag, o, c, "OK" if o == c else "X"))
ids = re.findall(r'id="([^"]+)"', doc)
dupes = [i for i, c in collections.Counter(ids).items() if c > 1]
gate(not dupes, "no duplicate ids", "dupes: %s" % dupes[:5])
anchors = set(re.findall(r'href="#([^"]+)"', doc)) - {""}
gate(anchors <= set(ids), "all TOC anchors resolve", "dangling %d: %s" % (len(anchors-set(ids)), list(anchors-set(ids))[:5]))
gate('class="side"' in doc and 'tocgroup' in doc, "sidebar TOC present")

print("\n" + "=" * 58)
if fails:
    print("FAILED %d gate(s):" % len(fails))
    for f in fails: print("  - " + f)
    sys.exit(1)
print("ALL GATES PASSED  |  %d units, %d sections (%d new), %d KB"
      % (len(units), len(sections), n_new, len(doc)//1024))
