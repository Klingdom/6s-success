# -*- coding: utf-8 -*-
"""Collect refine-stage spec units from the workflow journal, in unit order."""
import json, io

WF = (r"C:\Users\philk\.claude\projects\C--Users-philk-6s-success"
      r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\subagents\workflows\wf_604176bd-f5f")
SCRATCH = (r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success"
           r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad")
ORDER = ["U1","U2","U3","U4","U5","U6","U7","U8","U9","U10","U11","U12"]

by_unit, n = {}, 0
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
    if not isinstance(val, dict) or not val.get("sections"):
        continue
    uid = val.get("unit")
    if uid:
        by_unit.setdefault(uid, []).append(val)

print("result records:", n)
units = []
for uid in ORDER:
    got = by_unit.get(uid) or []
    if not got:
        print("  MISSING:", uid); continue
    units.append(got[-1])            # last = refine
    if len(got) != 2:
        print("  ? %s produced %d (expected 2)" % (uid, len(got)))

# any units returned but not in ORDER
for uid, got in by_unit.items():
    if uid not in ORDER:
        print("  extra unit:", uid); units.append(got[-1])

for u in units:
    secs = u.get("sections") or []
    print("  %-4s %d sections: %s" % (u.get("unit"), len(secs),
          ", ".join((s.get("title") or "?")[:22] for s in secs)))
tot = sum(len(u.get("sections") or []) for u in units)
print("units: %d  sections: %d" % (len(units), tot))

io.open(SCRATCH + r"\spec.json", "w", encoding="utf-8").write(
    json.dumps({"units": units, "date": "2026-07-22"}, indent=1, ensure_ascii=False))
print("wrote spec.json")
