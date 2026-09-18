#!/usr/bin/env python3
"""Proves ops/image_local.py's split_negations() moves a negated object out
of the positive prompt in every shape the real corpus actually uses,
including a mid-clause "with no X" that the original leading-word-only
match missed.

Found 2026-09-18: EP-001's own shipped subject in ops/card-subjects.json,
"an empty console table with no keys on it, a jacket thrown over a chair",
does not start its clause with "no", so the pre-fix matcher (anchored
`^(no|without)\\b`) left "no keys" sitting in the positive prompt. A
diffusion model draws toward the nouns it is given regardless of "no" in
front of them, the exact failure this same function's own docstring
already paid to learn twice (a nursery crib, a kitchen counter). This
card is a PROBLEM card whose whole point is an empty table nobody has
given keys a home on; drawing keys onto it draws the opposite of the
problem.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_local import split_negations, CLUTTER               # noqa: E402


def test_leading_no_moves_the_named_objects():
    pos, neg = split_negations(
        "a crib with a bare white fitted sheet only, no blankets or toys, "
        "monitor cable clipped high on the wall")
    assert "blankets" not in pos and "toys" not in pos
    assert neg == "blankets, toys"


def test_leading_without_moves_the_named_object():
    pos, neg = split_negations(
        "mail avalanche, Without a mail station, mail takes over surfaces")
    assert "without" not in pos.lower()
    assert neg == "a mail station"


def test_nothing_else_drops_to_generic_clutter_not_the_named_noun():
    pos, neg = split_negations(
        "a tray holding keys, a wallet and a phone, "
        "nothing else on the surface")
    assert "nothing else" not in pos.lower()
    assert neg == CLUTTER


def test_bare_nothing_without_else_is_left_alone():
    # "nothing" alone (not "nothing else") is excluded on purpose per the
    # function's own docstring: it is usually a benefit clause, not an
    # instruction to leave a surface clear.
    pos, neg = split_negations(
        "drawer organizer, a place for loose items so nothing gets lost")
    assert "nothing gets lost" in pos
    assert neg == ""


def test_mid_clause_with_no_is_caught_the_real_ep001_shape():
    pos, neg = split_negations(
        "an empty console table with no keys on it, "
        "a jacket thrown over a chair")
    assert "no keys" not in pos.lower()
    assert "keys" not in pos.lower()
    assert "an empty console table" in pos
    assert "a jacket thrown over a chair" in pos
    assert neg == "keys"


def test_mid_clause_with_no_strips_a_trailing_pronoun_tail():
    pos, neg = split_negations("a hook with no coats on it")
    assert neg == "coats"
    assert "a hook" in pos


def test_subject_with_no_negation_at_all_is_unchanged():
    pos, neg = split_negations("a tidy entryway shoe zone")
    assert pos == "a tidy entryway shoe zone"
    assert neg == ""


if __name__ == "__main__":
    test_leading_no_moves_the_named_objects()
    test_leading_without_moves_the_named_object()
    test_nothing_else_drops_to_generic_clutter_not_the_named_noun()
    test_bare_nothing_without_else_is_left_alone()
    test_mid_clause_with_no_is_caught_the_real_ep001_shape()
    test_mid_clause_with_no_strips_a_trailing_pronoun_tail()
    test_subject_with_no_negation_at_all_is_unchanged()
    print("7 of 7 cases pass")
