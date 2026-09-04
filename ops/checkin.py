"""The hourly self check-in. What moved, what did not, what is next.

Phil's instruction, 2026-09-02: check in every hour, hold myself accountable to
improving the site and the product, and keep working, testing and improving.

The existing hourly brief reports numbers to Phil. This is the other half and
points inward: it measures the things GOALS.md says matter, compares them to
the previous check-in, and writes the delta to CHECKIN-LOG.md so a claim of
progress can be checked against a number rather than a feeling.

It has teeth on purpose. If nothing measurable moved since the last check-in it
says so plainly and exits non-zero, because "I was busy" and "something
improved" are different claims and this repository has produced a lot of the
first while reporting the second: 427 commits in a week against $0 of revenue.

    python ops/checkin.py            measure, record, print
    python ops/checkin.py --quiet    record without the narrative
"""
from __future__ import annotations

import datetime as dt
import glob
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "ops", "state-checkin.json")
LOG = os.path.join(ROOT, "CHECKIN-LOG.md")


def sh(*a) -> str:
    try:
        return subprocess.run(a, cwd=ROOT, capture_output=True, text=True,
                              timeout=120).stdout.strip()
    except Exception:                                           # noqa: BLE001
        return ""


def sh_checked(*a):
    """Like sh(), but a failed command reports None rather than "".

    Mirrors ops/dashboard.py's own sh_checked: an empty stdout must not be
    read as "zero", since a failed command produces the identical string.
    """
    try:
        r = subprocess.run(a, cwd=ROOT, capture_output=True, text=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:                                           # noqa: BLE001
        return None


def count(pattern: str) -> int:
    return len(glob.glob(os.path.join(ROOT, pattern), recursive=True))


def live_products():
    try:
        req = urllib.request.Request(
            "https://6s-success.com/assets/js/data.js",
            headers={"User-Agent": "6s-checkin"})
        s = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        return len(re.findall(r'"sku"\s*:', s))
    except Exception:                                           # noqa: BLE001
        return None


def youtube_videos():
    """How many videos are actually published. The point of the whole media
    pipeline, and the number most likely to be quietly zero."""
    try:
        req = urllib.request.Request("https://www.youtube.com/@6SSuccess/videos",
                                     headers={"User-Agent": "Mozilla/5.0"})
        s = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        return len(set(re.findall(r'"videoId":"([\w-]{11})"', s)))
    except Exception:                                           # noqa: BLE001
        return None


def commits_24h_count():
    """`git log --since=` does not fail on a shallow clone, it silently stops
    at the shallow boundary, undercounting rather than erroring. This
    environment's checkout is shallow on most cycles (issue #27), and
    ops/dashboard.py already had to fix this exact shape twice for
    commits_total and commits_7d (6.13, 6.17); this is the same bug one
    field over, in a file neither fix touched. Best-effort unshallow first,
    then report the true count; returns None, never a truncated number, if
    unshallowing did not succeed (no egress to origin).

    Also fixes a second, separate bug found while rewriting this: the old
    line `sh(...).count("\\n") or 0` counted newlines in stripped output, not
    lines, so it undercounted by exactly one whenever at least one commit
    existed (N lines of stripped text carry N-1 newlines). Confirmed live
    this cycle: the unedited function printed 43 in the same window
    `git log --oneline | wc -l` independently counted as 44.
    """
    if sh_checked("git", "rev-parse", "--is-shallow-repository") == "true":
        sh("git", "fetch", "--unshallow", "--quiet")
    if sh_checked("git", "rev-parse", "--is-shallow-repository") != "false":
        return None
    out = sh_checked("git", "log", "--since=24 hours ago", "--oneline")
    return out.count("\n") + 1 if out else 0


def commits_24h_text(commits_24h):
    """Pure so a gate can prove it without a real shallow clone."""
    return str(commits_24h) if commits_24h is not None else \
        "unknown (shallow clone, could not verify)"


def measure() -> dict:
    """Only things that are true outside this repository, plus asset counts.

    Commit count is deliberately NOT a success measure. It is recorded as
    context so effort and outcome can be told apart.
    """
    m = {
        "at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "commits_24h": commits_24h_count(),
        "videos_vertical": count("build/video/zones/*.mp4"),
        "videos_wide": count("build/video/zones-16x9/*.mp4"),
        "captions": count("build/video/zones/*.srt"),
        "youtube_published": youtube_videos(),
        "products_live": live_products(),
        "avif": count("site/**/*.avif"),
        # Video is no longer in git, so build/ is not a safe place for it to
        # live. A rebase deleted 377 rendered files from the working tree on
        # 2026-09-03 and only the Desktop copies saved them. This is the count
        # that exists in exactly one place.
        "undelivered_media": undelivered_media(),
    }
    return m


def undelivered_media() -> int:
    """Rendered files that exist only in build/, which nothing backs up."""
    r = subprocess.run([sys.executable,
                        os.path.join(ROOT, "ops", "verify_media_delivery.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    for line in r.stdout.split("\n"):
        if "exist only in build/" in line:
            try:
                return int(line.strip().split()[0])
            except (ValueError, IndexError):
                return -1        # unreadable, which is not the same as zero
    return 0 if "copy outside build/" in r.stdout else -1


# What each measure means when it moves, and which GOALS.md objective it serves.
MEANING = {
    "youtube_published": ("O1 arrivals", "videos a stranger can actually find"),
    "products_live": ("O3 purchase", "products live on the site"),
    "videos_vertical": ("O1 arrivals", "vertical videos built"),
    "videos_wide": ("O1 arrivals", "16:9 videos built"),
    "captions": ("O1 arrivals", "caption files built"),
    "avif": ("O1 arrivals", "optimised images"),
    "undelivered_media": ("reliability",
                          "rendered files with no copy outside build/"),
}
# Moving these is real progress. Everything else is preparation.
OUTCOME_KEYS = ("youtube_published", "products_live")


def load_prev() -> dict:
    if os.path.exists(STATE):
        try:
            return json.load(io.open(STATE, encoding="utf-8"))
        except Exception:                                       # noqa: BLE001
            pass
    return {}


def carry_forward(key: str, now: dict, prev: dict) -> dict:
    """Keep the last MEASURED value of `key`, and say when it was taken.

    Found live this cycle: a real session measured youtube_published go from
    0 to 1 at 15:02 today, and this run, with no egress to YouTube, wrote
    None straight over it, which next_action() then rendered as "the channel
    holds None" next to a "Publish" recommendation, exactly backwards from
    the real state. Mirrors ops/dashboard.py's own carry_forward for
    revenue_month: the standing answer lives under its own key, written only
    by a run that actually measured, so no run of consecutive blind cycles
    can erase it, and a stale answer is always labelled with its own age
    rather than passed off as fresh.

    Returns (value, as_of, is_fresh).
    """
    if now.get(key) is not None:
        return now[key], now["at"], True
    last = prev.get(key + "_last_measured")
    when = prev.get(key + "_measured_at")
    if last is None:
        # No standing answer exists yet either (first run after this fix, or
        # never once measured). Fall back to whatever the previous run's raw
        # field held, which may itself be honestly None.
        last, when = prev.get(key), prev.get("at")
    return last, when, False


def next_action(persisted: dict) -> str:
    """The single next thing, chosen by the constraint in GOALS.md.

    Takes the persisted, carry-forward-merged state (see main()), not a raw
    measurement, so a run that could not reach YouTube reasons from the last
    real count instead of treating "could not check" as "confirmed empty."
    """
    yt = persisted.get("youtube_published_last_measured")
    yt_fresh = persisted.get("youtube_published") is not None
    yt_asof = persisted.get("youtube_published_measured_at")
    videos_ready = (persisted.get("videos_vertical") or 0) + (persisted.get("videos_wide") or 0)
    captions_ready = persisted.get("captions") or 0

    if yt is None:
        return ("Unknown: no run has ever been able to reach YouTube to check "
                "the channel. %d videos and %d caption files exist, ready to "
                "publish; needs a session with real egress to confirm the "
                "channel's real state before recommending publish over "
                "anything else." % (videos_ready, captions_ready))
    if yt == 0 and (persisted.get("videos_wide") or 0) >= 100:
        age = "" if yt_fresh else " (last confirmed %s, not rechecked this run)" % yt_asof
        return ("Publish. %d videos and %d caption files exist and the "
                "channel held 0%s. Nothing downstream of arrivals matters "
                "until this moves." % (videos_ready, captions_ready, age))
    if persisted.get("products_live") and persisted["products_live"] < 159:
        return "Production is behind the repository. Deploy."
    if not yt_fresh:
        return ("Last confirmed YouTube count was %s as of %s; this run could "
                "not reach YouTube to recheck. Work the next unblocked item "
                "in BACKLOG.md, checked against GOALS.md section 0 before "
                "starting." % (yt, yt_asof))
    return ("Work the next unblocked item in BACKLOG.md, checked against "
            "GOALS.md section 0 before starting.")


def main() -> int:
    quiet = "--quiet" in sys.argv
    now = measure()
    prev = load_prev()

    moved, flat = [], []
    for k, v in now.items():
        if k == "at" or k not in MEANING:
            continue
        p = prev.get(k)
        if p is None or v is None:
            continue
        if v != p:
            moved.append((k, p, v))
        else:
            flat.append(k)

    outcome_moved = [m for m in moved if m[0] in OUTCOME_KEYS]

    persisted = dict(now)
    for key in ("youtube_published", "products_live"):
        value, as_of, _fresh = carry_forward(key, now, prev)
        persisted[key + "_last_measured"] = value
        persisted[key + "_measured_at"] = as_of

    lines = ["", "## %s" % now["at"], ""]
    if moved:
        lines.append("**Moved**")
        for k, p, v in moved:
            obj, what = MEANING[k]
            lines.append("- %s: %s to %s  (%s, %s)" % (k, p, v, obj, what))
    else:
        lines.append("**Nothing measurable moved since the last check-in.**")
    if not outcome_moved:
        lines.append("")
        lines.append("**No outcome moved.** Published videos and live products "
                     "are the two numbers a stranger can see. Everything else "
                     "this hour was preparation, which is legitimate but is not "
                     "the same as progress.")
    lines.append("")
    lines.append("Commits in 24h: %s. Recorded as effort, not as a result."
                 % commits_24h_text(now["commits_24h"]))
    lines.append("")
    lines.append("**Next:** " + next_action(persisted))
    entry = "\n".join(lines)

    if not os.path.exists(LOG):
        io.open(LOG, "w", encoding="utf-8", newline="").write(
            "# Hourly check-in log\n\nWhat moved, what did not, and what is "
            "next. Written by ops/checkin.py so the record is measured rather "
            "than remembered.\n")
    io.open(LOG, "a", encoding="utf-8", newline="").write(entry + "\n")
    io.open(STATE, "w", encoding="utf-8", newline="").write(
        json.dumps(persisted, indent=1, sort_keys=True) + "\n")

    if not quiet:
        print(entry)
    # Non-zero when no outcome moved, so a run that only felt productive is
    # visible as such in CI rather than passing quietly.
    return 0 if outcome_moved else 1


if __name__ == "__main__":
    sys.exit(main())
