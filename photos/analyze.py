"""Look at a photo of one micro zone and say what to do next, in the method's own terms.

The model is allowed to OBSERVE. It is not allowed to invent the method. Its
reply is checked against the zone's published methodology (methodology.py):

- every step must name one of the six passes, and may point at a surface by
  the zone's own surface id; the "how" attached to that step is then the
  published method for that surface, not the model's wording;
- every root cause must be one of the 17 in ops/root_causes.py;
- after-photo checks are only made against the zone's own done-looks-like
  standard.

Anything outside that is dropped, and the response says how much was dropped,
so a reader can see when the model wandered.

Providers: Anthropic (ANTHROPIC_API_KEY). Without a key, analyze() returns the
zone's method with "image_analyzed": false. It never pretends to have looked.
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request

try:
    from . import methodology as M
except ImportError:                                       # run as a script
    import methodology as M

MODEL = os.environ.get("PHOTOS_MODEL", "claude-sonnet-4-5")
API = "https://api.anthropic.com/v1/messages"
STATUSES = {"belongs", "stray", "unclear"}
CHECK = {"met", "not_met", "unclear"}


class AnalysisError(Exception):
    pass


def _clip(s, n=400):
    return str(s or "").strip()[:n]


def prompt(meth, mode):
    m = {k: meth[k] for k in ("room", "name", "purpose", "done_looks_like", "common_items",
                               "belongs", "strays", "passes", "surfaces", "inspect",
                               "frictions", "causes", "standard")}
    task = {
        "before": "This is a BEFORE photo. Say what is in the zone, what does not belong, "
                  "which frictions you can actually see, their likely root causes, and the "
                  "next steps in pass order.",
        "after": "This is an AFTER photo. Check it against done_looks_like item by item, "
                 "then give only the steps still needed.",
        "compare": "The first image is BEFORE, the second is AFTER. Say what changed, check the "
                   "AFTER image against done_looks_like item by item, and give only the steps "
                   "still needed.",
    }[mode]
    return (
        "You are reviewing a household photo for the 6S Success method. You must work inside "
        "the method for ONE micro zone, given below as JSON. Be kind and specific; ordinary "
        "household mess is not a moral failure.\n\n" + task + "\n\n"
        "Rules: only describe what is visible. If the photo does not show this zone, say so in "
        "zone_visible and keep everything else short. Use only pass names from passes, only "
        "surface ids from surfaces, only cause ids from causes. Never give cleaning chemistry "
        "or safety advice beyond what the method states; if something looks unsafe, describe "
        "it in safety and say a professional may be needed.\n\n"
        "Reply with ONLY a JSON object with these keys:\n"
        '{"zone_visible": "yes|no|unsure", "summary": str, '
        '"items_seen": [{"item": str, "status": "belongs|stray|unclear"}], '
        '"frictions": [{"observed": str, "causes": [cause id]}], '
        '"steps": [{"pass": pass name, "surface_id": str or null, "action": str, "because": str}], '
        '"safety": [str], '
        '"after_check": [{"standard": str, "status": "met|not_met|unclear", "evidence": str}], '
        '"confidence": "low|medium|high"}\n\n'
        "METHOD:\n" + json.dumps(m, ensure_ascii=False))


def _call_anthropic(key, images, text):
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                            "data": base64.b64encode(b).decode("ascii")}}
               for b in images]
    content.append({"type": "text", "text": text})
    body = json.dumps({"model": MODEL, "max_tokens": 2000,
                       "messages": [{"role": "user", "content": content}]}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "x-api-key": key, "anthropic-version": "2023-06-01",
        "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise AnalysisError("vision provider returned HTTP %d" % e.code)
    except (urllib.error.URLError, TimeoutError) as e:
        raise AnalysisError("vision provider unreachable: %s" % type(e).__name__)
    txt = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text")
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        raise AnalysisError("vision provider reply was not JSON")
    try:
        return json.loads(m.group(0))
    except ValueError:
        raise AnalysisError("vision provider reply was not valid JSON")


def ground(raw, meth, mode):
    """Keep only what the method contains. Count what was dropped."""
    dropped = 0
    surf = {s["id"]: s for s in meth["surfaces"]}
    causes = M.CAUSES
    zone_causes = {c["id"] for c in meth["causes"]}
    out = {"zone_visible": raw.get("zone_visible") if raw.get("zone_visible") in ("yes", "no", "unsure") else "unsure",
           "summary": _clip(raw.get("summary"), 600)}

    items = []
    for it in (raw.get("items_seen") or [])[:30]:
        if not isinstance(it, dict) or not it.get("item"):
            dropped += 1
            continue
        st = it.get("status") if it.get("status") in STATUSES else "unclear"
        items.append({"item": _clip(it["item"], 120), "status": st})
    out["items_seen"] = items

    fr = []
    for f in (raw.get("frictions") or [])[:10]:
        if not isinstance(f, dict) or not f.get("observed"):
            dropped += 1
            continue
        cs = []
        for c in f.get("causes") or []:
            if c in causes:
                cs.append({"id": c, "name": causes[c]["name"], "meaning": causes[c]["meaning"],
                           "in_this_zones_diagnosis": c in zone_causes})
            else:
                dropped += 1
        fr.append({"observed": _clip(f["observed"], 300), "causes": cs})
    out["frictions"] = fr

    order = {p: i for i, p in enumerate(M.PASSES)}
    steps = []
    for s in (raw.get("steps") or [])[:20]:
        p = str((s or {}).get("pass", "")).lower()
        if p not in order:
            dropped += 1
            continue
        sid = s.get("surface_id")
        step = {"pass": p, "action": _clip(s.get("action"), 300), "because": _clip(s.get("because"), 300)}
        if sid:
            if sid in surf:
                step["surface"] = surf[sid]["surface"]
                step["method"] = surf[sid]["method"]       # the published how, not the model's
            else:
                dropped += 1
        steps.append(step)
    steps.sort(key=lambda s: order[s["pass"]])
    out["steps"] = steps
    out["safety"] = [_clip(x, 300) for x in (raw.get("safety") or [])[:6] if x]

    checks = []
    if mode in ("after", "compare"):
        for c in (raw.get("after_check") or [])[:12]:
            if not isinstance(c, dict) or c.get("status") not in CHECK or not c.get("standard"):
                dropped += 1
                continue
            checks.append({"standard": _clip(c["standard"], 200), "status": c["status"],
                           "evidence": _clip(c.get("evidence"), 300)})
    out["after_check"] = checks
    out["confidence"] = raw.get("confidence") if raw.get("confidence") in ("low", "medium", "high") else "low"
    out["dropped_as_outside_method"] = dropped
    return out


def method_only(meth, mode):
    """No image was analyzed. Return the zone's own steps, labeled as such."""
    steps = [{"pass": "sort", "action": "Take everything out, then return only what belongs.",
              "because": "Belongs here: %s. Strays in: %s." % ("; ".join(meth["belongs"]) or "see the zone page",
                                                               "; ".join(meth["strays"]) or "see the zone page")}]
    steps += [{"pass": "shine", "surface": s["surface"], "method": s["method"],
               "action": "Clean %s." % s["surface"], "because": "Published method for this surface."}
              for s in meth["surfaces"]]
    return {"zone_visible": "unknown", "summary": "No image was analyzed: no vision provider is "
            "configured. These are the zone's published steps.", "items_seen": [], "frictions": [],
            "steps": steps, "safety": list(meth["inspect"][:4]), "after_check": [],
            "confidence": "none", "dropped_as_outside_method": 0}


def analyze(zone, images, mode="before", key=None, call=None):
    """images: list of JPEG bytes (1, or 2 for compare). call: test hook."""
    meth = M.method(zone)
    if meth is None:
        raise AnalysisError("unknown zone")
    if mode not in ("before", "after", "compare"):
        raise AnalysisError("mode must be before, after or compare")
    if mode == "compare" and len(images) != 2:
        raise AnalysisError("compare needs a before and an after photo")
    key = key if key is not None else os.environ.get("ANTHROPIC_API_KEY", "")
    base = {"zone": zone, "zone_name": meth["name"], "room": meth["room"], "mode": mode,
            "zone_url": meth["url"], "standard": meth["standard"], "trigger": meth["trigger"]}
    if not key and call is None:
        return dict(base, image_analyzed=False, provider=None, **method_only(meth, mode))
    raw = (call or (lambda imgs, txt: _call_anthropic(key, imgs, txt)))(images, prompt(meth, mode))
    return dict(base, image_analyzed=True, provider="anthropic:%s" % MODEL,
                **ground(raw if isinstance(raw, dict) else {}, meth, mode))
