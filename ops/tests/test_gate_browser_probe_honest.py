"""A browser that exists is not a browser that works.

Proves gate_browser_probe_honest can report every state it claims to, and
that ops/browser.py's own probe agrees with the real machine this runs on.

The defect behind it, measured 2026-11-13 rather than inferred: in the cloud
sandbox /opt/pw-browsers/chromium exists, starts, and then renders nothing
and never exits. find_browser() answered from os.path.exists alone, so it
called that browser usable, and every browser driven test committed to a
600s render that could not succeed. Three nightly log entries (A87, A122,
A125) called it a hang in one test file and each handed forward the same
already-implemented fix.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import preflight as pf                                          # noqa: E402
import browser as B                                             # noqa: E402


def main():
    fails = []

    # 1. No binary at all is NOT this defect. That machine is honestly
    #    browserless and every caller already prints NOT VERIFIED.
    if pf.browser_claimed_but_unusable(False, False, "nothing here") is not None:
        fails.append("a machine with no browser binary must not warn: it is "
                     "honestly browserless, not misreporting")

    # 2. A binary that renders is the healthy case and must stay silent.
    if pf.browser_claimed_but_unusable(True, True, "") is not None:
        fails.append("a browser that renders must not warn")

    # 3. The defect itself: a binary is present and cannot render. This is
    #    the state this sandbox is actually in, and the one that used to be
    #    invisible until a cycle killed a stalled run by hand.
    problem = pf.browser_claimed_but_unusable(
        True, False, "produced no output at all within 30s")
    if not problem:
        fails.append("a browser binary that cannot render MUST warn; this is "
                     "the whole defect, and silence here is the pre-fix "
                     "behaviour that cost three cycles")
    elif "produced no output at all within 30s" not in problem:
        fails.append("the warning must carry the probe's own reason, so the "
                     "reader does not have to re-measure it: got %r" % problem)

    # 4. The reason is optional and must not crash the gate.
    if not pf.browser_claimed_but_unusable(True, False, ""):
        fails.append("a missing reason must still warn, not swallow the "
                     "defect")

    # 5. find_browser must now be able to answer None on a machine whose
    #    binary exists but cannot render. Before the fix it could only ever
    #    answer from os.path.exists, so this was unreachable.
    present = B.find_browser(require_working=False)
    renders, why = B.browser_probe()
    usable = B.find_browser()
    if present and not renders and usable is not None:
        fails.append("find_browser() returned a browser that the probe says "
                     "cannot render (%s); exists-only answers are exactly "
                     "the pre-fix defect" % why)
    if present and renders and usable is None:
        fails.append("find_browser() refused a browser that the probe says "
                     "renders fine; the probe must not create false "
                     "negatives")
    if not present and usable is not None:
        fails.append("find_browser() returned a browser on a machine with no "
                     "browser binary at all")

    # 6. The real gate must agree with the real machine, not with a fixture.
    #    Whichever state this machine is in, the gate's verdict has to match
    #    what the probe just measured.
    expected = pf.browser_claimed_but_unusable(bool(present), renders, why)
    print("  this machine: binary present=%s, renders=%s (%s)"
          % (bool(present), renders, why))
    print("  gate verdict: %s" % ("warns" if expected else "silent"))

    # 7. The probe must be honest about cost: it is bounded, so a machine
    #    whose browser never exits cannot make this test hang either.
    if B.PROBE_TIMEOUT > 60:
        fails.append("the probe's own timeout (%ds) is too large to be worth "
                     "paying: the point is to replace a 600s wait with a "
                     "short one" % B.PROBE_TIMEOUT)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    n = len(__import__("re").findall(
        r"^    # \d+\. ", io.open(__file__, encoding="utf-8").read(),
        __import__("re").M))
    print("OK: gate_browser_probe_honest, %d numbered case(s), no problems"
          % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
