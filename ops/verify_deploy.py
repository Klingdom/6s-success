#!/usr/bin/env python3
"""
Prove a deployment actually works, from the outside.

A green container proves nginx started. A 200 proves something answered. Neither
proves the customer can use the site. This checks the things that would actually
be broken.

The parking page check matters most: Hostinger's parked domain answers 200 on
every path, including paths that do not exist, so an uptime check that only looks
at status codes reports a parked domain as a healthy website.

Run:  python ops/verify_deploy.py https://6s-success.com
      python ops/verify_deploy.py http://VPS_IP        (before DNS is moved)
      python ops/verify_deploy.py http://VPS_IP 6s-success.com

The third form is the useful one while a domain is still parked. It connects to
the VPS by address but sends "Host: 6s-success.com", which is exactly what the
browser will send once DNS moves. That proves the virtual host is right BEFORE
changing any DNS record, so a broken vhost is found in private rather than in
public with the domain already pointed at it.
"""
import sys
import urllib.request
import urllib.error

PAGES = ["", "method", "rooms", "shop", "book", "consulting", "about", "contact",
         "cart", "resources", "privacy", "terms", "accessibility", "disclaimer"]
NONSENSE = "this-path-does-not-exist-6s-check"

results = []


HOST_HEADER = None


def get(url, timeout=20):
    headers = {"User-Agent": "6s-deploy-check"}
    if HOST_HEADER:
        # Ask the server the same question the browser will ask after DNS moves.
        headers["Host"] = HOST_HEADER
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, str(e)


def check(label, ok, detail=""):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" :: {detail}" if detail else ""))


def main(base):
    base = base.rstrip("/")
    suffix = f"  asking as Host: {HOST_HEADER}" if HOST_HEADER else ""
    print(f"Verifying {base}{suffix}")
    print()

    # 1. The parking page test comes first, because if this fails every other
    #    check below passes for the wrong reason.
    code, body = get(f"{base}/{NONSENSE}")
    check("a path that does not exist returns 404, not 200",
          code == 404, f"got {code}")
    check("the response is not a parked domain page",
          "Parked Domain" not in body and "dns-parking" not in body)

    # 2. Every page answers, and answers with our content.
    code, home = get(base + "/")
    check("homepage answers 200", code == 200, f"got {code}")
    check("homepage is the 6S site",
          "6S Success" in home, "expected the site title in the body")

    missing = []
    for p in PAGES:
        c, _ = get(f"{base}/{p}")
        if c != 200:
            missing.append(f"{p or 'index'}={c}")
    check(f"all {len(PAGES)} pages answer 200", not missing, ", ".join(missing))

    # 3. The short URLs printed in all 50 book chapters. These depend on the
    #    try_files $uri.html rule, so they break silently if the nginx config
    #    is not the one in this repository.
    bad = [u for u in ("resources", "method", "book") if get(f"{base}/{u}")[0] != 200]
    check("book short URLs resolve without .html", not bad, ", ".join(bad))

    # 4. Assets, because a site that renders unstyled is not deployed.
    for asset in ("assets/css/site.css", "assets/js/site.js"):
        c, _ = get(f"{base}/{asset}")
        check(f"{asset} loads", c == 200, f"got {c}")

    # 5. The legal pages, which must exist before anything is sold.
    legal = [p for p in ("privacy", "terms", "accessibility", "disclaimer")
             if get(f"{base}/{p}")[0] != 200]
    check("all 4 legal pages load", not legal, ", ".join(legal))

    # 6. Truthfulness of the site as served, not as committed.
    _, contact = get(f"{base}/contact")
    check("contact page does not claim to send mail it cannot send",
          "does not send email yet" not in contact or "Nothing has been sent" in contact)

    passed = sum(1 for r in results if r)
    print(f"\n{passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python ops/verify_deploy.py URL [HOST_HEADER]")
    if len(sys.argv) > 2:
        HOST_HEADER = sys.argv[2]
    sys.exit(main(sys.argv[1]))
