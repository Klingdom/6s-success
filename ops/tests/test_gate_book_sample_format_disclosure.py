#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_book_sample_format_disclosure() catches a
missing disclosure and a disclosure that has gone stale, and passes clean
on the real committed files.

Found 2026-09-07 in REVIEW-QA-2026-09-07.md, fixed 2026-09-17: site/book.html
offered the free HTML sample and the PDF side by side with no hint that the
HTML sample renders most figures as a text description instead of a
picture. Fixed by adding a disclosure sentence; this test proves the gate
would catch either the sentence disappearing or the underlying fact it
states becoming false.

Run:  python ops/tests/test_gate_book_sample_format_disclosure.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

MARKER = ("The online version is lighter and shows most figures as a "
          "described caption")


def _run(book_html, sample_html=None):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "book.html"), "w",
                encoding="utf-8").write(book_html)
        if sample_html is not None:
            downloads = os.path.join(tmp, "downloads")
            os.makedirs(downloads)
            io.open(os.path.join(
                downloads,
                "6S Success Home Edition - Sample (Chapters 1-30).html"),
                "w", encoding="utf-8").write(sample_html)
        old_site = preflight.SITE
        preflight.SITE = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_book_sample_format_disclosure()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp)


def _sample(total_figs, text_only):
    parts = []
    for i in range(total_figs):
        if i < text_only:
            parts.append("<figure>Figure description of a scene</figure>")
        else:
            parts.append("<figure><svg></svg></figure>")
    return "<html><body>" + "\n".join(parts) + "</body></html>"


def main() -> int:
    fails = []

    # 1. No disclosure at all on the page: must fail by name.
    f, w = _run("<html><body>no disclosure here</body></html>",
                _sample(231, 172))
    if not any("no longer discloses" in m for _, m in f):
        fails.append("missing disclosure NOT caught: %s" % f)

    # 2. Disclosure present, real counts still a majority text-only: clean.
    f, w = _run("<html><body>%s</body></html>" % MARKER, _sample(231, 172))
    if f:
        fails.append("a genuinely current disclosure was wrongly flagged: %s" % f)

    # 3. Disclosure present but the underlying fact has gone stale (now a
    #    minority of figures are text-only): must fail by name.
    f, w = _run("<html><body>%s</body></html>" % MARKER, _sample(231, 50))
    if not any("no longer a majority" in m for _, m in f):
        fails.append("stale disclosure NOT caught: %s" % f)

    # 4. Sample file missing entirely: must warn, not silently pass or fail.
    f, w = _run("<html><body>%s</body></html>" % MARKER, None)
    if f:
        fails.append("missing sample file should warn, not fail: %s" % f)
    if not w:
        fails.append("missing sample file did not even warn")

    # 5. The real committed files, end to end.
    real_book = os.path.join(ROOT, "site", "book.html")
    real_sample = os.path.join(
        ROOT, "site", "downloads",
        "6S Success Home Edition - Sample (Chapters 1-30).html")
    if os.path.exists(real_book) and os.path.exists(real_sample):
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_book_sample_format_disclosure()
        if preflight.FAIL:
            fails.append("the real committed files failed: %s" % preflight.FAIL)
    else:
        fails.append("real book.html or the sample HTML is missing")

    if fails:
        print("FAIL:")
        for x in fails:
            print(" -", x)
        return 1
    print("5 case(s) pass: gate_book_sample_format_disclosure catches a "
          "missing or stale disclosure and the real committed files are "
          "clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
