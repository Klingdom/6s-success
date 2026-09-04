#!/usr/bin/env python3
"""Read the real Kindle Store browse tree, so category choices are checked.

WHY NOT JUST WRITE THE PATHS DOWN
---------------------------------
Amazon renames and reshuffles browse nodes, and a category path that no longer
exists is worse than none: it sends the person filling in the form hunting for
something that is not in the picker. This walks the bestseller navigation from
a starting node and prints the children it actually finds today, with their
node IDs, so a listing package can quote a path that was observed rather than
remembered.

It reads only the category navigation. It does not collect titles, ranks or
sales figures, and nothing it prints should be presented as demand evidence:
a bestseller list is an ordering, not a volume.

  python build/listings/amazon_nodes.py 154606011
  python build/listings/amazon_nodes.py 154606011 --depth 2
"""
from __future__ import annotations

import argparse
import gzip
import io
import re
import sys
import time
import urllib.request
import zlib

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")


def fetch(node: str) -> str:
    url = "https://www.amazon.com/gp/bestsellers/digital-text/" + node
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    })
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read()
        enc = resp.headers.get("Content-Encoding", "")
    if enc == "gzip":
        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    elif enc == "deflate":
        raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    return raw.decode("utf-8", "replace")


def children(html: str):
    """Pull the sub-category links out of the left-hand browse navigation."""
    out = []
    seen = set()
    pattern = re.compile(
        r'"href"\s*:\s*"([^"]*?/digital-text/(\d+)[^"]*)"\s*,\s*"name"\s*:\s*"([^"]*)"')
    for _, node, name in pattern.findall(html):
        if node not in seen:
            seen.add(node)
            out.append((node, name.strip()))
    if out:
        return out
    pattern = re.compile(
        r'href="[^"]*?/digital-text/(\d+)[^"]*"[^>]*>\s*([^<]{2,60})\s*<')
    for node, name in pattern.findall(html):
        name = re.sub(r"\s+", " ", name).strip()
        if node not in seen and name and not name[0].isdigit():
            seen.add(node)
            out.append((node, name))
    return out


def title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.S)
    text = match.group(1).strip() if match else "?"
    return text.replace("Amazon Best Sellers: Best ", "")


def walk(node: str, depth: int, prefix: str = "") -> None:
    try:
        html = fetch(node)
    except Exception as exc:
        print(prefix + node + "  FETCH FAILED: " + str(exc))
        return
    print(prefix + node + "  " + title(html))
    if depth <= 0:
        return
    for child_node, name in children(html):
        if child_node == node:
            continue
        print(prefix + "  " + child_node + "  " + name)
        if depth > 1:
            time.sleep(0.6)
            walk(child_node, depth - 1, prefix + "    ")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("node")
    ap.add_argument("--depth", type=int, default=1)
    args = ap.parse_args()
    walk(args.node, args.depth)
    return 0


if __name__ == "__main__":
    sys.exit(main())
