#!/usr/bin/env python3
"""
Prove ops/candidate_history.py actually finds a prior decline rather than
only looking like it does.

WHY THIS EXISTS
---------------
At least four recent operator cycles (A270, A277, A279, A282) each spent
part of their one workstream slot manually grepping ops/NIGHTLY-LOG.md and
its archives to confirm a room-guide candidate had already been
investigated and declined, the exact recurring cost GitHub issue #42
names. ops/candidate_history.py automates that grep. This test proves it
on synthetic files first (so it cannot pass by accident against whatever
the real log happens to contain today), then anchors it to one real,
already-documented precedent in the committed history, so the tool is
checked against both a controlled case and the actual data it exists to
search.

Run: python ops/tests/test_candidate_history.py
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import candidate_history as ch  # noqa: E402


class TestCandidatePhrases(unittest.TestCase):
    def test_exact_query_tried_first(self):
        first = next(ch.candidate_phrases("how to organize bulk snacks"))
        self.assertEqual(first, "how to organize bulk snacks")

    def test_strips_leading_stopwords_progressively(self):
        phrases = list(ch.candidate_phrases("how to organise a car boot"))
        self.assertIn("how to organise a car boot", phrases)
        self.assertIn("car boot", phrases)

    def test_does_not_strip_below_two_words(self):
        phrases = list(ch.candidate_phrases("how to store it"))
        # "store" and "it" are each stoplisted/too short; stripping must stop
        # once fewer than 2 words would remain, never yielding an empty phrase.
        self.assertNotIn("", phrases)
        self.assertTrue(all(p.strip() for p in phrases))

    def test_single_word_fallback_is_last(self):
        phrases = list(ch.candidate_phrases("how to organize a very specific widget"))
        self.assertEqual(phrases[-1], "specific")  # longest content word


class TestSearchHistorySynthetic(unittest.TestCase):
    """Proof this can fail: these assertions are checked against files this
    test writes itself, not the real repository, so a change to the real
    NIGHTLY-LOG.md can never make this test pass for the wrong reason."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.f1 = os.path.join(self.tmpdir, "fake-log.md")
        self.f2 = os.path.join(self.tmpdir, "fake-log-2.md")
        with open(self.f1, "w", encoding="utf-8") as f:
            f.write("line one, nothing here\n")
            f.write("A99: declined 'how to organize bulk snacks' as off-topic\n")
            f.write("line three\n")
        with open(self.f2, "w", encoding="utf-8") as f:
            f.write("unrelated content\n")

    def test_finds_exact_phrase_hit(self):
        result = ch.search_history("how to organize bulk snacks", files=[
            os.path.relpath(self.f1, ch.ROOT), os.path.relpath(self.f2, ch.ROOT),
        ])
        self.assertIsNotNone(result)
        self.assertEqual(result["strength"], "strong")
        self.assertEqual(result["matched_on"], "how to organize bulk snacks")
        self.assertTrue(any("fake-log.md" in h["file"] for h in result["hits"]))

    def test_finds_via_prefix_stripping(self):
        # The synthetic file only contains the bare phrase; the query carries
        # extra leading words a real cycle would plausibly type.
        result = ch.search_history("how do i organize bulk snacks", files=[
            os.path.relpath(self.f1, ch.ROOT),
        ])
        self.assertIsNotNone(result)
        self.assertNotEqual(result["matched_on"], "how do i organize bulk snacks")

    def test_no_match_returns_none(self):
        # Every word here, including the fallback single-word candidate,
        # must be absent from both fake files, or the single-word weak
        # fallback can coincidentally match unrelated prose (as "unrelated"
        # itself did against fake-log-2.md's own "unrelated content" line
        # the first time this test was written).
        result = ch.search_history("zyzzyva wombat quixotic lorem", files=[
            os.path.relpath(self.f1, ch.ROOT), os.path.relpath(self.f2, ch.ROOT),
        ])
        self.assertIsNone(result)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)


class TestSearchHistoryRealPrecedent(unittest.TestCase):
    """Anchored to a real, already-documented decline (A79/A192/A195, and
    restated in ops/NIGHTLY-LOG.md's own 2026-11-26 entries) so this test
    fails if the tool ever stops finding evidence that genuinely exists."""

    def test_known_declined_garage_candidate_is_found(self):
        result = ch.search_history("how to organize bulk snacks")
        self.assertIsNotNone(result, "expected to find the real, documented A79/A192/A195 precedent")
        self.assertEqual(result["strength"], "strong")

    def test_fabricated_query_does_not_strong_match(self):
        result = ch.search_history("xyznonexistentquery howtoorganizethisneverexists")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
