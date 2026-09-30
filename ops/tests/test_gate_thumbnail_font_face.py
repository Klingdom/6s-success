#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_thumbnail_font_face() catches a YouTube
thumbnail rendered with no working @font-face rule.

Real shape found 2026-09-30, cold-reading ops/build_thumbnails.py (a
2026-09-25 ledger entry). html_for() inserted vz.FONTS, a bare filesystem
directory path such as "/home/user/6s-success/site/assets/fonts", as the
first line inside <style>, the exact spot every sibling generator
(video_zone.py, build_social_pins.py) puts a real @font-face rule. No
@font-face was ever emitted in any of the 114 already-built thumbnails, so
"font-family: Inter" on .room/.zone never actually loaded Inter; every
render silently used whatever system-ui/sans-serif font the host happened
to have installed, invisible to every prior check because the PNG still
rendered, still had the right dimensions, and still passed
gate_dashboard_thumbnails_live's count.

This test swaps in a fake ops.build_thumbnails module carrying each shape
(the real fixed generator, the old bug, a partial fix that declares
@font-face but not the weight actually used) and runs the real gate
function against each, rather than re-deriving the check's own logic.

Run:  python ops/tests/test_gate_thumbnail_font_face.py
"""
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight  # noqa: E402

FONTS = "/fake/site/assets/fonts"


class _VZ:
    FONTS = FONTS


def _fake_module(html: str) -> types.ModuleType:
    m = types.ModuleType("build_thumbnails")
    m.html_for = lambda room, zone, vz: html
    return m


def _run(html: str):
    old = sys.modules.get("build_thumbnails")
    sys.modules["build_thumbnails"] = _fake_module(html)
    old_vz = sys.modules.get("video_zone")
    fake_vz = types.ModuleType("video_zone")
    fake_vz.FONTS = FONTS
    sys.modules["video_zone"] = fake_vz
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_thumbnail_font_face()
        return list(preflight.FAIL)
    finally:
        if old is not None:
            sys.modules["build_thumbnails"] = old
        else:
            sys.modules.pop("build_thumbnails", None)
        if old_vz is not None:
            sys.modules["video_zone"] = old_vz
        else:
            sys.modules.pop("video_zone", None)


REAL_BUG_HTML = (
    "<!doctype html><style>\n%s\n*{margin:0}\n"
    ".room{font-weight:800}.zone{font-weight:800}</style><body></body>" % FONTS
)

FIXED_HTML = (
    "<!doctype html><style>\n"
    "@font-face{font-family:Inter;src:url('file:///%s/Inter-800-normal.woff2')"
    "format('woff2');font-weight:800}\n*{margin:0}\n"
    ".room{font-weight:800}.zone{font-weight:800}</style><body></body>" % FONTS
)

NO_FONT_FACE_AT_ALL = (
    "<!doctype html><style>*{margin:0}"
    ".room{font-weight:800}.zone{font-weight:800}</style><body></body>"
)

WRONG_WEIGHT_HTML = (
    "<!doctype html><style>\n"
    "@font-face{font-family:Inter;src:url('file:///%s/Inter-700-normal.woff2')"
    "format('woff2');font-weight:700}\n*{margin:0}\n"
    ".room{font-weight:800}.zone{font-weight:800}</style><body></body>" % FONTS
)


def main() -> int:
    fails = []

    r = _run(FIXED_HTML)
    if r:
        fails.append("a correctly fixed thumbnail was wrongly failed: %r" % (r,))

    r = _run(REAL_BUG_HTML)
    if not r or not any("raw fonts directory path" in m for _, m in r):
        fails.append("the real 2026-09-30 bug shape (bare path in <style>) "
                     "was not caught by name: %r" % (r,))

    r = _run(NO_FONT_FACE_AT_ALL)
    if not r or not any("no @font-face rule" in m for _, m in r):
        fails.append("a thumbnail with no @font-face at all was not caught: %r" % (r,))

    r = _run(WRONG_WEIGHT_HTML)
    if not r or not any("must synthesize" in m for _, m in r):
        fails.append("an @font-face declaring the wrong weight (700, not "
                     "the 800 actually used) was not caught: %r" % (r,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_thumbnail_font_face, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
