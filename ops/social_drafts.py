#!/usr/bin/env python3
"""
Daily Facebook and X drafts, emailed for Phil to post himself.

WHY THIS EXISTS
---------------
GOALS.md names LinkedIn as "the only channel we actually post to," and
ops/linkedin_drafts.py has been serving Phil's own LinkedIn posts out of the
book corpus since before this file existed. The same corpus holds 155
Facebook posts and 723 X posts, real, finished, written by Phil, and until
this file, corpus_posts.py could read them (pool("facebook-post"),
pool("x-post")) but nothing turned that into something a person opens over
coffee and posts. Two more channels sat fully written and fully unused, the
same "distribution beats production" gap GOALS.md decision rule 1 names,
just on two more platforms nobody had pointed a draft mailer at yet.

No account exists for either platform yet (OWNER-ACTIONS.md item 18). This
still ships now rather than waiting for one: CLAUDE.md 0.5 says build
everything up to the gate so the owner's action is a single step, and
Pinterest/Instagram's own captions were built the same way, ahead of the
account.

WHAT THIS IS AND IS NOT
------------------------
It drafts. Phil posts. No API call to either platform exists here and none
should: Facebook and X both restrict what a script may post as a page or
account without going through their own developer review, and a message
that was plainly not chosen by a person is worse than none.

WHY X GETS A CHARACTER FILTER AND FACEBOOK DOES NOT
----------------------------------------------------
A single X post is capped at 280 characters. Facebook has no limit that
would bind here. Filtering happens through corpus_posts.take()'s own
`where` predicate, before rotation, so an over-length post is never marked
served: it stays in the pool for a future cycle where clean() might have
been tightened, rather than being silently spent on nothing.

Run:  python ops/social_drafts.py --preview
      python ops/social_drafts.py --platform facebook --preview
      python ops/social_drafts.py --send ADDRESS
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus_posts import take, pool                             # noqa: E402

X_CHAR_CAP = 280

PLATFORMS = {
    "facebook": {"kind": "facebook-post", "n": 3, "label": "Facebook posts",
                 "where": None},
    "x": {"kind": "x-post", "n": 4, "label": "X posts",
          "where": lambda p: len(p["body"]) <= X_CHAR_CAP},
}


def build(platform: str, today: datetime.date | None = None,
          record: bool = False) -> tuple[str, str]:
    if platform not in PLATFORMS:
        raise SystemExit(f"unknown platform {platform!r}, choose from "
                          f"{sorted(PLATFORMS)}")
    cfg = PLATFORMS[platform]
    today = today or datetime.date.today()

    posts = take(cfg["kind"], cfg["n"], record=record, where=cfg["where"])
    remaining = len(pool(cfg["kind"]))
    if cfg["where"]:
        remaining = len([p for p in pool(cfg["kind"]) if cfg["where"](p)])
        # Re-check the actual posts against the platform limit directly,
        # rather than trust that the filter passed to take() was applied
        # correctly: the whole point of a hard platform limit is that a post
        # over it cannot be published as written.
        over = [p for p in posts if len(p["body"]) > X_CHAR_CAP]
        assert not over, (f"{len(over)} post(s) exceed X's {X_CHAR_CAP}-"
                           f"character limit and should never have been "
                           f"selected: {[p['title'] for p in over]}")

    L = [f"{cfg['n']} {cfg['label']} to publish today, {today:%A %d %B}.", ""]
    if posts:
        L += [f"These are your own writing, out of the chapter content "
              f"packages. {remaining} usable {cfg['label'].lower()} sit in "
              "that corpus and none had ever been published. Post as "
              "written, or edit freely.", ""]
        for i, p in enumerate(posts, 1):
            tag = f", {len(p['body'])} chars" if platform == "x" else ""
            L += ["=" * 64,
                  f"{i}. {p['title']}   [{p['chapter']}, {p['words']} words{tag}]",
                  "", p["body"], ""]
    else:
        L += ["The corpus could not be read this run, so there is nothing "
              "to post today.", ""]

    subject = f"{cfg['n']} {cfg['label']} to publish, {today:%a %d %b}"
    return subject, "\n".join(L)


def build_all(today: datetime.date | None = None,
              record: bool = False) -> tuple[str, str]:
    """Both platforms in one message, one email a day rather than two.

    Phil already reads a separate LinkedIn digest every morning
    (linkedin-drafts.yml); adding two more standalone emails for two
    platforms he has not yet created an account on is more inbox than the
    content is worth today. One combined message keeps this to one new
    email, in the same shape as the LinkedIn one, until there is a reason
    to split it.
    """
    today = today or datetime.date.today()
    parts, subjects = [], []
    for platform in ("facebook", "x"):
        subject, text = build(platform, today=today, record=record)
        subjects.append(subject.split(" to publish", 1)[0])
        parts.append(text)
    combined_subject = f"{' + '.join(subjects)} to publish, {today:%a %d %b}"
    combined_text = ("\n\n" + "#" * 64 + "\n\n").join(parts)
    return combined_subject, combined_text


if __name__ == "__main__":
    will_send = "--send" in sys.argv
    to = sys.argv[sys.argv.index("--send") + 1] if will_send else None

    if "--platform" in sys.argv:
        platform = sys.argv[sys.argv.index("--platform") + 1]
        subject, text = build(platform, record=will_send)
    else:
        subject, text = build_all(record=will_send)

    assert "TODO" not in text and "[insert" not in text.lower(), \
        "an unfinished corpus file reached the draft"

    if will_send:
        from mailer import send                                # noqa: E402
        send(to, subject, text)
        print("sent:", subject)
    else:
        print("SUBJECT:", subject, "\n")
        print(text)
