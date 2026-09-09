#!/usr/bin/env python3
"""
Prove ops/indexnow.py's --changed mode only records a URL's content hash as
"announced" when that URL was actually accepted by this run, never merely
attempted.

Found 2026-09-08, testing offline before wiring --changed into the hourly
CI job (which has real internet access, unlike every sandbox this operator
has run in). The pre-fix code called run(todo, "changed") and then, whatever
the return code, updated log["hashes"] for every URL in todo. A run that
fails before submitting anything (key file unreachable, no network, the
endpoint down) still marked every one of 187 already-once-submitted URLs as
"announced in its current shape". The next run would then treat a real,
unannounced content change as already covered and never retry it: the exact
failure mode ops/indexnow.py's own --changed docstring was written to close
for --new (a rewritten page silently never announced), reopened one layer
deeper.

The fix: run() now returns the set of URLs it actually accepted THIS call,
not the cumulative log["submitted"] set (which already contains any URL
ever accepted in this tool's whole history, so checking membership there
cannot distinguish "sent just now" from "sent, once, weeks ago"). --changed
only updates hashes for URLs in that per-call set.

Run:  python ops/tests/test_indexnow_changed.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import indexnow as inx                                          # noqa: E402


def make_sandbox(tmpdir, prior_hash="oldhash0000000a"):
    """A minimal site/ordinal + a log already recording one URL as announced
    in an old shape, the state --changed is meant to notice has changed."""
    site = os.path.join(tmpdir, "site")
    os.makedirs(site, exist_ok=True)
    with io.open(os.path.join(site, "index.html"), "w", encoding="utf-8") as fh:
        fh.write("<html><body>new content, different from what was hashed</body></html>")
    with io.open(os.path.join(site, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write("<urlset><url><loc>https://6s-success.com/</loc></url></urlset>")
    log_path = os.path.join(tmpdir, "indexnow-log.json")
    with io.open(log_path, "w", encoding="utf-8") as fh:
        json.dump({
            "submitted": ["https://6s-success.com/"],
            "runs": [],
            "hashes": {"https://6s-success.com/": prior_hash},
        }, fh)
    return site, log_path


def run_changed(tmpdir, key_is_live, submit_result):
    """Runs --changed with ROOT/SITE/LOG pointed at an isolated sandbox and
    every network call stubbed, restoring the real module state after."""
    real = (inx.ROOT, inx.SITE, inx.LOG, inx.key_is_live, inx.live_status,
            inx.submit)
    site, log_path = make_sandbox(tmpdir)
    try:
        inx.ROOT = tmpdir
        inx.SITE = site
        inx.LOG = log_path
        inx.key_is_live = lambda: key_is_live
        inx.live_status = lambda url: 200
        inx.submit = lambda batch: submit_result
        rc = inx.main(["indexnow.py", "--changed"])
        with io.open(log_path, encoding="utf-8") as fh:
            log = json.load(fh)
        return rc, log
    finally:
        (inx.ROOT, inx.SITE, inx.LOG, inx.key_is_live, inx.live_status,
         inx.submit) = real


def main() -> int:
    fails = []

    # 1. The regression itself: the site cannot be reached at all
    #    (key_is_live() returns None, the real behaviour with no network).
    #    The pre-fix code overwrote the hash anyway; the fix must not.
    tmpdir = tempfile.mkdtemp()
    try:
        rc, log = run_changed(tmpdir, key_is_live=None, submit_result=None)
        if log["hashes"]["https://6s-success.com/"] != "oldhash0000000a":
            fails.append(
                "REGRESSION: an unreachable run (rc="
                f"{rc}) still overwrote the hash; this is the exact bug "
                "found 2026-09-08")
        if rc == 0:
            fails.append("an unreachable run should not report success")
    finally:
        shutil.rmtree(tmpdir)

    # 2. A run that reaches the site (key live) but whose actual submit
    #    fails (endpoint down, non-2xx) must also leave the hash alone.
    tmpdir = tempfile.mkdtemp()
    try:
        rc, log = run_changed(tmpdir, key_is_live=True,
                              submit_result=(503, "Service Unavailable", ""))
        if log["hashes"]["https://6s-success.com/"] != "oldhash0000000a":
            fails.append("a rejected submission still overwrote the hash")
    finally:
        shutil.rmtree(tmpdir)

    # 3. The real success path must still work: a genuine 200 has to record
    #    the new hash, or the fix would have traded one silent failure for
    #    another (a --changed that never learns anything succeeded either).
    tmpdir = tempfile.mkdtemp()
    try:
        rc, log = run_changed(tmpdir, key_is_live=True,
                              submit_result=(200, "OK", ""))
        if rc != 0:
            fails.append(f"a genuine 200 should report success, got rc={rc}")
        if "https://6s-success.com/" not in log.get("hashes", {}) or \
                log["hashes"]["https://6s-success.com/"] == "oldhash0000000a":
            fails.append(
                "a genuinely accepted submission did not record its new hash")
        if "https://6s-success.com/" not in log.get("submitted", []):
            fails.append("an accepted URL should be recorded as submitted")
    finally:
        shutil.rmtree(tmpdir)

    if fails:
        print("FAIL")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"PASS ({os.path.basename(__file__)}): unreachable and rejected "
          "runs leave hashes untouched; a genuine accept still records one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
