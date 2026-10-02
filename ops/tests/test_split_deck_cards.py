#!/usr/bin/env python3
"""
Prove ops/split_deck_cards.py's main() returns a nonzero exit code when
every source sheet fails verification, instead of silently reporting 0.

Found 2026-10-02, second-pass cold-reading the 2026-09-26-dated ops/*.py
tier (ops/cold_read_ledger.py) per CLAUDE.md step 5d. Both return paths at
the end of main() (the --check "nothing written" branch and the final
--apply branch) returned 0 unconditionally, regardless of how many cards
came out usable. A run where every sheet failed the ratio/blank check
still reported success: a CI step or script chain keying off this exit
code would see "0 usable cards, exit 0" as clean. Fixed by failing when
there were source sheets to process and not one of them produced a usable
card.

This sandbox has neither PIL nor numpy, so `find_gutter()`/`trim()` (real
matrix maths) are monkeypatched out, and a minimal fake `PIL.Image` plus a
tiny `numpy` stub (just enough for the ink-density check's `< 242` /
`.mean()`) are injected, the same technique test_render_cards.py already
uses for this sandbox's missing image libraries.

Run:  python ops/tests/test_split_deck_cards.py
"""
import glob
import io
import os
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))


class _FakeImage:
    """A bare-bones stand-in whose crop() always yields a panel with a
    ratio far from TARGET_RATIO, so the real ratio check in main() marks
    every panel bad without needing real pixel maths."""

    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height

    def convert(self, _mode):
        return self

    def crop(self, _box):
        return _FakeImage(width=10, height=10)   # ratio 1.0, far from 0.714


def _install_fakes():
    pil_pkg = types.ModuleType("PIL")
    pil_image = types.ModuleType("PIL.Image")
    pil_image.open = lambda _path: _FakeImage(width=100, height=100)
    pil_pkg.Image = pil_image
    sys.modules["PIL"] = pil_pkg
    sys.modules["PIL.Image"] = pil_image

    np_mod = types.ModuleType("numpy")
    np_mod.float32 = float

    class _Arr:
        def __lt__(self, _other):
            return self

        def mean(self):
            return 0.5   # plenty of ink: never trips the "blank" branch

    np_mod.asarray = lambda *_a, **_k: _Arr()
    sys.modules["numpy"] = np_mod


def _write_fake_sheet(dir_path, name="EM-003-Entryway-Test.png"):
    p = os.path.join(dir_path, name)
    io.open(p, "wb").write(b"\x89PNG\r\n")   # content is never read; Image.open is faked
    return p


def main() -> int:
    _install_fakes()
    import split_deck_cards as S                                 # noqa: E402

    orig_decks = dict(S.DECKS)
    orig_find_gutter, orig_trim = S.find_gutter, S.trim
    S.find_gutter = lambda _g: 50
    S.trim = lambda im: im
    fails = []

    try:
        with tempfile.TemporaryDirectory() as src:
            S.DECKS["entryway"] = src

            # 1. One source sheet, every panel fails the ratio check: 0
            #    usable cards must produce a nonzero exit code.
            _write_fake_sheet(src)
            rc = S.main(apply_it=False, deck="entryway")
            if rc == 0:
                fails.append("--check with every sheet failing verification "
                              "returned 0 (the real historical defect)")

            # 2. Empty source directory: nothing to process is not the same
            #    defect and must stay 0, not newly misclassified as a failure.
            for f in glob.glob(os.path.join(src, "*")):
                os.remove(f)
            rc = S.main(apply_it=False, deck="entryway")
            if rc != 0:
                fails.append("an empty source directory (nothing to "
                              "process) was wrongly flagged as a failure: "
                              "rc=%r" % (rc,))
    finally:
        S.DECKS.clear()
        S.DECKS.update(orig_decks)
        S.find_gutter, S.trim = orig_find_gutter, orig_trim
        sys.modules.pop("PIL", None)
        sys.modules.pop("PIL.Image", None)
        sys.modules.pop("numpy", None)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: split_deck_cards.py zero-usable-cards exit code, 2/2 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
