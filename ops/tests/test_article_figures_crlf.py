"""article_figures.apply() must be line-ending neutral on a CRLF page.

Found 2026-10-29: on a Windows checkout (core.autocrlf=true) the figure
block was inserted with bare LF, so apply(page, src) never equalled a CRLF
src and gate_article_figures_current reported every such article as
unwired, a false failure. apply() now works in LF and hands back the page's
own line endings, the same fix as article_figures.apply().

CR and LF are built with chr() so no backslash escape has to survive the
tooling that writes this file.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import article_figures as SC                                         # noqa: E402

CR, LF = chr(13), chr(10)
CRLF = CR + LF
PAGE = "articles/how-to-organize-an-attic"
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
        print("FAIL: article_figures.apply line endings")
        for x in fails:
            print("  - " + x)
        return 1
    print("OK: article_figures.apply keeps CRLF pages clean, %d/%d checks pass"
          % (len(tests), len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
