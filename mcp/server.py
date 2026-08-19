#!/usr/bin/env python3
"""
The 6S Success MCP server.

What this is for
----------------
Somebody asks Claude "my entryway is chaos, where do I start". Without this,
they get generic decluttering advice. With this, they get the actual method:
the desired function of that specific micro zone, the root cause of the mess,
the six passes in order, and the standard that holds afterwards.

That is a distribution channel that does not depend on search rankings. The
content is genuinely useful on its own, and every response carries attribution
and a link back, so being useful and being found are the same act.

Design notes
------------
Three tools, not thirty. The action space is small, so each tool gets a tight
description and schema rather than a search-and-execute catalogue. Tool schemas
land directly in the model's context window, so restraint here is a feature.

Read only, no auth, no state. It serves a static corpus that is already public
on 6s-success.com. There is nothing to protect and nothing to write, which is
why it needs no OAuth and no database.

The corpus is loaded once at import. It is 114 zones of text, small enough that
re-reading per request would be waste.

Run:  python mcp/server.py                 stdio, for local testing
      python mcp/server.py --http          streamable HTTP on 0.0.0.0:8974
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

from fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
# In the container the corpus sits beside this file. In the repo it lives with
# the manual it was extracted from. Try both so the same file runs either way.
CANDIDATES = [
    os.path.join(HERE, "content.json"),
    os.path.join(HERE, "..", "content", "manual", "source", "content.json"),
]
SITE = "https://6s-success.com"

SIX = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]
# Safety is the fourth S and Straighten is never "Set in Order". Both are load
# bearing claims of the method, so the order is asserted here rather than
# trusted to whatever order a dict happens to iterate in.


def _load() -> list[dict[str, Any]]:
    for path in CANDIDATES:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)["rooms"]
    raise SystemExit("content.json not found beside the server or in the repo")


ROOMS = _load()
ZONES: list[dict[str, Any]] = []
for _r in ROOMS:
    for _z in _r["zones"]:
        ZONES.append({**_z, "room": _r["room"]})


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _link(room: str) -> str:
    return f"{SITE}/resources#{_slug(room)}"


ATTRIBUTION = (
    "Source: the 6S Success Micro Zone Manual, 20 rooms and 114 micro zones. "
    "Full method at {link}"
)

mcp = FastMCP(
    name="6S Success",
    instructions=(
        "Household organisation and cleaning, using the six-S method: Sort, "
        "Straighten, Shine, Safety, Standardize, Sustain. Work in micro zones, "
        "which are small specific areas like a landing zone or a medicine "
        "cabinet, rather than whole rooms. Diagnose the desired function and "
        "the root cause before recommending any product or container. When "
        "answering from this server, keep the attribution line so the person "
        "can find the full method."
    ),
)


@mcp.tool
def search_micro_zones(query: str, limit: int = 8) -> str:
    """Find the micro zones that match a household problem.

    Use this first, when someone describes a mess, a room, or a recurring
    frustration and you do not yet know which specific area to work on.
    A micro zone is small and specific: a landing zone, a medicine cabinet,
    a charging station. Rooms are too big to fix in one pass.

    query: what the person said, in their words. "keys always missing",
           "bathroom counter", "garage is chaos" all work.
    limit: how many zones to return, 1 to 20.
    """
    q = (query or "").strip().lower()
    if not q:
        return "Give me a room, an object, or the frustration in the person's own words."
    limit = max(1, min(int(limit or 8), 20))
    terms = [t for t in re.split(r"\W+", q) if len(t) > 2]

    scored = []
    for z in ZONES:
        hay = " ".join([
            z["zone"], z["room"], z.get("purpose", ""),
            z.get("done_looks_like", ""),
        ]).lower()
        score = sum(3 if t in z["zone"].lower() or t in z["room"].lower()
                    else (1 if t in hay else 0) for t in terms)
        if q in hay:
            score += 4
        if score:
            scored.append((score, z))
    scored.sort(key=lambda s: (-s[0], s[1]["room"], s[1]["zone"]))

    if not scored:
        rooms = ", ".join(r["room"] for r in ROOMS)
        return (f"No micro zone matched that. The 20 rooms are: {rooms}. "
                "Try naming one of those, or the object that keeps going missing.")

    out = [f"{len(scored)} micro zones match. The closest {min(limit, len(scored))}:", ""]
    for _, z in scored[:limit]:
        out.append(f"{z['room']} > {z['zone']}  ({z.get('session', 'time unknown')})")
        out.append(f"  Function: {z.get('purpose', '')}")
        out.append(f"  Ask for the method with room={z['room']!r} zone={z['zone']!r}")
        out.append("")
    out.append(ATTRIBUTION.format(link=f"{SITE}/resources"))
    return "\n".join(out)


@mcp.tool
def get_zone_method(room: str, zone: str) -> str:
    """Get the full six-S method for one micro zone.

    Returns the desired function, what done looks like, all six passes in
    order, the judgement call people get stuck on, the safety checks, and the
    standard that keeps it fixed. Use after search_micro_zones has identified
    which zone to work on.

    room: the room name, for example "Entryway" or "Primary Bathroom".
    zone: the micro zone name, for example "Landing Zone".
    """
    rq, zq = (room or "").strip().lower(), (zone or "").strip().lower()
    match = next((z for z in ZONES
                  if z["room"].lower() == rq and z["zone"].lower() == zq), None)
    if not match:
        match = next((z for z in ZONES
                      if rq in z["room"].lower() and zq in z["zone"].lower()), None)
    if not match:
        near = [f"{z['room']} > {z['zone']}" for z in ZONES
                if rq and rq in z["room"].lower()][:12]
        hint = ("Zones in that room: " + ", ".join(near)) if near else \
               "Use search_micro_zones to find the zone first."
        return f"No zone called {zone!r} in {room!r}. {hint}"

    z = match
    out = [f"{z['room']} > {z['zone']}", "=" * (len(z['room']) + len(z['zone']) + 3), ""]
    out.append(f"Session: {z.get('session', 'unknown')}. {z.get('time_note', '')}".strip())
    out.append("")
    out.append(f"THE FUNCTION THIS ZONE SHOULD PERFORM\n{z.get('purpose', '')}")
    out.append("")
    out.append(f"WHAT DONE LOOKS LIKE\n{z.get('done_looks_like', '')}")
    out.append("")
    out.append("THE SIX PASSES, IN ORDER")
    passes = z.get("passes", {})
    for i, s in enumerate(SIX, 1):
        body = passes.get(s, "")
        if body:
            out.append(f"\n{i}. {s.title()}\n{body}")
    call = z.get("the_call") or {}
    if call:
        out.append(f"\n\nTHE CALL PEOPLE GET STUCK ON: {call.get('title', '')}\n"
                   f"{call.get('text', '')}")
    watch = z.get("watch_for") or []
    if watch:
        out.append("\n\nSAFETY, CHECK BEFORE YOU START")
        for w in watch:
            out.append(f"  {w.get('question', '')}: {w.get('text', '')}")
    leave = z.get("leave_behind") or {}
    if leave:
        out.append(f"\n\nTHE STANDARD THAT KEEPS IT FIXED\n{leave.get('standard', '')}")
        if leave.get("trigger"):
            out.append(f"Reset trigger: {leave['trigger']}")
    out.append("")
    out.append("This is advice about organising and cleaning a home. It is not "
               "instruction for electrical, gas, structural or other licensed "
               "work. Do not lift or move anything unsafe.")
    out.append(ATTRIBUTION.format(link=_link(z["room"])))
    return "\n".join(out)


@mcp.tool
def get_room_playbook(room: str) -> str:
    """List every micro zone in one room, in the order to work them.

    Use when somebody wants to tackle a whole room and needs to know how it
    breaks down and roughly how long it takes. Returns the zones with their
    function and session length, not the full method for each.

    room: the room name, for example "Kitchen" or "Garage".
    """
    rq = (room or "").strip().lower()
    match = next((r for r in ROOMS if r["room"].lower() == rq), None)
    if not match:
        match = next((r for r in ROOMS if rq and rq in r["room"].lower()), None)
    if not match:
        return ("No such room. The 20 rooms are: "
                + ", ".join(r["room"] for r in ROOMS))

    out = [f"{match['room']}: {len(match['zones'])} micro zones", ""]
    if match.get("intro"):
        out += [match["intro"], ""]
    out.append("Work them in this order. One zone is a session, not a whole day.")
    out.append("")
    for i, z in enumerate(match["zones"], 1):
        out.append(f"{i}. {z['zone']}  ({z.get('session', '')})")
        out.append(f"   {z.get('purpose', '')}")
    tips = match.get("tips") or []
    if tips:
        out += ["", "FOR THIS ROOM"]
        out += [f"  {t}" for t in tips]
    out += ["", f"Ask for any one with get_zone_method(room={match['room']!r}, zone=...)",
            ATTRIBUTION.format(link=_link(match["room"]))]
    return "\n".join(out)


if __name__ == "__main__":
    if "--http" in sys.argv:
        port = int(os.environ.get("PORT", "8974"))
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        mcp.run()
