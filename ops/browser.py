"""One place that knows how to find a headless, Chromium-family browser.

Edge is what exists on Phil's own Windows machine, where these tools were
written. The pre-installed Chromium at /opt/pw-browsers/chromium is what
exists in the cloud sandbox this operator runs in; Edge never does. Both are
Chromium under the hood and accept the same --headless=new, --dump-dom and
--screenshot flags, so one calling convention covers either, and only the
sandbox binary needs --no-sandbox (it runs as root in a container; Edge on
Windows does not and should not get a flag it has no reason for).

Before this, every browser-driven tool and test hardcoded only the two Edge
paths, so each one reported "no Edge here, cannot verify" on every single
cloud run, every day, regardless of whether the thing it was supposed to
check was actually fine. That is not a report. It is the same fixed answer
repeated back, and the whole point of a check is that it can say something
else.
"""
import os

EDGE_CANDIDATES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)

CHROMIUM_CANDIDATES = (
    "/opt/pw-browsers/chromium",
)


def find_browser():
    """Return (executable_path, extra_args) for the first real browser found
    on this machine, or None if neither Edge nor the sandbox Chromium exists
    here. extra_args carries whatever flags that specific browser needs that
    the others do not."""
    for c in EDGE_CANDIDATES:
        if os.path.exists(c):
            return c, []
    for c in CHROMIUM_CANDIDATES:
        if os.path.exists(c):
            return c, ["--no-sandbox"]
    return None
