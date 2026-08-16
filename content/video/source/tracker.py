# -*- coding: utf-8 -*-
"""Build the 114-row production tracker CSV (one row per zone video)."""
import json, io, csv, os

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\philk\Desktop\6S-Video-Production-Plan\6S-Micro-Zone-Reset-tracker.csv"

rooms = json.load(io.open(SCRATCH + r"\video.json", encoding="utf-8"))["rooms"]

cols = ["episode_code", "room_index", "zone_index", "room", "zone", "title",
        "runtime", "thumbnail_text", "shorts_count", "status_script",
        "status_shot", "status_edit", "status_published", "publish_order", "notes"]

with io.open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(cols)
    ep = 0
    for ri, r in enumerate(rooms, 1):
        for zi, v in enumerate(r.get("videos") or [], 1):
            ep += 1
            w.writerow([
                "MZ-%03d" % ep, "R%02d" % ri, "R%02d.%02d" % (ri, zi),
                r["room"], v.get("zone", ""), v.get("title", ""),
                v.get("runtime", ""), v.get("thumbnail_text", ""),
                len(v.get("segments") or []),
                "not started", "not started", "not started", "no",
                ep, "",
            ])
print("wrote:", OUT, "rows:", ep)
