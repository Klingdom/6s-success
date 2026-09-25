#!/usr/bin/env python3
"""
Prove ops/generate_card_art.py's torch_status() reports what is actually
true about local GPU generation, rather than asserting one fixed state.

Found 2026-09-25, cold-reading the file: main()'s "NO PROVIDER AVAILABLE"
branch used to print "torch is CPU only with no CUDA" unconditionally,
whether or not torch was even installed. In this sandbox torch is not
installed at all, so the line was a specific, false claim about a state
nothing had looked at, the "unchecked reported as checked" defect CLAUDE.md
0.4 names. Fixed by pulling the check into torch_status(), which imports
torch itself and reports absent, CPU only, or CUDA available, matching
ops/media_capability.py's own torch check.

Run:  python ops/tests/test_generate_card_art.py
"""
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import generate_card_art as gca                                  # noqa: E402


def _with_fake_torch(cuda_available, name="Fake GPU", version="9.9.9"):
    """Install a fake torch module for the duration of one call, then
    restore whatever was really there (usually nothing, in this sandbox).
    """
    fake = types.ModuleType("torch")
    fake.__version__ = version
    fake.cuda = types.SimpleNamespace(
        is_available=lambda: cuda_available,
        get_device_name=lambda i: name)
    return fake


def main() -> int:
    fails = []
    real_torch = sys.modules.pop("torch", None)

    try:
        # 1. torch genuinely absent (the real state in this sandbox): must
        #    say so plainly, never claim a specific CPU/CUDA state it never
        #    checked.
        status = gca.torch_status()
        if "not installed" not in status:
            fails.append("torch absent was not reported as absent: %r" % status)
        if "CPU only" in status or "CUDA" in status:
            fails.append(
                "torch absent still asserted a CPU/CUDA state: %r" % status)

        # 2. torch installed, no CUDA: must say CPU only, and must not claim
        #    the old unconditional "torch is CPU only with no CUDA" text
        #    verbatim (that exact phrasing is the regression signature).
        sys.modules["torch"] = _with_fake_torch(False, version="2.1.0")
        status = gca.torch_status()
        if "CPU only" not in status or "2.1.0" not in status:
            fails.append("torch CPU-only case not reported correctly: %r"
                         % status)
        if "CUDA GPU available" in status:
            fails.append("torch CPU-only case falsely claimed a CUDA GPU: %r"
                         % status)
        del sys.modules["torch"]

        # 3. torch installed, CUDA available: must say so, and name the
        #    device, not fall through to the CPU-only or absent text.
        sys.modules["torch"] = _with_fake_torch(True, name="Test T4")
        status = gca.torch_status()
        if "CUDA GPU available" not in status or "Test T4" not in status:
            fails.append("torch CUDA case not reported correctly: %r" % status)
        del sys.modules["torch"]

    finally:
        sys.modules.pop("torch", None)
        if real_torch is not None:
            sys.modules["torch"] = real_torch

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: generate_card_art.torch_status() reports absent/CPU/CUDA "
          "honestly, 3/3 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
