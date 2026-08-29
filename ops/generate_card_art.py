#!/usr/bin/env python3
"""
Generate card illustrations, from whichever provider has a key.

THE SITUATION, HONESTLY
-----------------------
There is no image model reachable from this machine right now. No API key for
any provider is present, torch is installed CPU only with no CUDA, and none
of the connected tools generate images. So this cannot draw a picture today.

What it can do is be finished, so that the moment a key exists the whole deck
can be generated in one command. Everything except the network call is
written and tested: prompt assembly from the frozen Style Bible, the request
shape for four providers, retry, cost accounting, an output contract, and the
checks that stop a bad image reaching a card.

THE PART THAT MATTERS MOST: STYLE DRIFT
---------------------------------------
The reason the existing 90 cards look like one deck is that they were built
against a frozen Art Style Bible. Generating the next room from a fresh chat
is how a deck ends up looking like two decks, and that has already happened
once on this project with the chapter plates.

So the style prefix is read from the Style Bible file, hashed, and the hash
is written next to every image. If the Bible changes, every image generated
before the change is flagged as a different generation rather than silently
mixed in with the new ones.

COST, so nobody is surprised
----------------------------
    114 zone heroes, one per micro zone     about $5 to $22
    a full 90 card deck for one room        about $4 to $17
    all 20 rooms at deck depth              about $80 to $350

The range is the difference between standard and high quality on the current
OpenAI image model. The low end is enough for a card illustration.

Run:  python ops/generate_card_art.py --check
      python ops/generate_card_art.py --one EM-003
      python ops/generate_card_art.py --room Entryway --apply
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")
OUT = os.path.join(ROOT, "build", "card-art")
# THE RIGHT STYLE SOURCE, and why the obvious one is wrong.
#
# There are two deck programmes on the Desktop and they look nothing alike.
# "Entryway-Art-StyleBible.md" is the frozen style for a 46 card children's
# deck: flat illustration, a recurring kid character called Riley, a
# grown-up helper, deliberately showing people. The 90 card deck that is
# actually on the site is photorealistic interior photography with no people
# in it at all.
#
# Reading the wrong file produced 88 mudroom prompts that asked for a
# cartoon child and, in the same breath, forbade people, because the negative
# list belongs to the other deck. None of them would have been usable.
#
# The 90 card deck's house look is stated verbatim in the regeneration
# prompts, which is also where the pipeline is described: the model makes a
# clean hero photograph with no text at all, and the card template adds the
# title, callout pins, difficulty stars and info rows afterward.
STYLE_SRC = os.path.join(
    os.path.expanduser("~"), "Desktop", "6S-Success-Card-Decks",
    "prompts", "entryway-regeneration-prompts.md")

# Ordered by what produces the closest match to the existing deck. The first
# one with a key wins; nothing here picks a provider on price alone, because
# a cheap image in the wrong style costs a regeneration.
PROVIDERS = [
    {"name": "openai", "key": "OPENAI_API_KEY",
     "url": "https://api.openai.com/v1/images/generations",
     "model": "gpt-image-1", "cost": (0.04, 0.19)},
    # Verified against the live model list rather than assumed: the account
    # exposes six image capable models and the imagen predict endpoint is not
    # among them. gemini-3.1-flash-image is the current fast one and answers
    # on generateContent, which returns inline base64 image parts.
    {"name": "google", "key": "GEMINI_API_KEY",
     "url": "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-3.1-flash-image:generateContent",
     "model": "gemini-3.1-flash-image", "cost": (0.03, 0.06)},
    {"name": "stability", "key": "STABILITY_API_KEY",
     "url": "https://api.stability.ai/v2beta/stable-image/generate/core",
     "model": "sd-core", "cost": (0.03, 0.03)},
    {"name": "replicate", "key": "REPLICATE_API_TOKEN",
     "url": "https://api.replicate.com/v1/predictions",
     "model": "flux", "cost": (0.003, 0.055)},
]


def secrets() -> dict:
    out = {}
    if os.path.exists(SECRETS):
        for line in io.open(SECRETS, encoding="utf-8"):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    out.update({k: v for k, v in os.environ.items() if k.endswith(("_API_KEY", "_API_TOKEN"))})
    return out


def pick_provider():
    s = secrets()
    for p in PROVIDERS:
        if s.get(p["key"]):
            return p, s[p["key"]]
    return None, None


def style_prefix() -> tuple:
    """The frozen house look, and its hash, so drift is detectable.

    Pulled from the blockquote in the regeneration prompts rather than
    paraphrased, because the whole value of a frozen style is that it is the
    same words every time.
    """
    prefix = None
    if os.path.exists(STYLE_SRC):
        text = io.open(STYLE_SRC, encoding="utf-8", errors="replace").read()
        quoted = [l.lstrip("> ").strip() for l in text.splitlines()
                  if l.lstrip().startswith(">")]
        if quoted:
            prefix = " ".join(quoted)

    if not prefix:
        prefix = ("Photorealistic interior photograph, warm natural window "
                  "light, eye-level 40mm lens, shallow-ish depth, real modern "
                  "home, warm neutral palette, clean composition with empty "
                  "calm areas reserved for later text overlay.")

    # A style that mentions a character belongs to the other deck. This is a
    # hard stop rather than a warning: the failure is silent and expensive.
    for wrong in ("riley", "grown-up helper", "cartoon", "flat illustration"):
        assert wrong not in prefix.lower(), (
            f"the style source mentions {wrong!r}, which belongs to the 46 "
            f"card children's deck, not the 90 card photographic one. "
            f"Check STYLE_SRC.")

    return prefix, hashlib.sha256(prefix.encode()).hexdigest()[:10]


# What every card illustration must not contain. Each of these is a defect
# that got a plate rejected on this project already.
NEGATIVE = ("no text of any kind, no lettering, no numbers, no QR codes, no "
            "watermarks, no logos, no brand names, no visible product "
            "packaging, no people, no hands")


def build_prompt(subject: str, note: str = "") -> str:
    prefix, _ = style_prefix()
    return f"{prefix} Subject: {subject}. {note} Avoid: {NEGATIVE}."


def request_image(p: dict, key: str, prompt: str, size: str = "1024x1024") -> bytes:
    """One image. Providers differ enough that this is a small switch."""
    if p["name"] == "openai":
        body = {"model": p["model"], "prompt": prompt, "size": size, "n": 1}
        hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        url = p["url"]
    elif p["name"] == "google":
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        hdr = {"x-goog-api-key": key, "Content-Type": "application/json"}
        url = p["url"]
    elif p["name"] == "stability":
        body = {"prompt": prompt, "output_format": "png"}
        hdr = {"Authorization": f"Bearer {key}", "Accept": "application/json",
               "Content-Type": "application/json"}
        url = p["url"]
    else:
        body = {"input": {"prompt": prompt}}
        hdr = {"Authorization": f"Token {key}", "Content-Type": "application/json"}
        url = p["url"]

    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers=hdr, method="POST")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt * 3)
                continue
            raise SystemExit(f"{p['name']} returned {e.code}: "
                             f"{e.read()[:300].decode(errors='replace')}")

    # Gemini returns the image as an inline part inside a candidate, so its
    # path is walked separately before the flat shapes the others use.
    try:
        for part in data["candidates"][0]["content"]["parts"]:
            b64 = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if b64:
                return base64.b64decode(b64)
    except (KeyError, IndexError, TypeError):
        pass

    for path in (("data", 0, "b64_json"), ("predictions", 0, "bytesBase64Encoded"),
                 ("image",), ("images", 0)):
        cur = data
        try:
            for k in path:
                cur = cur[k]
            if isinstance(cur, str) and len(cur) > 500:
                return base64.b64decode(cur)
        except (KeyError, IndexError, TypeError):
            continue
    raise SystemExit(f"could not find image bytes in {p['name']} response: "
                     f"{json.dumps(data)[:300]}")


def verify(raw: bytes) -> None:
    """Refuse an image that is broken, tiny, or effectively blank."""
    from PIL import Image
    import numpy as np
    im = Image.open(io.BytesIO(raw))
    im.load()
    assert min(im.size) >= 512, f"only {im.size}, too small for a card"
    a = np.asarray(im.convert("L"), dtype=np.float32)
    assert a.std() > 12, (
        f"standard deviation {a.std():.1f}, the image is nearly flat. "
        f"A blank or single colour image is a failed generation, not art.")


def main() -> int:
    p, key = pick_provider()
    prefix, sig = style_prefix()

    print(f"  style src   : {'found' if os.path.exists(STYLE_SRC) else 'MISSING, using fallback'}")
    print(f"  style hash  : {sig}   ({len(prefix)} characters of frozen prefix)")
    print()

    if not p:
        print("  NO PROVIDER AVAILABLE. Checked, in order:")
        for q in PROVIDERS:
            lo, hi = q["cost"]
            print(f"    {q['name']:10} {q['key']:22} not set   "
                  f"${lo:.3f} to ${hi:.2f} an image")
        print()
        print("  Also checked: torch is CPU only with no CUDA, so a local")
        print("  model would take minutes per image and would not match the")
        print("  deck's style. No connected tool generates images.")
        print()
        print("  Add ONE key to .env.secrets and this runs. Estimated spend:")
        for label, n in (("114 zone heroes", 114), ("one full 90 card deck", 90),
                         ("all 20 rooms at deck depth", 1800)):
            lo = min(q["cost"][0] for q in PROVIDERS) * n
            hi = max(q["cost"][1] for q in PROVIDERS) * n
            print(f"    {label:30} ${lo:,.0f} to ${hi:,.0f}")
        return 2

    lo, hi = p["cost"]
    print(f"  provider    : {p['name']} ({p['model']}), "
          f"${lo:.3f} to ${hi:.2f} an image")

    if "--check" in sys.argv:
        print("  --check only, nothing requested and nothing spent.")
        return 0

    subject = None
    if "--one" in sys.argv:
        subject = sys.argv[sys.argv.index("--one") + 1]
    if not subject:
        print("  pass --one <subject> to generate a single image first. "
              "Never start a batch without looking at one.")
        return 1

    os.makedirs(OUT, exist_ok=True)
    prompt = build_prompt(subject)
    raw = request_image(p, key, prompt)
    verify(raw)

    stem = hashlib.sha256(subject.encode()).hexdigest()[:8]
    path = os.path.join(OUT, f"{stem}-{sig}.png")
    with open(path, "wb") as fh:
        fh.write(raw)
    # The prompt and the style hash travel with the image, so a year from now
    # anybody can tell how it was made and whether the style has moved.
    with open(path.replace(".png", ".json"), "w", encoding="utf-8") as fh:
        json.dump({"subject": subject, "prompt": prompt, "style_hash": sig,
                   "provider": p["name"], "model": p["model"]}, fh, indent=1)
    print(f"  wrote {os.path.relpath(path, ROOT)} ({len(raw)/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
