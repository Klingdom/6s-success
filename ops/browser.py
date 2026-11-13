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
import subprocess
import tempfile

EDGE_CANDIDATES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)

CHROMIUM_CANDIDATES = (
    "/opt/pw-browsers/chromium",
)


# The smallest page that proves a browser can actually render and exit: it
# has to parse HTML, run one line of script and hand the result back through
# the DOM, which is the same round trip every real probe in ops/tests makes.
PROBE_HTML = ('<!doctype html><title>t</title><p id="p">no</p>'
              '<script>document.getElementById("p").textContent='
              '"BROWSERPROBEOK";</script>')

PROBE_MARKER = "BROWSERPROBEOK"

# Generous enough that a merely loaded machine still passes (the real probes
# settle in well under a minute when idle), small enough that six browser
# driven test files cost seconds rather than the hour they cost before.
PROBE_TIMEOUT = 30

_PROBE_CACHE = None


def browser_renders(exe, extra, timeout=PROBE_TIMEOUT):
    """Does this browser actually render a trivial page and exit?

    EXISTS IS NOT WORKS, AND THAT DISTINCTION COST WEEKS.

    Measured 2026-11-13, scheduled operator cycle, by running it rather than
    inferring it: in this cloud sandbox /opt/pw-browsers/chromium starts,
    forks its zygote and gpu children, and then produces ZERO bytes of
    --dump-dom output and never exits, for a four line local file with a
    five second --virtual-time-budget. Not slow: nothing, ever.

    find_browser() used to answer purely from os.path.exists, so it reported
    that browser as available, and every browser driven test then committed
    to its own 600s render that could not succeed. ops/preflight.py's
    gate_tests runs those files one after another, so a full preflight run
    could not reach its own end inside any practical cycle budget. Three
    consecutive nightly log entries (A87, A122, A125) each recorded that as
    "a sandbox hang in test_contact_form_interactive.py" and each handed
    forward the same proposed fix, a per test timeout in gate_tests. That
    fix was already there the whole time (_run_bounded, 700s, process group
    kill); it was never the defect. The defect is that the check could not
    tell "I looked and the browser works" from "a file of that name exists",
    which is CLAUDE.md 0.4 exactly: unknown reported as known.

    Every caller already handles "no usable browser" correctly, by printing
    NOT VERIFIED and returning 0, and gate_tests already warns by name about
    every file that did so. So proving the browser here rather than assuming
    it turns an hour of silent waiting into an honest, named, seconds long
    "could not look".

    Returns (True, note) or (False, reason). Never raises.
    """
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".html", prefix="6s-browserprobe-")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(PROBE_HTML)
        profile = tempfile.mkdtemp(prefix="6s-browserprobe-profile-")
        try:
            r = subprocess.run(
                [exe] + list(extra) +
                ["--headless=new", "--disable-gpu", "--hide-scrollbars",
                 "--allow-file-access-from-files",
                 "--user-data-dir=" + profile,
                 "--virtual-time-budget=2000", "--dump-dom",
                 "file:///" + tmp.replace("\\", "/")],
                capture_output=True, timeout=timeout)
        finally:
            _rmtree_quietly(profile)
        dom = r.stdout.decode("utf-8", "replace")
        if PROBE_MARKER in dom:
            return True, "rendered a probe page in under %ds" % timeout
        if not dom.strip():
            return False, ("produced no output at all within %ds (the "
                           "browser starts but never renders or exits here)"
                           % timeout)
        return False, "rendered something, but not the probe marker"
    except subprocess.TimeoutExpired:
        return False, ("did not exit within %ds on a four line local page, "
                       "so no browser driven check can complete here"
                       % timeout)
    except OSError as exc:
        return False, "could not be started: %s" % exc
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def _rmtree_quietly(path):
    import shutil
    shutil.rmtree(path, ignore_errors=True)


def browser_probe(exe=None, extra=None):
    """(usable, reason) for this machine's browser, measured once per process.

    Honours SIXS_BROWSER_PROBE when a parent process has already paid for the
    probe ("ok" or "unusable:<reason>"), so gate_tests' ~130 children do not
    each re-run it.
    """
    global _PROBE_CACHE
    if _PROBE_CACHE is not None:
        return _PROBE_CACHE
    inherited = os.environ.get("SIXS_BROWSER_PROBE", "")
    if inherited == "ok":
        _PROBE_CACHE = (True, "probed by the parent process")
        return _PROBE_CACHE
    if inherited.startswith("unusable:"):
        _PROBE_CACHE = (False, inherited.split(":", 1)[1] or "unusable")
        return _PROBE_CACHE
    if exe is None:
        found = _find_browser_path()
        if not found:
            _PROBE_CACHE = (False, "no browser binary on this machine")
            return _PROBE_CACHE
        exe, extra = found
    _PROBE_CACHE = browser_renders(exe, extra or [])
    return _PROBE_CACHE


def _find_browser_path():
    """The old exists-only lookup. Says a binary is present, nothing more."""
    for c in EDGE_CANDIDATES:
        if os.path.exists(c):
            return c, []
    for c in CHROMIUM_CANDIDATES:
        if os.path.exists(c):
            return c, ["--no-sandbox"]
    return None


def find_browser(require_working=True):
    """Return (executable_path, extra_args) for a browser that actually works
    on this machine, or None.

    None now means either "no browser binary here" or "a binary is here and
    it cannot render", and both are the same thing to a caller: this check
    cannot be performed on this machine, so say NOT VERIFIED rather than
    pretend. See browser_renders for the measurement behind that change.

    require_working=False restores the old exists-only answer, for the one
    caller that wants to report on the gap between the two.
    """
    found = _find_browser_path()
    if not found or not require_working:
        return found
    ok, _why = browser_probe(found[0], found[1])
    return found if ok else None
