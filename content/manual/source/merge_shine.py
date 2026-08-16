# -*- coding: utf-8 -*-
"""Pull the refine-stage shine detail from the workflow journal and merge into content.json."""
import json, io

WF = (r"C:\Users\philk\.claude\projects\C--Users-philk-6s-success"
      r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\subagents\workflows\wf_60082e3a-2be")
CONTENT = r"C:\Users\philk\Desktop\6S-Micro-Zone-Manual-Package\source\content.json"

content = json.load(io.open(CONTENT, encoding="utf-8"))
rooms = content["rooms"]
zoneset = {r["room"]: {z["zone"] for z in r["zones"]} for r in rooms}

def identify(val):
    zs = {z.get("zone", "") for z in (val.get("zones") or [])}
    best, sc = None, 0.0
    for room, s in zoneset.items():
        if not s:
            continue
        j = len(zs & s) / float(len(zs | s))
        if j > sc:
            best, sc = room, j
    return best, sc

by_room, n = {}, 0
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
    if not isinstance(val, dict) or not val.get("zones"):
        continue
    room, sc = identify(val)
    if not room or sc < 0.5:
        print("  ! unmatched (best %s %.2f)" % (room, sc)); continue
    by_room.setdefault(room, []).append(val)

print("result records:", n)
# build zone -> shine_detail (last result per room = refine)
merged = 0
missing_rooms = []
for r in rooms:
    got = by_room.get(r["room"]) or []
    if not got:
        missing_rooms.append(r["room"]); continue
    sd_by_zone = {z.get("zone"): z for z in (got[-1].get("zones") or [])}
    for z in r["zones"]:
        sd = sd_by_zone.get(z["zone"])
        if sd:
            z["shine_detail"] = {
                "shine_summary": sd.get("shine_summary"),
                "surfaces": sd.get("surfaces"),
                "products_used": sd.get("products_used"),
                "inspect_as_you_clean": sd.get("inspect_as_you_clean"),
            }
            merged += 1

if missing_rooms:
    print("  MISSING ROOMS:", missing_rooms)
print("zones merged with shine_detail: %d / 114" % merged)

# report any zone missing detail
gaps = [(r["room"], z["zone"]) for r in rooms for z in r["zones"] if not z.get("shine_detail")]
if gaps:
    print("  zones WITHOUT shine_detail:", gaps[:10], ("...and %d more" % (len(gaps)-10)) if len(gaps) > 10 else "")

SCRATCH_CONTENT = (r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success"
                   r"\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad\content.json")
blob = json.dumps(content, indent=1, ensure_ascii=False)
io.open(CONTENT, "w", encoding="utf-8").write(blob)          # authoritative package copy
io.open(SCRATCH_CONTENT, "w", encoding="utf-8").write(blob)  # copy the builder/validator read
print("updated content.json (package + scratch)")
