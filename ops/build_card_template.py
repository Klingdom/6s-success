#!/usr/bin/env python3
"""
Lay out a 6S Success card front and back at real print sizes.

WHAT CHANGED, AND WHY IT HAD TO
-------------------------------
The card canvas is 750 x 1050 px, which is 2.5 x 3.5 inches at 300 dpi. One
printed point is therefore 4.1667 px. The previous template set its body copy
at 8.5px to 13.5px, which is 2.0pt to 3.2pt on a card in somebody's hand. The
callout list under the photograph was 10.5px, or 2.52pt. Print body copy starts
being readable around 6 to 7pt.

So the deck was not "a bit tight". It was unreadable, and it was being sold.

Nothing in the pipeline could catch it, because sizes were bare numbers with no
unit attached to a physical object, and because the render step verified only
that a PNG existed and was not one flat colour.

Two rules now govern this file, both enforced in code:

  1. Every size comes from ops/card_spec.py, declared in POINTS. Floor 7pt for
     any glyph, 8.5pt for anything that is a sentence.
  2. Content is fitted to the card, never the other way round. If a block does
     not fit at a legible size it is trimmed at a sentence boundary or moved to
     the back. A card that cannot be read is worth less than a card that says
     less.

WHAT THE CARD CARRIES NOW
-------------------------
The corpus holds roughly 2,500 characters per card. A 2.5 x 3.5 inch card holds
about 1,300 at legible sizes, across both faces. Half of it has to leave the
card, so it was cut on purpose rather than by shrinking:

  FRONT, "what is this and what do I do"
    family colour + glyph + word, card code, difficulty, title, tagline,
    photograph, ONE action block, footer meta (6S step, reset time, brand).

  BACK, "how do I run it and what is next"
    HOW IT WORKS or KEY POINTS (the callouts, as a numbered checklist), THE
    QUEST (the home quest challenge), and a footer carrying the next card and
    the card's own closing line. Two blocks, because two is what a 2.5 by 3.5
    inch back holds at 8.5pt.

  CUT FROM THE PRINTED CARD, still in build/entryway-cardtext.json for the site
  and the booklet:
    did_you_know      unsourced factual claims. CLAUDE.md section 8 forbids
                      fabricated statistics, and "the speed at which temporary
                      items are processed has a major impact" has no source
                      behind it. Cut on trust grounds before space grounds.
    best_practices    a near-duplicate of callouts. Printing both spent a
                      quarter of the back saying one thing twice.
    related_path      five rows of cross references. That is a booklet index.
    progress_tracker  tick boxes on a card that gets reshuffled and reused.
    objective         restates the title and the quick win.
    six_s_lesson      teaching copy. The 6S step chip in the footer carries the
                      same signal in one word.
    game_effect       "Gain +1 Momentum. Reveal 1 Problem Card." is a rule
                      for a rulebook this repository does not hold, and the
                      quest is the more useful of the two on a card that has
                      room for exactly one. It stays in the data for the app.
    real_world_action, banner
                      good copy, no room, already absent from the old front.
    pro_tip, why_it_matters
                      no room. The most spare space on any back in this deck
                      is 158px and a labelled two-line block needs 193.

COLOUR
------
Family colour comes from the six-S palette in ops/card_spec.py, not from a
private set of browns. Eight playing families over six brand hues, so two take
a documented deep shade, and every family also carries a glyph, because colour
alone fails across a table for a colour-blind player and fails anyway when two
warm hues sit next to each other under a lamp.

Run:  python ops/build_card_template.py --list
      python ops/build_card_template.py --all
      python ops/build_card_template.py --card EE-001
      python ops/build_card_template.py --all --bleed   (print-ready sheets)

Then ops/render_cards.py, which photographs each card and then measures it:
the deck is only built if no glyph fell under the floor, nothing overflowed a
box, and nothing landed outside the safe area.
"""
from __future__ import annotations

import collections
import glob
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import card_spec as S                                          # noqa: E402

HEROES = os.path.join(ROOT, "build", "heroes")
OUT = os.path.join(ROOT, "build", "card-fronts")
FONTS = os.path.join(ROOT, "site", "assets", "fonts")

CARD_W, CARD_H = S.CARD_W, S.CARD_H     # kept: ops/render_cards.py imports them

# MEASURED, not guessed. ops/render_cards.py renders a calibration strip in
# each role's exact style and reports the advance width per character; these
# are those numbers in em, so they stay true if a size in card_spec changes.
# The first version of this table guessed 44 characters per line for the
# tagline. The real answer is 23, because the tagline is uppercase and tracked,
# and that single wrong guess is what put a card 436px over its own height.
# A pair is (lowercase, uppercase). Capitals are about 21% wider in Inter, and
# this corpus writes half its sentences with an uppercase phrase in front of
# them: "INSPECT WHILE CLEANING CHALLENGE. During your next weekly reset..."
# A single average put that quest at four lines when it renders in five, and
# the card's back overflowed by exactly one line on a fifth of the deck.
# Per-character advance in em, each character measured twenty times in the
# card's own CSS, one table per role.
#
# An average will not do here. Fraunces 900 runs from 0.19em for a space to
# 1.10em for a W, so an average called EM-011's name one line when it renders
# as two; and in the running text an average built from a punctuation-free
# sentence over-reserved a line on ES-001, which cost that card its tagline
# for nothing. Both directions of that error are defects: one overflows the
# card, the other silently deletes copy that would have fitted.
#
# The roles the CSS uppercases show identical values for a and A, which is
# the measurement confirming text-transform is in force.
ADVANCE = {
    "title": {
        ' ': 0.1855, '!': 0.3260, '"': 0.4300, '%': 0.8495, '&': 0.7840,
        "'": 0.2015, '(': 0.3815, ')': 0.3815, '+': 0.5525, ',': 0.3205,
        '-': 0.3800, '.': 0.3080, '/': 0.4890, ':': 0.3080, ';': 0.3210,
        '?': 0.5885, '0': 0.7105, '1': 0.4915, '2': 0.6475, '3': 0.5990,
        '4': 0.6785, '5': 0.6140, '6': 0.6545, '7': 0.5535, '8': 0.6715,
        '9': 0.6545, 'A': 0.7670, 'B': 0.7545, 'C': 0.7025, 'D': 0.8165,
        'E': 0.6725, 'F': 0.6320, 'G': 0.7650, 'H': 0.8820, 'I': 0.4420,
        'J': 0.5800, 'K': 0.8445, 'L': 0.6470, 'M': 0.9650, 'N': 0.7520,
        'O': 0.7850, 'P': 0.7470, 'Q': 0.7855, 'R': 0.8110, 'S': 0.6290,
        'T': 0.7260, 'U': 0.7475, 'V': 0.7380, 'W': 1.0995, 'X': 0.7340,
        'Y': 0.6910, 'Z': 0.6420, 'a': 0.5810, 'b': 0.6295, 'c': 0.5370,
        'd': 0.6395, 'e': 0.5400, 'f': 0.4355, 'g': 0.5980, 'h': 0.6650,
        'i': 0.3320, 'j': 0.3320, 'k': 0.6415, 'l': 0.3325, 'm': 0.9880,
        'n': 0.6650, 'o': 0.6030, 'p': 0.6440, 'q': 0.6305, 'r': 0.5145,
        's': 0.5115, 't': 0.4215, 'u': 0.6540, 'v': 0.5630, 'w': 0.8680,
        'x': 0.5800, 'y': 0.5860, 'z': 0.5100
    },
    "lead": {
        ' ': 0.2818, '!': 0.3828, '"': 0.5966, '%': 1.0604, '&': 0.7167,
        "'": 0.3838, '(': 0.4219, ')': 0.4219, '+': 0.7235, ',': 0.3789,
        '-': 0.5126, '.': 0.3789, '/': 0.4331, ':': 0.3789, ';': 0.3877,
        '?': 0.6044, '0': 0.7191, '1': 0.4761, '2': 0.6747, '3': 0.6903,
        '4': 0.7211, '5': 0.6669, '6': 0.6942, '7': 0.6449, '8': 0.6957,
        '9': 0.6942, 'A': 0.8053, 'B': 0.7065, 'C': 0.7846, 'D': 0.7670,
        'E': 0.6523, 'F': 0.6317, 'G': 0.7953, 'H': 0.7919, 'I': 0.3257,
        'J': 0.6293, 'K': 0.7640, 'L': 0.6103, 'M': 0.9764, 'N': 0.8070,
        'O': 0.8153, 'P': 0.6928, 'Q': 0.8216, 'R': 0.7016, 'S': 0.6996,
        'T': 0.7123, 'U': 0.7767, 'V': 0.8053, 'W': 1.1032, 'X': 0.7831,
        'Y': 0.7758, 'Z': 0.7089, 'a': 0.8053, 'b': 0.7065, 'c': 0.7846,
        'd': 0.7670, 'e': 0.6523, 'f': 0.6317, 'g': 0.7953, 'h': 0.7919,
        'i': 0.3257, 'j': 0.6293, 'k': 0.7640, 'l': 0.6103, 'm': 0.9764,
        'n': 0.8070, 'o': 0.8153, 'p': 0.6928, 'q': 0.8216, 'r': 0.7016,
        's': 0.6996, 't': 0.7123, 'u': 0.7767, 'v': 0.8053, 'w': 1.1032,
        'x': 0.7831, 'y': 0.7758, 'z': 0.7089
    },
    "body": {
        ' ': 0.2813, '!': 0.2876, '"': 0.4658, '%': 0.9820, '&': 0.6440,
        "'": 0.2998, '(': 0.3647, ')': 0.3647, '+': 0.6616, ',': 0.2881,
        '-': 0.4600, '.': 0.2881, '/': 0.3604, ':': 0.2881, ';': 0.3018,
        '?': 0.5112, '0': 0.6309, '1': 0.4068, '2': 0.6099, '3': 0.6177,
        '4': 0.6460, '5': 0.5933, '6': 0.6201, '7': 0.5845, '8': 0.6187,
        '9': 0.6201, 'A': 0.7039, 'B': 0.6543, 'C': 0.7305, 'D': 0.7217,
        'E': 0.6011, 'F': 0.5903, 'G': 0.7461, 'H': 0.7432, 'I': 0.2686,
        'J': 0.5708, 'K': 0.6719, 'L': 0.5654, 'M': 0.9033, 'N': 0.7534,
        'O': 0.7646, 'P': 0.6387, 'Q': 0.7646, 'R': 0.6436, 'S': 0.6416,
        'T': 0.6455, 'U': 0.7441, 'V': 0.7039, 'W': 1.0086, 'X': 0.6821,
        'Y': 0.6787, 'Z': 0.6289, 'a': 0.5615, 'b': 0.6123, 'c': 0.5713,
        'd': 0.6123, 'e': 0.5830, 'f': 0.3330, 'g': 0.6133, 'h': 0.5913,
        'i': 0.2422, 'j': 0.2422, 'k': 0.5488, 'l': 0.2422, 'm': 0.8760,
        'n': 0.5908, 'o': 0.5996, 'p': 0.6123, 'q': 0.6123, 'r': 0.3913,
        's': 0.5278, 't': 0.3272, 'u': 0.5913, 'v': 0.5620, 'w': 0.8184,
        'x': 0.5459, 'y': 0.5620, 'z': 0.5523
    },
    "body_sm": {
        ' ': 0.2812, '!': 0.2875, '"': 0.4657, '%': 0.9817, '&': 0.6439,
        "'": 0.2997, '(': 0.3647, ')': 0.3647, '+': 0.6614, ',': 0.2880,
        '-': 0.4598, '.': 0.2880, '/': 0.3603, ':': 0.2880, ';': 0.3017,
        '?': 0.5111, '0': 0.6307, '1': 0.4066, '2': 0.6097, '3': 0.6175,
        '4': 0.6458, '5': 0.5931, '6': 0.6199, '7': 0.5843, '8': 0.6185,
        '9': 0.6199, 'A': 0.7037, 'B': 0.6541, 'C': 0.7303, 'D': 0.7215,
        'E': 0.6009, 'F': 0.5902, 'G': 0.7459, 'H': 0.7430, 'I': 0.2685,
        'J': 0.5707, 'K': 0.6717, 'L': 0.5653, 'M': 0.9031, 'N': 0.7532,
        'O': 0.7644, 'P': 0.6385, 'Q': 0.7644, 'R': 0.6434, 'S': 0.6414,
        'T': 0.6453, 'U': 0.7440, 'V': 0.7037, 'W': 1.0083, 'X': 0.6820,
        'Y': 0.6785, 'Z': 0.6287, 'a': 0.5614, 'b': 0.6121, 'c': 0.5711,
        'd': 0.6121, 'e': 0.5828, 'f': 0.3329, 'g': 0.6131, 'h': 0.5911,
        'i': 0.2421, 'j': 0.2421, 'k': 0.5487, 'l': 0.2421, 'm': 0.8757,
        'n': 0.5907, 'o': 0.5995, 'p': 0.6121, 'q': 0.6121, 'r': 0.3912,
        's': 0.5277, 't': 0.3271, 'u': 0.5911, 'v': 0.5619, 'w': 0.8181,
        'x': 0.5458, 'y': 0.5619, 'z': 0.5521
    },
    "point": {
        ' ': 0.2368, '!': 0.3378, '"': 0.5516, '%': 1.0153, '&': 0.6717,
        "'": 0.3388, '(': 0.3769, ')': 0.3769, '+': 0.6785, ',': 0.3339,
        '-': 0.4676, '.': 0.3339, '/': 0.3881, ':': 0.3339, ';': 0.3427,
        '?': 0.5594, '0': 0.6741, '1': 0.4310, '2': 0.6297, '3': 0.6453,
        '4': 0.6761, '5': 0.6219, '6': 0.6492, '7': 0.5999, '8': 0.6507,
        '9': 0.6492, 'A': 0.7603, 'B': 0.6614, 'C': 0.7395, 'D': 0.7220,
        'E': 0.6073, 'F': 0.5868, 'G': 0.7503, 'H': 0.7469, 'I': 0.2807,
        'J': 0.5843, 'K': 0.7190, 'L': 0.5653, 'M': 0.9314, 'N': 0.7620,
        'O': 0.7703, 'P': 0.6478, 'Q': 0.7766, 'R': 0.6566, 'S': 0.6546,
        'T': 0.6673, 'U': 0.7317, 'V': 0.7603, 'W': 1.0582, 'X': 0.7381,
        'Y': 0.7308, 'Z': 0.6639, 'a': 0.5804, 'b': 0.6302, 'c': 0.5882,
        'd': 0.6302, 'e': 0.5956, 'f': 0.3584, 'g': 0.6317, 'h': 0.6224,
        'i': 0.2709, 'j': 0.2709, 'k': 0.5799, 'l': 0.2709, 'm': 0.9124,
        'n': 0.6224, 'o': 0.6131, 'p': 0.6302, 'q': 0.6302, 'r': 0.4141,
        's': 0.5599, 't': 0.3559, 'u': 0.6224, 'v': 0.5995, 'w': 0.8499,
        'x': 0.5799, 'y': 0.6019, 'z': 0.5726
    },
    "label": {
        ' ': 0.2687, '!': 0.4084, '"': 0.6365, '%': 1.0793, '&': 0.7331,
        "'": 0.4045, '(': 0.4323, ')': 0.4323, '+': 0.7355, ',': 0.4026,
        '-': 0.5212, '.': 0.4026, '/': 0.4499, ':': 0.4026, ';': 0.4099,
        '?': 0.6291, '0': 0.7419, '1': 0.4914, '2': 0.6877, '3': 0.7067,
        '4': 0.7385, '5': 0.6838, '6': 0.7116, '7': 0.6565, '8': 0.7141,
        '9': 0.7116, 'A': 0.8335, 'B': 0.7146, 'C': 0.7937, 'D': 0.7727,
        'E': 0.6599, 'F': 0.6355, 'G': 0.8024, 'H': 0.7985, 'I': 0.3357,
        'J': 0.6399, 'K': 0.7883, 'L': 0.6155, 'M': 0.9934, 'N': 0.8156,
        'O': 0.8230, 'P': 0.7019, 'Q': 0.8317, 'R': 0.7121, 'S': 0.7102,
        'T': 0.7268, 'U': 0.7771, 'V': 0.8335, 'W': 1.1281, 'X': 0.8113,
        'Y': 0.8020, 'Z': 0.7287, 'a': 0.8335, 'b': 0.7146, 'c': 0.7937,
        'd': 0.7727, 'e': 0.6599, 'f': 0.6355, 'g': 0.8024, 'h': 0.7985,
        'i': 0.3357, 'j': 0.6399, 'k': 0.7883, 'l': 0.6155, 'm': 0.9934,
        'n': 0.8156, 'o': 0.8230, 'p': 0.7019, 'q': 0.8317, 'r': 0.7121,
        's': 0.7102, 't': 0.7268, 'u': 0.7771, 'v': 0.8335, 'w': 1.1281,
        'x': 0.8113, 'y': 0.8020, 'z': 0.7287
    },
    "micro": {
        ' ': 0.3520, '!': 0.4213, '"': 0.6230, '%': 1.1044, '&': 0.7626,
        "'": 0.4257, '(': 0.4731, ')': 0.4731, '+': 0.7729, ',': 0.4189,
        '-': 0.5654, '.': 0.4189, '/': 0.4789, ':': 0.4189, ';': 0.4291,
        '?': 0.6435, '0': 0.7597, '1': 0.5229, '2': 0.7231, '3': 0.7363,
        '4': 0.7660, '5': 0.7123, '6': 0.7397, '7': 0.6947, '8': 0.7401,
        '9': 0.7397, 'A': 0.8415, 'B': 0.7592, 'C': 0.8368, 'D': 0.8222,
        'E': 0.7055, 'F': 0.6879, 'G': 0.8490, 'H': 0.8456, 'I': 0.3769,
        'J': 0.6796, 'K': 0.8031, 'L': 0.6654, 'M': 1.0224, 'N': 0.8593,
        'O': 0.8686, 'P': 0.7450, 'Q': 0.8730, 'R': 0.7524, 'S': 0.7504,
        'T': 0.7602, 'U': 0.8359, 'V': 0.8415, 'W': 1.1414, 'X': 0.8197,
        'Y': 0.8134, 'Z': 0.7524, 'a': 0.8415, 'b': 0.7592, 'c': 0.8368,
        'd': 0.8222, 'e': 0.7055, 'f': 0.6879, 'g': 0.8490, 'h': 0.8456,
        'i': 0.3769, 'j': 0.6796, 'k': 0.8031, 'l': 0.6654, 'm': 1.0224,
        'n': 0.8593, 'o': 0.8686, 'p': 0.7450, 'q': 0.8730, 'r': 0.7524,
        's': 0.7504, 't': 0.7602, 'u': 0.8359, 'v': 0.8415, 'w': 1.1414,
        'x': 0.8197, 'y': 0.8134, 'z': 0.7524
    },
    "bline": {
        ' ': 0.2587, '!': 0.3984, '"': 0.6265, '%': 1.0693, '&': 0.7231,
        "'": 0.3945, '(': 0.4223, ')': 0.4223, '+': 0.7255, ',': 0.3926,
        '-': 0.5112, '.': 0.3926, '/': 0.4399, ':': 0.3926, ';': 0.3999,
        '?': 0.6191, '0': 0.7319, '1': 0.4814, '2': 0.6777, '3': 0.6967,
        '4': 0.7285, '5': 0.6738, '6': 0.7016, '7': 0.6465, '8': 0.7041,
        '9': 0.7016, 'A': 0.8235, 'B': 0.7046, 'C': 0.7837, 'D': 0.7627,
        'E': 0.6499, 'F': 0.6255, 'G': 0.7925, 'H': 0.7885, 'I': 0.3256,
        'J': 0.6299, 'K': 0.7783, 'L': 0.6055, 'M': 0.9834, 'N': 0.8056,
        'O': 0.8130, 'P': 0.6919, 'Q': 0.8217, 'R': 0.7021, 'S': 0.7002,
        'T': 0.7168, 'U': 0.7671, 'V': 0.8235, 'W': 1.1181, 'X': 0.8013,
        'Y': 0.7920, 'Z': 0.7187, 'a': 0.8235, 'b': 0.7046, 'c': 0.7837,
        'd': 0.7627, 'e': 0.6499, 'f': 0.6255, 'g': 0.7925, 'h': 0.7885,
        'i': 0.3256, 'j': 0.6299, 'k': 0.7783, 'l': 0.6055, 'm': 0.9834,
        'n': 0.8056, 'o': 0.8130, 'p': 0.6919, 'q': 0.8217, 'r': 0.7021,
        's': 0.7002, 't': 0.7168, 'u': 0.7671, 'v': 0.8235, 'w': 1.1181,
        'x': 0.8013, 'y': 0.7920, 'z': 0.7187
    },
    "nxt": {
        ' ': 0.3568, '!': 0.4579, '"': 0.6718, '%': 1.1356, '&': 0.7919,
        "'": 0.4589, '(': 0.4970, ')': 0.4970, '+': 0.7987, ',': 0.4540,
        '-': 0.5878, '.': 0.4540, '/': 0.5082, ':': 0.4540, ';': 0.4628,
        '?': 0.6796, '0': 0.7943, '1': 0.5512, '2': 0.7499, '3': 0.7655,
        '4': 0.7963, '5': 0.7421, '6': 0.7694, '7': 0.7201, '8': 0.7709,
        '9': 0.7694, 'A': 0.8805, 'B': 0.7816, 'C': 0.8597, 'D': 0.8422,
        'E': 0.7274, 'F': 0.7069, 'G': 0.8705, 'H': 0.8671, 'I': 0.4008,
        'J': 0.7045, 'K': 0.8393, 'L': 0.6854, 'M': 1.0516, 'N': 0.8822,
        'O': 0.8905, 'P': 0.7680, 'Q': 0.8969, 'R': 0.7768, 'S': 0.7748,
        'T': 0.7875, 'U': 0.8520, 'V': 0.8805, 'W': 1.1785, 'X': 0.8583,
        'Y': 0.8510, 'Z': 0.7841, 'a': 0.8805, 'b': 0.7816, 'c': 0.8597,
        'd': 0.8422, 'e': 0.7274, 'f': 0.7069, 'g': 0.8705, 'h': 0.8671,
        'i': 0.4008, 'j': 0.7045, 'k': 0.8393, 'l': 0.6854, 'm': 1.0516,
        'n': 0.8822, 'o': 0.8905, 'p': 0.7680, 'q': 0.8969, 'r': 0.7768,
        's': 0.7748, 't': 0.7875, 'u': 0.8520, 'v': 0.8805, 'w': 1.1785,
        'x': 0.8583, 'y': 0.8510, 'z': 0.7841
    },
}

# Fallback for any character not in the table above.
EM_FALLBACK = {
    "title": 0.6082,
    "lead": 0.6875,
    "body": 0.5704,
    "body_sm": 0.5702,
    "point": 0.5954,
    "label": 0.7021,
    "micro": 0.7350,
    "bline": 0.6921,
    "nxt": 0.7627,
}


BRAND_EM = 0.815   # .foot .brand, wider than .foot for its extra tracking
def text_w(role: str, size_px: float, text: str) -> float:
    """Rendered width of a string at a size, from the measured tables."""
    tbl, avg = ADVANCE[role], EM_FALLBACK[role]
    return size_px * sum(tbl.get(ch, avg) for ch in text)

# Vertical rhythm. These same numbers are written into the CSS below, so the
# fitter's estimate and the browser's layout cannot drift apart.
PAD_X = S.SAFE_INSET                       # 48, the safe margin
BAND_PB = 26                               # below the band text
BAND_H = (S.SAFE_INSET + max(round(S.SCALE_PX['id'] * 1.1),
                             round(S.SCALE_PX['kind'] * 1.4))
          + BAND_PB)
FOOT_H = S.SAFE_INSET + round(S.SCALE_PX['micro'] * 1.3) + 14
BFOOT_PAD = 30
HEAD_PT, HEAD_PB = 24, 22
ACT_PT, ACT_PB = 26, 26
LAB_H = round(S.SCALE_PX["label"] * 1.3)   # eyebrow line
LAB_MB = 18
TAG_MT = 16                                # tagline above the photograph
PT_MB = 10                                 # gap between numbered points
BLOCK_GAP = 34
BBODY_PAD = 34
SHOT_MIN, SHOT_MAX = 280, 420              # the photograph's share, in px
# A handful of cards carry a three-word name and a single 120-character
# sentence that cannot be broken at a full stop. Rather than truncate the
# sentence or fail the card, those spend picture: the photograph is allowed
# down to this before any word is cut, because a smaller picture is a far
# smaller loss than a clipped instruction.
SHOT_FLOOR = 170
SLACK = 12       # rounding reserve, so a 4px estimate error is not a defect
MAX_ACT_LINES = 5
# The action sits in a flex row beside its colour bar, so its text column is
# narrower than the safe box. Estimating it at the full 654 is what made a
# two-line paragraph render as three and pushed the card 54px past its own
# bottom edge while every number on paper said it fitted.
ACT_W = (S.SAFE_W - round(S.SCALE_PX["micro"] * 0.28)
         - round(S.SCALE_PX["label"]))

LH = {"title": 1.02, "lead": 1.3, "body": 1.36, "body_sm": 1.4,
      "label": 1.3, "micro": 1.3}

# The title ladder, in points. One line when the name fits at 17pt or better,
# otherwise two lines at 20pt, which covers the deck's longest name (22
# characters) with room to spare. Nothing here goes near the floor.
TITLE_LADDER = (28.0, 24.0, 20.0, 17.0)
TITLE_TWO_LADDER = (20.0, 18.0, 16.0)


def lines_for(text: str, role: str, size_px: float,
              width: int = S.SAFE_W) -> int:
    """Line count by greedy word wrap, not by dividing the character count.

    Dividing underestimates, because a line break wastes whatever is left at
    the end of the line, and the error compounds with long words. The first
    version did divide and put a card 53px past its own bottom edge with
    everything apparently fitting on paper.
    """
    width *= 0.985
    space = text_w(role, size_px, " ")
    lines, cur = 1, 0.0
    for word in clean(text).split():
        w = text_w(role, size_px, word)
        if cur and cur + space + w > width:
            lines += 1
            cur = w
        else:
            cur += (space if cur else 0) + w
    return lines


def fit_lines(text: str, role: str, size_px: float, nlines: int,
              width: int = S.SAFE_W) -> str:
    """The longest whole-sentence prefix that wraps into nlines."""
    t = clean(text)
    if not t:
        return ""
    parts = _SENT.split(t)
    kept = []
    for part in parts:
        trial = " ".join(kept + [part])
        if lines_for(trial, role, size_px, width) > nlines:
            break
        kept.append(part)
    return " ".join(kept)


def word_lines(text: str, role: str, size_px: float, nlines: int,
               width: int = S.SAFE_W) -> str:
    """Sentence boundary if one fits, otherwise the last whole word."""
    t = fit_lines(text, role, size_px, nlines, width)
    if t:
        return t
    words, out = clean(text).split(), []
    for w in words:
        if lines_for(" ".join(out + [w]), role, size_px, width) > nlines:
            break
        out.append(w)
    return " ".join(out)


def title_fit(title: str) -> tuple:
    """(font size in px, line count) for a card name.

    Sized from the longest word as well as the whole string, because a card
    called CONTINUOUS IMPROVEMENT has an eleven-character word in it and no
    hyphenation, so a size chosen from the average would push that word past
    the trim edge.
    """
    def longest_w(px):
        return max((text_w("title", px, w) for w in title.split()), default=0)
    room = S.SAFE_W * 0.97
    for p in TITLE_LADDER:
        px = S.pt(p)
        if (longest_w(px) <= room
                and lines_for(title, "title", px) == 1):
            return px, 1
    # Two lines, at the largest size the name actually wraps into. The first
    # version returned min(2, lines) here, which is not a fit, it is a claim:
    # FAMILY COMMAND CENTER wrapped to three lines at 20pt and the card was
    # 85px too tall with the estimate saying it was fine.
    for p in TITLE_TWO_LADDER:
        px = S.pt(p)
        if (longest_w(px) <= room
                and lines_for(title, "title", px) <= 2):
            return px, 2
    # A three-word name whose first two words will not share a line reads
    # better set at 18pt over three lines than shrunk to 14pt over two, so the
    # ladder stops at 16pt and spends a line instead of two more points.
    for p in TITLE_TWO_LADDER[:2]:
        px = S.pt(p)
        if (longest_w(px) <= room
                and lines_for(title, "title", px) <= 3):
            return px, 3
    px = S.pt(TITLE_TWO_LADDER[-1])
    return px, lines_for(title, "title", px)


# --------------------------------------------------------------- card data
def cards() -> dict:
    """Card data, richest source first.

    build/entryway-cardtext.json is the full copy transcribed back off the 90
    finished cards. The two thin json files only carry a name, a category and
    a canonical line, so they fill gaps rather than override.
    """
    out = {}
    for f in ("mudroom-cards.json", "entryway-cards.json"):
        p = os.path.join(ROOT, "build", f)
        if os.path.exists(p):
            for c in json.load(io.open(p, encoding="utf-8")):
                out[c["ID"]] = {
                    "id": c["ID"], "title": c.get("Card", ""),
                    "type": (c.get("Category", "") + " card").upper().strip(),
                    "difficulty": sum(1 for ch in (c.get("Difficulty") or "")
                                      if ch in "★⭐*") or None,
                    "six_s": c.get("Primary 6S", ""),
                    "objective": c.get("Objective / Behavior", ""),
                    "six_s_lesson": c.get("Canonical text", ""),
                    "benefit": c.get("Benefit / Effect", ""),
                }
    rich = os.path.join(ROOT, "build", "entryway-cardtext.json")
    if os.path.exists(rich):
        for c in json.load(io.open(rich, encoding="utf-8"))["cards"]:
            base = out.get(c["id"], {})
            merged = {k: v for k, v in base.items()}
            for k, v in c.items():
                if v not in (None, "", [], "UNREADABLE"):
                    merged[k] = v
            merged.setdefault("six_s", base.get("six_s", ""))
            out[c["id"]] = merged
    return out


def approved_heroes() -> set:
    """Only heroes a person has looked at may become a card.

    The verdict is bound to the image's sha, so regenerating a hero drops its
    card out of the deck until somebody looks again rather than silently
    shipping the new picture.
    """
    p = os.path.join(ROOT, "ops", "card-hero-verdicts.json")
    if not os.path.exists(p):
        return set()
    import hashlib
    raw = json.load(io.open(p, encoding="utf-8"))
    ok = set()
    for stem, rec in raw.items():
        f = os.path.join(HEROES, "entryway", stem + ".png")
        if not isinstance(rec, dict) or rec.get("verdict") != "ok":
            continue
        if not os.path.exists(f):
            continue
        got = hashlib.sha256(io.open(f, "rb").read()).hexdigest()[:10]
        if rec.get("sha") == got:
            ok.add(stem)
    return ok


# ------------------------------------------------------------- text fitting
_SENT = re.compile(r"(?<=[.!?])\s+")
NEXT_PREFIX = "Next -> "   # stands in for the rendered "Next  →  "


def clean(v) -> str:
    if v in (None, "", "UNREADABLE"):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()


def fit(text: str, chars: int) -> str:
    """Trim to a whole-sentence boundary inside the budget.

    Never mid-word, never with an ellipsis. On a printed card an ellipsis is a
    promise of more text the reader cannot reach. If not even the first
    sentence fits, this returns "" and the caller decides whether to drop the
    block or give it another line; it will not hand back a mangled sentence.
    """
    t = clean(text)
    if not t or len(t) <= chars:
        return t
    kept, total = [], 0
    for part in _SENT.split(t):
        add = len(part) + (1 if kept else 0)
        if total + add > chars:
            break
        kept.append(part)
        total += add
    return " ".join(kept)


SIX_WORDS = ("Sort", "Straighten", "Shine", "Safety", "Standardize", "Sustain")


def six_step(c: dict) -> str:
    """The card's 6S step, read from data, never inferred.

    54 of the 89 entryway cards carry no Primary 6S column, and most of those
    open their own six_s_lesson with the step's name -- "Straighten means
    everything has a logical home" -- so reading the card's own sentence is not
    inventing a value. Where neither exists the chip is simply absent, because
    a wrong step printed on a product is worse than a missing one.
    """
    s = clean(c.get("six_s")).title().replace("Standardise", "Standardize")
    if s in SIX_WORDS:
        return s
    m = re.match(r"\s*(Sort|Straighten|Shine|Safety|Standardi[sz]e|Sustain)\b",
                 clean(c.get("six_s_lesson")), re.I)
    return m.group(1).title().replace("Standardise", "Standardize") if m else ""


TIME_RE = re.compile(r"^\((\s*[^)]{1,14}\s*)\)\s*")


def split_time(text: str) -> tuple:
    """'(30 SEC) Remove shoes...' -> ('30 SEC', 'Remove shoes...').

    The duration was buried mid-sentence in the copy. It is the first thing a
    person wants to know before starting, so it becomes a pill next to the
    label instead of four characters of running text.
    """
    t = clean(text)
    m = TIME_RE.match(t)
    return (m.group(1).strip(), t[m.end():].strip()) if m else ("", t)


def boilerplate(allc: dict, ids: list) -> set:
    """Opening tagline sentences that appear on three or more cards.

    Thirteen taglines are three taglines glued together: EU-001 reads
    "IMPROVE THE ENTRYWAY SYSTEM. TOMORROW IS ALREADY READY. ONE PLACE.
    EVERYTHING YOU NEED. ZERO STRESS." at 100 characters, and every Upgrade
    card opens with that same first sentence, which identifies the family the
    band already names in colour, glyph and word. Detected by counting rather
    than by a hand-written list, so it stays true when the corpus changes.
    """
    n = collections.Counter()
    for i in ids:
        t = clean(allc[i].get("tagline"))
        if t:
            n[_SENT.split(t)[0].rstrip(".").strip().upper()] += 1
    return {k for k, v in n.items() if v >= 3}


def tagline_of(c: dict, boiler: set) -> str:
    t = clean(c.get("tagline"))
    if not t:
        return ""
    parts = [p for p in _SENT.split(t) if p.strip()]
    if parts and parts[0].rstrip(".").strip().upper() in boiler:
        # Dropped even when it is the only sentence. "RECOGNIZE SUCCESS."
        # appears on all eight Win cards, so it names the family, and the band
        # names the family already in colour, glyph and word.
        parts = parts[1:]
    return " ".join(parts)


# ------------------------------------------------------------ the fitters
#
# Both faces are laid out by the same rule: choose the content, measure it with
# the measured tables, and if it does not fit, take content away. Sizes never
# change.
# The order of the reductions is the design decision; it is written down here
# rather than emerging from whatever the browser happened to do.

def fit_front(c: dict, boiler: set) -> dict:
    """Decide the front's content and line counts for one card."""
    title = clean(c.get("title")).upper()
    tpx, tlines = title_fit(title)

    label, tlabel = "Do this now", ""
    src = clean(c.get("quick_win"))
    if src:
        tlabel, src = split_time(src)
    if not src:
        src, label = clean(c.get("game_effect")), "In play"
    if not src:
        src, label = clean(c.get("objective")), "The goal"

    body_px, lead_px = S.SCALE_PX["body"], S.SCALE_PX["body_sm"]
    plan = {"title": title, "title_px": tpx, "title_lines": tlines,
            "label": label, "time": tlabel, "trimmed": False}

    # Keep as much of the action as the card can hold, then as much of the
    # tagline as fits under it. The action is why the card exists and the
    # tagline is deck flavour, so the tagline is what gives way. Sizes never
    # do.
    need = min(MAX_ACT_LINES, lines_for(src, "body", body_px, ACT_W))
    raw_tag = tagline_of(c, boiler)
    for floor in (SHOT_MIN, SHOT_FLOOR):
        for act_lines in range(need, 1, -1):
            act = fit_lines(src, "body", body_px, act_lines, ACT_W)
            if not act:
                continue
            al = lines_for(act, "body", body_px, ACT_W)
            act_h = (ACT_PT + LAB_H + LAB_MB
                     + round(body_px * LH["body"]) * al + ACT_PB)
            for tag_lines in (2, 1, 0):
                tag = (fit_lines(raw_tag, "lead", lead_px, tag_lines)
                       if tag_lines else "")
                tl = lines_for(tag, "lead", lead_px) if tag else 0
                head = (HEAD_PT + round(tpx * LH["title"]) * tlines
                        + (TAG_MT + round(lead_px * LH["lead"]) * tl
                           if tag else 0) + HEAD_PB)
                shot = S.CARD_H - BAND_H - head - act_h - FOOT_H - SLACK
                if shot >= floor:
                    plan.update(tag=tag, action=act, shot=min(shot, SHOT_MAX),
                                trimmed=len(act) < len(clean(src)))
                    return plan

    # Nothing fitted at a legible size, so the action is cut to the last whole
    # word of a two-line box. The render-time check is the backstop.
    act = word_lines(src, "body", body_px, MAX_ACT_LINES, ACT_W)
    head = HEAD_PT + round(tpx * LH["title"]) * tlines + HEAD_PB
    act_h = (ACT_PT + LAB_H + LAB_MB
             + round(body_px * LH["body"]) * MAX_ACT_LINES + ACT_PB)
    plan.update(tag="", action=act, trimmed=True,
                shot=min(SHOT_MAX,
                         max(SHOT_FLOOR,
                             S.CARD_H - BAND_H - head - act_h - FOOT_H)))
    return plan


def fit_back(c: dict) -> dict:
    """Decide the back's content and line counts for one card."""
    sm = S.SCALE_PX["body_sm"]
    ind = round(sm * 1.35) + round(S.SCALE_PX["micro"] * 0.6)   # pip + gap
    pw = S.SAFE_W - ind
    raw = [clean(x) for x in (c.get("callouts") or [])
           if clean(x) and clean(x) != "UNREADABLE"][:5]
    raw = [re.sub(r"^\d+[.)]\s*", "", x) for x in raw]
    colonish = sum(1 for x in raw if ":" in x)

    nxt, nc = "", c.get("next_card") or {}
    if isinstance(nc, dict) and nc.get("id"):
        nxt = f'{nc["id"]} {clean(nc.get("title"))}'
    foot = word_lines(c.get("footer_line") or "6S Success", "bline",
                      S.SCALE_PX["label"], 2)
    # The next-card line wraps as readily as anything else. Assuming it was
    # always one line is what left several backs 33px over, every one of them
    # a card whose next card had a long name.
    nxt_h = (round(S.SCALE_PX["micro"] * LH["micro"])
             * lines_for(NEXT_PREFIX + nxt, "nxt", S.SCALE_PX["micro"])
             + 8) if nxt else 0
    foot_h = (BFOOT_PAD + S.SAFE_INSET + nxt_h
              + round(S.SCALE_PX["label"] * LH["label"])
              * lines_for(foot, "bline", S.SCALE_PX["label"]))
    room = S.CARD_H - BAND_H - foot_h - BBODY_PAD * 2 - SLACK

    def points(nlines, keep):
        out, h = [], LAB_H + LAB_MB
        for x in raw[:keep]:
            head, _, rest = x.partition(":")
            if rest and nlines > 1:
                head = head.strip()
                body = word_lines(rest, "point", sm, nlines, pw)
                # The label already eats part of line one, so the clause is
                # re-fitted against what is left rather than the whole box.
                while body and lines_for(f"{head} - {body}", "point", sm,
                                         pw) > nlines:
                    body = body.rsplit(" ", 1)[0]
                out.append((head, body))
                h += round(sm * LH["body_sm"]) * nlines + PT_MB
            else:
                one = word_lines(head.strip() if rest else x, "point", sm,
                                 nlines, pw)
                out.append((one, ""))
                h += (round(sm * LH["body_sm"])
                      * lines_for(one, "point", sm, pw) + PT_MB)
        return out, (h if out else 0)

    src = clean(c.get("home_quest_challenge"))
    line_h = round(sm * LH["body_sm"])
    # The quest is given every line the points leave behind, rather than a
    # fixed number from a ladder. The ladder version stopped at two lines and
    # left 98px of blank card under it, which reads as a card that ran out of
    # things to say rather than one that was cut to fit.
    #
    # The explanatory clause on each point gives way before any point is
    # dropped, and a point is dropped before the quest, because the points are
    # the card's checklist and the quest is its next action.
    for plines, keep in ((2, 5), (1, 5), (1, 4), (1, 3)):
        pts, ph = points(plines, keep)
        avail = room - ph - BLOCK_GAP - LAB_H - LAB_MB
        qlines = int(avail // line_h)
        if qlines < 2:
            continue
        quest = fit_lines(src, "body_sm", sm, min(qlines, 6))
        if not quest:
            continue
        # A third block was tried here and removed. The most spare space on
        # any back in this deck is 158px, and a labelled two-line block needs
        # 193, so a pro tip could never appear on a single card; the branch
        # existed and never ran, which is worse than not having it. What
        # spare there is comes from a card whose quest is genuinely short, and
        # .bbody spreads it between the two blocks it does have.
        return {"points": pts, "quest": quest, "next": nxt, "foot": foot,
                "heading": ("How it works" if colonish >= 3
                            else "Key points")}
    pts, _ = points(1, 3)
    return {"points": pts, "quest": "", "next": nxt, "foot": foot,
            "heading": "Key points"}


# ------------------------------------------------------------ shared markup
def font_face(rel_prefix: str) -> str:
    """Self-hosted @font-face, not a Google Fonts link.

    The old template fetched three families over the network at render time. A
    card that renders in Times because the network hiccuped looks like a
    different product and fails silently, and the repository already carries
    the exact woff2 files the site uses. Newsreader is dropped: at 8.5pt a
    grotesque holds together where a text serif fills in, and Fraunces 900
    replaces the 700 the old CSS asked for and never had, which the browser was
    faking by smearing the 600.
    """
    faces = [("Fraunces", 900, "Fraunces-900-normal.woff2"),
             ("Inter", 400, "Inter-400-normal.woff2"),
             ("Inter", 600, "Inter-600-normal.woff2"),
             ("Inter", 700, "Inter-700-normal.woff2"),
             ("Inter", 800, "Inter-800-normal.woff2")]
    return "".join(
        f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;"
        f"font-display:block;src:url('{rel_prefix}{f}') format('woff2')}}"
        for fam, w, f in faces)


FIT_SCRIPT = """
<script>
/* Measures the finished card and writes the result into the DOM so
   ops/render_cards.py can read it back with --dump-dom. An exit code cannot
   tell you that a paragraph overflowed its box, or that something printed at
   2pt. This can, and it measures what the browser actually did rather than
   what the CSS asked for. */
(function(){
  function report(){
    var card=document.querySelector('.card'), out={sizes:[],over:[],min:999};
    var seen={};
    card.querySelectorAll('*').forEach(function(el){
      var has=Array.prototype.some.call(el.childNodes,function(n){
        return n.nodeType===3 && n.textContent.trim().length; });
      if(has){
        var fs=parseFloat(getComputedStyle(el).fontSize);
        var key=(el.getAttribute('data-role')||el.className||el.tagName)+'';
        if(!seen[key]||fs<seen[key]) seen[key]=fs;
        if(fs<out.min) out.min=fs;
      }
      if(el.scrollHeight-el.clientHeight>1 &&
         getComputedStyle(el).overflow!=='visible')
        out.over.push([(el.getAttribute('data-role')||el.className)+'',
                       el.scrollHeight, el.clientHeight]);
    });
    if(card.scrollHeight-card.clientHeight>1)
      out.over.push(['CARD',card.scrollHeight,card.clientHeight]);
    /* Anything whose ink lands outside the safe box would be cut off or sit
       too near the blade. Measured against the card's own border box. */
    var cb=card.getBoundingClientRect(), pad=window.__SAFE__;
    card.querySelectorAll('[data-safe]').forEach(function(el){
      var r=el.getBoundingClientRect();
      var l=r.left-cb.left, t=r.top-cb.top;
      var side='';
      if(l<pad.x-0.5) side='left by '+Math.round(pad.x-l);
      else if(t<pad.y-0.5) side='top by '+Math.round(pad.y-t);
      else if(r.right-cb.left>cb.width-pad.x+0.5)
        side='right by '+Math.round(r.right-cb.left-cb.width+pad.x);
      else if(r.bottom-cb.top>cb.height-pad.y+0.5)
        side='bottom by '+Math.round(r.bottom-cb.top-cb.height+pad.y);
      if(side) out.over.push(['SAFE AREA: '+el.getAttribute('data-safe')+
                              ' past the '+side+'px', 0, 0]);
    });
    out.h={};
    ['band','head','shot','act','foot','bbody','bfoot','lab'].forEach(
      function(c){var el=card.querySelector('.'+c);
        if(el) out.h[c]=Math.round(el.getBoundingClientRect().height);});
    Object.keys(seen).forEach(function(k){out.sizes.push([k,seen[k]]);});
    var pre=document.createElement('pre');
    pre.id='fitreport'; pre.style.display='none';
    pre.textContent='FIT'+'REPORT '+JSON.stringify(out)+' END'+'FIT';
    document.documentElement.appendChild(pre);
  }
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(report);
  else window.addEventListener('load',report);
})();
</script>"""


def base_css(colour: str, fg: str, tx: str, bleed: bool, plan: dict) -> str:
    """Geometry and the type scale. Every size comes from card_spec."""
    px = S.SCALE_PX
    tpx = plan.get("title_px", px["display"])
    shot = plan.get("shot", SHOT_MIN)
    if bleed:
        # The sheet is trim plus 0.125in on every side. The art runs to the
        # sheet edge, the trim line is where the blade is meant to fall, and
        # nothing that matters may sit outside SAFE.
        frame = (f"body{{margin:0;background:{S.INK};width:{S.BLEED_W}px;"
                 f"height:{S.BLEED_H}px}}"
                 f".card{{width:{S.BLEED_W}px;height:{S.BLEED_H}px;"
                 f"border-radius:0}}")
        # No trim marks are drawn. A guide line in the artwork is a guide line
        # in the printed card; the trim geometry is stated in the build output
        # and belongs in the printer's job ticket, not in the file.
        pad_x = PAD_X + S.BLEED_PX
    else:
        frame = (f"body{{margin:0;background:#8C8478;width:{S.CARD_W}px;"
                 f"height:{S.CARD_H}px}}"
                 f".card{{width:{S.CARD_W}px;height:{S.CARD_H}px;"
                 f"border-radius:{S.CORNER_R}px}}")
        pad_x = PAD_X
    cg = max(70, min(round(shot * 0.5), round(px["display"] * 1.9)))
    # The band runs to the trim edge but its text does not: it starts at
    # the safe inset, because a card cut 1/16in high otherwise loses the
    # top of the card code.
    pad_y = pad_x
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
{frame}
.card{{position:relative;background:{S.PAPER};color:{S.INK};overflow:hidden;
  display:flex;flex-direction:column;font-family:'Inter',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;--tc:{colour};--fg:{fg};--tx:{tx}}}
/* ---- band: the across-the-table signal. Colour, glyph and word together,
   because two warm hues under a lamp are not enough on their own and colour
   alone is nothing at all to a colour-blind player. */
/* Every item is flex:0 0 auto and nowrap. They were shrinkable, so on any
   card whose family word is long the browser quietly narrowed the card code
   and wrapped "EM-005" onto two lines, making the band 202px instead of 138
   and pushing the whole card 64px past its own bottom edge. A band that
   cannot fit should overflow where the safe-area check can see it, not
   reflow into something that looks deliberate. */
.band{{flex:0 0 {BAND_H}px;background:var(--tc);color:var(--fg);display:flex;
  align-items:center;gap:20px;padding:{pad_y}px {pad_x}px {BAND_PB}px}}
.band>*{{flex:0 0 auto;white-space:nowrap}}
.glyph{{width:{round(px['kind']*1.4)}px;height:{round(px['kind']*1.4)}px;
  border-radius:50%;border:2px solid var(--fg);display:flex;
  align-items:center;justify-content:center;font-size:{px['kind']}px;
  line-height:1}}
.code{{font-weight:800;font-size:{px['id']}px;line-height:1.1;
  font-variant-numeric:tabular-nums}}
.kind{{font-weight:700;font-size:{px['kind']}px;line-height:1.1;
  letter-spacing:.12em;text-transform:uppercase}}
.diff{{margin-left:auto;display:flex;gap:5px;align-items:center}}
.diff i{{width:16px;height:16px;
  border-radius:50%;border:2px solid var(--fg);display:block}}
.diff i.on{{background:var(--fg)}}
/* ---- title */
.head{{flex:0 0 auto;padding:{HEAD_PT}px {pad_x}px {HEAD_PB}px}}
h1{{font-family:'Fraunces',Georgia,serif;font-weight:900;font-size:{tpx}px;
  line-height:{LH['title']};letter-spacing:-.018em;text-wrap:balance}}
.tag{{margin-top:{TAG_MT}px;font-size:{px['body_sm']}px;font-weight:700;
  line-height:{LH['lead']};letter-spacing:.045em;text-transform:uppercase;
  color:var(--tx)}}
/* ---- photograph. Full width to the trim edge, and about a third of the
   face rather than the 60% it used to take with the instructions squeezed
   underneath at 2.5pt. It is still the largest single element on the card. */
/* flex 1 1, not 0 0. The fitter's line estimate can be one line out either
   way, and the photograph is the one element that can absorb that without
   anything being lost: it grows when the action renders shorter than
   estimated and shrinks when it renders taller, instead of leaving a hole or
   pushing the footer off the card. */
.shot{{flex:1 1 {shot}px;min-height:{SHOT_FLOOR}px;max-height:{SHOT_MAX}px;
  overflow:hidden;background:#F2EADC;
  border-top:{round(px['micro']*0.28)}px solid var(--tc);
  border-bottom:1px solid {S.LINE}}}
.shot img{{width:100%;height:100%;object-fit:cover;display:block}}
.shot.concept{{display:flex;align-items:center;justify-content:center;
  background:color-mix(in srgb,var(--tc) 7%,{S.PAPER})}}
/* One large family mark. The first version drew six ascending bars, and on a
   card it read as a bar chart from an analytics dashboard, which is the one
   aesthetic this product should never borrow. A single mark says the same
   thing, matches the badge in the band, and cannot be mistaken for a
   photograph that failed to load. */
.cinner{{display:flex;flex-direction:column;align-items:center;gap:18px;
  width:100%}}
/* Sized from the photograph's own height, not from a constant. A fixed 214px
   mark did not fit the two cards whose action block had squeezed the picture
   down to its floor. */
.cglyph{{display:flex;align-items:center;justify-content:center;
  width:{cg}px;height:{cg}px;border-radius:50%;
  border:{max(3, round(cg * 0.028))}px solid var(--tc);color:var(--tc);
  font-size:{round(cg * 0.52)}px;line-height:1;opacity:.75}}
.ckind{{font-weight:800;font-size:{px['kind']}px;letter-spacing:.3em;
  text-indent:.3em;color:var(--tx)}}
/* ---- the one action block */
.act{{flex:0 0 auto;padding:{ACT_PT}px {pad_x}px {ACT_PB}px;display:flex;
  gap:{round(px['label'])}px}}
.actbar{{flex:0 0 {round(px['micro']*0.28)}px;border-radius:3px;
  background:var(--tc)}}
.actbody{{flex:1 1 auto;min-width:0}}
.lab{{display:flex;align-items:center;gap:{round(px['micro']*0.6)}px;
  height:{LAB_H}px;margin-bottom:{LAB_MB}px;font-size:{px['label']}px;
  font-weight:800;letter-spacing:.05em;text-transform:uppercase;
  color:var(--tx)}}
.pill{{font-size:{px['micro']}px;font-weight:700;letter-spacing:.08em;
  color:var(--fg);background:var(--tc);border-radius:99px;line-height:1.25;
  padding:{round(px['micro']*0.24)}px {round(px['micro']*0.6)}px}}
.act p.txt{{font-size:{px['body']}px;line-height:{LH['body']};font-weight:400}}
/* ---- footer meta */
.foot{{flex:0 0 {FOOT_H}px;display:flex;align-items:flex-end;
  gap:{round(px['micro'])}px;padding:0 {pad_x}px {pad_y + 3}px;
  border-top:1px solid {S.LINE};font-size:{px['micro']}px;font-weight:600;
  letter-spacing:.1em;text-transform:uppercase;color:#5B534A;
  line-height:{LH['micro']};white-space:nowrap}}
.foot .swatch{{width:{round(px['micro']*0.72)}px;
  height:{round(px['micro']*0.72)}px;border-radius:3px;display:inline-block;
  vertical-align:-1px;margin-right:5px}}
.foot .brand{{margin-left:auto;letter-spacing:.18em;font-weight:800;
  color:var(--tx)}}
/* ---- back */
/* space-between, not a top-aligned stack. Whatever the fitter could not fill
   is spread between the blocks instead of pooling as a hole above the footer,
   which is what a card looks like when it has run out of things to say rather
   than one that was composed. */
.bbody{{flex:1 1 auto;padding:{BBODY_PAD}px {pad_x}px;display:flex;
  flex-direction:column;justify-content:space-between;gap:{BLOCK_GAP}px;
  overflow:hidden}}
.blk h3{{height:{LAB_H}px;margin-bottom:{LAB_MB}px;font-size:{px['label']}px;
  font-weight:800;letter-spacing:.05em;text-transform:uppercase;
  color:var(--tx)}}
.blk p{{font-size:{px['body_sm']}px;line-height:{LH['body_sm']}}}
ol.pts{{list-style:none}}
ol.pts li{{display:flex;gap:{round(px['micro']*0.6)}px;align-items:flex-start;
  font-size:{px['body_sm']}px;line-height:{LH['body_sm']};
  margin-bottom:{PT_MB}px}}
ol.pts li b{{font-weight:700}}
ol.pts i{{flex:0 0 {round(px['body_sm']*1.35)}px;
  height:{round(px['body_sm']*1.35)}px;border-radius:50%;background:var(--tc);
  color:var(--fg);font-style:normal;font-weight:800;font-size:{px['micro']}px;
  text-align:center;line-height:{round(px['body_sm']*1.35)}px;margin-top:1px}}
.bfoot{{flex:0 0 auto;background:var(--tc);color:var(--fg);
  padding:{BFOOT_PAD}px {pad_x}px {pad_y + 3}px;display:flex;
  flex-direction:column;gap:8px}}
.bfoot .nxt{{font-size:{px['micro']}px;font-weight:700;letter-spacing:.12em;
  text-transform:uppercase;line-height:{LH['micro']};opacity:.9}}
.bfoot .line{{font-size:{px['label']}px;font-weight:800;letter-spacing:.04em;
  text-transform:uppercase;line-height:{LH['label']}}}
"""


def band(c: dict, fam: str, glyph: str) -> str:
    e = html.escape
    n = int(c.get("difficulty") or 0)
    pips = "".join(f'<i class="{"on" if i < n else ""}"></i>'
                   for i in range(5)) if n else ""
    return (f'<div class="band">'
            f'<span class="glyph" aria-hidden="true">{glyph}</span>'
            f'<span class="code" data-role="code" data-safe="id">'
            f'{e(c["id"])}</span>'
            f'<span class="kind" data-role="kind" data-safe="family">'
            f'{e(fam)}</span>'
            f'<span class="diff" title="difficulty {n} of 5">{pips}</span>'
            f'</div>')


def doc(title: str, css: str, body: str, bleed: bool) -> str:
    rel = os.path.relpath(FONTS, OUT + ("-bleed" if bleed else ""))
    rel = rel.replace(os.sep, "/") + "/"
    pad_x = PAD_X + (S.BLEED_PX if bleed else 0)
    pad_y = PAD_X + (S.BLEED_PX if bleed else 0)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{html.escape(title)}</title>'
            f'<style>{font_face(rel)}{css}</style></head><body>{body}'
            f'<script>window.__SAFE__={{x:{pad_x},y:{pad_y}}};</script>'
            f'{FIT_SCRIPT}</body></html>')


# ------------------------------------------------------------------- front
def card_html(c: dict, hero: str, boiler: set, bleed: bool = False) -> str:
    e = html.escape
    fam = S.family_of(c.get("type"))
    colour, glyph, _hue = S.FAMILY[fam]
    fg, tx = S.on(colour), S.readable_on(colour)
    colour = S.band_bg(colour)
    p = fit_front(c, boiler)

    # The footer is a single non-wrapping row, so it is budgeted by measured
    # width rather than by hope. Six cards had a long step name, a long reset
    # time and the brand in one row and the brand walked past the trim edge.
    # The reset time gives way first, then the step; the brand stays, because
    # a card with no brand on it is not this product.
    px_m, gap = S.SCALE_PX["micro"], round(S.SCALE_PX["micro"])
    step = six_step(c)
    reset = clean(c.get("reset_time")).title()
    brand_w = len("6S Success") * BRAND_EM * px_m
    step_w = (len(step) * text_w("micro", px_m, step) / max(1, len(step))
              + round(px_m * 0.72) + 5 + gap) if step else 0
    reset_w = (len(reset) * text_w("micro", px_m, reset) / max(1, len(reset))
               + gap) if reset else 0
    if step_w + reset_w + brand_w > S.SAFE_W:
        reset, reset_w = "", 0
    if step_w + brand_w > S.SAFE_W:
        step, step_w = "", 0
    meta = []
    if step:
        meta.append(f'<span data-safe="step"><span class="swatch" '
                    f'style="background:{S.SIX_S[step]}"></span>'
                    f'{e(step)}</span>')
    if reset:
        meta.append(f'<span data-safe="reset">{e(reset)}</span>')

    body = f"""<div class="card">
  {band(c, fam, glyph)}
  <div class="head">
    <h1 data-role="title" data-safe="title">{e(p["title"])}</h1>
    {f'<p class="tag" data-role="tagline" data-safe="tagline">'
     f'{e(p["tag"])}</p>' if p.get("tag") else ''}
  </div>
  {hero}
  <div class="act">
    <span class="actbar" aria-hidden="true"></span>
    <div class="actbody">
      <p class="lab"><span>{e(p["label"])}</span>
        {f'<span class="pill">{e(p["time"])}</span>' if p["time"] else ''}</p>
      <p class="txt" data-role="action" data-safe="action">
        {e(p["action"])}</p>
    </div>
  </div>
  <div class="foot">{''.join(meta)}
    <span class="brand" data-safe="brand">6S Success</span></div>
</div>"""
    return doc(f'{c["id"]} {p["title"]}',
               base_css(colour, fg, tx, bleed, p), body, bleed)


def concept_hero(c: dict) -> str:
    """A designed panel for the cards no photograph passed review for.

    Twelve of the 88 failed three rounds of prompting for structural reasons:
    five name an idea with no object in it, and the rest need legible lettering
    in the picture, which the negative prompt suppresses on purpose because
    that suppression is what keeps garbled text off the deck. Card games have
    always drawn concept cards differently from object cards. It never pretends
    to be a photograph, which is the part that matters.
    """
    fam = S.family_of(c.get("type"))
    glyph = S.FAMILY[fam][1]
    return ('<div class="shot concept"><div class="cinner">'
            f'<span class="cglyph" aria-hidden="true">{glyph}</span>'
            f'<p class="ckind">{html.escape(fam.upper())}</p>'
            '</div></div>')


# -------------------------------------------------------------------- back
def back_html(c: dict, bleed: bool = False) -> str:
    e = html.escape
    fam = S.family_of(c.get("type"))
    colour, glyph, _hue = S.FAMILY[fam]
    fg, tx = S.on(colour), S.readable_on(colour)
    colour = S.band_bg(colour)
    b = fit_back(c)

    pts_html = ""
    if b["points"]:
        items = "".join(
            f'<li><i>{i}</i><span data-safe="point{i}"><b>{e(h)}</b>'
            f'{(" &mdash; " + e(r)) if r else ""}</span></li>'
            for i, (h, r) in enumerate(b["points"], 1))
        pts_html = (f'<section class="blk"><h3>{e(b["heading"])}</h3>'
                    f'<ol class="pts" data-role="points">{items}</ol>'
                    f'</section>')
    quest_html = (f'<section class="blk"><h3>The quest</h3>'
                  f'<p data-role="quest" data-safe="quest">'
                  f'{e(b["quest"])}</p></section>' if b["quest"] else "")

    nxt = (f'<p class="nxt" data-safe="next">Next &nbsp;&rarr;&nbsp; '
           f'{e(b["next"])}</p>' if b["next"] else "")  # see NEXT_PREFIX

    body = f"""<div class="card">
  {band(c, fam, glyph)}
  <div class="bbody">{pts_html}{quest_html}</div>
  <div class="bfoot">{nxt}
    <p class="line" data-safe="footer">{e(b["foot"])}</p></div>
</div>"""
    return doc(f'{c["id"]} back',
               base_css(colour, fg, tx, bleed, {}), body, bleed)


# -------------------------------------------------------------------- main
def main() -> int:
    allc = cards()
    ok = approved_heroes()
    have, held = {}, []
    # Scan the entryway folder only. entryway-legacy holds the same card codes
    # under longer filenames, and two files matching one code resolved by glob
    # order is a coin toss, not a lookup.
    for f in sorted(glob.glob(os.path.join(HEROES, "entryway", "*.png"))):
        m = re.match(r"([A-Z]{2}-\d{3})", os.path.basename(f))
        if not m:
            continue
        (have.__setitem__(m.group(1), f) if m.group(1) in ok
         else held.append(m.group(1)))
    if held:
        print(f"  held back        {len(held)} hero(es) not approved in review")

    if "--list" in sys.argv or len(sys.argv) == 1:
        print(f"  heroes available : {len(have)}")
        for code, f in sorted(have.items()):
            c = allc.get(code, {})
            print(f"    {code}  {c.get('title','?'):26} "
                  f"{'ok' if c else 'NO CARD DATA'}")
        return 0

    corpus = json.load(io.open(os.path.join(ROOT, "build",
                                            "entryway-cardtext.json"),
                               encoding="utf-8"))
    want = [c["id"] for c in corpus["cards"]]
    others = sorted(set(allc) - set(want))
    if others:
        print(f"  {len(others)} card(s) belong to another deck or have no "
              f"transcribed text and are not built here")
    if "--card" in sys.argv:
        want = [sys.argv[sys.argv.index("--card") + 1].upper()]

    bleed = "--bleed" in sys.argv
    out = OUT + ("-bleed" if bleed else "")
    os.makedirs(out, exist_ok=True)
    boiler = boilerplate(allc, [i for i in want if i in allc])
    if boiler:
        print(f"  tagline boilerplate dropped from the front: "
              f"{sorted(boiler)}")

    made, concept, stepped, trimmed, noquest = 0, 0, 0, 0, 0
    clash = []
    for code in want:
        if code not in allc:
            print(f"  {code}: no card data, refusing to invent it")
            continue
        c = allc[code]
        if code in have:
            rel = os.path.relpath(have[code], out).replace(os.sep, "/")
            hero = f'<div class="shot"><img src="{rel}" alt=""></div>'
        else:
            hero = concept_hero(c)
            concept += 1
        if six_step(c):
            stepped += 1
        col = clean(c.get("six_s")).title()
        m = re.match(r"\s*(Sort|Straighten|Shine|Safety|Standardi[sz]e|Sustain)",
                     clean(c.get("six_s_lesson")), re.I)
        if col and m and col != m.group(1).title():
            clash.append(f"{code} column={col} lesson={m.group(1).title()}")
        plan = fit_front(c, boiler)
        trimmed += 1 if plan["trimmed"] else 0
        back = fit_back(c)
        noquest += 0 if back["quest"] else 1
        io.open(os.path.join(out, f"{code}.html"), "w",
                encoding="utf-8", newline="").write(
                    card_html(c, hero, boiler, bleed))
        io.open(os.path.join(out, f"{code}-back.html"), "w",
                encoding="utf-8", newline="").write(back_html(c, bleed))
        made += 1

    print(f"  wrote {made} fronts and {made} backs to "
          f"{os.path.relpath(out, ROOT).replace(os.sep, '/')}/")
    if concept:
        print(f"  {concept} use the designed panel: no photograph passed "
              f"review for that card")
    print(f"  {stepped} of {made} carry a 6S step chip; the rest have no step "
          f"in the data and are not given one")
    if clash:
        # Not fixed here. The chip follows the Primary 6S column, which is the
        # authoritative field; the lesson sentence is prose. Where they
        # disagree the data is wrong and content owns the correction, so this
        # says so rather than quietly picking one.
        print(f"  DATA CONFLICT: {len(clash)} card(s) name one 6S step in the "
              f"Primary 6S column and a different one in their own lesson "
              f"sentence. The chip follows the column. {clash[:6]}")
    if trimmed:
        print(f"  {trimmed} action block(s) trimmed to a sentence boundary to "
              f"stay at {S.SCALE_PT['body']}pt rather than shrinking the type")
    if noquest:
        print(f"  {noquest} back(s) had no room for the quest block after the "
              f"points, so it was dropped rather than set below "
              f"{S.BODY_MIN_PT}pt")
    if bleed:
        print(f"  bleed sheets {S.BLEED_W}x{S.BLEED_H} "
              f"({S.BLEED_W/S.DPI:.2f} x {S.BLEED_H/S.DPI:.2f} in), trim "
              f"{S.CARD_W}x{S.CARD_H}, text inside a "
              f"{S.SAFE_W}x{S.SAFE_H} safe box")
    else:
        print(f"  trim {S.CARD_W}x{S.CARD_H} (2.5 x 3.5 in at {S.DPI} dpi); "
              f"add --bleed for print sheets")
    print(f"  type floor {S.FLOOR_PT}pt = {S.pt(S.FLOOR_PT):.1f}px, "
          f"body {S.SCALE_PT['body']}pt = {S.SCALE_PX['body']:.1f}px")
    print(f"\n  Render with ops/render_cards.py, which measures the finished "
          f"card\n  and fails on any glyph under the floor or any block that "
          f"overflows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
