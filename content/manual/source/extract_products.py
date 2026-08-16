# -*- coding: utf-8 -*-
"""Extract the product library workbook into JSON for the manual + appendices."""
import openpyxl, io, json, collections

F = (r"C:\Users\philk\Desktop\Process Kaizen\Process Kaizen\Work Folder\Nova Consulting"
     r"\06 - Lean Six Sigma Initiative\07 - 6S Materials\6S Environment\Master"
     r"\6S Success Home Edition\6S_Success_Master_Product_Library_v2_Micro_Zone_Integrated.xlsx")
SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"

wb = openpyxl.load_workbook(F, read_only=True, data_only=True)

def sheet(name):
    ws = wb[name]
    rows = [r for r in ws.iter_rows(values_only=True)]
    hdr = list(rows[0])
    out = []
    for r in rows[1:]:
        if all(c is None for c in r):
            continue
        out.append({hdr[i]: r[i] for i in range(len(hdr)) if hdr[i] is not None})
    return hdr, out

# ---- Product Master v2 ----
_, master = sheet("Product Master v2")
master = [m for m in master if m.get("Product ID")]
by_id = {m["Product ID"]: m for m in master}
print("products:", len(master))

# ---- Micro Zone Product Map: group by (room, zone) ----
_, mp = sheet("Micro Zone Product Map")
zone_products = collections.OrderedDict()
prod_zone_count = collections.Counter()
for r in mp:
    room = (r.get("Room") or "").strip()
    zone = (r.get("Micro Zone") or "").strip()
    pid = r.get("Product ID")
    if not (room and zone and pid):
        continue
    key = room + "||" + zone
    fam = by_id.get(pid, {}).get("Product Family", "")
    zone_products.setdefault(key, []).append({
        "id": pid,
        "name": r.get("Product Standard Name") or by_id.get(pid, {}).get("Product Standard Name", ""),
        "family": fam,
        "level": r.get("Recommendation Level"),
        "use": r.get("Use in This Micro Zone"),
        "phase": r.get("Primary 6S Use"),
        "qty": r.get("Standard Quantity"),
        "unit": r.get("Unit"),
        "safety": r.get("Safety Note"),
    })
    prod_zone_count[pid] += 1
print("zone->product groups:", len(zone_products))

# ---- Coverage ----
_, cov = sheet("Micro Zone Coverage")
coverage = {}
for r in cov:
    room = (r.get("Room") or "").strip()
    zone = (r.get("Micro Zone") or "").strip()
    if room and zone:
        coverage[room + "||" + zone] = r

# annotate each master product with how many zones use it
for m in master:
    m["_zone_count"] = prod_zone_count.get(m["Product ID"], 0)

io.open(SCRATCH + r"\products.json", "w", encoding="utf-8").write(
    json.dumps({"master": master}, indent=1, ensure_ascii=False, default=str))
io.open(SCRATCH + r"\zone_products.json", "w", encoding="utf-8").write(
    json.dumps(zone_products, indent=1, ensure_ascii=False, default=str))
io.open(SCRATCH + r"\coverage.json", "w", encoding="utf-8").write(
    json.dumps(coverage, indent=1, ensure_ascii=False, default=str))

# quick sanity
fam = collections.Counter(m["Product Family"] for m in master)
print("families:", dict(fam))
sample = list(zone_products.items())[1]
print("sample zone:", sample[0], "->", len(sample[1]), "products")
cleaning = [p for p in sample[1] if p["family"] in ("Cleaning Supplies", "Cleaning Tools")]
print("  cleaning items in that zone:", [p["name"][:30] for p in cleaning])
