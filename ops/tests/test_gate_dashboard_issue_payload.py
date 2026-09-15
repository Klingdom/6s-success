"""Regression test for the false-clean GitHub issues bug in dashboard.py.

`gh_issues()` fetches the open/closed issue list to compute the dashboard's
P0 count, decision count and "need your call" panel. On 2026-09-15 a run of
`ops/dashboard.py` rendered "GREEN / Nothing is blocked on you right now /
No open issues" while GitHub genuinely had 7 open issues (2 of them P0).
Independent replay showed the request itself succeeded (an isolated call
moments later returned all 7, correctly labelled); the live symptom
(printed "P0 0 | need-you 0", not "P0 UNKNOWN") only matches one code path:
`json.loads()` returned something that is not a list (a dict, e.g. `{}` from
a transient malformed/rate-limited body), and the un-guarded list
comprehension `[i for i in data if "pull_request" not in i]` iterated that
dict's *keys* as strings instead of raising, silently producing an empty (or
wrong) result that then reads as "issues_available = True, 0 issues" rather
than "unreachable, UNKNOWN".

`dashboard.py` runs entirely at import time (no `if __name__` guard), so it
cannot be imported directly in a test process without triggering real git
and network calls. This test extracts just the `gh_issues` function's source
text and execs it into an isolated namespace with a stubbed
`urllib.request.urlopen`, proving the parsing behaviour alone, fail-then-pass
against the pre-fix and post-fix source.
"""
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]


def _extract_gh_issues_source(text: str) -> str:
    start = re.search(r"^def gh_issues\(state\):\n", text, re.M)
    assert start, "gh_issues() not found in dashboard.py"
    # Next line at column 0 (a top-level statement or def) ends the function;
    # if there is none, the function runs to the end of the given text.
    end = re.search(r"^\S", text[start.end():], re.M)
    stop = start.end() + end.start() if end else len(text)
    return text[start.start():stop]


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


def _run_with_body(gh_issues, body: bytes):
    with patch("urllib.request.urlopen", return_value=_FakeResponse(body)), \
         patch.dict("os.environ", {"GH_TOKEN": "test-token"}):
        return gh_issues("open")


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
        result = _run_with_body(self.gh_issues, body)
        self.assertIsNotNone(result)
        self.assertEqual([i["number"] for i in result], [2])

    def test_error_object_body_is_not_zero_issues(self):
        body = json.dumps({"message": "API rate limit exceeded"}).encode()
        result = _run_with_body(self.gh_issues, body)
        self.assertIsNone(result, "a dict payload must read as unreachable (None), "
                                   "not an empty issue list")

    def test_empty_object_body_is_not_zero_issues(self):
        """The exact shape observed live: a bare '{}' body, 200 status."""
        body = b"{}"
        result = _run_with_body(self.gh_issues, body)
        self.assertIsNone(result, "'{}' must read as unreachable (None), not [] (0 issues)")


# The exact pre-fix `gh_issues` body, kept as a literal rather than fetched
# from git history: CI's checkout can be shallow, and a test must not depend
# on a specific commit still being reachable (gate_no_hardcoded_git_history).
_PRE_FIX_SOURCE = '''
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


class GhIssuesFailThenPass(unittest.TestCase):
    """Prove the bug was real: the pre-fix source silently returns []."""

    def test_pre_fix_source_had_the_bug(self):
        gh_issues = _load_gh_issues(_PRE_FIX_SOURCE)
        result = _run_with_body(gh_issues, b"{}")
        self.assertEqual(result, [],
                          "expected the pre-fix code to demonstrate the bug "
                          "(silently reading '{}' as zero issues)")

    def test_post_fix_working_tree_is_fixed(self):
        current = (REPO / "ops" / "dashboard.py").read_text(encoding="utf-8")
        gh_issues = _load_gh_issues(current)
        result = _run_with_body(gh_issues, b"{}")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
