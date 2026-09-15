#!/usr/bin/env python3
"""
Prove gate_ci_path_filter_covers_preflight_inputs() catches a real file
class preflight.py reads that no push-triggered workflow's path filter
would ever match, and leaves a correctly-covered set alone.

Found by building the general version of a defect fixed three times by
hand: a commit touching only linkedin-drafts.yml (2026-09-14), one touching
only build/listings/build_etsy_assets.py (2026-09-15), and one touching
only mobile/quest-app/App.js (2026-09-15, later) each landed on main with
zero Checks runs, because nothing checked whether the file a real gate
depends on was actually reachable by any push trigger. Run for the first
time against the real repository, this gate immediately named two more,
already-live instances: every root *.md operating document, and
content/manual/source/content.json (commits e8ef3bed and 7e644cf0,
2026-09-14, each landed with no Checks run). Both fixed in checks.yml.

Run:  python ops/tests/test_gate_ci_path_filter_covers_preflight_inputs.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


# --------------------------------------------------------------- glob translator

def test_glob_star_does_not_cross_slash():
    rx = preflight._gh_path_glob_to_regex("*.md")
    import re
    assert re.match(rx, "GOALS.md")
    assert not re.match(rx, "content/notes.md"), \
        "a bare '*.md' must not match a nested path"


def test_glob_double_star_crosses_slash():
    rx = preflight._gh_path_glob_to_regex("mobile/quest-app/assets/zones/**")
    import re
    assert re.match(rx, "mobile/quest-app/assets/zones/a/b.jpg")
    assert not re.match(rx, "mobile/quest-app/assets/other.js")


def test_glob_plain_double_star_prefix():
    rx = preflight._gh_path_glob_to_regex("ops/**")
    import re
    assert re.match(rx, "ops/preflight.py")
    assert re.match(rx, "ops/cardtext/build_kitchen_deck.py")
    assert not re.match(rx, "site/index.html")


# --------------------------------------------------------------- YAML paths parser

WF_TEXT = """\
name: Checks
on:
  push:
    branches: [main]
    paths:
      - 'ops/**'
      - 'content/**'
      - '!ops/state.json'
  pull_request:
    paths:
      - 'ops/**'
  workflow_dispatch:

jobs:
  checks:
    runs-on: ubuntu-latest
"""


def test_workflow_on_paths_reads_push_block_only():
    inc, exc = preflight._workflow_on_paths(WF_TEXT, "push")
    assert inc == ["ops/**", "content/**"], inc
    assert exc == ["ops/state.json"], exc


def test_workflow_on_paths_does_not_leak_into_pull_request():
    inc, exc = preflight._workflow_on_paths(WF_TEXT, "pull_request")
    assert inc == ["ops/**"], inc
    assert exc == [], exc


def test_workflow_on_paths_missing_event_returns_empty():
    inc, exc = preflight._workflow_on_paths(WF_TEXT, "schedule")
    assert inc == [] and exc == []


def test_path_triggers_workflow_honours_excludes():
    inc, exc = ["ops/**"], ["ops/state.json"]
    assert preflight._path_triggers_workflow("ops/preflight.py", inc, exc)
    assert not preflight._path_triggers_workflow("ops/state.json", inc, exc)
    assert not preflight._path_triggers_workflow("site/index.html", inc, exc)


# --------------------------------------------------------------- dependency scan

def test_declared_dependencies_finds_join_and_bare_literals():
    src = """
import os
ROOT = "/repo"
SITE = "/repo/site"

def gate_a():
    p = os.path.join(ROOT, "content", "manual", "source", "content.json")
    return p

def gate_b():
    q = os.path.join(SITE, "index.html")
    return q

def gate_c():
    return "GOALS.md"

def gate_d():
    # not a real tracked path, must not appear
    return "this-file-does-not-exist.md"
"""
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "fake_preflight.py")
        io.open(path, "w", encoding="utf-8").write(src)
        deps = preflight._preflight_declared_dependencies(src_path=path)
        assert "content/manual/source/content.json" in deps
        assert "site/index.html" in deps
        assert "GOALS.md" in deps
        assert "this-file-does-not-exist.md" not in deps
    finally:
        shutil.rmtree(tmp)


# --------------------------------------------------------------- the gate itself

FAKE_SRC = """
import os
ROOT = "/repo"
SITE = "/repo/site"

def gate_reads_covered():
    return os.path.join(ROOT, "ops", "preflight.py")

def gate_reads_root_doc():
    return "GOALS.md"

def gate_reads_uncovered_tree():
    return os.path.join(ROOT, "content", "manual", "source", "content.json")
"""

WF_COVERS_ROOT_MD = """\
name: Checks
on:
  push:
    branches: [main]
    paths:
      - 'ops/**'
      - '*.md'
  workflow_dispatch:
"""

WF_COVERS_NOTHING_EXTRA = """\
name: Checks
on:
  push:
    branches: [main]
    paths:
      - 'ops/**'
  workflow_dispatch:
"""

WF_PUBLISH_SITE_ONLY = """\
name: Publish
on:
  push:
    branches: [main]
    paths:
      - 'site/**'
  workflow_dispatch:
"""


def _run_gate(src_text, wf_texts):
    tmp = tempfile.mkdtemp()
    try:
        src_path = os.path.join(tmp, "fake_preflight.py")
        io.open(src_path, "w", encoding="utf-8").write(src_text)

        wf_dir = os.path.join(tmp, "workflows")
        os.makedirs(wf_dir)
        for name, text in wf_texts.items():
            io.open(os.path.join(wf_dir, name), "w", encoding="utf-8").write(text)

        # git ls-files (run from ROOT, the real repo) would not know about
        # our synthetic tmp-dir paths, so stub tracked-file membership for
        # just this call.
        real_run = preflight.subprocess.run

        class FakeCompleted:
            def __init__(self, stdout):
                self.stdout = stdout

        def fake_run(args, **kwargs):
            if args[:2] == ["git", "ls-files"]:
                return FakeCompleted(
                    "ops/preflight.py\nGOALS.md\n"
                    "content/manual/source/content.json\n")
            return real_run(args, **kwargs)

        preflight.FAIL, preflight.WARN = [], []
        preflight.subprocess.run = fake_run
        try:
            preflight.gate_ci_path_filter_covers_preflight_inputs(
                wf_dir=wf_dir, src_path=src_path)
        finally:
            preflight.subprocess.run = real_run
        return list(preflight.FAIL)
    finally:
        shutil.rmtree(tmp)


def test_gate_fails_naming_the_uncovered_tree():
    # checks.yml has no publish-image.yml counterpart here, and neither
    # covers content/**, so the content.json dependency must be named.
    fails = _run_gate(FAKE_SRC, {"checks.yml": WF_COVERS_NOTHING_EXTRA})
    assert fails, "an uncovered dependency should fail the gate"
    msg = fails[0][1]
    assert "content/manual/source/content.json" in msg, msg
    assert "GOALS.md" in msg, \
        "the root doc, also uncovered by this synthetic checks.yml, should be named too"


def test_gate_passes_once_publish_image_covers_the_gap():
    # A second workflow covering content/** closes the gap even though
    # checks.yml alone would not.
    fails = _run_gate(FAKE_SRC, {
        "checks.yml": WF_COVERS_ROOT_MD,
        "publish-image.yml": """\
name: Publish
on:
  push:
    branches: [main]
    paths:
      - 'content/**'
  workflow_dispatch:
""",
    })
    assert not fails, "coverage split across both workflows should pass: %r" % (fails,)


def test_gate_ignores_exempt_paths():
    src = """
import os
ROOT = "/repo"

def gate_reads_exempt():
    return "ops/NIGHTLY-LOG.md"
"""
    fails = _run_gate(src, {"checks.yml": WF_COVERS_NOTHING_EXTRA})
    assert not fails, \
        "a deliberately exempt path must not fail the gate: %r" % (fails,)


def test_gate_fails_closed_if_no_workflow_readable():
    tmp = tempfile.mkdtemp()
    try:
        empty_wf_dir = os.path.join(tmp, "workflows")
        os.makedirs(empty_wf_dir)
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_ci_path_filter_covers_preflight_inputs(wf_dir=empty_wf_dir)
        assert preflight.FAIL, \
            "no readable push.paths anywhere should fail, not silently pass"
    finally:
        shutil.rmtree(tmp)


def test_real_repository_is_clean():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_ci_path_filter_covers_preflight_inputs()
    fails = list(preflight.FAIL)
    assert not fails, \
        "the real checks.yml/publish-image.yml should cover every real " \
        "dependency: %r" % (fails,)


TESTS = [
    test_glob_star_does_not_cross_slash,
    test_glob_double_star_crosses_slash,
    test_glob_plain_double_star_prefix,
    test_workflow_on_paths_reads_push_block_only,
    test_workflow_on_paths_does_not_leak_into_pull_request,
    test_workflow_on_paths_missing_event_returns_empty,
    test_path_triggers_workflow_honours_excludes,
    test_declared_dependencies_finds_join_and_bare_literals,
    test_gate_fails_naming_the_uncovered_tree,
    test_gate_passes_once_publish_image_covers_the_gap,
    test_gate_ignores_exempt_paths,
    test_gate_fails_closed_if_no_workflow_readable,
    test_real_repository_is_clean,
]


def main():
    n = 0
    for t in TESTS:
        t()
        n += 1
    print("  %d of %d cases pass" % (n, len(TESTS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
