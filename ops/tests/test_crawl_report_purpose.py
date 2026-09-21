#!/usr/bin/env python3
"""
Prove ops/crawl_report.py can tell a training crawler fetch from a
retrieval crawler fetch (REVIEW-DISCOVERY-2026-09-07.md D15).

Before this, GPTBot and ClaudeBot (which only feed a model's training
corpus and never send this site a visitor) were counted the same way as
Bingbot or Googlebot (which can put a page in front of a person). D15's
acceptance line: the report lists the two classes separately and names
which retrieval crawlers were NOT seen in the window. Exercises classify()
and purpose() directly, no network or SSH key needed.

Run:  python ops/tests/test_crawl_report_purpose.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import crawl_report as CR                                     # noqa: E402


def main() -> int:
    fails = []

    # Training crawlers: a licensing/ingestion fetch, never a discovery one.
    for ua, want in [
        ("Mozilla/5.0 (compatible; GPTBot/1.1; +https://openai.com/gptbot)", "GPTBot"),
        ("Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)", "ClaudeBot"),
        ("CCBot/2.0 (https://commoncrawl.org/faq/)", "CCBot"),
        ("Mozilla/5.0 (compatible; Google-Extended)", "Google-Extended"),
    ]:
        got = CR.classify(ua)
        if got != want:
            fails.append(f"classify({ua!r}) = {got!r}, expected {want!r}")
        if CR.purpose(got) != "training":
            fails.append(f"purpose({got!r}) = {CR.purpose(got)!r}, expected 'training'")

    # Retrieval crawlers: can actually put a page in front of a person.
    for ua, want in [
        ("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", "Googlebot"),
        ("Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)", "Bingbot"),
        ("Mozilla/5.0 (compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot)", "OAI-SearchBot"),
        ("Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)", "PerplexityBot"),
        ("Mozilla/5.0 (Applebot/0.1; +http://www.apple.com/go/applebot)", "Applebot"),
    ]:
        got = CR.classify(ua)
        if got != want:
            fails.append(f"classify({ua!r}) = {got!r}, expected {want!r}")
        if CR.purpose(got) != "retrieval":
            fails.append(f"purpose({got!r}) = {CR.purpose(got)!r}, expected 'retrieval'")

    # Google-Extended must not fall into the old lumped Google-Other bucket,
    # or it would silently vanish from the training count.
    other = CR.classify("Mozilla/5.0 (compatible; GoogleOther)")
    if other != "Google-Other":
        fails.append(f"GoogleOther classified as {other!r}, expected 'Google-Other'")
    if CR.purpose("Google-Other") is not None:
        fails.append("Google-Other (verification/misc tool) must stay unclassified, "
                      f"got purpose={CR.purpose('Google-Other')!r}")

    # A bot in neither named set (e.g. Yandex) must not be guessed into
    # either bucket: unclassified is honest, a wrong guess is not.
    if CR.purpose("YandexBot") is not None:
        fails.append(f"YandexBot must be unclassified, got {CR.purpose('YandexBot')!r}")

    # The acceptance line itself: a retrieval crawler with zero fetches in
    # the window must be nameable as absent, not silently omitted.
    seen = {"Googlebot", "Bingbot"}
    missing = sorted(CR.RETRIEVAL_BOTS - seen)
    want_missing = sorted({"OAI-SearchBot", "PerplexityBot", "Applebot"})
    if missing != want_missing:
        fails.append(f"missing retrieval set = {missing!r}, expected {want_missing!r}")

    if fails:
        print("FAIL:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"OK: {len(CR.TRAINING_BOTS)} training bot(s), "
          f"{len(CR.RETRIEVAL_BOTS)} retrieval bot(s), all classification checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
