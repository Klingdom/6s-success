#!/usr/bin/env python3
"""
Tell search engines the pages exist, without waiting to be crawled.

IndexNow is a protocol Bing, Yandex, Seznam and Naver support. You host a key
file at the site root and POST a list of URLs; they fetch the key to prove you
control the domain, then queue the URLs. No account, no verification, no waiting
for a crawler to find its own way in.

Google does not participate, which is why Search Console still matters and is
still on Phil's list (OWNER-ACTIONS.md). This covers everybody else, and it
covers them today.

Why it matters here: 185 pages live on a domain that almost nothing on the
internet links to. Left alone, a crawler might find the sitemap in days or
weeks. This is the difference between the traffic clock starting now and
starting whenever.

The key is not a secret. Its whole job is to be fetched by a search engine to
prove the same person controls both the key file and the submission.

WHAT THIS FILE LEARNED THE HARD WAY
-----------------------------------
The first version printed "accepted: 181 of 181" and kept no record. Three
weeks later nobody could answer two questions that matter more than that line:
*when* did we last submit, and *which* URLs have never been submitted at all.
A page added yesterday looked exactly like a page submitted a month ago.

So every run now appends to ops/indexnow-log.json, and the set of
already-submitted URLs is kept there. --new submits only the difference, which
is what the protocol is actually for: it is a change-notification channel, and
re-blasting the whole site daily is how a domain earns a rate limit rather than
a crawl.

Run:  python ops/indexnow.py            what would be submitted, and what is new
      python ops/indexnow.py --new      submit only URLs never accepted before
      python ops/indexnow.py --submit   submit every URL in the sitemap
      python ops/indexnow.py --status   last submission, and the unsubmitted count
"""
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
LOG = os.path.join(ROOT, "ops", "indexnow-log.json")
HOST = "6s-success.com"
BASE = f"https://{HOST}"
# A fixed key, committed on purpose: it must stay stable, and it is public by
# design. Regenerating it would just orphan the file already on the site.
KEY = "6a1f4c2e8b7d4a3f9e5c1b8d2a7f6e30"
# The shared endpoint. It forwards to every participating engine, so one POST
# reaches Bing, Yandex, Seznam and Naver. Submitting to each engine's own
# endpoint as well would send the same URLs several times for no extra reach.
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH = 500          # documented ceiling is 10,000; well under it on purpose


# ------------------------------------------------------------------ inputs
def urls():
    """The canonical public URL set, read from the sitemap this site actually
    serves. Reading site/sitemap.xml rather than walking site/ means a page the
    sitemap deliberately excludes (noindex utility pages, the ownership
    verification file) is never announced to a search engine."""
    sm = os.path.join(SITE, "sitemap.xml")
    with open(sm, encoding="utf-8") as fh:
        return re.findall(r"<loc>([^<]+)</loc>", fh.read())


def load_log():
    try:
        with open(LOG, encoding="utf-8") as fh:
            d = json.load(fh)
    except FileNotFoundError:
        return {"submitted": [], "runs": []}
    except (ValueError, OSError) as e:
        # Loud. A log that silently reads as empty turns --new into --submit,
        # which is the exact behaviour this file exists to stop.
        print(f"  WARNING: {os.path.relpath(LOG, ROOT)} unreadable ({e}).")
        print("  Treating every URL as unsubmitted, which may re-send the whole site.")
        return {"submitted": [], "runs": []}
    d.setdefault("submitted", [])
    d.setdefault("runs", [])
    return d


def save_log(d):
    d["submitted"] = sorted(set(d["submitted"]))
    # Keep the run history bounded; the last 60 entries is months of daily runs.
    d["runs"] = d["runs"][-60:]
    with open(LOG, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, indent=1)
        fh.write("\n")


# ------------------------------------------------------------------ key file
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


def key_is_live():
    """Returns True, False, or None for 'could not tell'.

    Three states, not two, deliberately. A sandbox with no egress and a
    genuinely missing key file both used to render as 'NO, deploy it first',
    which is an assumption written over a measurement. This session's own
    network failure is not evidence about the site.
    """
    try:
        with urllib.request.urlopen(f"{BASE}/{KEY}.txt", timeout=15) as r:
            return r.read().decode().strip() == KEY
    except urllib.error.HTTPError:
        return False
    except Exception:
        return None


# ------------------------------------------------------------------ submit
def live_status(url):
    """HTTP status production actually returns for one URL, or None if the
    request could not be made at all."""
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "6s-success-indexnow/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:                                             # noqa: BLE001
        return None


def withhold_undeployed(candidates):
    """Never announce a page production does not serve.

    The sitemap is generated from the repository, so it can list a page that
    has been built and not yet deployed. On 2026-09-03 it listed
    /affiliate-disclosure.html, which production answered with 404. Submitting
    that to a search engine asks four engines to come and fetch a 404, on a
    domain whose whole problem is that it has no crawl trust to spend.

    Returns (live, withheld). A URL we could not reach at all is withheld too,
    and said out loud, because unreachable is not the same as fine.
    """
    live, withheld = [], []
    for u in candidates:
        code = live_status(u)
        if code == 200:
            live.append(u)
        else:
            withheld.append((u, code))
    return live, withheld


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
            return r.status, r.reason, r.read().decode("utf-8", "replace")[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.reason, e.read().decode("utf-8", "replace")[:300]
    except Exception as e:                                        # noqa: BLE001
        return None, "no response", str(e)[:200]


def describe(code, reason, body):
    """IndexNow answers 200 with an empty body on success, which reads like a
    failure to anyone who has not met the protocol before. Say what it means."""
    if code in (200, 202):
        return f"HTTP {code} {reason} - accepted{' | ' + body if body.strip() else ' (empty body is the documented success response)'}"
    if code is None:
        return f"NO RESPONSE - {body}. Nothing was submitted."
    return f"HTTP {code} {reason} - REJECTED | {body.strip() or '(no body)'}"


# ------------------------------------------------------------------ modes
def status():
    u = urls()
    log = load_log()
    done = set(log["submitted"])
    never = [x for x in u if x not in done]
    print(f"  sitemap URLs        : {len(u)}")
    print(f"  ever accepted       : {len(done & set(u))}")
    print(f"  never submitted     : {len(never)}")
    for x in never[:10]:
        print(f"      {x}")
    if len(never) > 10:
        print(f"      ... and {len(never)-10} more")
    runs = log["runs"]
    if not runs:
        print("  last submission     : NEVER RECORDED (this log starts 2026-09-03;"
              " an earlier run on 2026-08-25 accepted 181 URLs and kept no record)")
    else:
        last = runs[-1]
        print(f"  last submission     : {last['at']} - {last['accepted']} of "
              f"{last['offered']} accepted, {last['result']}")
    stale = [x for x in done if x not in set(u)]
    if stale:
        print(f"  submitted but no longer in the sitemap: {len(stale)}")
        for x in stale[:5]:
            print(f"      {x}")
    return 0


def run(batch_urls, label):
    if not batch_urls:
        print(f"  nothing to submit ({label}). Every sitemap URL has already"
              " been accepted at least once.")
        return 0

    live = key_is_live()
    if live is None:
        print("  UNCHECKED: could not reach the site to confirm the key file is"
              " served. Refusing to submit rather than guess.")
        return 2
    if not live:
        print("  Refusing to submit: the key file is not live, so every"
              " submission would be rejected as unverified. Deploy first.")
        return 1

    print(f"  checking what production actually serves for {len(batch_urls)} URL(s)...")
    batch_urls, withheld = withhold_undeployed(batch_urls)
    for u, code in withheld:
        print(f"  WITHHELD {u} -> "
              + (f"HTTP {code}" if code else "no response, could not check"))
    if withheld:
        print(f"  {len(withheld)} URL(s) withheld: the sitemap lists them and "
              "production does not serve them. Deploy, then run this again.")
    if not batch_urls:
        print("  nothing left to submit.")
        return 1

    log = load_log()
    accepted, results = 0, []
    for i in range(0, len(batch_urls), BATCH):
        chunk = batch_urls[i:i + BATCH]
        code, reason, body = submit(chunk)
        line = describe(code, reason, body)
        print(f"  batch {i//BATCH + 1}: {len(chunk)} urls -> {line}")
        results.append(line)
        if code in (200, 202):
            accepted += len(chunk)
            log["submitted"].extend(chunk)

    log["runs"].append({
        "at": datetime.datetime.now(datetime.timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": label,
        "offered": len(batch_urls),
        "accepted": accepted,
        "result": "; ".join(results)[:400],
    })
    save_log(log)
    print(f"  accepted: {accepted} of {len(batch_urls)}")
    print(f"  recorded in {os.path.relpath(LOG, ROOT)}")
    # Accepted means queued, not indexed. Say so, so nobody reads this as proof.
    print("  NOTE: accepted means the URLs are queued. It is not evidence that"
          " any engine has crawled or indexed them.")
    return 0 if accepted else 1


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--check"

    if mode == "--status":
        return status()

    p = write_key()
    print(f"  wrote {os.path.relpath(p, ROOT)} and site/indexnow.txt")
    u = urls()
    log = load_log()
    new = [x for x in u if x not in set(log["submitted"])]
    print(f"  {len(u)} URLs in the sitemap, {len(new)} never submitted")
    print(f"  key file: {BASE}/{KEY}.txt")

    if mode == "--new":
        return run(new, "new")
    if mode == "--submit":
        return run(u, "full")

    live = key_is_live()
    print("  key file reachable: "
          + {True: "yes", False: "NO, deploy it first",
             None: "UNCHECKED, no network from this session"}[live])
    for x in (new or u)[:4]:
        print(f"    {x}")
    rest = len(new or u) - 4
    if rest > 0:
        print(f"    ... and {rest} more")
    print("  nothing submitted. Use --new (only unsubmitted URLs) or --submit (all).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
