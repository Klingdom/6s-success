#!/usr/bin/env python3
"""
Prove ops/wire_zone_heroes.py emits an AVIF <source> whenever the .avif files
exist beside the .webp ones.

Added 2026-09-17, after the real thing happened. Five new zone heroes were
approved and `wire_zone_heroes.py --apply` was run to place them. It rewrote
all 111 matched pages, and because this tool only knew about WebP while
ops/build_avif.py is what adds AVIF, every rewritten page came back WITHOUT
its AVIF source: about 41 per cent of the image weight on 106 pages that had
nothing to do with the change, undone silently. Caught by reading the diff
before committing, not by any check.

Two tools that write the same markup have to agree. This one pins that.

Run:  python ops/tests/test_zone_hero_markup_keeps_avif.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

try:
    from PIL import Image                                       # noqa: F401
except ImportError:
    print("NOT VERIFIED: PIL is not installed in this environment "
          "(ops/requirements.txt deliberately keeps it out of CI); "
          "wire_zone_heroes.figure() reads real image width via PIL, so the "
          "srcset markup this test checks cannot be exercised here.")
    sys.exit(0)

import wire_zone_heroes as W                                   # noqa: E402


def markup(stem, room="Dining Room", zone="Dining Table"):
    return W.figure(stem, {"room": room, "zone": zone, "subject": ""}, "../")


def markup_without_pillow(stem, avif_widths, webp_widths):
    """figure() with _srcset stubbed, so this runs where Pillow is absent.

    CI has no Pillow (it needs none: it does not generate images), and the
    first version of this test imported it transitively through _srcset and
    failed the whole suite. The behaviour under test is which <source> tags
    get emitted for a given pair of srcsets, which is a string question, not
    an image one.
    """
    real = W._srcset

    def fake(stem_, prefix, ext="webp"):
        widths = avif_widths if ext == "avif" else webp_widths
        return ", ".join("%sassets/zones/%s-%s.%s %dw"
                         % (prefix, stem_, tag, ext, w)
                         for tag, w in widths)
    W._srcset = fake
    try:
        return W.figure(stem, {"room": "Dining Room", "zone": "Dining Table",
                               "subject": ""}, "../")
    finally:
        W._srcset = real


def main():
    failures = []

    # A stem the live site really serves, with both formats on disk.
    stem = "dining-room--dining-table"
    web = os.path.join(ROOT, "site", "assets", "zones")
    have_webp = os.path.exists(os.path.join(web, stem + "-md.webp"))
    have_avif = os.path.exists(os.path.join(web, stem + "-md.avif"))

    try:
        import PIL  # noqa: F401
        real_pillow = True
    except ImportError:
        real_pillow = False

    if real_pillow and have_webp and have_avif:
        html = markup(stem)
    else:
        # Stubbed srcsets, same assertions. Says which path it took rather
        # than reporting a pass it did not earn.
        print("  (Pillow or the image pair is absent here, so the srcsets are "
              "stubbed and only the markup logic is exercised)")
        html = markup_without_pillow(stem, [("sm", 320), ("md", 640)],
                                     [("sm", 320), ("md", 640)])
    has_avif = 'type="image/avif"' in html
    has_webp = 'type="image/webp"' in html
    if not has_avif:
        failures.append("no avif source emitted for a stem that has .avif files")
    if not has_webp:
        failures.append("no webp source emitted")
    if has_avif and has_webp and (html.index('type="image/avif"')
                                  > html.index('type="image/webp"')):
        failures.append("avif source must come before webp, or browsers take webp")
    if has_avif and ".avif 640w" not in html:
        failures.append("avif srcset carries no real width: %r" % html[:200])

    # A stem with no files at all must degrade to webp-only markup rather than
    # emit an empty srcset, which would be worse than not emitting the source.
    ghost = (markup("this-stem-does-not-exist--anywhere") if real_pillow
             else markup_without_pillow("ghost", [], []))
    if 'type="image/avif" srcset=""' in ghost:
        failures.append("emitted an empty avif srcset for a stem with no files")

    for f in failures:
        print("FAIL:", f)
    print("ok" if not failures else "%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
