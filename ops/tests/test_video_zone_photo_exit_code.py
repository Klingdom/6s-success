#!/usr/bin/env python3
"""
ops/video_zone_photo.py --build used to `return 0` unconditionally at the end
of main(), even when every render in the batch had just been appended to
`failed`. The exact defect its own sibling ops/render_all_zone_videos.py
names, in that file's own docstring, as "the same defect that has cost this
repository more than any other: a run reporting a success it never observed".
A caller (a human, a future automation) trusting the exit code would see 0
and believe the batch worked while `failed` sat non-empty in the printed
output above it.

Not reproducible end to end against the real corpus in this sandbox: no
approved zone photo exists here (build/heroes/ is gitignored), so plan()
always returns an empty list and main() takes the "nothing to do" branch
before ever reaching the loop that builds `failed`. This test drives main()
directly with plan() and the render/verify calls it depends on monkeypatched,
so the exit-code contract is proved against the real function, not a
re-description of it.

Run:  python ops/tests/test_video_zone_photo_exit_code.py
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import video as V                                                 # noqa: E402
import video_zone_photo as vzp                                    # noqa: E402


def main() -> int:
    fails = []
    tmp = tempfile.mkdtemp()
    old_out, old_plan = vzp.OUT, vzp.plan
    old_render, old_verify = V.render, V.verify
    old_argv = sys.argv
    item = {"room": "Test Room", "zone": "Test Zone",
            "stem": "test-room--test-zone", "png": "/nonexistent.png",
            "lines": ["a"], "phrases": [(0.0, 1.0, "a")], "done": False}
    try:
        vzp.OUT = tmp
        vzp.plan = lambda: [item]
        sys.argv = ["video_zone_photo.py", "--build"]

        # Case 1: the pre-fix regression, proved directly. A render that
        # raises must produce a non-zero exit, not the old bare `return 0`.
        def boom(png, phrases, out):
            raise RuntimeError("simulated render failure")
        V.render = boom
        rc = vzp.main()
        if rc != 1:
            fails.append(f"a render that raised an exception must exit 1, "
                          f"got {rc} (this is the exact pre-fix bug: a "
                          f"failed batch reporting success)")

        # Case 2: render succeeds and verify() finds nothing wrong -> exit 0.
        def ok_render(png, phrases, out):
            io.open(out, "w", encoding="utf-8").write("x")
        V.render = ok_render
        V.verify = lambda out, want: []
        rc = vzp.main()
        if rc != 0:
            fails.append(f"a clean build with no failures must exit 0, got {rc}")

        # Case 3: render succeeds but verify() reports a problem -> exit 1.
        V.verify = lambda out, want: ["duration too short"]
        rc = vzp.main()
        if rc != 1:
            fails.append(f"a build where verify() finds a problem must exit "
                          f"1, got {rc}")
    finally:
        vzp.OUT, vzp.plan = old_out, old_plan
        V.render, V.verify = old_render, old_verify
        sys.argv = old_argv
        shutil.rmtree(tmp, ignore_errors=True)

    total = 3
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
