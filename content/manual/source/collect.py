# -*- coding: utf-8 -*-
"""Pull refine-stage results out of the workflow journal, in book order.

The journal has no labels, so rooms are identified by matching their zone-name
set against the source inventory. Each room appears twice (draft, then refine);
the pipeline guarantees refine completes after its draft, so the LAST result
wins.
"""
import json, io

WF = (r"C:\Users\philk\.claude\projects\C--Users-philk-6s-success"
      r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\subagents\workflows\wf_f7d87f10-8e7")
SCRATCH = (r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success"
           r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad")

src = json.load(io.open(SCRATCH + r"\zones.json", encoding="utf-8"))
ORDER = [r["room"] for r in src]
# zone-name set -> room
zoneset = {r["room"]: {z["zone"] for z in r["zones"]} for r in src}

def identify(val):
    zs = {z.get("zone", "") for z in (val.get("zones") or [])}
    best, score = None, 0.0
    for room, s in zoneset.items():
        if not s:
            continue
        j = len(zs & s) / float(len(zs | s))
        if j > score:
            best, score = room, j
    return best, score

order_seen = {}
by_room = {}
n_res = 0
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
    if not isinstance(val, dict) or not val.get("zones"):
        continue
    room, score = identify(val)
    if not room or score < 0.5:
        print("  ! unmatched result (best %s, %.2f)" % (room, score))
        continue
    val["room"] = room
    by_room.setdefault(room, []).append(val)

print("result records: %d" % n_res)
rooms = []
for room in ORDER:
    got = by_room.get(room) or []
    if not got:
        print("  MISSING:", room); continue
    rooms.append(got[-1])          # last = refine
    if len(got) != 2:
        print("  ? %s produced %d results (expected 2)" % (room, len(got)))

print()
for r in rooms:
    exp = len(zoneset[r["room"]])
    got = len(r.get("zones") or [])
    flag = "" if got == exp else "  <-- expected %d" % exp
    print("  %-18s %2d zones%s" % (r["room"], got, flag))

tot = sum(len(r.get("zones") or []) for r in rooms)
print("\nrooms: %d   zones: %d" % (len(rooms), tot))

io.open(SCRATCH + r"\content.json", "w", encoding="utf-8").write(
    json.dumps({"rooms": rooms}, indent=1, ensure_ascii=False))
print("wrote content.json")
