#!/usr/bin/env python3
"""
Daily Bluesky drafts, emailed for Phil to post himself.

WHY THIS EXISTS
---------------
Bluesky already has a real account and already sends this site real
visitors: 5 all time (go.bsky.app 3, bsky.app 2), read from the all-time
referrer table (ops/NIGHTLY-LOG.md, 2026-09-29; GOALS.md section 3;
OWNER-ACTIONS.md's own 30-day table), at zero authored cost, since nobody
had ever built anything for it. LinkedIn and Bluesky are the two channels
GOALS.md names as proven to work; ops/linkedin_drafts.py has served Phil's
own LinkedIn posts for weeks and ops/social_drafts.py drafts for Facebook
and X before either even has an account (OWNER-ACTIONS.md item 18). Bluesky,
already live, already producing traffic, had no drafting pipeline at all,
the exact "distribution beats production" gap GOALS.md decision rule 1
names, on the one channel that does not even need an owner gate first.

WHAT IT DRAFTS FROM
--------------------
Bluesky's post limit is 300 characters. ops/social_drafts.py already filters
the same corpus's x-post entries to X's 280-character cap before serving
them, a strict subset of Bluesky's own limit, so the identical, already
vetted pool fits without touching a single word of it. Tracked under its
own rotation key ("bluesky-post"), not "x-post": corpus_posts.take()'s new
pool_kind parameter reads the x-post pool while recording served ids under
a key this file owns, so once X gets its own account, neither pipeline will
silently exhaust the other's supply by marking a post served under one name
and skipping it under the other without either reader ever having shown it.

WHAT THIS IS AND IS NOT
------------------------
It drafts. Phil posts. No Bluesky API call exists here and none should: the
AT Protocol takes an app password, a real account credential this repository
does not hold and should not (CLAUDE.md sections 32/34), and a post that was
plainly not chosen by a person lands worse than none.

Run:  python ops/bluesky_drafts.py --preview
      python ops/bluesky_drafts.py --send ADDRESS
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus_posts import take, pool, load_rotation              # noqa: E402

BSKY_CHAR_CAP = 300
KIND = "bluesky-post"
POOL_KIND = "x-post"
N = 3


def _fits(p: dict) -> bool:
    return len(p["body"]) <= BSKY_CHAR_CAP


def build(today: datetime.date | None = None, record: bool = False) -> tuple[str, str]:
    today = today or datetime.date.today()

    posts = take(KIND, N, record=record, where=_fits, pool_kind=POOL_KIND)

    # Re-derive "remaining" the same honest way social_drafts.py does: the
    # filtered pool minus what is actually served, not a bare pool size that
    # never moves. Found for that file 2026-09-12; guarded against here from
    # the start rather than reintroducing the same bug.
    filtered = [p for p in pool(POOL_KIND) if _fits(p)]
    served = set(load_rotation()["served"].get(KIND, []))
    served |= {p["id"] for p in posts}
    remaining = len([p for p in filtered if p["id"] not in served])

    # Re-check the actual posts against Bluesky's own limit directly, rather
    # than trust that the filter passed to take() was applied correctly.
    over = [p for p in posts if len(p["body"]) > BSKY_CHAR_CAP]
    assert not over, (f"{len(over)} post(s) exceed Bluesky's {BSKY_CHAR_CAP}-"
                       f"character limit and should never have been "
                       f"selected: {[p['title'] for p in over]}")

    L = [f"{N} Bluesky posts to publish today, {today:%A %d %B}.", ""]
    if posts:
        L += [f"Your own writing, the same already-280-character-filtered "
              f"pool your X drafts would use once X has an account, which "
              f"fits Bluesky's higher 300-character cap without editing a "
              f"word. {remaining} usable post(s) left in that pool, none "
              f"published before. Post as written, or edit freely.", ""]
        for i, p in enumerate(posts, 1):
            L += ["=" * 64,
                  f"{i}. {p['title']}   [{p['chapter']}, {len(p['body'])} chars]",
                  "", p["body"], ""]
    else:
        L += ["The corpus could not be read this run, so there is nothing "
              "to post today.", ""]

    subject = f"{N} Bluesky posts to publish, {today:%a %d %b}"
    return subject, "\n".join(L)


if __name__ == "__main__":
    will_send = "--send" in sys.argv
    to = sys.argv[sys.argv.index("--send") + 1] if will_send else None
    subject, text = build(record=will_send)

    assert "TODO" not in text and "[insert" not in text.lower(), \
        "an unfinished corpus file reached the draft"

    if will_send:
        from mailer import send                                # noqa: E402
        send(to, subject, text)
        print("sent:", subject)
    else:
        print("SUBJECT:", subject, "\n")
        print(text)
