#!/usr/bin/env python3
"""
The cheap refusals in publish-image.yml must run BEFORE the long preflight.

WHY THIS TEST EXISTS
--------------------
Twice within a day (2026-10-03/04, runs 37162xxx and 37166876121) the image
build failed because a commit changed site/ and left site/build-id.txt
describing the older tree. Both times the explanation came out of the Preflight
step about seventeen minutes in, and both times the consequence was that
nothing could deploy until somebody pushed a one-line restamp.

A local control for exactly that commit already exists in .githooks/pre-commit.
It did not fire: git does not enable hooks on clone, and those commits came from
fresh checkouts where core.hooksPath was never set. gate_hooks_enabled warns
about it, correctly, as one warning among thirty-three.

So `python ops/build_id.py --check` now runs as its own step beside the
fingerprint check, before Preflight. The entire value of that change is the
ORDER: the same failure, thirty seconds in instead of seventeen minutes, with
the fix named in the first thing a reader sees. An edit that moves it after
Preflight would leave the step present and the benefit gone, which is the
shape this file exists to catch.

Run:  python ops/tests/test_publish_image_cheap_checks_first.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
WF = os.path.join(ROOT, '.github', 'workflows', 'publish-image.yml')

# Every step whose whole point is to fail fast, and which therefore must come
# before the seventeen-minute one. Named exactly as they appear.
CHEAP = [
    'Refuse to publish a secret',
    'Refuse to publish stale asset fingerprints',
    'Refuse to publish a stale build id',
]
SLOW = 'Preflight, including generator ownership'


def step_names(text):
    return re.findall(r'^' + chr(32) * 6 + r'- name: (.+?)' + chr(36),
                      text, re.M)


def main():
    fails = []
    text = io.open(WF, encoding='utf-8').read()
    names = [n.strip() for n in step_names(text)]
    if len(names) < 8:
        print('NOT VERIFIED: parsed only %d step name(s) from %s, so the '
              'ordering below was never checked. The step syntax has probably '
              'changed.' % (len(names), os.path.relpath(WF, ROOT)))
        return 0
    if SLOW not in names:
        fails.append('the long step %r is not in publish-image.yml any more, '
                     'so this test cannot order anything against it' % SLOW)
    else:
        slow_at = names.index(SLOW)
        for cheap in CHEAP:
            if cheap not in names:
                fails.append('the fast-failing step %r is gone from '
                             'publish-image.yml' % cheap)
                continue
            if names.index(cheap) > slow_at:
                fails.append('%r runs AFTER %r, so the build pays the full '
                             'preflight before reporting a defect it could '
                             'have reported in seconds' % (cheap, SLOW))

    # The build-id step must check, never restamp. Deploy verification compares
    # the LIVE build id against the one committed in the repository, so an image
    # stamped with a value no commit carries would make production permanently
    # unable to report itself current.
    m = re.search(r'- name: Refuse to publish a stale build id(.*?)(?=^' + chr(32) * 6 + r'- name: )', text, re.S | re.M)
    if not m:
        fails.append('could not isolate the build-id step body to check what '
                     'it runs')
    else:
        body = m.group(1)
        run = [l for l in body.splitlines() if l.strip().startswith('run:')]
        if not run:
            fails.append('the build-id step has no run: line')
        elif '--check' not in run[0]:
            fails.append('the build-id step runs %r without --check, so it '
                         'would RESTAMP during the build and ship an id no '
                         'commit carries' % run[0].strip())

    if fails:
        print('FAIL')
        for f in fails:
            print(' -', f)
        return 1
    print('OK: publish-image.yml runs all %d cheap refusal(s) before the long '
          'preflight, and the build-id step checks rather than restamps'
          % len(CHEAP))
    return 0


if __name__ == '__main__':
    sys.exit(main())
