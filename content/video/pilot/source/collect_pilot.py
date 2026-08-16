# -*- coding: utf-8 -*-
"""Collect refine-stage Entryway scripts from the workflow journal, in zone order."""
import json, io

WF = (r"C:\Users\philk\.claude\projects\C--Users-philk-6s-success"
      r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\subagents\workflows\wf_ee691799-f78")
SCRATCH = (r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success"
           r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad")

ORDER = ['Landing Zone','Coat and Outerwear Zone','Shoe and Boot Zone',
         'Entry Console or Bench','Door, Mat, and Immediate Floor']

def zkey(v):
    return (v.get("zone") or "").strip().lower()

by_zone, n_res = {}, 0
for line in io.open(WF + r"\journal.jsonl", encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    if rec.get("type") != "result":
        continue
    n_res += 1
    val = rec.get("result")
    if isinstance(val, str):
        try:
            val = json.loads(val)
        except Exception:
            continue
    if not isinstance(val, dict) or not val.get("segments"):
        continue
    by_zone.setdefault(zkey(val), []).append(val)

print("result records: %d" % n_res)
zones = []
for z in ORDER:
    got = by_zone.get(z.lower()) or []
    if not got:
        print("  MISSING:", z); continue
    zones.append(got[-1])       # last = refine
    if len(got) != 2:
        print("  ? %s produced %d results (expected 2)" % (z, len(got)))

for v in zones:
    segs = [s.get("step") for s in (v.get("segments") or [])]
    print("  %-28s %d segments" % (v.get("zone"), len(segs)))

io.open(SCRATCH + r"\pilot.json", "w", encoding="utf-8").write(
    json.dumps({"zones": zones}, indent=1, ensure_ascii=False))
print("wrote pilot.json  (%d zones)" % len(zones))
