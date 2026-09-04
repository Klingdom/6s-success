"""Put the shop's 159 products into the HTML, instead of only into JavaScript.

Measured against production 2026-09-03: /shop.html serves 136 KB, and a client
that does not run JavaScript reads 1,218 characters of it and NOT ONE product.
All 155 buy links live inside a <script> block. The page carrying every product
this business sells has, as far as plain HTML is concerned, no products on it.

That costs us three ways. A search engine has no product text to rank, only
JSON-LD, which feeds rich results but is not page content. A slow phone shows
an empty shop until a 74 KB catalogue downloads and executes. And any failure
of that one file empties the store completely.

HOW, AND WHY NOT THE OBVIOUS WAY
The obvious fix is to write the card markup again in Python. That duplicates
window.renderProduct, and a second copy of the same logic drifts from the first
the moment either changes; this repository has paid for that pattern more than
once. So instead the real page is loaded in the same headless browser the video
and thumbnail pipelines already use, the real renderProduct runs, and its
output is lifted out and written into the file. One implementation, no second
source of truth.

The injected markup is inert on arrival and the client replaces it wholesale on
the first filter click, which is what shop.js already does. So this is a
progressive-enhancement layer, not a second rendering path.

Idempotent: the block sits between two markers and is replaced, never appended.

    python ops/prerender_shop.py
    python ops/prerender_shop.py --check     is the page currently pre-rendered
"""
from __future__ import annotations

import io
import os
import re
import subprocess
import sys
import tempfile
import threading
import http.server
import socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
SITE = os.path.join(ROOT, "site")
PAGE = os.path.join(SITE, "shop.html")
START = "<!-- prerendered-shop:start -->"
END = "<!-- prerendered-shop:end -->"


def serve(directory: str):
    """A real http server, because file:// breaks same-origin script loading.

    Returns (port, shutdown). Bound to loopback only.
    """
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=directory, **k)

        def log_message(self, *a):
            pass

    httpd = socketserver.TCPServer(("127.0.0.1", 0), H)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd.server_address[1], httpd.shutdown


def rendered_grid(port: int) -> str | None:
    """Load the page, let its own JS build the grid, return the grid's HTML."""
    import video_zone as vz
    exe, extra = vz.browser()
    with tempfile.TemporaryDirectory() as prof:
        out = os.path.join(prof, "dom.html")
        p = subprocess.run(
            [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--user-data-dir=%s" % prof, "--virtual-time-budget=12000",
             "--dump-dom", *extra,
             "http://127.0.0.1:%d/shop.html" % port],
            capture_output=True, text=True, timeout=180)
        dom = p.stdout or ""
        if os.path.exists(out):
            dom = io.open(out, encoding="utf-8").read()
    m = re.search(r'<div[^>]*id="grid"[^>]*>(.*?)</div>\s*</section>', dom, re.S)
    if not m:
        m = re.search(r'id="grid"[^>]*>(.*)', dom, re.S)
        if not m:
            return None
    return m.group(1).strip()


def main() -> int:
    page = io.open(PAGE, encoding="utf-8").read()

    if "--check" in sys.argv:
        has = START in page and END in page
        n = page.count("buy.stripe.com") if has else 0
        body = re.sub(r"(?is)<script.*?</script>", " ", page)
        print("  pre-rendered block present : %s" % has)
        print("  products in plain markup   : %d"
              % len(re.findall(r'class="[^"]*product', body)))
        return 0 if has else 1

    port, stop = serve(SITE)
    try:
        grid = rendered_grid(port)
    finally:
        stop()

    if not grid or "buy.stripe.com" not in grid and "product" not in grid:
        # Writing an empty grid would silently DELETE the shop from the page,
        # which is far worse than leaving it JavaScript-only.
        print("  REFUSING to write: the browser returned no product markup. "
              "The page is unchanged.")
        return 1

    # The browser is rendering a page that may ALREADY contain a pre-rendered
    # block, so the markup lifted back out can carry the markers with it. Left
    # in, each run nests one block inside the last: the second run produced a
    # file with one start marker and two ends. Strip them before writing.
    grid = grid.replace(START, "").replace(END, "").strip()

    # Before this, shop.html's first image was whatever the page's own chrome
    # loaded. Now it is the first product card, and renderProduct marks every
    # card image lazy, which is right for the 158 below the fold and wrong for
    # the one that is the largest paint. audit_pages.py caught it as hero-lazy
    # the first time this ran, which is the check doing its job on a fault this
    # tool introduced.
    grid = re.sub(r'(<img\b[^>]*?)\sloading="lazy"', r"\1", grid, count=1)

    cards = len(re.findall(r'class="[^"]*product', grid))
    if cards < 100:
        print("  REFUSING to write: only %d product cards rendered, expected "
              "far more. The page is unchanged." % cards)
        return 1

    block = "%s\n%s\n%s" % (START, grid, END)
    if START in page and END in page:
        page = re.sub(re.escape(START) + r".*?" + re.escape(END), block, page,
                      flags=re.S)
    else:
        page = re.sub(r'(<div[^>]*id="grid"[^>]*>)', r"\1\n" + block, page,
                      count=1)
    io.open(PAGE, "w", encoding="utf-8", newline="").write(page)

    body = re.sub(r"(?is)<script.*?</script>", " ", page)
    text = re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", body)).strip()
    print("  product cards written into the HTML : %d" % cards)
    print("  text a JS-less crawler now reads    : %d chars (was 1,218)"
          % len(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
