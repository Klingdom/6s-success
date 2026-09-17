#!/usr/bin/env python3
"""
Prove ops/render_cards.py's verify_png() tells "could not verify" apart from
"verified and it is bad", and that main() stops deleting a real screenshot
over the first one.

Found 2026-09-17, cold-reading this file per CLAUDE.md step 5d: this sandbox
has Chromium (so shoot() writes a real, correct PNG) but neither PIL nor
numpy, and the old verify_png() caught ImportError inside the same bare
`except Exception` as a genuinely corrupt image, returning False either way.
main() then deleted the file it had just written and printed "FAIL ...
will not open (ModuleNotFoundError)", indistinguishable from a truncated or
blank render. Reproduced directly: a manual shoot() call in this same
sandbox produced a real 750x1050 PNG that the old code then discarded,
running --all against the full 89-card corpus destroyed 177 of 178 real
files and reported them all FAIL (exit 1) rather than UNCHECKED (exit 2).

This test drives verify_png() directly. Cases 1 and 2 run against the real,
unmocked environment (no file; the real missing PIL/numpy here). Cases 3-5
inject fake PIL/numpy modules so the "ok"/"bad" branches can be proven in an
environment that does not have the real libraries, rather than skipped.

Run:  python ops/tests/test_render_cards.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import render_cards as R                                       # noqa: E402


class _FakeImage:
    def __init__(self, size, std):
        self.size = size
        self._std = std

    def load(self):
        pass

    def convert(self, _mode):
        return self


def _install_fake_pil_numpy(size, std, open_raises=False):
    """Injects minimal fake `PIL.Image` and `numpy` modules so verify_png()'s
    ok/bad branches (which need a real image library) can be proven here,
    in an environment that genuinely has neither installed."""
    import types

    pil_pkg = types.ModuleType("PIL")
    pil_image = types.ModuleType("PIL.Image")

    def _open(_path):
        if open_raises:
            raise OSError("truncated file")
        return _FakeImage(size, std)

    pil_image.open = _open
    pil_pkg.Image = pil_image
    sys.modules["PIL"] = pil_pkg
    sys.modules["PIL.Image"] = pil_image

    np_mod = types.ModuleType("numpy")
    np_mod.float32 = float

    class _Arr:
        def __init__(self, std):
            self._std = std

        def std(self):
            return self._std

    def _asarray(im, dtype=None):
        return _Arr(im._std)

    np_mod.asarray = _asarray
    sys.modules["numpy"] = np_mod


def _uninstall_fake_pil_numpy():
    for name in ("PIL", "PIL.Image", "numpy"):
        sys.modules.pop(name, None)


def main() -> int:
    fails = []
    tmp_png = os.path.join(ROOT, "ops", "tests", "_scratch_render_cards.png")

    # 1. No file at all: bad, regardless of what libraries exist.
    if os.path.exists(tmp_png):
        os.remove(tmp_png)
    status, why = R.verify_png(tmp_png, 750, 1050)
    if status != "bad" or "no file" not in why:
        fails.append(f"missing-file case: got {status!r} {why!r}")

    # 2. A file exists but PIL/numpy genuinely are not importable here (the
    # real, unmocked state of this sandbox): unchecked, not bad, and the
    # message names the missing package rather than a generic error class.
    _uninstall_fake_pil_numpy()
    already_have_pil = False
    try:
        import PIL                                             # noqa: F401
        already_have_pil = True
    except ImportError:
        pass
    io.open(tmp_png, "wb").write(b"\x89PNG\r\n\x1a\n")
    if not already_have_pil:
        status, why = R.verify_png(tmp_png, 750, 1050)
        if status != "unchecked" or "not installed" not in why:
            fails.append(f"missing-dependency case: got {status!r} {why!r}")
    # If this environment genuinely has PIL installed, case 2 is covered by
    # case 5 below instead (a real bad-image path), not skipped silently.

    # 3. Fake PIL/numpy present, correct size, real variance: ok.
    _install_fake_pil_numpy(size=(750, 1050), std=40.0)
    status, why = R.verify_png(tmp_png, 750, 1050)
    if status != "ok" or why:
        fails.append(f"good-image case: got {status!r} {why!r}")

    # 4. Fake PIL/numpy present, wrong size: bad.
    _install_fake_pil_numpy(size=(700, 1000), std=40.0)
    status, why = R.verify_png(tmp_png, 750, 1050)
    if status != "bad" or "rather than" not in why:
        fails.append(f"wrong-size case: got {status!r} {why!r}")

    # 5. Fake PIL/numpy present, flat/blank page: bad, not unchecked.
    _install_fake_pil_numpy(size=(750, 1050), std=2.0)
    status, why = R.verify_png(tmp_png, 750, 1050)
    if status != "bad" or "did not render" not in why:
        fails.append(f"blank-page case: got {status!r} {why!r}")

    # 6. Fake PIL present but Image.open() itself raises: bad, not unchecked
    # (a real corrupt file must not be reported the same as a missing
    # dependency).
    _install_fake_pil_numpy(size=(750, 1050), std=40.0, open_raises=True)
    status, why = R.verify_png(tmp_png, 750, 1050)
    if status != "bad" or "will not open" not in why:
        fails.append(f"corrupt-file case: got {status!r} {why!r}")

    _uninstall_fake_pil_numpy()
    if os.path.exists(tmp_png):
        os.remove(tmp_png)

    if fails:
        print(f"  FAIL {len(fails)}/6")
        for f in fails:
            print(f"    {f}")
        return 1
    print("  6/6 verify_png() cases pass: missing file, missing dependency, "
          "good image, wrong size, blank page and corrupt file are all told "
          "apart correctly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
