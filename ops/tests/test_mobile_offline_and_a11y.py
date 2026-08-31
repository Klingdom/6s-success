"""The mobile app must stay offline, and its controls must stay announceable.

Two promises from the mobile product principles, both of the kind that hold
until somebody adds one convenient line:

  "Local-first and offline-first. Garages, basements, workshops, and patios are
   core terrain."
  "Photographs of home interiors are sensitive. Private by default, never used
   for model training, never shared without a deliberate user action."

The web app already proves the second in its own way: site/assets/js/photos.js
contains no fetch, no XMLHttpRequest and no FormData, and its comment says so
where a person can read it. Nothing enforced the same thing on the mobile side,
where adding a sync call is a two line change and would be entirely invisible
in review.

WCAG 2.2 AA is the stated floor. A static check cannot cover announcement order,
focus movement or gesture alternatives, and this file does not pretend to: it
covers the part that is decidable from source, which is that every control
carries a role and a label, and that decorative colour is hidden rather than
read aloud.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP = os.path.join(ROOT, "mobile", "quest-app")

# Source the app actually ships. node_modules is third party and dist is a
# build product; neither is a promise this project made.
def app_sources() -> list:
    out = []
    for base, dirs, files in os.walk(APP):
        dirs[:] = [d for d in dirs
                   if d not in ("node_modules", "dist", ".expo", "assets")]
        for f in files:
            if f.endswith(".js") and not f.endswith(".test.js"):
                out.append(os.path.join(base, f))
    return sorted(out)


# Anything that could carry a byte off the device.
NETWORK = re.compile(
    r"\bfetch\s*\(|XMLHttpRequest|WebSocket|EventSource|navigator\.sendBeacon|"
    r"axios|\bnew\s+FormData\b|https?://(?!schema\.org)", re.I)

# Legitimate mentions in prose. A comment explaining that there is no network
# call must not be read as one, which is exactly the mistake I made about
# photos.js the first time.
def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    src = re.sub(r"^\s*//.*$", " ", src, flags=re.M)
    return src


def main() -> int:
    if not os.path.isdir(APP):
        print("  no mobile app in this checkout, nothing to check. NOT VERIFIED.")
        return 0

    srcs = app_sources()
    if not srcs:
        print("  found no app source files, so nothing was checked. "
              "Unchecked, not clean.")
        return 1

    bad = []

    # 1. Offline promise.
    for p in srcs:
        code = strip_comments(io.open(p, encoding="utf-8", errors="replace").read())
        for m in NETWORK.finditer(code):
            bad.append("%s carries something that can reach the network: %r"
                       % (os.path.relpath(p, ROOT).replace(os.sep, "/"),
                          m.group(0)))

    # 2. Every control announceable.
    app_js = os.path.join(APP, "App.js")
    if os.path.exists(app_js):
        src = io.open(app_js, encoding="utf-8", errors="replace").read()
        pressables = src.count("<Pressable")
        roles = src.count("accessibilityRole=")
        labels = src.count("accessibilityLabel=")
        if roles < pressables:
            bad.append("%d Pressable(s) but only %d accessibilityRole(s): a "
                       "screen reader cannot say what can be activated"
                       % (pressables, roles))
        if labels < pressables:
            bad.append("%d Pressable(s) but only %d accessibilityLabel(s)"
                       % (pressables, labels))
        # Decorative colour must not be read out.
        if "s.dots" in src and "accessibilityElementsHidden" not in src:
            bad.append("the finish screen's colour dots are decorative and are "
                       "not hidden from assistive technology")

    for b in bad:
        print("  FAIL " + b)
    if bad:
        return 1
    print("  ok  %d app source file(s) make no network call, and every control "
          "carries a role and a label" % len(srcs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
