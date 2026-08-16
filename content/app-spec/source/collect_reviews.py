# -*- coding: utf-8 -*-
"""Collect the 7 discipline reviews from the workflow journal."""
import json, io

WF = (r"C:\Users\philk\.claude\projects\C--Users-philk-6s-success"
      r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\subagents\workflows\wf_af7cc6f1-409")
SCRATCH = (r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success"
           r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad")
ORDER = ["Product Management","Software Quality Assurance","Front-End Engineering",
         "Back-End Engineering","Marketing","Customer Success","Support"]

seen, n = [], 0
for line in io.open(WF + r"\journal.jsonl", encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    if rec.get("type") != "result":
        continue
    n += 1
    val = rec.get("result")
    if isinstance(val, str):
        try: val = json.loads(val)
        except Exception: continue
    if isinstance(val, dict) and val.get("findings"):
        seen.append(val)

# de-dup by role, keep first
byrole = {}
for v in seen:
    byrole.setdefault(v.get("role","?"), v)
reviews = list(byrole.values())
# order roughly by ORDER
def rank(v):
    r = v.get("role","")
    for i, o in enumerate(ORDER):
        if o.lower() in r.lower() or r.lower() in o.lower():
            return i
    return 99
reviews.sort(key=rank)

print("result records:", n, "reviews:", len(reviews))
for v in reviews:
    fs = v.get("findings") or []
    themes = {}
    for f in fs: themes[f.get("theme")] = themes.get(f.get("theme"),0)+1
    print("  %-26s %d findings %s" % (v.get("role","?"), len(fs), themes))
tot = sum(len(v.get("findings") or []) for v in reviews)
print("total findings:", tot)

io.open(SCRATCH + r"\reviews.json", "w", encoding="utf-8").write(
    json.dumps({"reviews": reviews}, indent=1, ensure_ascii=False))
print("wrote reviews.json")
