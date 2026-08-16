# -*- coding: utf-8 -*-
"""Pull refine-stage video plans out of the workflow journal, in book order.

Same approach as collect.py: the journal carries no labels, so rooms are
identified by matching their zone-name sets against the manual content, and the
LAST result per room wins (refine always completes after its draft).
"""
import json, io

WF = (r"C:\Users\philk\.claude\projects\C--Users-philk-6s-success"
      r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\subagents\workflows\wf_8c47301f-735")
SCRATCH = (r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success"
           r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad")
MANUAL = r"C:\Users\philk\Desktop\6S-Micro-Zone-Manual-Package\source\content.json"

man = json.load(io.open(MANUAL, encoding="utf-8"))["rooms"]
ORDER = [r["room"] for r in man]
zoneset = {r["room"]: {z["zone"] for z in r["zones"]} for r in man}

def identify(val):
    zs = {v.get("zone", "") for v in (val.get("videos") or [])}
    best, score = None, 0.0
    for room, s in zoneset.items():
        if not s:
            continue
        j = len(zs & s) / float(len(zs | s))
        if j > score:
            best, score = room, j
    return best, score

by_room, n_res = {}, 0
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
    if not isinstance(val, dict) or not val.get("videos"):
        continue
    room, score = identify(val)
    if not room or score < 0.5:
        print("  ! unmatched (best %s, %.2f)" % (room, score)); continue
    val["room"] = room
    by_room.setdefault(room, []).append(val)

print("result records: %d" % n_res)
rooms = []
for room in ORDER:
    got = by_room.get(room) or []
    if not got:
        print("  MISSING:", room); continue
    rooms.append(got[-1])
    if len(got) != 2:
        print("  ? %s produced %d results (expected 2)" % (room, len(got)))

print()
for r in rooms:
    exp, got = len(zoneset[r["room"]]), len(r.get("videos") or [])
    print("  %-18s %2d videos%s" % (r["room"], got, "" if got == exp else "  <-- expected %d" % exp))

nv = sum(len(r.get("videos") or []) for r in rooms)
ns = sum(len(v.get("segments") or []) for r in rooms for v in (r.get("videos") or []))
print("\nrooms: %d   videos: %d   shorts: %d" % (len(rooms), nv, ns))

io.open(SCRATCH + r"\video.json", "w", encoding="utf-8").write(
    json.dumps({"rooms": rooms}, indent=1, ensure_ascii=False))
print("wrote video.json")
