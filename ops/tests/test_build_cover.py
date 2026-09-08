#!/usr/bin/env python3
"""
Prove the cover generator's font fallback cannot silently regress.

2026-09-02: ops/build_cover.py only ever found a real face on Windows, so
every other machine fell through to PIL's tiny fixed-size default font and
produced an illegible cover that still "wrote" a PNG and exited clean. The
script was fixed to refuse rather than ship that, not to stop the regression
from happening, only to stop it shipping. 2026-09-03: it now also finds a
real, metric-compatible face via the Liberation fonts this sandbox already
has installed, which is what actually lets the cover render (and be
verified) outside Windows. Two things have to both be true:

    a real name it cannot find anywhere must still trip the refusal;
    a real name it can only find via Liberation must not trip it, and must
    return an actual scalable font, not the tiny bitmap default.

Only the second is new here. The first is what stops this fix from quietly
turning into the exact bug it replaces the next time a font list changes.

Run:  python ops/tests/test_build_cover.py
"""
import os
import sys
from unittest import SkipTest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

try:
    from PIL import ImageFont
except ImportError:
    print("NOT VERIFIED: PIL is not installed in this environment "
          "(ops/requirements.txt deliberately keeps it out of CI); "
          "cannot exercise build_cover.py's font loader.")
    sys.exit(0)

import build_cover as BC                                       # noqa: E402

# build_cover.py imports PIL lazily, only inside its own `if __name__ ==
# "__main__":` block (preflight.py's run_gate() docstring explains why: a
# top-level PIL import used to crash gate_cover_author_current on any
# machine without Pillow and take every earlier gate down with it). font()
# still references the bare name `ImageFont` from that block's own import,
# so calling it from outside a real `python build_cover.py` run needs the
# same name bound first, exactly as the real run would have by the time it
# reaches font(). This is that precondition, not a workaround for a bug.
BC.ImageFont = ImageFont


def _liberation_installed() -> bool:
    """Is there an actual Liberation face on THIS machine?"""
    return any(os.path.exists(os.path.join(BC.LIBERATION, v))
               for v in BC.LINUX_FALLBACK.values())


def test_every_display_name_has_a_liberation_mapping():
    """The invariant the fallback test only ASSERTS on a machine that has the
    fonts. This one holds everywhere, so it is the part that actually guards
    the regression.

    The check below reads "a real Liberation face exists for every DISPLAY_B
    name", but on a machine with no Liberation directory it was testing the
    machine rather than the code, and it failed on Windows for a reason that
    had nothing to do with build_cover.py. Whether every display name has a
    substitute DEFINED is the thing a code change can break, and it can be
    answered without a single font file on disk.
    """
    for tier in (BC.DISPLAY_B, BC.DISPLAY_I, BC.DISPLAY_R):
        assert any(n in BC.LINUX_FALLBACK for n in tier), (
            "no name in %r has a Liberation substitute, so on any machine "
            "without the Windows fonts this tier falls straight through to "
            "PIL's tiny bitmap default and the cover ships illegible" % (tier,))


def test_liberation_fallback_used_when_windows_absent():
    if not _liberation_installed():
        raise SkipTest(
            "no Liberation faces under %s, so the fallback cannot be exercised "
            "here. This is a statement about this machine, not about the code: "
            "test_every_display_name_has_a_liberation_mapping covers what a "
            "code change can actually break." % BC.LIBERATION)
    BC.WINDOWS_FONTS = os.path.join(ROOT, "no-such-windows-fonts-here")
    BC._MISSING_FONT = False
    f = BC.font(BC.DISPLAY_B, 40)
    assert not BC._MISSING_FONT, (
        "a real Liberation face exists for every DISPLAY_B name; the "
        "fallback should have found one instead of giving up")
    # Pillow 10.1+'s load_default() is itself a real, if tiny, FreeTypeFont,
    # so isinstance() can no longer tell "found a real face" apart from
    # "gave up" the way it could when this generator's refusal was written.
    # Two things load_default() never does: honour the requested size (it
    # is fixed at 10 regardless of what is asked for, the actual
    # caption-sized-text symptom this whole fix exists to prevent), and
    # load from a real file path on disk (it reads from an in-memory
    # BytesIO instead).
    assert f.size == 40, (
        "font() ignored the requested size, the exact 'succeeded but "
        f"illegible' shape this test exists to catch (got {f.size})")
    assert isinstance(getattr(f, "path", None), str), (
        "font() did not load from a real file on disk, meaning it fell "
        "back to PIL's built-in default rather than a Liberation face")
    assert "liberation" in f.path.lower(), (
        f"expected a Liberation face, got {f.path}")


def test_refusal_still_trips_with_no_face_anywhere():
    BC.WINDOWS_FONTS = os.path.join(ROOT, "no-such-windows-fonts-here")
    BC._MISSING_FONT = False
    BC.font(["no-such-font-anywhere.ttf"], 40)
    assert BC._MISSING_FONT, (
        "a name with neither a Windows face nor a Liberation fallback must "
        "still trip the missing-font flag, or the __main__ refusal at the "
        "bottom of build_cover.py can never fire")


if __name__ == "__main__":
    real_windows_fonts = BC.WINDOWS_FONTS
    skipped = []
    try:
        test_every_display_name_has_a_liberation_mapping()
        try:
            test_liberation_fallback_used_when_windows_absent()
        except SkipTest as e:
            skipped.append(str(e))
        test_refusal_still_trips_with_no_face_anywhere()
    finally:
        BC.WINDOWS_FONTS = real_windows_fonts
        BC._MISSING_FONT = False
    # A skip is reported, never swallowed. A run that could not look must not
    # print the same line as a run that looked and passed.
    if skipped:
        print("ok  build_cover's font loader still refuses when nothing at "
              "all is available, and every display tier has a Liberation "
              "substitute defined.")
        print("    NOT VERIFIED HERE: " + skipped[0])
    else:
        print("ok  build_cover's font loader finds the Liberation fallback "
              "and still refuses when nothing at all is available")
