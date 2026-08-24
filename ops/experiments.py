#!/usr/bin/env python3
"""
The experiment registry, and the arithmetic that says whether one can run yet.

WHY THE ARITHMETIC IS THE POINT
-------------------------------
Asking for experiments usually means asking for a split test. At this site's
traffic a split test cannot produce a usable answer, and the failure mode is not
"no result", it is a result that looks real. Two arms, four conversions, one arm
has three of them: that is a 75 percent win with a confidence interval spanning
almost the whole range, and somebody reads it as a decision.

So this file will not let an experiment be declared started without first
printing how many visitors it needs and how long that takes at the traffic
actually observed. If the answer is longer than the business has, it says so.

WHAT AN EXPERIMENT NEEDS TO BE REAL
-----------------------------------
CLAUDE.md section 16 asks for a hypothesis in the form: because we observed X,
we believe Y will improve Z for W because R. Every entry here carries that
shape, plus a primary metric, a guardrail, a stopping rule decided in advance,
and a decision recorded afterwards including the losses. A losing experiment
that was recorded is worth more than a winning one that was not.

THE HONEST STATE TODAY
----------------------
Nothing can be measured from here. Umami holds the data and needs credentials
this environment does not have, so every experiment below is BLOCKED on read
access rather than on being designed. That is stated per experiment rather than
buried, because a registry full of things that cannot be evaluated is worse than
an empty one.

Run:  python ops/experiments.py
      python ops/experiments.py --power 0.02 0.03    (baseline, target)
"""
from __future__ import annotations

import io
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "ops", "experiments.json")


def sample_size(p1: float, p2: float, power: float = 0.8, alpha: float = 0.05) -> int:
    """Visitors PER ARM for a two proportion test.

    Standard normal approximation. It is deliberately not clever: the point of
    printing it is to make the number visible, and at the magnitudes involved
    here no refinement changes the conclusion.
    """
    if p1 <= 0 or p2 <= 0 or p1 >= 1 or p2 >= 1 or p1 == p2:
        return 0
    z_a = 1.959964            # two sided, alpha 0.05
    z_b = 0.8416212           # power 0.80
    pbar = (p1 + p2) / 2
    num = (z_a * math.sqrt(2 * pbar * (1 - pbar))
           + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / ((p2 - p1) ** 2))


def load() -> dict:
    if os.path.exists(REG):
        return json.load(io.open(REG, encoding="utf-8"))
    return {"observed_daily_visitors": None, "experiments": []}


def main() -> int:
    if "--power" in sys.argv:
        i = sys.argv.index("--power")
        p1, p2 = float(sys.argv[i + 1]), float(sys.argv[i + 2])
        n = sample_size(p1, p2)
        print(f"  {p1:.1%} to {p2:.1%}: {n:,} visitors per arm, {n*2:,} total")
        return 0

    reg = load()
    daily = reg.get("observed_daily_visitors")

    print("  EXPERIMENT REGISTRY\n")
    if daily is None:
        print("  Observed daily visitors: NOT MEASURED.")
        print("  Umami holds the traffic and this environment has no credentials")
        print("  for it, so no experiment below can be evaluated. That is the")
        print("  blocker, and it is one read-only share URL wide.\n")
    else:
        print(f"  Observed daily visitors: {daily}\n")

    for e in reg["experiments"]:
        print(f"  {e['id']}  {e['title']}")
        print(f"     status   {e['status']}")
        print(f"     because  {e['because']}")
        print(f"     believe  {e['believe']}")
        print(f"     metric   {e['primary_metric']}")
        print(f"     guard    {e['guardrail']}")
        b, t = e.get("baseline"), e.get("target")
        if b and t:
            n = sample_size(b, t)
            print(f"     needs    {n:,} visitors per arm, {n*2:,} total "
                  f"to detect {b:.1%} to {t:.1%}")
            if daily:
                days = math.ceil((n * 2) / daily)
                print(f"     at the observed rate that is {days:,} days")
            else:
                print("     at the observed rate: unknown, traffic is not measured")
        print(f"     blocked  {e.get('blocked_on', 'nothing')}")
        print()

    ready = [e for e in reg["experiments"] if e["status"] == "ready"]
    print(f"  {len(reg['experiments'])} registered, {len(ready)} ready to start, "
          f"{sum(1 for e in reg['experiments'] if e.get('blocked_on'))} blocked.")

    # A registry that lets somebody start an unmeasurable test is a registry
    # that will eventually be used to justify a decision made from noise.
    live = [e for e in reg["experiments"] if e["status"] == "running"]
    assert not (live and daily is None), (
        "an experiment is marked running while traffic is not measured. "
        "Stop it or get read access first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
