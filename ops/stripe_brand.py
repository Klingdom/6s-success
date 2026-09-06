#!/usr/bin/env python3
"""
Make the Stripe checkout page look like this business, and point it at this
business.

WHY
---
Three things a buyer sees, and all three were wrong or missing.

**The account's business URL pointed at ledgerium.ai**, which is a different
company that happens to share a VPS. That URL appears on receipts and is what a
card issuer looks at during a dispute. A buyer who paid 6S Success and follows
the link to somebody else's product is a chargeback waiting to happen, and an
account review after that.

**No support email**, although support@6s-success.com exists and is read. Stripe
puts it on every receipt. Without it the only route back to us is the line on a
card statement.

**No logo, no icon, no colours.** The checkout page is the single moment a buyer
decides whether this is a real business. Stripe renders a generic placeholder
when branding is unset, on a page asking for a card number.

The mark is drawn here rather than shipped as a binary, so it cannot drift from
the palette the site uses. Same arc gauge as the site header: the six-S ramp
from chaos to calm, with the needle resting at the calm end.

Idempotent. Uploads the icon only when the account has none, so running it twice
does not fill the account's file list with copies.

Run:  python ops/stripe_brand.py --check
      python ops/stripe_brand.py --apply
"""
from __future__ import annotations

import io
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")

SITE = "https://6s-success.com"
SUPPORT = "support@6s-success.com"

# Straight from site/assets/css/site.css. Not re-picked by eye.
INK = (0x2B, 0x26, 0x22)
PAPER = (0xF7, 0xF2, 0xE9)
LINE = (0xE2, 0xD8, 0xC4)
TERRA = "#BC4B2A"
DEEP = "#22323C"
# The six-S ramp, chaos to calm, in canonical order.
RAMP = ["#CB4B36", "#BC4B2A", "#D98A2B", "#DDA63A", "#6E8B5B", "#4E7A57"]

ICON_PX = 512      # Stripe wants a square icon, at least 128
LOGO_W = 1024      # the wordless mark reads better than tiny type at this size


def secret_key() -> str:
    env = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if env:
        return env
    if not os.path.exists(SECRETS):
        sys.exit(".env.secrets not found")
    for line in io.open(SECRETS, encoding="utf-8"):
        if line.startswith("STRIPE_SECRET_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("STRIPE_SECRET_KEY not in .env.secrets")


_KEY: str | None = None


def key() -> str:
    """Lazy on purpose, same convention as stripe_catalog.py's key(): importing
    this module (for a test, or a future gate) must not require a live
    credential. Only an actual API call should."""
    global _KEY
    if _KEY is None:
        _KEY = secret_key()
    return _KEY


def call(method: str, path: str, pairs=None) -> dict:
    url = "https://api.stripe.com/v1/" + path
    body = urllib.parse.urlencode(pairs).encode() if pairs else None
    req = urllib.request.Request(url, data=body, method=method,
                                 headers={"Authorization": "Bearer " + key()})
    try:
        return json.load(urllib.request.urlopen(req, timeout=20))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Stripe {method} {path}: {e.code} "
                         f"{json.load(e).get('error', {}).get('message', '')}")


# ---------------------------------------------------------------- the mark
def draw_mark(size: int, square: bool = True):
    """The site's arc gauge: six coloured segments from chaos to calm, and a
    needle resting at the calm end. Drawn at 4x and downsampled, because the
    arc ends are the only thing anybody sees at 32 pixels."""
    from PIL import Image, ImageDraw

    ss = 4
    w = size * ss
    h = w if square else int(w * 0.62)
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)

    cx, cy = w / 2, h * (0.66 if square else 0.74)
    r = w * (0.40 if square else 0.34)
    width = int(w * (0.098 if square else 0.086))

    # A 180 degree sweep split into the six S's, drawn left to right so the
    # colour order is the method's order and not decoration.
    span = 180 / len(RAMP)
    for i, hexcol in enumerate(RAMP):
        start = 180 + i * span
        d.arc([cx - r, cy - r, cx + r, cy + r], start, start + span + 0.6,
              fill=hexcol, width=width)

    # The needle rests at the CALM end, up and to the right, matching the mark
    # in the site header. Pointing it at the red end would say the opposite of
    # what the method claims, on the one image a buyer sees while deciding
    # whether to hand over a card.
    ang = math.radians(342)
    nx, ny = cx + r * 0.80 * math.cos(ang), cy + r * 0.80 * math.sin(ang)
    d.line([cx, cy, nx, ny], fill=INK, width=int(w * 0.030))
    hub = int(w * 0.052)
    d.ellipse([cx - hub, cy - hub, cx + hub, cy + hub], fill=INK)

    return im.resize((size, h // ss), Image.LANCZOS)


def png_bytes(im) -> bytes:
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def upload(name: str, data: bytes) -> str:
    """Stripe's file upload is multipart, which urlencode cannot express, so the
    body is assembled by hand rather than pulling in a dependency for it."""
    boundary = "----6s" + uuid.uuid4().hex
    parts = []
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                 f'name="purpose"\r\n\r\nbusiness_logo\r\n'.encode())
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                 f'name="file"; filename="{name}"\r\n'
                 f"Content-Type: image/png\r\n\r\n".encode())
    parts.append(data)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)

    req = urllib.request.Request(
        "https://files.stripe.com/v1/files", data=body, method="POST",
        headers={"Authorization": "Bearer " + key(),
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=20))["id"]
    except urllib.error.HTTPError as e:
        raise SystemExit(f"file upload failed: {e.code} "
                         f"{json.load(e).get('error', {}).get('message', '')}")


def main(apply_it: bool) -> int:
    if apply_it:
        os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
        for nm, im in (("6s-icon.png", draw_mark(ICON_PX, True)),
                       ("6s-logo.png", draw_mark(LOGO_W, False))):
            im.save(os.path.join(ROOT, "build", nm))
            print("  wrote build/" + nm)

    acct = call("GET", "account")
    prof = acct.get("business_profile") or {}
    brand = ((acct.get("settings") or {}).get("branding") or {})

    wrong_url = (prof.get("url") or "") != SITE
    no_support = (prof.get("support_email") or "") != SUPPORT
    no_icon = not brand.get("icon")
    no_logo = not brand.get("logo")
    no_colour = not brand.get("primary_color")

    print(f"  mode: {'LIVE' if key().startswith('sk_live_') else 'test'}   "
          f"{'applying' if apply_it else 'dry run'}\n")
    print(f"  business url    {prof.get('url') or 'NOT SET'}"
          f"{'   WRONG, points at another company' if wrong_url else '   ok'}")
    print(f"  support email   {prof.get('support_email') or 'NOT SET'}"
          f"{'   missing from every receipt' if no_support else '   ok'}")
    print(f"  support url     {prof.get('support_url') or 'NOT SET'}")
    print(f"  checkout icon   {'NOT SET' if no_icon else brand['icon']}")
    print(f"  checkout logo   {'NOT SET' if no_logo else brand['logo']}")
    print(f"  brand colours   {brand.get('primary_color') or 'NOT SET'} / "
          f"{brand.get('secondary_color') or 'NOT SET'}")

    gaps = []
    if wrong_url:
        gaps.append(("Business website points at another company",
                     "Settings, Business details, Public details, Edit"))
    if no_support:
        gaps.append(("No support email on receipts",
                     "Settings, Business details, Public details, Edit"))
    if no_icon or no_colour:
        gaps.append(("Checkout page carries no branding",
                     "Settings, Branding, then upload build/6s-icon.png"))

    if not gaps:
        print(chr(10) + "  Nothing to fix.")
        return 0

    print(chr(10) + "  These are Dashboard settings. POST /v1/account is refused")
    print("  on your own account, so none can be written from here.")
    for what, where in gaps:
        print("    " + what)
        print("      " + where)
    print(chr(10) + "  python ops/stripe_brand.py --apply writes the icon to upload.")
    return 1


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
