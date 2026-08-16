import re, json, html, io, sys

SRC = r"C:\Users\philk\Desktop\Process Kaizen\Process Kaizen\Work Folder\Nova Consulting\06 - Lean Six Sigma Initiative\07 - 6S Materials\6S Environment\Master\6S Success Home Edition\6S Home Micro Zone SOP Field Manual v2.html"
doc = io.open(SRC, encoding="utf-8").read()

def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).replace("—", "-").strip()

rooms = []
# split on room sections
parts = re.split(r'<section class="room" id="([^"]+)">', doc)
for i in range(1, len(parts), 2):
    rid, body = parts[i], parts[i+1]
    name = clean(re.search(r"<h2>(.*?)</h2>", body, re.S).group(1))
    brief_m = re.search(r'<p class="brief">(.*?)</p>', body, re.S)
    brief = clean(brief_m.group(1)) if brief_m else ""
    tips = [clean(t) for t in re.findall(r"<div class='tip [^']*'>(.*?)</div>", body, re.S)]
    zones = []
    zblocks = re.split(r'<article class="zone-block">', body)[1:]
    for zb in zblocks:
        zname = clean(re.search(r"<h3>(.*?)</h3>", zb, re.S).group(1))
        mono = clean(re.search(r'<span class="mono">(.*?)</span>', zb, re.S).group(1))
        grid = re.findall(r"<div[^>]*><b>(.*?)</b>(.*?)</div>", zb, re.S)
        g = {clean(k): clean(v).lstrip("- ").strip() for k, v in grid}
        cue_m = re.search(r"<div class='cue'><b>Expert cue</b>(.*?)</div>", zb, re.S)
        cue = clean(cue_m.group(1)) if cue_m else ""
        # hazards live in the Safety row "known concerns: X."
        haz_m = re.search(r"known concerns: (.*?)\.</td>", zb, re.S)
        haz = clean(haz_m.group(1)) if haz_m else ""
        # total time from mono e.g. "Zone 1 of 7 - 60 min"
        t_m = re.search(r"(\d+)\s*min", mono)
        zones.append({
            "zone": zname,
            "v2_minutes": int(t_m.group(1)) if t_m else None,
            "primary_function": g.get("Primary function", ""),
            "completed_state": g.get("Completed state", ""),
            "items_storage": g.get("Common items & storage", ""),
            "hazards": haz,
            "expert_cue": cue,
        })
    rooms.append({"id": rid, "room": name, "brief": brief, "tips": tips, "zones": zones})

OUT = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad\zones.json"
io.open(OUT, "w", encoding="utf-8").write(json.dumps(rooms, indent=1, ensure_ascii=False))
print("rooms:", len(rooms), "zones:", sum(len(r["zones"]) for r in rooms))
for r in rooms:
    print(f'  {r["room"]}: {len(r["zones"])} zones')
