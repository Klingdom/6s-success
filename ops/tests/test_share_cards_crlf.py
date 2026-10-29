"""share_cards.apply() must not leave stray carriage returns on a CRLF page.

Found 2026-10-29: on a Windows checkout (core.autocrlf=true) every
`share_cards.py --wire` run left a bare CR behind each meta line _EXTRA
removed, and two per page reached a commit on three articles. apply() now
works in LF and hands back the page's own line endings.

CR and LF are built with chr() so no backslash escape has to survive the
tooling that writes this file.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import share_cards as SC                                         # noqa: E402

CR, LF = chr(13), chr(10)
CRLF = CR + LF
PAGE = "articles/how-to-organize-a-basement"
PATH = os.path.join(SC.SITE, PAGE + ".html")


def _lf_source():
    with open(PATH, encoding="utf-8") as f:       # universal newlines: LF
        return f.read()


def _bare_crs(text):
    return text.replace(CRLF, "").count(CR)


def test_crlf_page_gets_no_stray_carriage_returns():
    crlf = _lf_source().replace(LF, CRLF)
    out = SC.apply(PAGE, crlf)
    assert _bare_crs(out) == 0


def test_crlf_page_keeps_its_own_line_endings():
    lf = _lf_source()
    out = SC.apply(PAGE, lf.replace(LF, CRLF))
    assert out == SC.apply(PAGE, lf).replace(LF, CRLF)


def test_apply_is_idempotent_on_crlf():
    crlf = _lf_source().replace(LF, CRLF)
    once = SC.apply(PAGE, crlf)
    assert SC.apply(PAGE, once) == once


def test_lf_page_unchanged_behaviour():
    lf = _lf_source()
    out = SC.apply(PAGE, lf)
    assert CR not in out
    assert SC.apply(PAGE, out) == out


def main():
    tests = [test_crlf_page_gets_no_stray_carriage_returns,
             test_crlf_page_keeps_its_own_line_endings,
             test_apply_is_idempotent_on_crlf,
             test_lf_page_unchanged_behaviour]
    fails = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            fails.append("%s: %s" % (t.__name__, e))
    if fails:
        print("FAIL: share_cards.apply line endings")
        for x in fails:
            print("  - " + x)
        return 1
    print("OK: share_cards.apply keeps CRLF pages clean, %d/%d checks pass"
          % (len(tests), len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
