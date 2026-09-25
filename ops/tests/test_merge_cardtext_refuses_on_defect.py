#!/usr/bin/env python3
"""
Prove ops/merge_cardtext.py itself refuses to write the merged corpus, and
exits nonzero, when the batches it reads carry a dangling next_card/
related_path reference or a banned em/en dash.

Found 2026-09-25, cold-reading ops/merge_cardtext.py per the standing
cold-read lane: main() computed dangling links and dashes, printed them
under an alarming heading, then wrote build/entryway-cardtext.json and
returned 0 regardless. ops/preflight.py's own gate_card_related_links
docstring has claimed since 2026-09-10 that this script "already refuses to
write the merged corpus when a reference is dangling", which was false; the
live catalogue was never at risk because that preflight gate re-derives the
same check independently from the source batches, but anyone running this
script by hand and trusting `$?` got a false pass on a real defect, the
"check that cannot fail" shape this repository's own gates exist to catch.
Fixed: main() now refuses to write and returns 1 when dangling links or a
banned dash are found, leaving duplicate ids and brand_visible notes
non-fatal on purpose (see the source comment for why: brand_visible is a
note about the artwork, not shipped text, and is independently withheld at
the site layer by gate_deck_art_withheld).

Run:  python ops/tests/test_merge_cardtext_refuses_on_defect.py
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "ops", "merge_cardtext.py")


def _run_isolated(batch_cards):
    """Import the real module, patch its ROOT/SRC/OUT at module level, run main()."""
    import importlib.util
    tmp = tempfile.mkdtemp()
    try:
        ct = os.path.join(tmp, "ops", "cardtext")
        os.makedirs(ct)
        bd = os.path.join(tmp, "build")
        os.makedirs(bd)
        io.open(os.path.join(ct, "batch-00.json"), "w", encoding="utf-8").write(
            json.dumps(batch_cards, ensure_ascii=False))

        spec = importlib.util.spec_from_file_location("merge_cardtext_iso", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.SRC = ct
        mod.OUT = os.path.join(bd, "entryway-cardtext.json")

        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = mod.main()
        wrote = os.path.exists(mod.OUT)
        return rc, buf.getvalue(), wrote
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _card(cid, **extra):
    c = {"id": cid, "title": cid}
    c.update(extra)
    return c


def main() -> int:
    fails = []

    # 1. Clean batch: writes and exits 0.
    clean = [_card("EM-001"), _card("EM-002")]
    rc, out, wrote = _run_isolated(clean)
    if rc != 0 or not wrote:
        fails.append("clean batch was wrongly refused: rc=%r wrote=%r" % (rc, wrote))

    # 2. A dangling next_card: must refuse to write, must exit nonzero.
    bad_next = [_card("EM-001", next_card={"id": "EM-999", "title": "gone"})]
    rc, out, wrote = _run_isolated(bad_next)
    if rc == 0:
        fails.append("dangling next_card did not fail the exit code: %r" % (out,))
    if wrote:
        fails.append("dangling next_card still wrote the merged corpus")
    if "REFUSING" not in out:
        fails.append("dangling next_card case gave no refusal message: %r" % (out,))

    # 3. A dangling related_path: same contract.
    bad_rel = [_card("EM-001", related_path={"tools": "EX-002"})]
    rc, out, wrote = _run_isolated(bad_rel)
    if rc == 0 or wrote:
        fails.append("dangling related_path was not refused: rc=%r wrote=%r" % (rc, wrote))

    # 4. An em dash: must refuse.
    em_dash = [_card("EM-001", pro_tip="do this — then that")]
    rc, out, wrote = _run_isolated(em_dash)
    if rc == 0 or wrote:
        fails.append("em dash was not refused: rc=%r wrote=%r" % (rc, wrote))

    # 5. An en dash: must refuse.
    en_dash = [_card("EM-001", pro_tip="pages 3–10")]
    rc, out, wrote = _run_isolated(en_dash)
    if rc == 0 or wrote:
        fails.append("en dash was not refused: rc=%r wrote=%r" % (rc, wrote))

    # 6. A brand_visible note with no dangling link or dash: still writes,
    #    on purpose (a note about the artwork, not shipped text; withheld
    #    at the site layer by gate_deck_art_withheld, independent of this
    #    file).
    brand = [_card("EM-001", brand_visible="Amazon logo on the box")]
    rc, out, wrote = _run_isolated(brand)
    if rc != 0 or not wrote:
        fails.append("a brand_visible-only card was wrongly refused: rc=%r wrote=%r" % (rc, wrote))

    # 7. A benign duplicate (same id, same title, two batches): still
    #    writes; only an UNEXPLAINED (differing-title) duplicate is fatal,
    #    unchanged behaviour this fix does not touch.
    # (single-batch harness above cannot express two batches; covered by
    # the existing unexplained-duplicate path in load_batches() itself,
    # left untouched by this change.)

    # 8. The real committed batches: clean, still writes, exit 0.
    real = subprocess.run([sys.executable, SCRIPT], cwd=ROOT, capture_output=True, text=True)
    if real.returncode != 0:
        fails.append("the real committed batches now fail: %r" % (real.stdout[-500:],))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: merge_cardtext.py refuses to write on a dangling link or a "
          "banned dash, still writes on a clean batch or a brand_visible-"
          "only note, 6/6 checks pass (plus the real committed batches)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
