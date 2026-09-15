"""Regression test for two independently observed false-clean bugs in
dashboard.py's `gh_issues()`.

`gh_issues()` fetches the open/closed issue list to compute the dashboard's
P0 count, decision count and "need your call" panel. Two distinct failure
shapes were found live on 2026-09-15, both rendering "GREEN / Nothing is
blocked on you right now / No open issues" while GitHub genuinely had 7
open issues (2 of them P0):

1. A non-list JSON body (a dict, e.g. `{}` from a transient malformed or
   rate-limited response). The un-guarded list comprehension
   `[i for i in data if "pull_request" not in i]` iterated the dict's own
   *keys* as strings instead of raising, silently producing a wrong result.
2. Found immediately after fixing (1): a syntactically valid but WRONG
   empty list, genuine `[]`/200, alternating with a correct 7-item answer
   on immediate retries a second apart (`X-Ratelimit-Remaining` moved by 1
   between calls, so these are two real, different upstream responses
   through this sandbox's proxy, not one cached reply misread).

`dashboard.py` runs entirely at import time (no `if __name__` guard), so it
cannot be imported directly in a test process without triggering real git
and network calls. This test extracts just the `_gh_issues_once` and
`gh_issues` function source text and execs it into an isolated namespace
with a stubbed `urllib.request.urlopen`, proving the parsing and retry
behaviour alone, fail-then-pass against the pre-fix and post-fix source.
"""
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]


def _extract_gh_issues_source(text: str) -> str:
    start = re.search(r"^def _gh_issues_once\(state, token\):\n", text, re.M)
    assert start, "_gh_issues_once() not found in dashboard.py"
    # Capture through the end of the *next* top-level def (gh_issues itself)
    # too: find the first column-0 line after that point which is neither
    # blank nor part of gh_issues's own body, i.e. the next thing entirely.
    after_first = text[start.end():]
    second = re.search(r"^def gh_issues\(state\):\n", after_first, re.M)
    assert second, "gh_issues() not found in dashboard.py"
    tail = after_first[second.end():]
    end = re.search(r"^\S", tail, re.M)
    stop = second.end() + (end.start() if end else len(tail))
    return text[start.start():start.end() + stop]


def _load_gh_issues(source_text: str):
    ns: dict = {"json": json, "gh_token": lambda: "test-token"}
    exec(compile(_extract_gh_issues_source(source_text), "<gh_issues>", "exec"), ns)
    return ns["gh_issues"]


class _FakeResponse:
    def __init__(self, body: bytes):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _run_with_bodies(gh_issues, *bodies: bytes):
    """Feed one body per call to urlopen, in order (one per retry attempt)."""
    responses = [_FakeResponse(b) for b in bodies]
    with patch("urllib.request.urlopen", side_effect=responses), \
         patch("time.sleep", return_value=None), \
         patch.dict("os.environ", {"GH_TOKEN": "test-token"}):
        return gh_issues("open")


def _run_with_body(gh_issues, body: bytes):
    # A single attempt succeeding means the retry loop never needs a second
    # or third urlopen call, so one fake response is enough here.
    return _run_with_bodies(gh_issues, body)


class GhIssuesMalformedPayload(unittest.TestCase):
    """A body that is not a JSON list must read as unreachable, not zero."""

    def setUp(self):
        current = (REPO / "ops" / "dashboard.py").read_text(encoding="utf-8")
        self.gh_issues = _load_gh_issues(current)

    def test_real_list_still_parses(self):
        body = json.dumps([
            {"number": 2, "labels": [{"name": "P0"}]},
            {"number": 31, "labels": [{"name": "decision"}], "pull_request": {}},
        ]).encode()
        # All three retry attempts see the same good body; the loop still
        # runs to completion and should keep the correct, longest result.
        result = _run_with_bodies(self.gh_issues, body, body, body)
        self.assertIsNotNone(result)
        self.assertEqual([i["number"] for i in result], [2])

    def test_error_object_body_is_not_zero_issues(self):
        body = json.dumps({"message": "API rate limit exceeded"}).encode()
        result = _run_with_bodies(self.gh_issues, body, body, body)
        self.assertIsNone(result, "a dict payload must read as unreachable (None), "
                                   "not an empty issue list")

    def test_empty_object_body_is_not_zero_issues(self):
        """The exact shape observed live: a bare '{}' body, 200 status."""
        body = b"{}"
        result = _run_with_bodies(self.gh_issues, body, body, body)
        self.assertIsNone(result, "'{}' must read as unreachable (None), not [] (0 issues)")

    def test_flaky_empty_list_does_not_beat_a_real_answer(self):
        """The second bug found live: a genuinely valid but wrong `[]`,
        alternating with the correct 7-item answer moments apart. The
        retry loop must keep the longer (more informative) reading."""
        empty = b"[]"
        real = json.dumps([
            {"number": 2, "labels": [{"name": "P0"}]},
            {"number": 15, "labels": [{"name": "P0"}, {"name": "decision"}]},
        ]).encode()
        result = _run_with_bodies(self.gh_issues, empty, real, empty)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2, "the flaky '[]' must not win over the real 2-item answer")

    def test_sustained_real_zero_still_reports_zero(self):
        """A genuine, sustained zero (every attempt agrees) must still
        report as zero, not be forced non-empty by the fix above."""
        result = _run_with_bodies(self.gh_issues, b"[]", b"[]", b"[]")
        self.assertEqual(result, [])


# The exact pre-fix `gh_issues` bodies, kept as literals rather than fetched
# from git history: CI's checkout can be shallow, and a test must not depend
# on a specific commit still being reachable (gate_no_hardcoded_git_history).

# Bug 1: no isinstance guard at all (before the first, 2026-09-15 fix).
_BUG1_SOURCE = '''
def gh_issues(state):
    import urllib.request, urllib.error
    token = gh_token()
    if not token:
        return None
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/klingdom/6s-success/issues"
            f"?state={state}&per_page=100",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "User-Agent": "6s-dashboard"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        # the issues endpoint also returns pull requests; exclude them
        return [i for i in data if "pull_request" not in i]
    except Exception:
        return None
'''

# Bug 2: isinstance guard present, but no retry, so a single flaky "[]"
# still wins outright (this is what commit c8e3bc76 shipped).
_BUG2_SOURCE = '''
def gh_issues(state):
    import urllib.request, urllib.error
    token = gh_token()
    if not token:
        return None
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/klingdom/6s-success/issues"
            f"?state={state}&per_page=100",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "User-Agent": "6s-dashboard"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        if not isinstance(data, list):
            return None
        return [i for i in data if "pull_request" not in i]
    except Exception:
        return None
'''


def _load_single_attempt_gh_issues(source_text: str):
    ns: dict = {"json": json, "gh_token": lambda: "test-token"}
    exec(compile(source_text, "<gh_issues>", "exec"), ns)
    return ns["gh_issues"]


class GhIssuesFailThenPass(unittest.TestCase):
    """Prove both bugs were real, and that the current source fixes both."""

    def test_bug1_source_read_malformed_body_as_zero_issues(self):
        gh_issues = _load_single_attempt_gh_issues(_BUG1_SOURCE)
        result = _run_with_body(gh_issues, b"{}")
        self.assertEqual(result, [],
                          "expected the bug-1 code to demonstrate the bug "
                          "(silently reading '{}' as zero issues)")

    def test_bug2_source_let_one_flaky_empty_list_win(self):
        gh_issues = _load_single_attempt_gh_issues(_BUG2_SOURCE)
        result = _run_with_body(gh_issues, b"[]")
        self.assertEqual(result, [],
                          "expected the bug-2 code (isinstance guard, no retry) "
                          "to still be fooled by a single flaky '[]'")

    def test_post_fix_working_tree_fixes_bug1(self):
        current = (REPO / "ops" / "dashboard.py").read_text(encoding="utf-8")
        gh_issues = _load_gh_issues(current)
        result = _run_with_bodies(gh_issues, b"{}", b"{}", b"{}")
        self.assertIsNone(result)

    def test_post_fix_working_tree_fixes_bug2(self):
        current = (REPO / "ops" / "dashboard.py").read_text(encoding="utf-8")
        gh_issues = _load_gh_issues(current)
        empty = b"[]"
        real = json.dumps([{"number": 2, "labels": [{"name": "P0"}]}]).encode()
        result = _run_with_bodies(gh_issues, empty, real, empty)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
