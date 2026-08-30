#!/usr/bin/env python3
"""
Render card front HTML to PNG with a headless Chromium, no new dependencies.

WHY THIS WAY
------------
The card fronts are typographic objects: a display serif, a tracked out sans,
a real type scale. Placing that by hand in a bitmap library produces something
that looks like a spreadsheet, so they are laid out in HTML and CSS and
photographed by a browser.

Playwright, Selenium and the rest are not installed and none of them are worth
adding for this. Microsoft Edge is Chromium and it ships on the machine, so it
renders these with the same engine the site is tested in, at exact card size,
for nothing.

WHAT IT GUARANTEES
------------------
Fonts are given time to arrive before the shot, because a card rendered in
Times instead of Fraunces looks like a different product and the failure is
silent. Every output is then checked: right dimensions, not blank, and not a
single flat colour, which is what a page that failed to load looks like.

Run:  python ops/render_cards.py --all
      python ops/render_cards.py --card EM-005
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "build", "card-fronts")
OUT = os.path.join(ROOT, "build", "cards-rendered")

CARD_W, CARD_H = 750, 1050

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome",
                 "Application", "chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def browser() -> str:
    for p in CANDIDATES:
        if p and os.path.exists(p):
            return p
    raise SystemExit(
        "no Chromium browser found. Chrome or Edge is needed to render "
        "these; both use the same engine and either is fine.")


def shoot(exe: str, html_path: str, png_path: str) -> None:
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([
            exe,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--user-data-dir={profile}",
            f"--window-size={CARD_W},{CARD_H}",
            # Fonts come from the network. Without a time budget the shot can
            # land before they arrive and the card renders in Times, which is
            # a silent failure that looks like a different product.
            "--virtual-time-budget=9000",
            f"--screenshot={png_path}",
            "file:///" + html_path.replace(os.sep, "/"),
        ], capture_output=True, timeout=90)


def verify(png: str) -> tuple:
    if not os.path.exists(png):
        return False, "no file was written"
    try:
        from PIL import Image
        import numpy as np
        im = Image.open(png)
        im.load()
    except Exception as e:                                    # noqa: BLE001
        return False, f"will not open ({type(e).__name__})"
    if im.size != (CARD_W, CARD_H):
        return False, f"{im.size} rather than {(CARD_W, CARD_H)}"
    a = np.asarray(im.convert("L"), dtype=np.float32)
    if a.std() < 8:
        return False, (f"standard deviation {a.std():.1f}, the page did not "
                       f"render")
    return True, ""


def main() -> int:
    exe = browser()
    print(f"  renderer  {os.path.basename(exe)}")

    files = sorted(glob.glob(os.path.join(SRC, "*.html")))
    if "--card" in sys.argv:
        code = sys.argv[sys.argv.index("--card") + 1].upper()
        files = [f for f in files if os.path.basename(f).startswith(code)]
    if not files:
        print(f"  no card HTML in build/card-fronts. Run "
              f"ops/build_card_template.py first.")
        return 1

    os.makedirs(OUT, exist_ok=True)
    ok, bad = [], []
    for f in files:
        code = os.path.splitext(os.path.basename(f))[0]
        # Backs are named EE-001-back.html and were coming out as
        # EE-001-back-front.png, which is not a name anything can pair up.
        png = os.path.join(OUT, f"{code}.png" if code.endswith("-back")
                           else f"{code}-front.png")
        if os.path.exists(png):
            os.remove(png)
        shoot(exe, os.path.abspath(f), png)
        good, why = verify(png)
        if good:
            ok.append((code, os.path.getsize(png)))
        else:
            bad.append((code, why))
            if os.path.exists(png):
                os.remove(png)

    for code, size in ok:
        print(f"    ok    {code}  {size//1024} KB")
    for code, why in bad:
        print(f"    FAIL  {code}  {why}")

    print(f"\n  rendered {len(ok)} of {len(files)} to build/cards-rendered/")
    print(f"  {CARD_W}x{CARD_H}, which is 2.5 by 3.5 inches at 300 dpi")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
