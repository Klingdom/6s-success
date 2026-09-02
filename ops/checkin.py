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


def measure() -> dict:
    """Only things that are true outside this repository, plus asset counts.

    Commit count is deliberately NOT a success measure. It is recorded as
    context so effort and outcome can be told apart.
    """
    m = {
        "at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "commits_24h": int(sh("git", "log", "--since=24 hours ago",
                              "--oneline").count("\n") or 0),
        "videos_vertical": count("build/video/zones/*.mp4"),
        "videos_wide": count("build/video/zones-16x9/*.mp4"),
        "captions": count("build/video/zones/*.srt"),
        "youtube_published": youtube_videos(),
        "products_live": live_products(),
        "avif": count("site/**/*.avif"),
    }
    return m


# What each measure means when it moves, and which GOALS.md objective it serves.
MEANING = {
    "youtube_published": ("O1 arrivals", "videos a stranger can actually find"),
    "products_live": ("O3 purchase", "products live on the site"),
    "videos_vertical": ("O1 arrivals", "vertical videos built"),
    "videos_wide": ("O1 arrivals", "16:9 videos built"),
    "captions": ("O1 arrivals", "caption files built"),
    "avif": ("O1 arrivals", "optimised images"),
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


def next_action(now: dict) -> str:
    """The single next thing, chosen by the constraint in GOALS.md."""
    if now.get("youtube_published") in (0, None) and now.get("videos_wide", 0) >= 100:
        return ("Publish. 228 videos and 114 caption files exist and the channel "
                "holds %s. Nothing downstream of arrivals matters until this "
                "moves." % now.get("youtube_published"))
    if now.get("products_live") and now["products_live"] < 159:
        return "Production is behind the repository. Deploy."
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
                 % now["commits_24h"])
    lines.append("")
    lines.append("**Next:** " + next_action(now))
    entry = "\n".join(lines)

    if not os.path.exists(LOG):
        io.open(LOG, "w", encoding="utf-8", newline="").write(
            "# Hourly check-in log\n\nWhat moved, what did not, and what is "
            "next. Written by ops/checkin.py so the record is measured rather "
            "than remembered.\n")
    io.open(LOG, "a", encoding="utf-8", newline="").write(entry + "\n")
    io.open(STATE, "w", encoding="utf-8", newline="").write(
        json.dumps(now, indent=1, sort_keys=True) + "\n")

    if not quiet:
        print(entry)
    # Non-zero when no outcome moved, so a run that only felt productive is
    # visible as such in CI rather than passing quietly.
    return 0 if outcome_moved else 1


if __name__ == "__main__":
    sys.exit(main())
