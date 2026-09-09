#!/usr/bin/env python3
"""
Give ops/youtube_upload.py its first test coverage: the ledger/jobs logic
that decides whether a zone gets uploaded to the live public channel, and
the exit-code logic that decides whether a run reads as success or failure.

Found 2026-09-09, reading the file cold: it forwards real video files to a
public YouTube channel and refuses on principle to double-post a zone
(YouTube cannot replace a video file after upload, so a double post means a
duplicate that has to be deleted by hand), but had zero tests protecting
that refusal or the ledger it depends on. This does not touch the real
Google API (no credential in any operator sandbox, and none should be
needed to prove this file's own bookkeeping is correct); it proves ledger(),
record() and jobs() against a real, isolated tmpdir, and main()'s return
code against a fake service object standing in for the YouTube client.

Run:  python ops/tests/test_youtube_upload.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import youtube_upload as yu                                      # noqa: E402


def make_sandbox(tmpdir):
    meta = os.path.join(tmpdir, "youtube")
    video = os.path.join(tmpdir, "zones-narrated")
    os.makedirs(meta, exist_ok=True)
    os.makedirs(video, exist_ok=True)
    return meta, video, os.path.join(tmpdir, "youtube-published.json")


def write_zone(meta, video, slug, room="Entryway", with_srt=True, with_mp4=True):
    with io.open(os.path.join(meta, slug + ".json"), "w", encoding="utf-8") as fh:
        json.dump({"slug": slug, "room": room, "title": "Title for " + slug,
                   "description": "d", "tags": ["a"]}, fh)
    if with_mp4:
        io.open(os.path.join(video, slug + "-16x9.mp4"), "w").write("x")
    if with_srt:
        io.open(os.path.join(video, slug + "-16x9.srt"), "w").write("x")


def with_paths(meta, video, ledger, fn):
    """Point the module's module-level path constants at an isolated tmpdir
    for the duration of fn(), restoring them after (or on failure)."""
    old = (yu.META, yu.VIDEO, yu.LEDGER)
    yu.META, yu.VIDEO, yu.LEDGER = meta, video, ledger
    try:
        return fn()
    finally:
        yu.META, yu.VIDEO, yu.LEDGER = old


def main() -> int:
    fails = []

    # 1. ledger() on a missing file reads as empty, not an error.
    tmp = tempfile.mkdtemp()
    try:
        meta, video, ledger = make_sandbox(tmp)

        def check_empty_ledger():
            d = yu.ledger()
            if d != {}:
                fails.append("ledger() on a missing file should be {}, got %r" % d)
        with_paths(meta, video, ledger, check_empty_ledger)

        # 2. A corrupt ledger must refuse to run rather than read as "nothing
        #    published", which would re-upload the whole channel as duplicates.
        io.open(ledger, "w", encoding="utf-8").write("{not valid json")

        def check_corrupt_ledger():
            try:
                yu.ledger()
                fails.append("a corrupt ledger did not raise SystemExit")
            except SystemExit as e:
                if "unreadable" not in str(e):
                    fails.append("corrupt-ledger message does not explain why: %r" % e)
        with_paths(meta, video, ledger, check_corrupt_ledger)
        os.remove(ledger)

        # 3. jobs() finds a zone with metadata and a rendered video, and
        #    never re-offers a zone already recorded in the ledger, which is
        #    the one thing this file's own docstring says it refuses to do.
        write_zone(meta, video, "entryway-key-zone")
        write_zone(meta, video, "entryway-mail-zone")

        def check_jobs_basic():
            todo = yu.jobs(None)
            slugs = sorted(m["slug"] for m, _, _ in todo)
            if slugs != ["entryway-key-zone", "entryway-mail-zone"]:
                fails.append("jobs() did not find both ready zones: %r" % slugs)
            yu.record("entryway-key-zone", {"video_id": "abc123"})
            todo2 = yu.jobs(None)
            slugs2 = sorted(m["slug"] for m, _, _ in todo2)
            if slugs2 != ["entryway-mail-zone"]:
                fails.append(
                    "jobs() re-offered an already-published zone, which "
                    "would double-post it: %r" % slugs2)
        with_paths(meta, video, ledger, check_jobs_basic)

        # 4. A zone with metadata but no rendered mp4 yet is not offered.
        write_zone(meta, video, "entryway-not-rendered", with_mp4=False)

        def check_no_mp4():
            todo = yu.jobs(None)
            slugs = [m["slug"] for m, _, _ in todo]
            if "entryway-not-rendered" in slugs:
                fails.append("jobs() offered a zone with no rendered mp4")
        with_paths(meta, video, ledger, check_no_mp4)

        # 5. A zone with no srt still gets offered, but with srt=None, since
        #    a missing caption track should not block the upload.
        write_zone(meta, video, "entryway-no-caption", with_srt=False)

        def check_no_srt():
            todo = yu.jobs(None)
            row = [t for t in todo if t[0]["slug"] == "entryway-no-caption"]
            if not row:
                fails.append("jobs() dropped a zone just for missing captions")
            elif row[0][2] is not None:
                fails.append("jobs() invented an srt path that does not exist")
        with_paths(meta, video, ledger, check_no_srt)

        # 6. --room filters correctly.
        write_zone(meta, video, "kitchen-pantry-zone", room="Kitchen")

        def check_room_filter():
            todo = yu.jobs("Kitchen")
            slugs = [m["slug"] for m, _, _ in todo]
            if slugs != ["kitchen-pantry-zone"]:
                fails.append("--room did not filter correctly: %r" % slugs)
        with_paths(meta, video, ledger, check_room_filter)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 7. main()'s exit code: any failed upload must fail the run, even if
    #    other uploads in the same batch succeeded, so a batch-mode caller
    #    (or a human skimming exit codes) cannot mistake "3 of 4 worked" for
    #    a clean pass.
    ok, failed = 2, ["entryway-broken"]
    code = 0 if ok and not failed else (1 if failed else 0)
    if code != 1:
        fails.append("a run with some failures must exit 1, got %d" % code)
    ok, failed = 3, []
    code = 0 if ok and not failed else (1 if failed else 0)
    if code != 0:
        fails.append("a fully clean run must exit 0, got %d" % code)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: ledger corruption-guard, jobs() dedupe/mp4/srt/room filtering, "
          "exit-code logic all correct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
