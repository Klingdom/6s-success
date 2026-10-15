"""ops/video_cleanalong.py: the pieces that decide what a viewer sees and
whether YouTube accepts the chapter list. Run: python ops/tests/test_video_cleanalong.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_argv_before = list(sys.argv)
import video_cleanalong as v
import video_zone as vz

fails = []
def check(name, cond):
    if not cond:
        fails.append(name)

# Importing this module must force video_zone wide regardless of import
# order, and must not do it by mutating sys.argv: a prior narrow import of
# video_zone in the same process used to leave WIDE/W/H wrong, silently,
# because video_zone only reads sys.argv once, at its own import time.
check("forces-wide", vz.WIDE is True and (vz.W, vz.H) == (1920, 1080))
check("argv-untouched", sys.argv == _argv_before)

# One action per sub-step, every word kept.
s = v.sentences("Lift the tray right out. Wipe the ring off, then wash the tray; dry it.")
check("split", s == ["Lift the tray right out.", "Wipe the ring off.", "Wash the tray.", "Dry it."])

# Chapters: first at 0:00, none under 10s, a short one folds into the next.
bs = [("", "", "A", 0), ("", "", "B", 0), ("", "", "C", 0)]
ch = v.chapters([(0, 7.4), (0, 14), (0, 30)], bs).splitlines()
check("first-at-zero", ch[0].startswith("0:00 "))
check("short-folded", ch == ["0:00 B", "0:22 C"])

# Before/after never renders from a missing or unlabelled pair.
check("no-pair", v.find_pair("no-such-zone-anywhere") is None)

# Every zone with shine_detail produces a step per surface and an end card.
rooms = vz.zones()
room, z = next((r, z) for r, z in rooms if z["zone"] == "Landing Zone")
b = v.beats(room, z)
steps = [x for x in b if x[2] and x[2].startswith("Step ")]
check("one-step-per-surface", len(steps) == len(z["shine_detail"]["surfaces"]))
check("no-before-after-without-pair", not any(x[2] == "Before and after" for x in b))

if fails:
    print("FAIL:", fails); sys.exit(1)
print("OK: video_cleanalong, 8/8 checks pass")
