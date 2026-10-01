#!/usr/bin/env python3
"""
main()'s --run path must not exit 0 when the batch it just ran left items in
`failed`. Found 2026-10-01, second-pass cold-read: the exact shape found and
fixed in two sibling batch tools on 2026-09-26 (video_zone_photo.py,
render_all_zone_videos.py) was still live here, unnoticed because this file
had no test of its own. A FAILED line could scroll past above a $? of 0.

No real model is loaded: ops/image_local.py needs torch/CUDA, so this
monkeypatches sys.modules["image_local"] with a fake generate()/verify()
pair before main()'s own `import image_local as L` runs, and writes only to
a scratch output directory, never build/heroes/entryway.

Run:  python ops/tests/test_generate_card_heroes.py
"""
import io
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import generate_card_heroes as GCH                                # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, detail))


class _FakeImage:
    def save(self, path):
        with open(path, "wb") as fh:
            fh.write(b"\0")


def _run_with_fake_backend(verify_result, limit=1):
    """Runs main() --run --limit N with a fake image_local backend that
    always reports `verify_result` as the verify() problems list, so the
    item either always "fails verification" (non-empty) or always "passes"
    (empty), without ever loading a real model.
    """
    scratch = os.path.join(ROOT, "ops", "tests", "_scratch_card_heroes_out")
    os.makedirs(scratch, exist_ok=True)

    fake_module = types.ModuleType("image_local")
    fake_module.generate = lambda subject: (_FakeImage(), {"subject": subject})
    fake_module.verify = lambda im: list(verify_result)

    old_out = GCH.OUT
    old_argv = sys.argv
    old_modules = dict(sys.modules)
    try:
        GCH.OUT = scratch
        sys.modules["image_local"] = fake_module
        sys.argv = ["generate_card_heroes.py", "--run", "--limit", str(limit)]
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            rc = GCH.main()
        finally:
            sys.stdout = old_stdout
        return rc, captured.getvalue()
    finally:
        GCH.OUT = old_out
        sys.argv = old_argv
        sys.modules.clear()
        sys.modules.update(old_modules)
        if os.path.isdir(scratch):
            for f in os.listdir(scratch):
                os.remove(os.path.join(scratch, f))
            os.rmdir(scratch)


def test_all_items_failing_verification_exits_nonzero():
    rc, out = _run_with_fake_backend(["standard deviation 0.0, effectively flat"])
    check("failed-batch-exit-code", rc != 0,
          "a run where every generated image failed verify() returned exit "
          "%r instead of nonzero: %s" % (rc, out.strip()[-200:]))
    check("failed-batch-reports-failed", "FAILED" in out, out.strip()[-200:])


def test_all_items_passing_verification_exits_zero():
    rc, out = _run_with_fake_backend([])
    check("passing-batch-exit-code", rc == 0,
          "a run where every generated image passed verify() returned "
          "nonzero: %r, %s" % (rc, out.strip()[-200:]))


if __name__ == "__main__":
    test_all_items_failing_verification_exits_nonzero()
    test_all_items_passing_verification_exits_zero()
    if FAILS:
        print("FAIL")
        for f in FAILS:
            print("  " + f)
        sys.exit(1)
    print("PASS  2 of 2 cases")
