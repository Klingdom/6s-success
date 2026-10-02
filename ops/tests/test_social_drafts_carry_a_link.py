#!/usr/bin/env python3
"""
Prove every social draft carries a working, attributable link to the site.

WHY THIS EXISTS
---------------
Found 2026-10-02 by reading what these tools actually emit rather than what
their docstrings say they are for. Every LinkedIn draft ended in words like
"free in the online book" and "Read how in the online book, free", and every
Bluesky draft was a clean excerpt, and **not one of them contained a URL**.

GOALS.md names arrivals as the constraint and can show only two channels that
have ever produced a visitor: LinkedIn, which referred one on sixteen separate
days between 23 August and 28 September, and Bluesky. The posts being generated
for both had no clickable path to the site at all.

Two things are checked, and the second is the one that will rot first:

  1. The link is there, in every post, from both tools.
  2. It points at a page that actually exists in site/, and carries a `from=`
     parameter. A draft advertising a 404 is worse than a draft with no link,
     and an untracked link makes a channel that works indistinguishable from
     one that does not, because referrers are stripped by some clients and
     `(direct)` is already most of this site's traffic.

Nothing here sends anything or records a rotation.

Run:  python ops/tests/test_social_drafts_carry_a_link.py
"""
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import bluesky_drafts                                          # noqa: E402
import linkedin_drafts                                         # noqa: E402

SITE = os.path.join(ROOT, "site")


def page_exists(link):
    """Does the link's path resolve to a file we actually publish?"""
    path = urllib.parse.urlparse(link).path.lstrip("/")
    if not path:
        return os.path.exists(os.path.join(SITE, "index.html"))
    cand = os.path.join(SITE, path.replace("/", os.sep))
    return (os.path.exists(cand) or os.path.exists(cand + ".html")
            or os.path.isdir(cand))


def main():
    fails = []

    for mod, name, tracked in ((bluesky_drafts, "bluesky_drafts", "from=bsky"),
                               (linkedin_drafts, "linkedin_drafts", "from=li")):
        link = getattr(mod, "LINK", None)

        # 1. The module declares a link at all.
        if not link:
            fails.append("%s has no LINK, so its posts point nowhere" % name)
            continue

        # 2. It is attributable. An untracked link makes a channel that works
        #    look identical to one that does not.
        if tracked not in link:
            fails.append("%s's LINK %r carries no %r parameter, so arrivals "
                         "from it cannot be told from direct traffic"
                         % (name, link, tracked))

        # 3. It resolves to a page this site actually publishes.
        if not page_exists(link):
            fails.append("%s's LINK %r does not resolve to anything under "
                         "site/, so the drafts advertise a 404"
                         % (name, link))

        # 4. Every post in a real build carries it. record=False so this
        #    neither sends nor advances anybody's rotation.
        subject, text = mod.build(record=False)
        blocks = [b for b in text.split("=" * 64) if b.strip()]
        posts = [b for b in blocks
                 if re.search(r"^\s*\d+\.\s", b) and "CONNECTION NOTE" not in b]
        if len(posts) < 2:
            fails.append("%s produced %d post block(s), too few for this test "
                         "to be checking anything" % (name, len(posts)))
        for b in posts:
            if link not in b:
                head = re.sub(r"\s+", " ", b).strip()[:60]
                fails.append("%s emitted a post with no link: %r" % (name, head))

    # 5. Bluesky's cap, measured on what is actually published: body plus the
    #    link. The pool is pre-filtered to X's 280 characters and 280 plus the
    #    link is over 300, so filtering on the body alone would emit posts
    #    that cannot be published as written.
    cap = bluesky_drafts.BSKY_CHAR_CAP
    link = bluesky_drafts.LINK
    subject, text = bluesky_drafts.build(record=False)
    for b in text.split("=" * 64):
        m = re.search(r"^\s*\d+\..*?\n\n(.*?)\n\s*$", b, re.S)
        if not m:
            continue
        body = m.group(1).strip()
        if len(body) > cap:
            fails.append("a Bluesky post is %d characters with its link, over "
                         "the %d cap: %r"
                         % (len(body), cap, body[:50]))
        if not body.endswith(link):
            fails.append("a Bluesky post does not end with the link: %r"
                         % body[-50:])

    # 6. THE FILTER ITSELF, not whichever posts today's rotation happened to
    #    pick. Case 5 above checks the real build, and on the day this test
    #    was written every selected post was short enough that relaxing the
    #    filter still produced valid output: the planted defect passed. A
    #    selection-dependent check cannot pin a selection rule, so this drives
    #    _fits() directly with a post engineered to be legal on its own and
    #    illegal once the link is added.
    cap = bluesky_drafts.BSKY_CHAR_CAP
    link = bluesky_drafts.LINK
    too_long = cap - len(link)        # fits alone, overflows with the link
    if bluesky_drafts._fits({"body": "x" * too_long}):
        fails.append("bluesky _fits() accepted a %d-character post, which is "
                     "%d with the link against a %d cap, so the filter is not "
                     "accounting for the link"
                     % (too_long, too_long + 1 + len(link), cap))
    comfortable = cap - len(link) - 10
    if not bluesky_drafts._fits({"body": "x" * comfortable}):
        fails.append("bluesky _fits() rejected a %d-character post that fits "
                     "comfortably with the link, so the filter is now too "
                     "strict and is shrinking the pool for nothing"
                     % comfortable)

    if fails:
        print("FAIL")
        for f in sorted(set(fails)):
            print(" -", f)
        return 1
    print("OK: both draft tools emit an existing, attributable link on every "
          "post, and every Bluesky post fits the cap with it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
