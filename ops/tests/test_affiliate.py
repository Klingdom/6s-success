"""Prove affiliate.py cannot fail on its own scratch neighbour.

Found 2026-09-03: `delivered_documents()` globs everything in
`site/downloads/*` with no filter, and `audit_visual.py` writes a scratch
`_visual_probe.html` beside whatever page it is measuring, including any
page under `site/downloads/`, removing it again once that one page is
measured. Running `python ops/affiliate.py --check` while a deep preflight
pass has `audit_visual.py` mid-flight elsewhere in the site can catch that
probe between its write and its cleanup: `_text_of()` either reads a
half-written or already-deleted file and reports "could not read 1
delivered document(s)... failing closed" (a false compliance FAIL, not a
real one), or, if the read succeeds, scans a scratch copy of some page as
though a customer had received it. Reproduced live: running
`ops/affiliate.py --check` by hand while a backgrounded
`preflight.py --deep` had `audit_visual.py --all` active reported exactly
that FAIL; the file was gone a moment later, confirming it was transient
scratch, not a real defect.

Two things have to both be true:

    a real `_visual_probe.html` sitting in site/downloads/ must never be
    treated as a delivered document, readable or not;

    a real delivered document, and a real affiliate-link violation inside
    one, must still be caught even while a decoy probe file sits right
    next to it.
"""
import contextlib
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import affiliate                                                # noqa: E402

DOWNLOADS = os.path.join(ROOT, "site", "downloads")
PROBE = os.path.join(DOWNLOADS, "_visual_probe.html")


def _run_check():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = affiliate.check()
    return code, out.getvalue()


def test_stray_probe_file_is_never_a_delivered_document():
    assert not os.path.exists(PROBE), "a real probe file was already here"
    # Deliberately unreadable: truncated mid-write, the exact shape a killed
    # or concurrently-running audit_visual.py leaves behind.
    with io.open(PROBE, "wb") as fh:
        fh.write(b"\xff\xfe<htm")
    try:
        docs = affiliate.delivered_documents()
        assert PROBE not in docs, docs
        code, out = _run_check()
        assert "_visual_probe" not in out, out
        assert "could not read" not in out, out
    finally:
        os.remove(PROBE)


def test_real_affiliate_violation_in_a_document_still_fails():
    assert not os.path.exists(PROBE), "a real probe file was already here"
    marker = os.path.join(DOWNLOADS, "_test_bad_delivered_doc.html")
    ids = {v.get("publisher_id") for v in affiliate.accounts().values()
           if v.get("publisher_id")}
    fake_id = next(iter(ids), "fake-publisher-tag-123")
    with io.open(marker, "w", encoding="utf-8") as fh:
        fh.write(f"<html><body>buy it here {fake_id}</body></html>")
    # The decoy sits alongside the real defect, same as a live race would.
    with io.open(PROBE, "wb") as fh:
        fh.write(b"\xff\xfe<htm")
    try:
        code, out = _run_check()
        assert code == 1, (code, out)
        assert "_test_bad_delivered_doc" in out, out
        assert "_visual_probe" not in out, out
    finally:
        os.remove(marker)
        os.remove(PROBE)


if __name__ == "__main__":
    test_stray_probe_file_is_never_a_delivered_document()
    test_real_affiliate_violation_in_a_document_still_fails()
    print("ok  affiliate.py --check ignores audit_visual.py's own scratch "
          "probe file and still catches a real violation beside it")
