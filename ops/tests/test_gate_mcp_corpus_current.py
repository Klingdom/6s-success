#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_mcp_corpus_current() actually catches
mcp/content.json drifting from content/manual/source/content.json.

Found 2026-09-09, this operator: the MCP server's Docker image bundles
mcp/content.json as a self-contained copy of the manual's corpus, but
nothing checked that copy outside the one CI job that only triggers on a
push touching mcp/**. Every zone-content edit this week (the Sustain
rewrite, the diagnosis blocks) never touched mcp/, so the drift accumulated
silently for 114 of 114 zones while the live, already-deployed MCP server
kept answering real queries with the superseded text. This test proves the
gate fires on that exact shape and stays quiet on a matching pair.

Run:  python ops/tests/test_gate_mcp_corpus_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run_gate(src_text, copy_text, both_present=True):
    tmp_dir = tempfile.mkdtemp()
    try:
        src_dir = os.path.join(tmp_dir, "content", "manual", "source")
        mcp_dir = os.path.join(tmp_dir, "mcp")
        os.makedirs(src_dir)
        os.makedirs(mcp_dir)
        if src_text is not None:
            io.open(os.path.join(src_dir, "content.json"), "w",
                    encoding="utf-8").write(src_text)
        if both_present and copy_text is not None:
            io.open(os.path.join(mcp_dir, "content.json"), "w",
                    encoding="utf-8").write(copy_text)

        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before_fail, before_warn = len(preflight.FAIL), len(preflight.WARN)
        try:
            preflight.gate_mcp_corpus_current()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before_fail:], preflight.WARN[before_warn:]
    finally:
        shutil.rmtree(tmp_dir)


def test_matching_copy_passes_clean():
    fails, warns = _run_gate('{"rooms": []}', '{"rooms": []}')
    assert not fails, fails
    assert not warns, warns
    print("ok  a byte-identical copy passes with no failure and no warning")


def test_drifted_copy_fails_by_name():
    fails, warns = _run_gate('{"rooms": [{"room": "Kitchen"}]}',
                             '{"rooms": [{"room": "Kitchen old"}]}')
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "mcp-corpus", fails
    assert "differs" in msg, msg
    print("ok  a drifted copy fails naming mcp-corpus")


def test_missing_copy_warns_rather_than_fails():
    fails, warns = _run_gate('{"rooms": []}', None, both_present=False)
    assert not fails, fails
    assert len(warns) == 1, warns
    print("ok  a missing mcp/content.json warns rather than fails or crashes")


def test_real_repository_files_match_right_now():
    """Not a synthetic fixture: the actual files this gate protects, run
    through the real gate exactly as preflight.py's main() calls it, so a
    passing test here means the repository is clean, not just the logic.
    """
    before = len(preflight.FAIL)
    preflight.gate_mcp_corpus_current()
    new_fails = preflight.FAIL[before:]
    assert not new_fails, (
        "the real mcp/content.json and content/manual/source/content.json "
        "differ right now: %s" % new_fails)
    print("ok  the real committed files match right now")


if __name__ == "__main__":
    test_matching_copy_passes_clean()
    test_drifted_copy_fails_by_name()
    test_missing_copy_warns_rather_than_fails()
    test_real_repository_files_match_right_now()
    print("\nall gate_mcp_corpus_current tests passed")
