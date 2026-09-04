#!/usr/bin/env python3
"""
Render card HTML to PNG with a headless Chromium, and then check the card.

WHY THIS WAY
------------
The cards are typographic objects: a display serif, a tracked-out sans, a real
type scale. Placing that by hand in a bitmap library produces something that
looks like a spreadsheet, so they are laid out in HTML and CSS and photographed
by a browser. Playwright and the rest are not installed and none of them are
worth adding. Edge is Chromium and ships on the machine; the sandbox has its
own Chromium at /opt/pw-browsers/chromium. ops/browser.py finds either.

WHAT IT NOW GUARANTEES, AND WHY THAT LIST GREW
----------------------------------------------
The old verification was: the file exists, it is the right size, and it is not
one flat colour. Every card in the deck passed that check while carrying body
copy at 2.5pt, because a page of 2.5pt type has plenty of variance and exactly
the right dimensions. The check was green and the product was unreadable.

So the browser is now asked what it actually did. Each card's HTML carries a
measuring script that walks the rendered card, records the smallest computed
font size of any element holding text, and records any element whose content
overflows its box. This tool reads that back with --dump-dom and fails the card
when:

  * the smallest rendered glyph is under the 7pt floor in ops/card_spec.py, or
  * anything overflows its box, which on a printed card means clipped words.

A card that fails is not written. The type report is printed in points, because
points are the thing a person holding the card experiences and pixels are not.

Run:  python ops/render_cards.py --all
      python ops/render_cards.py --card EE-001
      python ops/render_cards.py --all --bleed
      python ops/render_cards.py --measure       (type report only, no PNGs)
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import card_spec as S                                          # noqa: E402

SRC = os.path.join(ROOT, "build", "card-fronts")
OUT = os.path.join(ROOT, "build", "cards-rendered")

CARD_W, CARD_H = S.CARD_W, S.CARD_H


def browser() -> tuple:
    import browser as B
    found = B.find_browser()
    if not found:
        raise SystemExit(
            "no Chromium browser found. Chrome, Edge or the sandbox's own "
            "Chromium is needed to render these.")
    return found


def _run(exe: str, extra: list, args: list, url: str, capture: bool):
    with tempfile.TemporaryDirectory() as profile:
        return subprocess.run(
            [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", f"--user-data-dir={profile}",
             # Fonts are self-hosted now, but layout and the measuring script
             # still need a moment. Without a time budget the shot can land
             # before either finishes, which is a silent failure.
             "--virtual-time-budget=8000", *extra, *args, url],
            capture_output=True, timeout=120)


def shoot(exe, extra, html_path, png_path, w, h) -> None:
    _run(exe, extra, [f"--window-size={w},{h}", f"--screenshot={png_path}"],
         "file:///" + os.path.abspath(html_path).replace(os.sep, "/"), False)


FIT_RE = re.compile(r"FITREPORT (.*?) ENDFIT", re.S)


def measure(exe, extra, html_path, w, h) -> dict | None:
    """What the browser actually rendered, read back out of the DOM."""
    r = _run(exe, extra, [f"--window-size={w},{h}", "--dump-dom"],
             "file:///" + os.path.abspath(html_path).replace(os.sep, "/"), True)
    dom = (r.stdout or b"").decode("utf-8", "replace")
    # The last match, not the first. --dump-dom returns the whole document,
    # which includes the measuring script's own source, and the first hit was
    # the literal "FITREPORT '+JSON.stringify(out)+' ENDFIT" inside it. That
    # cost a debugging round: the tool reported "the page did not finish
    # loading" for a page that had loaded and measured itself correctly.
    for raw in reversed(FIT_RE.findall(dom)):
        try:
            return json.loads(raw.replace("&quot;", '"'))
        except Exception:                                      # noqa: BLE001
            continue
    return None


def verify_png(png: str, w: int, h: int) -> tuple:
    if not os.path.exists(png):
        return False, "no file was written"
    try:
        from PIL import Image
        import numpy as np
        im = Image.open(png)
        im.load()
    except Exception as e:                                     # noqa: BLE001
        return False, f"will not open ({type(e).__name__})"
    if im.size != (w, h):
        return False, f"{im.size} rather than {(w, h)}"
    a = np.asarray(im.convert("L"), dtype=np.float32)
    if a.std() < 8:
        return False, f"standard deviation {a.std():.1f}, the page did not render"
    return True, ""


def main() -> int:
    exe, extra = browser()
    print(f"  renderer  {os.path.basename(exe)}")

    bleed = "--bleed" in sys.argv
    src = SRC + ("-bleed" if bleed else "")
    out = OUT + ("-bleed" if bleed else "")
    w, h = (S.BLEED_W, S.BLEED_H) if bleed else (S.CARD_W, S.CARD_H)

    files = sorted(glob.glob(os.path.join(src, "*.html")))
    if "--card" in sys.argv:
        code = sys.argv[sys.argv.index("--card") + 1].upper()
        files = [f for f in files if os.path.basename(f).startswith(code)]
    if not files:
        print(f"  no card HTML in {os.path.relpath(src, ROOT)}. Run "
              f"ops/build_card_template.py first.")
        return 1

    measure_only = "--measure" in sys.argv
    os.makedirs(out, exist_ok=True)
    ok, bad, sizes = [], [], {}
    floor_px = S.pt(S.FLOOR_PT)

    for f in files:
        code = os.path.splitext(os.path.basename(f))[0]
        fit = measure(exe, extra, f, w, h)
        if fit is None:
            bad.append((code, "the measuring script did not report; the page "
                              "did not finish loading"))
            continue
        for role, px in fit.get("sizes", []):
            sizes.setdefault(role, px)
            sizes[role] = min(sizes[role], px)
        problems = []
        if fit.get("min", 0) < floor_px - 0.01:
            problems.append(f"smallest glyph {fit['min']/S.PX_PER_PT:.2f}pt, "
                            f"under the {S.FLOOR_PT}pt floor")
        for role, sh, ch in fit.get("over", []):
            problems.append(
                role if sh == ch == 0 else
                f"'{role}' overflows its box by {sh - ch}px "
                f"({(sh - ch) / S.PX_PER_PT:.1f}pt of clipped text)")
        if problems:
            bad.append((code, "; ".join(problems)))
            continue
        if measure_only:
            ok.append((code, 0))
            continue
        png = os.path.join(out, f"{code}.png" if code.endswith("-back")
                           else f"{code}-front.png")
        if os.path.exists(png):
            os.remove(png)
        shoot(exe, extra, f, png, w, h)
        good, why = verify_png(png, w, h)
        if good:
            ok.append((code, os.path.getsize(png)))
        else:
            bad.append((code, why))
            if os.path.exists(png):
                os.remove(png)

    if sizes:
        print(f"\n  MEASURED TYPE, read off the rendered card, not the CSS")
        print(f"  {'role':34} {'px':>8} {'pt @300dpi':>11}")
        for role, px in sorted(sizes.items(), key=lambda x: -x[1]):
            flag = "  <-- UNDER FLOOR" if px < floor_px - 0.01 else ""
            print(f"  {role[:34]:34} {px:8.1f} "
                  f"{px/S.PX_PER_PT:11.2f}{flag}")
        print(f"  floor {S.FLOOR_PT}pt = {floor_px:.1f}px, "
              f"body minimum {S.BODY_MIN_PT}pt")

    print()
    for code, why in bad:
        print(f"    FAIL  {code}  {why}")
    if not measure_only:
        print(f"\n  rendered {len(ok)} of {len(files)} to "
              f"{os.path.relpath(out, ROOT).replace(os.sep, '/')}/")
    else:
        print(f"\n  measured {len(ok)} of {len(files)} clean")
    print(f"  {w}x{h}, which is {w/S.DPI:.2f} x {h/S.DPI:.2f} inches at "
          f"{S.DPI} dpi" + ("  [bleed sheet]" if bleed else "  [trim]"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
