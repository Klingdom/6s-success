#!/usr/bin/env python3
"""
The style token for local generation, sized to what CLIP can actually read.

THE PROBLEM THIS SOLVES
-----------------------
The frozen house look written for ChatGPT is 92 CLIP tokens. SDXL's text
encoder truncates at 77. So a prompt built as "style, then subject" fed the
model most of the style and none of the subject: a request for a shoe rack, a
boot tray and boots produced a generic bright room with a desk and a plant,
and nothing about it looked wrong enough to notice without checking the token
count.

That is a silent failure. The image is well formed, on palette, and of
something else entirely.

THE FIX HAS TWO PARTS
---------------------
1. Subject first. Whatever gets truncated should be the least important thing
   in the prompt, and that is never the subject.
2. A compressed style token of about 20 tokens carrying the same visual DNA:
   photographic, warm window light, eye level, warm neutral palette, no text.

The long form stays the canonical style for any surface without a token limit,
which is ChatGPT and every hosted API. Both are hashed, and the hash recorded
beside each image says which one produced it, so a deck generated locally can
never be silently mixed with one generated through an API.
"""
from __future__ import annotations

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

# About 20 tokens. Every word earns its place: medium, light, lens, palette,
# and the one instruction that matters most because generated lettering is
# always garbled.
SHORT_STYLE = ("photorealistic interior photograph, warm window light, "
               "eye level, warm neutral palette, no text")

# Short too, because a long negative eats the same budget on the second
# encoder and the biggest wins are the first few terms.
SHORT_NEGATIVE = ("text, letters, watermark, logo, brand, people, hands, "
                  "cluttered, blurry, distorted")

TOKEN_LIMIT = 77


def prompt_for(subject: str) -> str:
    """Subject first, style after. Order is the whole fix."""
    return f"{subject}. {SHORT_STYLE}"


def style_hash() -> str:
    return "local-" + hashlib.sha256(SHORT_STYLE.encode()).hexdigest()[:8]


def count(text: str) -> int:
    from transformers import CLIPTokenizer
    tok = CLIPTokenizer.from_pretrained(
        "stabilityai/sdxl-turbo", subfolder="tokenizer",
        cache_dir=os.path.join(ROOT, "build", "models"))
    return len(tok(text)["input_ids"])


def check(subject: str) -> list:
    """Refuse a prompt whose subject would be truncated away."""
    p = prompt_for(subject)
    n = count(p)
    bad = []
    if n > TOKEN_LIMIT:
        # How much of the subject survives is what actually matters.
        subj_tokens = count(subject)
        if subj_tokens > TOKEN_LIMIT - 8:
            bad.append(f"the subject alone is {subj_tokens} tokens, over the "
                       f"{TOKEN_LIMIT} limit, so part of it cannot reach the "
                       f"model however the prompt is ordered. Shorten it.")
        else:
            bad.append(f"{n} tokens, over {TOKEN_LIMIT}. The subject survives "
                       f"because it comes first, but some style is being cut.")
    return bad


if __name__ == "__main__":
    print(f"  short style   {count(SHORT_STYLE)} tokens")
    print(f"  short negative {count(SHORT_NEGATIVE)} tokens")
    print(f"  hash          {style_hash()}")
    s = ("A low wooden shoe rack with four pairs of plain shoes soles down, "
         "a black rubber boot tray with one pair of rain boots upright, "
         "warm oak floor, a small plant")
    print(f"\n  example subject {count(s)} tokens")
    print(f"  full prompt     {count(prompt_for(s))} tokens")
    print(f"  problems: {check(s) or 'none'}")
