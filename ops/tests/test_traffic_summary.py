"""ops/traffic_summary.py keeps only headline rows and never invents a zero."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import traffic_summary as T                                      # noqa: E402

SAMPLE = """== 6s-success.com (visitors = distinct session_id, visits = visit_id) ==
all_time|900|60|150|2026-08-20|2026-11-01
last_30d|300|25|70||
last_7d|80|9|20||
== top pages ==
/articles/secret-path|12
== referrers, last 30 days ==
linkedin.com|5
raw_week|80|9|20
ex_busiest_bucket|60|7|16
"""


def test_parses_all_rows():
    f = T.parse(SAMPLE)
    assert f["last_7d"] == {"pageviews": 80, "visitors": 9, "visits": 20}
    assert f["all_time"]["first_day"] == "2026-08-20"
    assert set(f) == set(T.ROWS)


def test_drops_paths_and_referrers():
    f = T.parse(SAMPLE)
    flat = repr(f)
    assert "secret-path" not in flat and "linkedin" not in flat


def test_missing_row_is_not_zero():
    f = T.parse("all_time|1|1|1|a|b\n")
    assert "last_7d" not in f


def test_empty_output_is_incomplete():
    assert T.parse("") == {}


def main():
    tests = [test_parses_all_rows, test_drops_paths_and_referrers,
             test_missing_row_is_not_zero, test_empty_output_is_incomplete]
    bad = []
    for t in tests:
        try:
            t()
        except Exception as e:                                  # noqa: BLE001
            bad.append("%s: %r" % (t.__name__, e))
    if bad:
        print("FAIL: traffic_summary")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK: traffic_summary, %d/%d" % (len(tests), len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
