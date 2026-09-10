#!/usr/bin/env python3
"""
Prove ops/build_zone_pages.py's general_reading() (PLAN-MICROZONES-DECKS-
APP.md M5) behaves the way the generator depends on: deterministic
regardless of Python's hash-randomised string/set iteration (the first
version of this function summed article-keyword weights over an
unsorted set intersection, and produced a different pick on about 1 run
in 5 depending on PYTHONHASHSEED alone, found by running it under five
different seeds before it ever reached the real corpus), every zone gets
3 to 5 links, and re-running it twice back to back is idempotent (the
property gate_generator_ownership's regenerate-and-diff check relies on
for every generator in ops/build_*.py).

Run:  python ops/tests/test_general_reading.py
"""
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))


def _picks_by_seed(seed: str) -> str:
    """Run general_reading() in a fresh interpreter with the given
    PYTHONHASHSEED and return its result as a stable, sorted string, so
    two runs can be diffed byte for byte."""
    code = (
        "import json, os, sys\n"
        "sys.path.insert(0, %r)\n"
        "import build_zone_pages as bzp\n"
        "src = os.path.join(%r, 'content', 'manual', 'source', 'content.json')\n"
        "rooms = json.load(open(src, encoding='utf-8'))['rooms']\n"
        "picks = bzp.general_reading(rooms)\n"
        "flat = {k: sorted(e[0] for e in v) for k, v in picks.items()}\n"
        "print(json.dumps(flat, sort_keys=True))\n"
    ) % (os.path.join(ROOT, "ops"), ROOT)
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = seed
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError("seed %s failed: %s" % (seed, out.stderr[-2000:]))
    # general_reading() prints a diagnostic line when it needs an over-cap
    # swap to keep every zone's set unique; only the final JSON line (the
    # print() above) matters for this comparison.
    return out.stdout.strip().splitlines()[-1]


def main() -> int:
    fails = []
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    if not os.path.exists(src):
        print("  note: content.json not found, skipping (nothing to test "
             "against)")
        return 0

    # 1. Deterministic across hash seeds: the exact failure mode found
    #    before general_reading() summed over sorted() keyword lists.
    results = {seed: _picks_by_seed(seed) for seed in ("0", "1", "2", "3")}
    first_seed, first = next(iter(results.items()))
    for seed, result in results.items():
        if result != first:
            fails.append("PYTHONHASHSEED=%s produced a different result "
                         "than PYTHONHASHSEED=%s" % (seed, first_seed))

    picks = json.loads(first)

    # 2. Every zone gets 3 to 5 links.
    bad_size = [k for k, v in picks.items() if not (3 <= len(v) <= 5)]
    if bad_size:
        fails.append("%d zone(s) outside the 3-5 link range: %s"
                     % (len(bad_size), bad_size[:3]))

    # 3. No two zones share an identical set.
    seen = {}
    dupes = []
    for k, v in sorted(picks.items()):
        fs = tuple(sorted(v))
        if fs in seen:
            dupes.append((seen[fs], k))
        else:
            seen[fs] = k
    if dupes:
        fails.append("%d duplicate related-reading set(s): %s"
                     % (len(dupes), dupes[:3]))

    # 4. Idempotent: calling it twice in the same process returns the
    #    same result (what gate_generator_ownership's regenerate-and-diff
    #    depends on for the whole site build).
    import build_zone_pages as bzp
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    a = bzp.general_reading(rooms)
    b = bzp.general_reading(rooms)
    flat_a = {k: sorted(e[0] for e in v) for k, v in a.items()}
    flat_b = {k: sorted(e[0] for e in v) for k, v in b.items()}
    if flat_a != flat_b:
        fails.append("general_reading() is not idempotent within one "
                     "process")

    # 5. The floor holds even under real cap starvation, not just in the
    #    real corpus's current numbers. Found 2026-09-10: mapping
    #    root_causes.py's EXCESS to a real article raised that article's
    #    diagnosed-zone usage enough that two late-processed, low-signal
    #    patio zones were starved to 2 links each by the article_cap check
    #    in the initial per-zone loop, silently under M5's 3-link floor,
    #    because that loop only respected the cap and never checked the
    #    floor it could push a zone below. A deliberately harsh
    #    article_cap=1 against the same real rooms forces every zone through
    #    that same starvation path; the floor must still hold for all of
    #    them.
    starved = bzp.general_reading(rooms, article_cap=1)
    under_floor = [k for k, v in starved.items() if len(v) < 3]
    if under_floor:
        fails.append("with article_cap=1, %d zone(s) still fall under the "
                     "3-link floor: %s" % (len(under_floor), under_floor[:5]))

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED: deterministic across 4 hash seeds, %d zones all 3-5 "
         "links, 0 duplicate sets, idempotent, floor holds under cap "
         "starvation" % len(picks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
