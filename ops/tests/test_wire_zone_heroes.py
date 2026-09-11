#!/usr/bin/env python3
"""
Prove a withdrawn zone-hero verdict can actually pull an already-wired
figure off a live page when no source PNGs exist in the environment.

Found 2026-09-11, reading ops/wire_zone_heroes.py cold against a live
content-accuracy defect (the "kitchen--primary-prep-counter" hero shows a
counter covered in bowls, boards and a vase of flowers, directly
contradicting the zone's own done_looks_like: "holding only the board, the
knife block or strip, and the salt... no fruit bowl... anywhere on the
surface"). Withdrawing that verdict should pull the picture from the live
page. It did not.

main()'s own PULLED sweep, which removes a figure from a page whose hero
verdict is no longer "ok", only runs in the `have > 0` branch: when
build/heroes/zones/ holds real source PNGs, which on every checkout but
Phil's own machine it never does (gitignored on purpose). Every other
environment takes the `fallback_wire()` path instead, which only ever
guarded against RE-adding a withdrawn hero to a page that did not already
have one ("stale += 1; continue"). It never checked whether an earlier run,
before the withdrawal, had already wired the page, so a verdict withdrawn
from any environment but Phil's own machine had no way to ever reach an
already-published page. That defeats the exact gate this module's own
docstring describes ("no image ships unless somebody has looked at it and
said so") for the one action ("un-approve it") every other environment is
actually able to take.

Run:  python ops/tests/test_wire_zone_heroes.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import wire_zone_heroes as W                                      # noqa: E402


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def read(path):
    return io.open(path, encoding="utf-8").read()


FIGURE_HTML = (
    '\n<figure class="zone-hero" id="zone-hero">'
    '<img src="../assets/zones/demo-zone-lg.jpg" alt="">'
    "<figcaption>An illustration of the finished state, not a photograph "
    "of a real home.</figcaption></figure>\n"
)

PAGE_WITH_HERO = (
    "<html><body><p>Intro text.</p>\n" + FIGURE_HTML.strip() +
    "\n<h2>Instructions</h2></body></html>"
)


def main():
    fails = []
    tmp = tempfile.mkdtemp(prefix="wire_zone_heroes_test_")
    real_site, real_heroes = W.SITE, W.HEROES
    real_fallback, real_verdicts = W.FALLBACK, W.VERDICTS
    try:
        site = os.path.join(tmp, "site")
        heroes = os.path.join(tmp, "heroes")  # left empty: no source PNGs
        os.makedirs(os.path.join(site, "zones"))
        os.makedirs(heroes)
        W.SITE, W.HEROES = site, heroes
        W.FALLBACK = os.path.join(tmp, "hero-fallback.json")
        W.VERDICTS = os.path.join(tmp, "hero-verdicts.json")

        page = os.path.join(site, "zones", "demo-zone.html")
        write(page, PAGE_WITH_HERO)
        json.dump({"demo-zone.html": {"stem": "demo-zone",
                                       "figure_html": FIGURE_HTML}},
                  io.open(W.FALLBACK, "w", encoding="utf-8"))

        # Case 1: verdict withdrawn ("no"), page already carries the figure.
        # --check must report the pull without touching the file.
        json.dump({"demo-zone": {"verdict": "no", "sha": "irrelevant"}},
                  io.open(W.VERDICTS, "w", encoding="utf-8"))
        before = read(page)
        pulled_dry = W.fallback_wire(False)
        if read(page) != before:
            fails.append("--check (apply_it=False) modified the page")

        # --apply must actually remove the figure block, leaving the rest
        # of the page untouched.
        W.fallback_wire(True)
        after = read(page)
        if 'id="zone-hero"' in after:
            fails.append("a withdrawn hero verdict left the figure on the "
                          "live page after --apply")
        if "<p>Intro text.</p>" not in after or "<h2>Instructions</h2>" not in after:
            fails.append("pulling the figure damaged surrounding page content")

        # Case 2: running again is idempotent (nothing left to pull).
        again = read(page)
        W.fallback_wire(True)
        if read(page) != again:
            fails.append("a second fallback_wire() run on an already-pulled "
                          "page changed it")

        # Case 3: regression guard. A page whose verdict is still "ok" must
        # be left alone (this is the pre-existing, already-correct path).
        page2 = os.path.join(site, "zones", "ok-zone.html")
        write(page2, PAGE_WITH_HERO)
        fb = json.load(io.open(W.FALLBACK, encoding="utf-8"))
        fb["ok-zone.html"] = {"stem": "ok-zone", "figure_html": FIGURE_HTML}
        json.dump(fb, io.open(W.FALLBACK, "w", encoding="utf-8"))
        verdicts = json.load(io.open(W.VERDICTS, encoding="utf-8"))
        verdicts["ok-zone"] = {"verdict": "ok", "sha": "irrelevant"}
        json.dump(verdicts, io.open(W.VERDICTS, "w", encoding="utf-8"))
        W.fallback_wire(True)
        if 'id="zone-hero"' not in read(page2):
            fails.append("an approved hero was removed from a page it "
                          "belongs on")

        # Case 4: a page with NO figure and a withdrawn verdict is a no-op,
        # not an error (nothing to pull).
        page3 = os.path.join(site, "zones", "never-had-one.html")
        write(page3, "<html><body><p>Intro.</p><h2>Instructions</h2></body></html>")
        fb = json.load(io.open(W.FALLBACK, encoding="utf-8"))
        fb["never-had-one.html"] = {"stem": "never-had-one",
                                     "figure_html": FIGURE_HTML}
        json.dump(fb, io.open(W.FALLBACK, "w", encoding="utf-8"))
        verdicts = json.load(io.open(W.VERDICTS, encoding="utf-8"))
        verdicts["never-had-one"] = {"verdict": "no", "sha": "x"}
        json.dump(verdicts, io.open(W.VERDICTS, "w", encoding="utf-8"))
        before3 = read(page3)
        W.fallback_wire(True)
        if read(page3) != before3:
            fails.append("a page that never had a figure was changed by "
                          "a withdrawn verdict for its stem")

    finally:
        W.SITE, W.HEROES = real_site, real_heroes
        W.FALLBACK, W.VERDICTS = real_fallback, real_verdicts
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: 4 case(s), a withdrawn verdict now pulls an already-wired "
          "hero even with no source PNGs present, idempotent, approved "
          "heroes and figure-less pages both left alone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
