#!/usr/bin/env python3
"""
Prove ops/build_social_captions.py's --check actually proves every zone has
a caption file, rather than being fooled by boards.json sitting in the same
output directory.

Found 2026-10-09, second-pass cold read: the old --check counted every
*.json file in OUT and compared the count to len(zs). boards.json, which
main() writes to that same directory whenever every zone is built, is a
*.json file too, so a run with 113 of 114 zone captions plus boards.json
produced a count of 114, byte-equal to len(zs), and passed. One missing
zone caption was invisible to the one check meant to catch it.

Run:  python ops/tests/test_build_social_captions.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_social_captions as C  # noqa: E402
import video_zone as VZ            # noqa: E402


def _populate(out_dir, zs, drop_one):
    """Write a real caption file per zone, skipping one when drop_one, plus
    boards.json, exactly the directory shape main() itself produces."""
    os.makedirs(out_dir, exist_ok=True)
    skipped = None
    for i, (room, z) in enumerate(zs):
        slug = VZ.zone_slug(room, z["zone"])
        if drop_one and skipped is None and i == 0:
            skipped = slug
            continue
        io.open(os.path.join(out_dir, slug + ".json"), "w",
                encoding="utf-8").write("{}")
    io.open(os.path.join(out_dir, "boards.json"), "w",
            encoding="utf-8").write("{}")
    return skipped


def main() -> int:
    fails = []
    zs = VZ.zones()
    tmp = tempfile.mkdtemp()
    old_out, old_argv = C.OUT, sys.argv

    try:
        # 1. Every zone captioned, plus boards.json: --check must pass.
        complete_dir = os.path.join(tmp, "complete")
        _populate(complete_dir, zs, drop_one=False)
        C.OUT = complete_dir
        sys.argv = ["build_social_captions.py", "--check"]
        rc = C.main()
        if rc != 0:
            fails.append("a fully captioned directory (plus boards.json) "
                         "should pass --check, got exit %r" % rc)

        # 2. Exactly one zone caption missing, boards.json still present:
        #    the exact shape that passed silently before this fix (113 zone
        #    files + boards.json == 114 == len(zs)).
        short_dir = os.path.join(tmp, "short")
        skipped = _populate(short_dir, zs, drop_one=True)
        if os.path.isdir(short_dir):
            n_json = len([f for f in os.listdir(short_dir) if f.endswith(".json")])
            if n_json != len(zs):
                fails.append("test setup is wrong: expected the short "
                             "directory's *.json count (%d) to equal "
                             "len(zs) (%d), the exact collision this test "
                             "exists to prove" % (n_json, len(zs)))
        C.OUT = short_dir
        sys.argv = ["build_social_captions.py", "--check"]
        rc = C.main()
        if rc == 0:
            fails.append("one missing zone caption (%r) was masked by "
                         "boards.json inflating the count; --check wrongly "
                         "passed" % skipped)
    finally:
        C.OUT, sys.argv = old_out, old_argv
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: build_social_captions, 2/2 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
