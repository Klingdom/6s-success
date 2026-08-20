#!/usr/bin/env python3
"""
Tell search engines the pages exist, without waiting to be crawled.

IndexNow is a protocol Bing, Yandex and Seznam support. You host a key file at
the site root and POST a list of URLs; they fetch the key to prove you control
the domain, then queue the URLs. No account, no verification, no waiting for a
crawler to find its own way in.

Google does not participate, which is why Search Console still matters and is
still on Phil's list. This covers everybody else, and it covers them today.

Why it matters here: 148 pages went live on a domain that was a parking page
yesterday. Nothing links to it from anywhere on the internet. Left alone, a
crawler might find the sitemap in days or weeks. This is the difference between
the traffic clock starting now and starting whenever.

The key is not a secret. Its whole job is to be fetched by a search engine to
prove the same person controls both the key file and the submission.

Run:  python ops/indexnow.py --check     show what would be submitted
      python ops/indexnow.py --submit    submit them
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
HOST = "6s-success.com"
BASE = f"https://{HOST}"
# A fixed key, committed on purpose: it must stay stable, and it is public by
# design. Regenerating it would just orphan the file already on the site.
KEY = "6a1f4c2e8b7d4a3f9e5c1b8d2a7f6e30"
ENDPOINT = "https://api.indexnow.org/indexnow"


def urls():
    sm = os.path.join(SITE, "sitemap.xml")
    with open(sm, encoding="utf-8") as fh:
        return re.findall(r"<loc>([^<]+)</loc>", fh.read())


def write_key():
    """The key file has to be reachable at the site root, or submissions are
    rejected as unverified."""
    p = os.path.join(SITE, f"{KEY}.txt")
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(KEY + "\n")
    # A second copy at a predictable name, so a human can find it later without
    # knowing the key.
    with open(os.path.join(SITE, "indexnow.txt"), "w", encoding="utf-8", newline="") as fh:
        fh.write(KEY + "\n")
    return p


def submit(batch):
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"{BASE}/{KEY}.txt",
        "urlList": batch,
    }).encode()
    req = urllib.request.Request(ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:200]
    except Exception as e:
        return None, str(e)[:160]


def main(do_submit):
    u = urls()
    print(f"  {len(u)} URLs in the sitemap")
    print(f"  key file: {BASE}/{KEY}.txt")
    live = None
    try:
        with urllib.request.urlopen(f"{BASE}/{KEY}.txt", timeout=15) as r:
            live = r.read().decode().strip()
    except Exception:
        pass
    print(f"  key file reachable: {'yes' if live == KEY else 'NO, deploy it first'}")

    if not do_submit:
        for x in u[:4]:
            print(f"    {x}")
        print(f"    ... and {len(u)-4} more")
        return 0

    if live != KEY:
        print("  Refusing to submit: the key file is not live yet, so every"
              " submission would be rejected as unverified.")
        return 1

    # 10,000 per request is the documented ceiling. Batching well under it.
    ok = 0
    for i in range(0, len(u), 500):
        batch = u[i:i + 500]
        code, body = submit(batch)
        print(f"  batch {i//500 + 1}: {len(batch)} urls -> HTTP {code} {body[:80]}")
        if code in (200, 202):
            ok += len(batch)
    print(f"  accepted: {ok} of {len(u)}")
    return 0 if ok else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode == "--check":
        p = write_key()
        print(f"  wrote {os.path.relpath(p, ROOT)} and site/indexnow.txt")
    sys.exit(main(mode == "--submit"))
