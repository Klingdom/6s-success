#!/usr/bin/env python3
"""
--check has to count the jobs THIS run was asked about, not every .mp4 in the
output directory, or a --room-filtered check reports false completeness the
moment any other room's videos already exist on disk.

Found 2026-09-08, cold-read: the file's own comment at the full-run tally
(now line ~93) already explains this exact failure mode ("Counting the whole
directory against a room-filtered job list printed '228 of 12'") and fixed
it there, but the --check branch a few lines above kept the original
unfiltered os.listdir() count. Reproduced without writing into the real
build/ directory by monkeypatching OUT to a scratch folder seeded with fake
finished videos for a room that was never asked about, then calling the
module's real main() with sys.argv set to "--check --room Entryway" (not a
subprocess, so no render is ever spawned; --check returns before any
subprocess.run call).

Run:  python ops/tests/test_render_all_narrated.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import render_all_narrated as ran                                 # noqa: E402
import video_zone as vz                                           # noqa: E402


def main() -> int:
    fails = []

    zs = vz.zones()
    entryway_zones = [(r, z) for r, z in zs if r == "Entryway"]
    if not entryway_zones:
        print("  SKIP  no Entryway zones in video_zone.zones(), cannot build the case")
        return 0
    n_jobs = len(entryway_zones) * 2  # wide + vertical per zone

    scratch = os.path.join(ROOT, "ops", "tests", "_scratch_narrated_out")
    os.makedirs(scratch, exist_ok=True)
    old_out, old_argv = ran.OUT, sys.argv
    try:
        # Seed real-sized .mp4 files for a room that was never asked about,
        # more than enough to exceed the Entryway-only job count.
        for i in range(n_jobs + 50):
            with open(os.path.join(scratch, f"other-room--zone-{i}.mp4"), "wb") as fh:
                fh.write(b"\0" * 200_001)

        ran.OUT = scratch
        sys.argv = ["render_all_narrated.py", "--check", "--room", "Entryway"]

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            rc = ran.main()
        finally:
            sys.stdout = old_stdout
        printed = captured.getvalue()

        # The real regression: with zero of Entryway's own files present but
        # 200+ unrelated files sitting in the same directory, --check must
        # report incomplete (rc == 1), not silently claim done (rc == 0).
        if rc == 0:
            fails.append(f"--check --room Entryway returned 0 (complete) with "
                         f"zero Entryway videos actually present, output: {printed.strip()!r}")
        if f"of {n_jobs}" not in printed:
            fails.append(f"expected the denominator to be the Entryway-only "
                         f"job count ({n_jobs}), got: {printed.strip()!r}")
        if not printed.strip().startswith("narrated videos: 0 of"):
            fails.append(f"expected 0 of Entryway's own videos counted, "
                         f"got: {printed.strip()!r}")
    finally:
        ran.OUT, sys.argv = old_out, old_argv
        for f in os.listdir(scratch):
            os.remove(os.path.join(scratch, f))
        os.rmdir(scratch)

    total = 3
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
