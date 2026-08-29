#!/usr/bin/env python3
"""
Which media credentials actually authenticate, and what each one costs.

WHY THIS EXISTS
---------------
The multimedia directive's section 3 says to inventory capability before
choosing a method, and to report only whether a credential is present, never
its value. A key sitting in a file is not a key that works: it can be revoked,
scoped to the wrong product, out of quota, or for an account with no billing.
Assuming it works and building a pipeline on it wastes the pipeline.

So this authenticates each one with the cheapest call the provider offers,
usually listing models, which costs nothing and still proves the credential.
It never generates an image, so running it is free.

NOTHING HERE PRINTS A SECRET. Keys are read by name, used, and reported only
as working or not.

Run:  python ops/media_capability.py
"""
from __future__ import annotations

import io
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")


def env() -> dict:
    out = dict(os.environ)
    if os.path.exists(SECRETS):
        for line in io.open(SECRETS, encoding="utf-8"):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def get(url: str, headers: dict, timeout: int = 25) -> tuple:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(4000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(400).decode("utf-8", errors="replace")
    except Exception as e:                                    # noqa: BLE001
        return 0, f"{type(e).__name__}: {e}"


# name, env var(s), how to check, what it would be used for, rough cost each
PROVIDERS = [
    ("openai", ["OPENAI_API_KEY"],
     lambda e: get("https://api.openai.com/v1/models",
                   {"Authorization": f"Bearer {e['OPENAI_API_KEY']}"}),
     "gpt-image-1, strongest for reference-led and matched pairs",
     "0.04 to 0.19"),
    # Either name works for Gemini. Requiring both meant a correctly
    # configured key reported as absent, which is a worse failure than a
    # missing one because it looks like the user did nothing.
    ("gemini", ["GEMINI_API_KEY|GOOGLE_API_KEY"],
     lambda e: get("https://generativelanguage.googleapis.com/v1beta/models",
                   {"x-goog-api-key": e.get("GEMINI_API_KEY")
                    or e.get("GOOGLE_API_KEY")}),
     "Imagen and Gemini image, strong photoreal interiors",
     "0.03 to 0.06"),
    ("cloudflare", ["CLOUDFLARE_API_TOKEN", "CF_ACCOUNT_ID"],
     lambda e: get(f"https://api.cloudflare.com/client/v4/accounts/"
                   f"{e['CF_ACCOUNT_ID']}/ai/models/search?per_page=1",
                   {"Authorization": f"Bearer {e['CLOUDFLARE_API_TOKEN']}"}),
     "Workers AI FLUX, cheapest per image at volume",
     "0.001 to 0.01"),
    ("replicate", ["REPLICATE_API_TOKEN"],
     lambda e: get("https://api.replicate.com/v1/account",
                   {"Authorization": f"Bearer {e['REPLICATE_API_TOKEN']}"}),
     "FLUX, SDXL, ControlNet and img2img for matched pairs",
     "0.003 to 0.055"),
    ("stability", ["STABILITY_API_KEY"],
     lambda e: get("https://api.stability.ai/v1/user/account",
                   {"Authorization": f"Bearer {e['STABILITY_API_KEY']}"}),
     "Stable Image, structure and style conditioning",
     "0.03"),
    ("huggingface", ["HF_TOKEN"],
     lambda e: get("https://huggingface.co/api/whoami-v2",
                   {"Authorization": f"Bearer {e['HF_TOKEN']}"}),
     "inference providers, and model weights for local use",
     "varies"),
    ("runway", ["RUNWAY_API_KEY"],
     lambda e: get("https://api.dev.runwayml.com/v1/organization",
                   {"Authorization": f"Bearer {e['RUNWAY_API_KEY']}",
                    "X-Runway-Version": "2024-11-06"}),
     "generative video, for atmospheric shots only",
     "high"),
]


def main() -> int:
    e = env()
    print("  provider      credential  auth   use\n")
    working = []
    for name, keys, check, use, cost in PROVIDERS:
        if not all(any(e.get(alt) for alt in k.split("|")) for k in keys):
            print(f"  {name:13} absent      -      {use[:44]}")
            continue
        code, body = check(e)
        ok = 200 <= code < 300
        if ok:
            working.append((name, cost, use))
        note = "ok" if ok else (f"{code}" if code else "net")
        print(f"  {name:13} present     {note:6} {use[:44]}")
        if not ok and code:
            reason = ""
            try:
                d = json.loads(body)
                reason = (d.get("error", {}).get("message")
                          if isinstance(d.get("error"), dict)
                          else str(d.get("error") or d.get("errors") or ""))[:90]
            except Exception:                                 # noqa: BLE001
                reason = body.replace("\n", " ")[:90]
            if reason:
                print(f"  {'':13} {'':11} why    {reason}")

    print(f"\n  {len(working)} of {len(PROVIDERS)} authenticate")
    if working:
        print("\n  usable now, cheapest first:")
        for name, cost, use in sorted(working, key=lambda x: x[1]):
            print(f"    {name:12} ${cost:14} {use}")

    # Local GPU is a real option for volume and for the structural control a
    # matched pair needs, but only with a CUDA build of torch.
    try:
        import torch
        if torch.cuda.is_available():
            print(f"\n  local gpu: {torch.cuda.get_device_name(0)}, usable")
        else:
            print(f"\n  local gpu: present but torch is a CPU build "
                  f"({torch.__version__}), so it cannot be used until the CUDA "
                  f"build is installed")
    except ImportError:
        print("\n  local gpu: torch absent")
    return 0 if working else 1


if __name__ == "__main__":
    raise SystemExit(main())
