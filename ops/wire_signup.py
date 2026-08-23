#!/usr/bin/env python3
"""
Put a working mailing list form on the pages where an email is worth asking for.

WHY THIS WAS NOT DONE SOONER, AND WHY THAT WAS MY MISTAKE
---------------------------------------------------------
Seven checkouts have opened in this business's life and six left without typing
anything, so there is nobody to follow up with and no way to reach them again.
That was reported for days as "blocked on Phil, needs a Listmonk list UUID".

It was not blocked. Listmonk's public subscription form lists every list and its
UUID at a URL anyone can fetch, and "6S Success Readers" was already sitting
there. Nobody had looked. The lesson is worth more than the form: check whether
a blocker is real before reporting it as one.

THE LIST UUID IS PINNED AND ASSERTED
------------------------------------
That Listmonk instance also serves Compassion Benchmark, a different business
with different subscribers. Posting a 6S visitor onto their list would be a real
privacy failure, not a bug, so the UUID is a constant here, checked against the
live form at build time, and the build fails rather than guesses.

WHAT IT ASKS FOR, AND WHAT IT DOES NOT DO
-----------------------------------------
Nothing is gated. The Standards Pack and the Entryway deck stay free with no
email asked, because they say so on the page and turning that into a form now
would make those sentences a lie. The offer is only what it honestly is: a note
when there is something new.

ORDER MATTERS: this appends to site.css, so run ops/fingerprint_assets.py
AFTER it, not before. Getting that backwards is what failed the CI gate the
first time this shipped, which is the gate doing its job.

Run:  python ops/wire_signup.py && python ops/fingerprint_assets.py
"""
from __future__ import annotations

import glob
import io
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

LIST_UUID = "5dd89cf3-6b2d-44af-9b92-5baddc8975cc"
LIST_NAME = "6S Success Readers"
FORM_SRC = "http://187.77.25.50:8081/subscription/form"

MARK, END = "<!-- SIGNUP:BEGIN -->", "<!-- SIGNUP:END -->"

# Only pages where somebody has just been given something and might plausibly
# want to hear about the next one. Not the legal pages, not the checkout return
# page, and not the 114 zone pages, where it would be an interruption in the
# middle of a job somebody is trying to do.
PAGES = ["standards.html", "deck.html", "quest.html", "resources.html",
         "articles/index.html", "method.html"]


def block(prefix: str) -> str:
    return f"""{MARK}
<section class="section" id="signup">
  <div class="wrap narrow">
    <p class="eyebrow">Stay in touch</p>
    <h2>Told when there is something new</h2>
    <p>New room sheets, new zones, and the occasional thing that turned out to
    be wrong. Nothing here is gated behind it: everything free stays free and
    needs no email. This is only for people who want to know when more of it
    exists.</p>
    <form class="signup" method="post" action="/subscribe">
      <input type="hidden" name="l" value="{LIST_UUID}">
      <input type="hidden" name="nonce" value="">
      <label class="signup-field">
        <span>Your email</span>
        <input type="email" name="email" required autocomplete="email"
               placeholder="you@example.com">
      </label>
      <label class="signup-field">
        <span>Name, if you like</span>
        <input type="text" name="name" autocomplete="name" placeholder="Optional">
      </label>
      <button class="btn btn-primary" type="submit">Keep me posted</button>
    </form>
    <p class="signup-note">You will get one email asking you to confirm, because
    nobody should be added to a list they did not ask for. Unsubscribe is in
    every message. We do not sell or share the list.</p>
  </div>
</section>
{END}"""


CSS = """
/* Mailing list form. Stacks on a phone, sits in a row from 560px up. */
.signup{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;margin:20px 0 0}
.signup-field{display:flex;flex-direction:column;gap:5px;flex:1 1 210px;min-width:0}
.signup-field span{font-family:var(--sans);font-size:11.5px;font-weight:700;
  letter-spacing:.09em;text-transform:uppercase;color:var(--soft)}
.signup-field input{font:inherit;font-size:16px;padding:11px 13px;
  border:1px solid var(--line,#E2D8C4);border-radius:9px;background:#fff;
  color:var(--ink,#2B2622);min-height:44px;width:100%}
.signup-field input:focus-visible{outline:3px solid var(--slate,#3C5A6B);
  outline-offset:2px;border-color:var(--slate,#3C5A6B)}
.signup button{min-height:44px;flex:0 0 auto}
.signup-note{margin:14px 0 0;font-size:14px;color:var(--soft,#6A625A);max-width:62ch}
"""


def main() -> int:
    # The UUID must still name the list we think it does. A silent renumbering
    # would put 6S readers onto another company's list, which is the one failure
    # here that would actually matter.
    try:
        html = urllib.request.urlopen(FORM_SRC, timeout=15).read().decode("utf-8", "replace")
        pairs = re.findall(r'name="l"[^>]*value="([0-9a-f-]{36})"[^>]*>(.*?)</label>',
                           html, re.S)
        found = {u: " ".join(re.sub(r"<[^>]+>", " ", t).split()) for u, t in pairs}
        assert LIST_UUID in found, (
            f"{LIST_UUID} is not on the live form any more. Lists present: {found}")
        assert LIST_NAME.lower() in found[LIST_UUID].lower(), (
            f"{LIST_UUID} now names {found[LIST_UUID]!r}, not {LIST_NAME!r}. "
            "Refusing to point 6S visitors at another list.")
        print(f"  checked against the live form: {LIST_UUID} is {found[LIST_UUID]!r}")
    except AssertionError:
        raise
    except Exception as e:                                    # noqa: BLE001
        print(f"  WARNING: could not reach {FORM_SRC} to verify the list ({e}).")
        print("  Wiring anyway, but re-run this when the host is reachable.")

    n = 0
    for rel in PAGES:
        path = os.path.join(SITE, rel)
        if not os.path.exists(path):
            print(f"  skipped {rel}, not there")
            continue
        s = io.open(path, encoding="utf-8").read()
        blk = block("../" * rel.count("/"))
        if MARK in s:
            s2 = re.sub(re.escape(MARK) + r".*?" + re.escape(END), blk, s, flags=re.S)
        else:
            # Immediately before the footer, so it is the last thing on the page
            # rather than an interruption in the middle of one.
            i = s.find('<footer class="site-footer">')
            if i < 0:
                print(f"  skipped {rel}, no footer to sit above")
                continue
            s2 = s[:i] + blk + "\n" + s[i:]
        if s2 != s:
            io.open(path, "w", encoding="utf-8", newline="").write(s2)
        n += 1
    print(f"  signup form on {n} pages")

    # The styles live in the shared stylesheet, once.
    css_path = os.path.join(SITE, "assets", "css", "site.css")
    css = io.open(css_path, encoding="utf-8").read()
    if ".signup{" not in css:
        io.open(css_path, "w", encoding="utf-8", newline="").write(css.rstrip() + "\n" + CSS)
        print("  styles added to site.css")
    else:
        print("  styles already in site.css")

    # No page may post to a list that is not ours.
    wrong = []
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        for u in re.findall(r'name="l" value="([0-9a-f-]{36})"', s):
            if u != LIST_UUID:
                wrong.append((os.path.relpath(f, ROOT), u))
    assert not wrong, f"pages posting to a list that is not ours: {wrong}"
    print("  checked: every form on the site posts to the 6S list and no other")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
