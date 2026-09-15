#!/usr/bin/env python3
"""
gate_home_hero_card_real: the home hero card must match quest-data.js.

The hero's retired gauge was replaced on 2026-09-15 with a real Quest card,
hand-placed in a hand-maintained page. This proves the gate passes on the real
files, fails by name when one line of the card drifts from quest-data.js, and
stays silent when the page carries no hero card at all.

Run:  python ops/tests/test_gate_home_hero_card_real.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))
os.environ.setdefault("SIXS_UNDER_PREFLIGHT", "1")
import preflight  # noqa: E402


def _run(index_html, quest_js):
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "site", "assets", "js"))
        io.open(os.path.join(tmp, "site", "index.html"), "w", encoding="utf-8").write(index_html)
        io.open(os.path.join(tmp, "site", "assets", "js", "quest-data.js"), "w",
                encoding="utf-8").write(quest_js)
        real_root = preflight.ROOT
        preflight.ROOT = tmp
        before = len(preflight.FAIL)
        try:
            preflight.gate_home_hero_card_real()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _real():
    home = io.open(os.path.join(ROOT, "site", "index.html"), encoding="utf-8").read()
    data = io.open(os.path.join(ROOT, "site", "assets", "js", "quest-data.js"),
                   encoding="utf-8").read()
    return home, data


def test_real_files_pass():
    home, data = _real()
    assert 'class="hero-card"' in home, "the real home page has no hero card to check"
    fails = _run(home, data)
    assert not fails, fails
    print("ok  the real home hero card matches quest-data.js")


def test_drifted_action_fails_by_name():
    home, data = _real()
    start = home.index('data-quest="action">') + len('data-quest="action">')
    drifted = home[:start] + "Tidy the tray. " + home[start:]
    fails = _run(drifted, data)
    assert fails, "a drifted action line was not caught"
    assert any("action" in msg for _, msg in fails), fails
    print("ok  an edited action line fails, naming the action field")


def test_badge_showing_the_cause_pass_fails():
    """The 2026-09-15 regression: a badge naming symptoms[0].sixS, the cause
    pass, instead of the pass the Quest opens on, must be caught."""
    home, data = _real()
    quest = json.JSONDecoder().raw_decode(data[data.index("window.QUEST = ") + len("window.QUEST = "):])[0]
    cause = quest["symptoms"][0]["sixS"]
    start = home.index('data-quest="sixS">') + len('data-quest="sixS">')
    end = home.index("</span>", start)
    if home[start:end].lower() == cause.lower():
        raise AssertionError("the real hero already shows the cause pass %r" % cause)
    fails = _run(home[:start] + cause + home[end:], data)
    assert fails, "a badge showing the cause pass was not caught"
    assert any("sixS" in msg for _, msg in fails), fails
    print("ok  a badge naming the cause pass instead of the opening pass fails")


def test_no_hero_card_is_silent():
    _home, data = _real()
    fails = _run("<!doctype html><title>x</title><p>no card here</p>", data)
    assert not fails, fails
    print("ok  a page with no hero card has nothing to drift")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print("FAIL %s: %s" % (t.__name__, e))
    print("\n%d of %d test(s) %s" % (len(tests) - failed if not failed else failed, len(tests),
                                     "pass" if not failed else "failed"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
