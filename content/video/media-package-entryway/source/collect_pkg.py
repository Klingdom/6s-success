# -*- coding: utf-8 -*-
"""Collect refine-stage YouTube metadata from the workflow journal, in zone order."""
import json, io

WF = (r"C:\Users\philk\.claude\projects\C--Users-philk-6s-success"
      r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\subagents\workflows\wf_4b8762c7-473")
SCRATCH = (r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success"
           r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad")

ORDER = ['Landing Zone','Coat and Outerwear Zone','Shoe and Boot Zone',
         'Entry Console or Bench','Door, Mat, and Immediate Floor']

def k(z): return (z or "").strip().lower()

by_zone, n = {}, 0
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
    if not isinstance(val, dict) or "shorts" not in val:
        continue
    by_zone.setdefault(k(val.get("zone")), []).append(val)

print("result records:", n)
meta = []
for z in ORDER:
    got = by_zone.get(k(z)) or []
    if not got:
        print("  MISSING:", z); continue
    got[-1]["zone"] = z
    meta.append(got[-1])
    if len(got) != 2:
        print("  ? %s produced %d (expected 2)" % (z, len(got)))

for m in meta:
    print("  %-30s %d shorts, %d tags" % (m["zone"], len(m.get("shorts") or []), len(m.get("tags") or [])))
print("total shorts:", sum(len(m.get("shorts") or []) for m in meta))

io.open(SCRATCH + r"\package.json", "w", encoding="utf-8").write(
    json.dumps({"zones": meta}, indent=1, ensure_ascii=False))
print("wrote package.json")
