#!/usr/bin/env python3
"""
Local image generation on the GPU. Free at any volume, and structurally
controllable, which is the part that matters.

WHY LOCAL RATHER THAN AN API
----------------------------
Two reasons, and the second is the real one.

Cost: 114 zone heroes plus card art plus before and after pairs runs to
several hundred images, and iteration is most of the work. Locally that is
free, so a bad batch costs time instead of money and nobody is tempted to
accept a poor image because regenerating it has a price.

Control: the multimedia directive's matched pair standard requires the before
image to be the geometry anchor and the after to preserve camera, architecture,
fixed furniture and light, changing only what the brief names. That needs
image to image with a low denoise strength, or depth and edge conditioning. An
API that only takes a text prompt cannot do it, and the directive is explicit
that two independently composed scenes must never be called a matched pair.

WHAT RUNS HERE
--------------
SDXL Turbo on an RTX 2070 SUPER with 8 GB. Turbo is a distilled model: it
wants one to four steps and a guidance scale of zero, which is why the
defaults below look wrong if you are used to ordinary Stable Diffusion.

The style prefix and its hash come from ops/generate_card_art.py, so local and
API generation share one frozen style and drift is detectable either way.

Run:  python ops/image_local.py --probe
      python ops/image_local.py --one "a tidy entryway shoe zone"
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("HF_HOME", os.path.join(ROOT, "build", "models"))
OUT = os.path.join(ROOT, "build", "generated")

# SD 1.5 rather than SDXL, decided by measurement rather than by which model
# sounds better. On this 8 GB card SDXL Turbo peaked at 9.0 GB, spilled into
# system RAM over PCIe, and took 168 seconds for a single step. SD 1.5 at the
# same 768x576 takes 5 seconds at 20 steps and peaks at 3.0 GB.
#
# That is 33 times faster, it turns a five hour batch into ten minutes, the
# images are better rather than worse, and the 5 GB it leaves free is what
# ControlNet needs for the matched before and after pairs. A bigger model that
# does not fit is slower and worse than a smaller one that does.
MODEL = "stable-diffusion-v1-5/stable-diffusion-v1-5"
STEPS = 25               # SD 1.5 with DPM Solver; not a distilled model
GUIDANCE = 7.0          # Ordinary model, so guidance does the prompt adherence.
# 768x576 is the largest 4:3 that fits. Measured, not guessed: SDXL at
# 1024x768 peaks at 9.0 GB on an 8 GB card, so it spills into system RAM over
# PCIe and one step takes over 100 seconds instead of a few. At 768x576 it
# stays resident. Upscale afterwards if a larger asset is needed; generating
# above the card's memory is slower than generating small and enlarging.
SIZE = (768, 576)

sys.path.insert(0, os.path.join(ROOT, "ops"))
# The long frozen style is 92 CLIP tokens and the encoder truncates at 77, so
# a prompt built style-first fed the model all style and no subject: a request
# for a shoe rack produced a room with a desk. image_style carries a 20 token
# version and puts the subject first.
from image_style import prompt_for, SHORT_NEGATIVE, style_hash, check  # noqa: E402

_PIPE = None


def pipe():
    global _PIPE
    if _PIPE is None:
        import torch
        from diffusers import (StableDiffusionPipeline,
                               DPMSolverMultistepScheduler)
        if not torch.cuda.is_available():
            raise SystemExit(
                "no CUDA device. torch is probably a CPU build: check with "
                "python -c \"import torch;print(torch.__version__)\"")
        p = StableDiffusionPipeline.from_pretrained(
            MODEL, torch_dtype=torch.float16,
            safety_checker=None, requires_safety_checker=False).to("cuda")
        # DPM Solver reaches a good image in 20 to 25 steps where the default
        # scheduler wants 50, which halves the batch time for no visible cost.
        p.scheduler = DPMSolverMultistepScheduler.from_config(p.scheduler.config)
        # No attention slicing. It is the usual advice for a small card and
        # here it made things worse: 262 seconds against 102 for the same
        # image. Slicing trades speed for memory, and memory was already
        # being found by spilling to system RAM, so it paid the cost twice.
        # At a size that fits, plain fp16 on the GPU is fastest.
        p.set_progress_bar_config(disable=True)
        _PIPE = p
    return _PIPE


def build_prompt(subject: str) -> str:
    return prompt_for(subject)


def generate(subject: str, seed: int | None = None,
             size: tuple = SIZE) -> tuple:
    """Returns (PIL image, metadata). Deterministic for a given seed."""
    import torch
    sig = style_hash()
    if seed is None:
        # Derived from the subject, so the same subject regenerates the same
        # picture. A random seed makes a batch impossible to reproduce.
        seed = int(hashlib.sha256(subject.encode()).hexdigest()[:8], 16) % (2**31)

    g = torch.Generator("cuda").manual_seed(seed)
    t0 = time.time()
    im = pipe()(
        prompt=build_prompt(subject),
        negative_prompt=SHORT_NEGATIVE,
        num_inference_steps=STEPS,
        guidance_scale=GUIDANCE,
        width=size[0], height=size[1],
        generator=g,
    ).images[0]
    return im, {"subject": subject, "seed": seed, "style_hash": sig,
                "model": MODEL, "steps": STEPS, "size": list(size),
                "seconds": round(time.time() - t0, 1)}


def verify(im) -> list:
    """An image that saved is not an image worth using."""
    import numpy as np
    a = np.asarray(im.convert("L"), dtype=np.float32)
    bad = []
    if a.std() < 12:
        bad.append(f"standard deviation {a.std():.1f}, effectively flat")
    if a.mean() < 24 or a.mean() > 236:
        bad.append(f"mean brightness {a.mean():.0f}, nearly black or blown out")
    return bad


def save(im, meta: dict, stem: str) -> str:
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{stem}.png")
    im.save(p)
    json.dump(meta, io.open(p.replace(".png", ".json"), "w",
                            encoding="utf-8", newline=""), indent=1)
    return p


if __name__ == "__main__":
    if "--probe" in sys.argv:
        import torch
        print(f"  torch {torch.__version__}  cuda={torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  {torch.cuda.get_device_name(0)}")
        print(f"  model {MODEL}")
        print(f"  cache {os.environ['HF_HOME']}")
        raise SystemExit(0)

    subject = (sys.argv[sys.argv.index("--one") + 1]
               if "--one" in sys.argv else "a tidy entryway shoe zone")
    im, meta = generate(subject)
    bad = verify(im)
    stem = hashlib.sha256(subject.encode()).hexdigest()[:10]
    p = save(im, meta, stem)
    print(f"  {meta['seconds']}s  seed {meta['seed']}  style {meta['style_hash']}")
    print(f"  {os.path.relpath(p, ROOT)}")
    print(f"  problems: {bad or 'none'}")
