#!/usr/bin/env python3
"""
The accept test: a checklist derived mechanically from the same record that
prints a card or a zone page, answered as closed yes/no questions, so a
generated image cannot pass while contradicting the content it illustrates.

WHY THIS EXISTS
---------------
ops/review_heroes.py's contact sheets show twelve images to a page at 320
pixels wide. At that size the only question a reviewer can answer is "is
this roughly the right kind of room", and the keyless key station (EM-003,
a photograph with no key, no bowl and no hooks anywhere in frame) passed
that question. The verdict was not dishonest, it was an answer to the wrong
question asked at a resolution that could not support a better one.

PLAN-MEDIA-2026-09-07.md section 4 works through why and specifies this
tool. Read that file for the full derivation and the three checked examples
this module's own self-test replays.

THE STRUCTURAL GUARANTEE
-------------------------
The checklist is built from the same fields the card or page itself prints:
a card's `callouts`, or a zone's `done_looks_like` and `leave_behind.standard`
from content/manual/source/content.json. Nobody hand-writes a checklist that
can drift from the content it is supposed to check, because there is no
second copy to drift.

THREE PARTS, EACH A CLOSED QUESTION
------------------------------------
must_show      concrete, countable nouns the image must contain. Item 0 is
               the subject's primary object and is called out as the hard
               fail in the source plan; this implementation still requires
               every must_show item to answer true, because "a picture
               cannot pass while contradicting its own card" does not carve
               out an exception for the second or third object.
must_not_show  a fixed, universal list per image class (see HERO_NEGATIVES
               and CARD_NEGATIVES below). Any true answer is a hard fail.
contradicts    the negative image of the standard: phrases like "no blank
               silhouettes" or "nothing else" already written into a zone's
               own done_looks_like/leave_behind text, extracted rather than
               invented. A zone whose text carries no such phrase gets an
               empty contradicts list rather than a fabricated one; this
               module never writes a claim the source content did not make.

WHAT IS AND IS NOT DONE HERE, HONESTLY
----------------------------------------
Built: checklist derivation for both card and zone sources, the scoring
logic, and the vision call plumbed the same way every other provider call
in this repo is (ops/generate_card_art.py's secrets()/key pattern, reused
rather than duplicated). --self-test replays the three outcomes verified by
hand against gemini-3.6-flash on 2026-09-07 (recorded in
PLAN-MEDIA-2026-09-07.md section 4) and needs no credential or network
access, so it can run in every environment including this one.

Not done here: wiring this in as the second half of
ops/generate_card_art.py's verify() (PLAN-MEDIA-2026-09-07.md item 6), and
an actual --all run over the 346 images, because this sandbox has neither
a GEMINI_API_KEY nor outbound egress (confirmed 2026-09-08: the agent
proxy answers connect_rejected on every outbound CONNECT, and
.env.secrets does not exist here). --all and --one report that plainly
and refuse rather than guess, the same way ops/generate_card_art.py
already does when a key is absent.

Run:  python ops/accept_image.py --self-test
      python ops/accept_image.py --check
      python ops/accept_image.py --one EM-003
      python ops/accept_image.py --all
"""
from __future__ import annotations

import base64
import io
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

CONTENT_JSON = os.path.join(ROOT, "content", "manual", "source", "content.json")
CARDTEXT = os.path.join(ROOT, "build", "entryway-cardtext.json")
HERO_VERDICTS = os.path.join(ROOT, "ops", "hero-verdicts.json")
CARD_VERDICTS = os.path.join(ROOT, "ops", "card-hero-verdicts.json")
ZONE_HEROES = os.path.join(ROOT, "build", "heroes", "zones")
CARD_HEROES = os.path.join(ROOT, "build", "heroes", "entryway")

MODEL = "gemini-3.6-flash"
API_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent")

# Fixed, universal hard-fail questions. Not derived per image, because they
# are not about what a specific zone or card needs; they are about what no
# published photograph on this site may ever contain, whatever it shows.
# Straight from PLAN-MEDIA-2026-09-07.md section 4, part 2.
HERO_NEGATIVES = [
    "readable lettering or text visible anywhere in the image",
    "a brand name, logo, or product packaging visible",
    "a human face or human figure visible",
    "an object that looks physically impossible or malformed",
]

# The card-face question set is different from the hero-photo one:
# PLAN-MEDIA-2026-09-07.md section A5 names these four explicitly, because a
# card face is a graphic on a game card, not a photograph of a room, and the
# defects that matter there are different (a fabricated statistic printed
# into the art, not a missing tray).
CARD_NEGATIVES = [
    "a numeric statistic or number rendered as text in the image",
    "garbled or nonsense lettering visible",
    "a block or pattern resembling a QR code",
    "a brand name, logo, or product packaging visible",
]


# --------------------------------------------------------------- checklist

def _noun_phrases(text: str, cap: int = 6) -> list:
    """Split a descriptive sentence into countable phrases, comma by comma.

    Not a parser. "One tray holding keys and sunglasses, one wallet and one
    phone per adult, ... and bare surface on both sides of the tray" becomes
    four phrases, each concrete enough to ask "is X visible: true/false"
    about, which is exactly what done_looks_like was written to support
    (CLAUDE.md section 7 asks for done_looks_like "in countable terms").
    Does not split inside a phrase on its own internal "and": that would
    turn "keys and sunglasses" into two fragments of one object group.
    """
    text = text.strip().rstrip(".")
    out = []
    for part in text.split(","):
        p = re.sub(r"^\s*and\s+", "", part.strip(), flags=re.I).strip()
        if p:
            out.append(p)
    return out[:cap]


def _negative_clauses(text: str) -> list:
    """Phrases already written as a negative in the zone's own words.

    Finds "no X" and "nothing X" up to the next comma/period/semicolon and
    returns the bare phrase (what must NOT be visible). A zone whose text
    never states its own negative gets an empty list here: PLAN-MEDIA's own
    contradicts examples come from a zone's real wording, not from a guess,
    and this function does not fabricate a phrase no source text contains.
    """
    out = []
    for m in re.finditer(r"\b(?:no|nothing)\s+([^,.;]+)", text, flags=re.I):
        phrase = re.sub(r"^\s*else\b\s*", "", m.group(1).strip(), flags=re.I).strip()
        if phrase:
            out.append(phrase)
    seen, uniq = set(), []
    for p in out:
        k = p.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


def _strip_parenthetical(callout: str) -> str:
    """"Key Bowl (Home Base)" -> "Key Bowl". The parenthetical names WHERE
    the object sits on the card layout, not what a photograph must show."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", callout).strip()


def checklist_for_zone(zone: dict) -> dict:
    """must_show/must_not_show/contradicts for one content.json zone record."""
    done = zone.get("done_looks_like", "")
    standard = (zone.get("leave_behind") or {}).get("standard", "")
    show = _noun_phrases(done)
    if not show:
        raise ValueError("zone has no done_looks_like text to derive a "
                          "checklist from: %r" % zone.get("zone"))
    return {
        "kind": "zone",
        "subject": zone.get("zone", ""),
        "must_show": show,
        "must_not_show": list(HERO_NEGATIVES),
        "contradicts": _negative_clauses(done + " " + standard),
    }


def checklist_for_card(card: dict) -> dict:
    """must_show/must_not_show for one Entryway card record. No contradicts:
    a card face is a graphic, not a photograph of a before/after state, so
    PLAN-MEDIA-2026-09-07.md's "negative image of the standard" concept does
    not apply to it; leaving the list empty is honest, not incomplete."""
    callouts = card.get("callouts") or []
    show = [_strip_parenthetical(c) for c in callouts]
    show = [s for s in show if s]
    if not show:
        raise ValueError("card has no callouts to derive a checklist from: "
                          "%r" % card.get("id"))
    return {
        "kind": "card",
        "subject": card.get("title", card.get("id", "")),
        "must_show": show,
        "must_not_show": list(CARD_NEGATIVES),
        "contradicts": [],
    }


def question_key(section: str, item: str) -> str:
    """One canonical key for a checklist item, used both when building the
    vision prompt and when scoring its answers, so the two cannot drift."""
    return f"{section}:{item}"


def all_questions(checklist: dict) -> list:
    out = []
    for item in checklist["must_show"]:
        out.append((question_key("must_show", item),
                    f"Is {item} visible in this image?"))
    for item in checklist["must_not_show"]:
        out.append((question_key("must_not_show", item),
                    f"Does this image contain {item}?"))
    for item in checklist["contradicts"]:
        out.append((question_key("contradicts", item),
                    f"Is {item} visible in this image?"))
    return out


# ------------------------------------------------------------------- score

def score(checklist: dict, answers: dict) -> tuple:
    """(passed, reasons). Pure logic, no network: this is what --self-test
    exercises against the three outcomes already verified by hand.

    answers maps a question_key() to True/False. A key missing from answers
    is treated as an unanswered hard fail rather than a silent pass, the
    same "unknown is not unused" rule CLAUDE.md 0.4 states for every other
    check in this repository.
    """
    reasons = []
    for i, item in enumerate(checklist["must_show"]):
        k = question_key("must_show", item)
        if k not in answers:
            reasons.append(f"not answered: {item}")
        elif not answers[k]:
            hard = " (hard fail, primary object)" if i == 0 else ""
            reasons.append(f"required but not shown: {item}{hard}")
    for item in checklist["must_not_show"]:
        k = question_key("must_not_show", item)
        if k not in answers:
            reasons.append(f"not answered: {item}")
        elif answers[k]:
            reasons.append(f"present but forbidden: {item}")
    for item in checklist["contradicts"]:
        k = question_key("contradicts", item)
        if k not in answers:
            reasons.append(f"not answered: {item}")
        elif answers[k]:
            reasons.append(f"shows the before state: {item}")
    return (len(reasons) == 0, reasons)


# ------------------------------------------------------------------ vision

def _secrets() -> dict:
    import generate_card_art as gca
    return gca.secrets()


def ask_vision(image_path: str, checklist: dict, key: str,
               order: list = None) -> dict:
    """One pass: every question in `order` (or checklist order), answered
    true/false by the model. Returns {question_key: bool}."""
    questions = dict(all_questions(checklist))
    keys = order or list(questions.keys())
    numbered = "\n".join(f"{i+1}. {questions[k]}" for i, k in enumerate(keys))
    prompt = (
        "Answer every numbered question about the attached image with only "
        "true or false. Reply with nothing but a JSON object mapping each "
        "question's number (as a string) to true or false, no other text.\n"
        + numbered)
    img = io.open(image_path, "rb").read()
    ext = os.path.splitext(image_path)[1].lstrip(".").lower()
    mime = "image/png" if ext == "png" else f"image/{ext}"
    body = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inlineData": {"mimeType": mime,
                             "data": base64.b64encode(img).decode()}},
        ]}],
    }
    req = urllib.request.Request(
        API_URL, data=json.dumps(body).encode(),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        method="POST")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt * 3)
                continue
            # NOT SystemExit. A vision call that fails is an image nobody
            # looked at, and that has to be reportable per image rather than
            # fatal to the run.
            #
            # Found 2026-09-09: the Gemini free quota ran out mid-review and
            # this killed the process. In --one that printed the checklist,
            # then an error, and no verdict, which reads as an inconclusive
            # review rather than as "the reviewer is blind". I recorded two
            # such runs as "no verdict" and drew a conclusion from the batch
            # they were in. In --all it would abort the whole pass partway
            # through, after some images had verdicts and the rest had none.
            #
            # 429 is the billing gate rather than a transient fault, so
            # retrying it is what exhausts the quota faster.
            _body = e.read()[:200].decode(errors="replace")
            raise VisionUnavailable("%s %s" % (e.code, " ".join(_body.split())))
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    raw = json.loads(re.sub(r"^```(?:json)?|```$", "", text.strip(),
                            flags=re.M).strip())
    return {keys[int(n) - 1]: bool(v) for n, v in raw.items()}


class VisionUnavailable(Exception):
    """The reviewer could not look. Never the same as a judgement.

    Every caller must turn this into UNCHECKED, never into PASS or FAIL. An
    image that was not seen has not been rejected, and a batch that could not
    see has not reviewed anything.
    """


def ask_vision_twice(image_path: str, checklist: dict, key: str) -> tuple:
    """Two passes, item order shuffled the second time, per PLAN-MEDIA-
    2026-09-07.md section 4 part 4: a single yes/no is evidence, not a
    gate, because the model is measurably permissive on category words.
    Returns (answers_if_they_agree_or_pass1, disagreement_keys)."""
    keys = list(dict(all_questions(checklist)).keys())
    a1 = ask_vision(image_path, checklist, key, order=keys)
    shuffled = keys[:]
    random.Random(0).shuffle(shuffled)
    a2 = ask_vision(image_path, checklist, key, order=shuffled)
    disagree = [k for k in keys if a1.get(k) != a2.get(k)]
    return a1, disagree


# -------------------------------------------------------------------- run

def _slug(s: str) -> str:
    """Mirrors ops/wire_zone_heroes.py's own slug(), not re-imported because
    that module executes top-level code (a NAME_MAP file read) on import."""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _zones_by_stem() -> dict:
    """hero stem ("entryway--landing-zone") -> zone record, all 114.

    Hero image stems are slug(room) + "--" + slug(zone), confirmed against
    ops/wire_zone_heroes.py's own ALT_VERIFIED table ("garage--hand-tool-
    wall-and-cabinets" for room "Garage", zone "Hand Tool Wall and
    Cabinets"). This is the identifier already used throughout this repo
    (ops/hero-verdicts.json, the web derivative filenames), so --one and
    --check use it rather than the bare zone name: three zone names repeat
    across rooms ("Dresser Drawers", "Shower or Tub", "Toilet Area"), and a
    dict keyed on the bare name would silently collapse 114 zones to 111,
    which is exactly the "count as a finding without opening a sample"
    shape CLAUDE.md 5c warns against, discovered by --check reporting 111
    where GOALS.md says 114 and re-deriving by hand instead of trusting it.
    """
    d = json.load(io.open(CONTENT_JSON, encoding="utf-8"))
    out = {}
    for room in d["rooms"]:
        for z in room["zones"]:
            stem = f"{_slug(room['room'])}--{_slug(z['zone'])}"
            out[stem] = z
    return out


def _cards() -> dict:
    d = json.load(io.open(CARDTEXT, encoding="utf-8"))
    return {c["id"]: c for c in d["cards"] if "callouts" in c}


def run_one(image_id: str) -> int:
    cards = _cards()
    if image_id in cards:
        checklist = checklist_for_card(cards[image_id])
        image_path = os.path.join(CARD_HEROES, image_id + ".png")
    else:
        stems = _zones_by_stem()
        if image_id not in stems:
            print(f"  {image_id!r} is not a known card id or zone hero "
                  f"stem. Known cards: {sorted(cards)[:5]}...; known zone "
                  f"stems: {sorted(stems)[:5]}...")
            return 1
        checklist = checklist_for_zone(stems[image_id])
        image_path = os.path.join(ZONE_HEROES, image_id + ".png")

    print(f"  subject: {checklist['subject']}")
    print(f"  must_show ({len(checklist['must_show'])}): {checklist['must_show']}")
    print(f"  must_not_show ({len(checklist['must_not_show'])}): "
          f"{checklist['must_not_show']}")
    print(f"  contradicts ({len(checklist['contradicts'])}): "
          f"{checklist['contradicts']}")

    if not os.path.exists(image_path):
        print(f"  no source image at {image_path}; nothing to test here. "
              f"Normal outside Phil's own machine, where build/heroes/ is "
              f"gitignored and not present.")
        return 0

    key = _secrets().get("GEMINI_API_KEY")
    if not key:
        print("  BLOCKED: no GEMINI_API_KEY in this environment, so the "
              "image cannot actually be judged. The checklist above is "
              "real; only the vision call is unavailable here.")
        return 1

    try:
        a1, disagree = ask_vision_twice(image_path, checklist, key)
    except VisionUnavailable as e:
        # UNCHECKED, and it says so in that word. The checklist above is real
        # and was derived from the zone's own text; only the looking failed.
        # Reporting this as FAIL would reject an image nobody saw, and on
        # 2026-09-09 that is exactly what a quota exhaustion looked like from
        # the outside: confident findings with nothing behind them.
        print("  UNCHECKED: the reviewer could not look at this image (%s)."
              % str(e)[:150])
        print("  This is NOT a rejection. The image has not been judged, and "
              "a 429 here is the image-generation billing gate, not a fault "
              "in the picture.")
        return 2
    if disagree:
        print(f"  DISAGREEMENT on {len(disagree)} item(s) between the two "
              f"shuffled passes, escalate to a human: {disagree}")
    passed, reasons = score(checklist, a1)
    print(f"  {'PASS' if passed else 'FAIL'}")
    for r in reasons:
        print(f"    - {r}")
    return 0 if passed else 1


def check_all() -> int:
    """Derive a checklist for every card and every zone, no vision call.
    Proves the derivation itself does not crash on the real corpus, which
    is everything that can be verified without a credential or egress."""
    cards = _cards()
    zones = _zones_by_stem()
    bad = []
    for cid, c in cards.items():
        try:
            checklist_for_card(c)
        except Exception as e:                                    # noqa: BLE001
            bad.append(f"card {cid}: {e}")
    for stem, z in zones.items():
        try:
            checklist_for_zone(z)
        except Exception as e:                                    # noqa: BLE001
            bad.append(f"zone {stem!r}: {e}")
    print(f"  {len(cards)} card checklist(s), {len(zones)} zone "
          f"checklist(s) derived, {len(bad)} error(s)")
    for b in bad:
        print(f"    - {b}")
    return 1 if bad else 0


# --------------------------------------------------------------- self-test

def self_test() -> int:
    """Replay the three outcomes verified by hand against gemini-3.6-flash
    on 2026-09-07 (PLAN-MEDIA-2026-09-07.md section 4 part 3), using the
    real checklist derivation and the real scoring logic, with the
    documented answers standing in for a live vision call. No network, no
    credential: this is what proves the accept test's LOGIC is right
    before a single paid image is generated, which is the item's own
    acceptance criterion.
    """
    fails = []
    zones = _zones_by_stem()
    cards = _cards()

    # 1. EM-003 (Key Station), approved "ok" by the old contact-sheet
    #    review, actually shows no key anywhere. Must fail, on must_show.
    cl = checklist_for_card(cards["EM-003"])
    answers = {question_key("must_show", "Location"): False,
               question_key("must_show", "Key Bowl"): False,
               question_key("must_show", "Key Hooks"): False,
               question_key("must_show", "Outgoing Mail Slot"): True,
               question_key("must_show", "Daily Catch-All Tray"): True,
               question_key("must_show", "Visual Cue / Reminder"): True}
    for item in cl["must_not_show"]:
        answers[question_key("must_not_show", item)] = False
    passed, reasons = score(cl, answers)
    if passed:
        fails.append("EM-003 scored PASS; the plan's own recorded run "
                      "found no key, bowl or hooks visible and must fail")
    elif not any("Key Bowl" in r for r in reasons):
        fails.append(f"EM-003 failed for the wrong reason(s): {reasons}")

    # 2. entryway--landing-zone, approved "ok", genuinely shows a tray, keys
    #    and a wallet. Must pass.
    cl = checklist_for_zone(zones["entryway--landing-zone"])
    answers = {question_key("must_show", item): True for item in cl["must_show"]}
    for item in cl["must_not_show"]:
        answers[question_key("must_not_show", item)] = False
    for item in cl["contradicts"]:
        answers[question_key("contradicts", item)] = False
    passed, reasons = score(cl, answers)
    if not passed:
        fails.append(f"entryway landing zone scored FAIL, should PASS: "
                      f"{reasons}")

    # 3. The bathroom medicine cabinet: independently caught a physically
    #    impossible/malformed object (the levitating sink) no human
    #    reviewer flagged. Must fail on must_not_show regardless of
    #    must_show, because must_not_show items are hard fails on their own.
    cl = checklist_for_zone(zones["primary-bathroom--medicine-cabinet-or-wall-storage"])
    answers = {question_key("must_show", item): True for item in cl["must_show"]}
    for item in cl["must_not_show"]:
        answers[question_key("must_not_show", item)] = False
    answers[question_key("must_not_show",
                          "an object that looks physically impossible or "
                          "malformed")] = True
    for item in cl["contradicts"]:
        answers[question_key("contradicts", item)] = False
    passed, reasons = score(cl, answers)
    if passed:
        fails.append("medicine cabinet scored PASS with a malformed object "
                      "flagged true; must_not_show should be a hard fail")

    # 4. The garage hand tool wall: done_looks_like states its own negative
    #    ("no blank silhouettes") in plain text. Confirms contradicts is
    #    derived from the real source rather than invented, and that a
    #    true answer on it fails the image even with every must_show met.
    cl = checklist_for_zone(zones["garage--hand-tool-wall-and-cabinets"])
    if not any("blank silhouette" in c.lower() for c in cl["contradicts"]):
        fails.append(f"garage tool wall: 'no blank silhouettes' was not "
                      f"derived into contradicts: {cl['contradicts']}")
    else:
        answers = {question_key("must_show", item): True
                   for item in cl["must_show"]}
        for item in cl["must_not_show"]:
            answers[question_key("must_not_show", item)] = False
        for item in cl["contradicts"]:
            answers[question_key("contradicts", item)] = True
        passed, reasons = score(cl, answers)
        if passed:
            fails.append("garage tool wall scored PASS with its own "
                          "contradicts phrase true; should FAIL")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  accept_image self-test: 4/4 historical outcomes reproduced")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    if "--self-test" in argv:
        return self_test()
    if "--check" in argv:
        return check_all()
    if "--one" in argv:
        return run_one(argv[argv.index("--one") + 1])
    if "--all" in argv:
        key = _secrets().get("GEMINI_API_KEY")
        if not key:
            print("  BLOCKED: no GEMINI_API_KEY in this environment. "
                  "Checklists derive fine (see --check); the vision call "
                  "that would actually judge an image cannot run here.")
            return 1
        cards, stems = _cards(), _zones_by_stem()
        bad = 0
        for cid in sorted(cards):
            print(f"\n{cid}")
            bad += run_one(cid) != 0
        for stem in sorted(stems):
            print(f"\n{stem}")
            bad += run_one(stem) != 0
        return 1 if bad else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
