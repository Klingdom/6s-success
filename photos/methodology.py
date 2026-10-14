"""The micro zone methodology a photo is judged against.

Everything here is read from the same sources the website is built from, so
an analysis can only ever point at a step, a surface, an item or a root cause
that the published method actually contains:

    content/manual/source/content.json   zones, passes, shine_detail, diagnosis
    ops/zone-name-map.json               the public zone names and page slugs
    ops/root_causes.py                   the 17-cause vocabulary

The zone key is the public page slug, e.g. "entryway-the-landing-spot", the
same string as https://6s-success.com/zones/<slug>.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("SIXS_ROOT") or os.path.dirname(HERE)
CONTENT = os.path.join(ROOT, "content", "manual", "source", "content.json")
NAMES = os.path.join(ROOT, "ops", "zone-name-map.json")
CAUSES_PY = os.path.join(ROOT, "ops", "root_causes.py")

PASSES = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]


def _slug(t):
    return re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")


def _load_causes():
    spec = importlib.util.spec_from_file_location("sixs_root_causes", CAUSES_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {c["id"]: {"id": c["id"], "name": c.get("name", ""),
                      "meaning": c.get("meaning", ""),
                      "six_s": c.get("six_s", "")} for c in mod.CAUSES}


def _load():
    corpus = json.load(io.open(CONTENT, encoding="utf-8"))
    names = json.load(io.open(NAMES, encoding="utf-8"))
    zones = {}
    for r in corpus["rooms"]:
        room = r["room"]
        for z in r["zones"]:
            public = names.get("%s|%s" % (room, z["zone"]), z["zone"])
            zones["%s-%s" % (_slug(room), _slug(public))] = (room, public, z)
    return zones


ZONES = _load()
CAUSES = _load_causes()


def zone_slugs():
    return sorted(ZONES)


def method(slug):
    """The structured method for one zone, or None if the slug is unknown."""
    hit = ZONES.get(slug)
    if not hit:
        return None
    room, name, z = hit
    sd = z.get("shine_detail") or {}
    diag = z.get("diagnosis") or {}
    frictions = []
    used = set()
    for f in (diag.get("frictions") or []):
        branches = []
        for b in f.get("branches") or []:
            cid = b.get("cause")
            if cid in CAUSES:
                used.add(cid)
                branches.append({"answer": b.get("answer", ""), "cause": cid})
        frictions.append({"symptom": f.get("symptom", ""), "branches": branches})
    scope = z.get("sort_scope") or {}
    return {
        "zone": slug,
        "room": room,
        "name": name,
        "url": "https://6s-success.com/zones/%s" % slug,
        "purpose": z.get("purpose", ""),
        "done_looks_like": z.get("done_looks_like", ""),
        "common_items": list(z.get("common_items") or []),
        "belongs": list(scope.get("belongs") or []),
        "strays": list(scope.get("strays") or []),
        "passes": {k: (z.get("passes") or {}).get(k, "") for k in PASSES},
        "surfaces": [{"id": "s%d" % (i + 1), "surface": s.get("surface", ""),
                      "method": s.get("method", "")}
                     for i, s in enumerate(sd.get("surfaces") or [])
                     if s.get("surface") and s.get("method")],
        "supplies": list(sd.get("products_used") or []),
        "inspect": list(sd.get("inspect_as_you_clean") or []),
        "frictions": frictions,
        "causes": [CAUSES[c] for c in sorted(used)],
        "standard": (z.get("leave_behind") or {}).get("standard", ""),
        "trigger": (z.get("leave_behind") or {}).get("trigger", ""),
        "watch_for": z.get("watch_for") or [],
    }
