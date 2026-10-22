"""Assembly, checks and output for ops/build_room_maps.py.

Kept apart from the room layouts so each file stays readable: the layouts are
long coordinate lists, and the rules a finished drawing must pass are short
and should be easy to find.
"""
import io
import json
import os
import re
import xml.etree.ElementTree as ET

from room_map_draw import PAPER, INK, SLATE, SERIF, SANS, esc, rect

PLAN_SCALE = 0.94
CX, TOP = 500, 70


def to_canvas(x, y):
    """Where a point drawn in plan coordinates lands after the set-back."""
    return CX + (x - CX) * PLAN_SCALE, TOP + (y - TOP) * PLAN_SCALE


NUM_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
             6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def corpus(path):
    data = json.load(io.open(path, encoding="utf-8"))
    return {r["room"]: [z.get("zone") or z.get("name") for z in r["zones"]]
            for r in data["rooms"]}


def build(spec, labels_cls):
    fn, start, noun, names, strap, kind = spec
    L = labels_cls(names, start)
    body, detail, height = fn(L)
    # The plan is drawn at full size and then set back to PLAN_SCALE about the
    # canvas centre, so the margin labels always have a clear gutter between
    # them and the walls. Leader ends are mapped the same way in Labels.add.
    body = ('<g transform="translate(%s %s) scale(%s) translate(%s %s)">'
            % (CX, TOP, PLAN_SCALE, -CX, -TOP) + body + "</g>")
    n = len(names)
    title = "The %s, drawn as its %s zones" % (noun, NUM_WORDS[n])
    aria = ("A warm %s of a %s with its %s zones marked and named. "
            % (kind, noun, NUM_WORDS[n]) + detail + " The zones, numbered in "
            "the order this page lists them: "
            + "; ".join("%d, %s" % (i + 1, s.lower())
                        for i, s in enumerate(names))
            + ". Start with %s." % names[start].lower())
    svg = ('<svg viewBox="0 0 1000 %d" role="img" aria-label="%s">'
           % (height, esc(aria))
           + rect(0, 0, 1000, height, fill=PAPER, stroke="none", sw=0)
           + '<text x="500" y="44" text-anchor="middle" font-family="%s" '
             'font-size="22" fill="%s">%s</text>' % (SERIF, INK, esc(title))
           + body + L.svg()
           + '<text x="500" y="%d" text-anchor="middle" font-family="%s" '
             'font-size="17" fill="%s">%s</text>'
             % (height - 22, SANS, SLATE, esc(strap))
           + "</svg>")
    return svg, L


def problems(spec, want, svg, L):
    names = spec[3]
    out = []
    if len(names) != want:
        out.append("%d labels for %d corpus zones" % (len(names), want))
    if L.placed != set(range(want)):
        out.append("zones never labelled on the drawing: %s"
                   % sorted(set(range(want)) - L.placed))
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        out.append("not well-formed XML: %s" % exc)
    if re.search(r'\bid="', svg):
        out.append("carries an id")
    if re.search(r'(?:href|xlink:href)="[^"#]', svg):
        out.append("references something outside itself")
    if re.search(r'<svg[^>]*\swidth="', svg):
        out.append("carries a fixed width")
    if re.search(r"photograph|\bphoto\b", svg, re.I):
        out.append("calls itself a photograph")
    m = re.search(r'aria-label="[^"]*? with its ([a-z]+) zones', svg)
    if not m or m.group(1) != NUM_WORDS[want]:
        out.append("accessible name does not state %d zones" % want)
    for x, w in re.findall(r'<rect x="(-?[\d.]+)" y="[\d.]+" '
                           r'width="([\d.]+)" height="34"', svg):
        if float(x) < 0 or float(x) + float(w) > 1000:
            out.append("a label runs off the canvas at x=%s" % x)
    return out


def write_preview(path, manifest):
    html = ["<!doctype html><meta charset=utf-8><body style='margin:0;"
            "background:#ddd'>"]
    for room, e in manifest.items():
        html.append("<div style='width:1000px;margin:0 0 12px'>%s</div>"
                    % e["svg"])
    io.open(path, "w", encoding="utf-8").write("".join(html))
