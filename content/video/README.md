# The 6S Micro Zone Reset — YouTube Production Plan

Video companion to **6S Success: Home Edition** and its Micro Zone Manual. Outline-level plan, 2026-07-21.

**20 rooms · 114 zone videos · 684 Shorts.**

## Contents

| File | What it is |
|---|---|
| `6S Micro Zone Reset - YouTube Production Plan.html` | The plan. Open in any browser. Sticky nav bar with room jump, live filter, expand-all, and a running count. Every video is a card; each of its six S segments expands to beats, shots, on-screen text, and its Short cut. |
| `6S-Micro-Zone-Reset-tracker.csv` | One row per zone video, with episode code, publish order, and blank status columns for script / shot / edit / published. Open in Excel or Sheets. |
| `review/validation-report.txt` | Full gate output, all passing. |
| `source/` | Everything needed to rebuild the plan. |

## What this is

Each of the 114 micro zones from the manual becomes one headless video, cut into six Shorts. "Headless" means **no presenter on camera at any point**: hands only, overhead and three-quarter tripod angles, detail and macro inserts, natural light, voiceover plus on-screen text. A validation gate fails the build on any shot that implies a visible presenter or gear beyond a one-person shoot.

Every video opens with a fixed 60 second cold open of three beats. Only beat 1, the problem, is written per zone, and it is drawn from that zone's hardest decision in the manual. Beats 2 (what 6S is) and 3 (the solution, the Micro Zone Room Reset) are fixed series-wide and recorded once as reusable assets.

Then six segments, one per S, in canonical order: Sort, Straighten, Shine, **Safety (the 4th S)**, Standardize, Sustain. Each segment is written so it lifts out as a standalone Short, which is where the 684 short-form assets come from.

**This is an outline, not a script.** It gives beats, shots, on-screen text, titles, thumbnails, tags, and Short cut points. It deliberately contains no verbatim narration and no timecodes; the narrator writes the voice, the editor sets the timing.

## Numbering

- `MZ-001` through `MZ-114`: stable series number, never changes.
- `R02.03`: room two, zone three, so files sort the way the manual reads.
- Shorts inherit the parent number plus the step, e.g. `MZ-014-SAFETY`.

Publish in manual order, Entryway first. Save the Garage and Workshop for last: those shoots are the longest and least forgiving.

## Every video is built from the manual

The plan is generated from `source/video.json`, which was written against the manual's own `content.json`. Each video inherits that zone's real done-state, hazards, and hard decision, so the manual and the videos stay in sync by construction. Change the manual, regenerate, and the videos follow.

## Rebuilding

Run from `source/`:

1. *(workflow)* — 20 room agents outline, 20 refine for producibility. Results land in `video.json`.
2. `collect_video.py` — pulls the refine-stage results out of the workflow journal into `video.json`.
3. `build_video.py` — assembles the HTML (design system, sticky nav, the filter/jump script).
4. `tracker.py` — regenerates the CSV.
5. `validate_video.py` — runs the gates; exits non-zero on any failure.

`video.json` is the editable source of truth. To fix an outline, edit it and re-run `build_video.py`, `tracker.py`, and `validate_video.py`; there is no need to re-run the agents. Paths inside the scripts are absolute to this session; update them before running elsewhere.

## Validation gates

Em dashes zero · six segments per video in canonical order, Safety fourth · all 114 videos and 684 Shorts complete with every field · no presenter on camera · no gear beyond a one-person shoot · no banned vocabulary, timecodes, statistics, or clickbait titles · HTML balanced with working nav · no beat or title repeated across videos.

## Known caveats

- The headless gate is a text heuristic. It cleared two rounds of false positives (a cloth "turned to camera", a box landing on "your head and shoulders") but a heuristic cannot prove the absence of a presenter. A human should still skim the shot lists before a shoot.
- The plan was reviewed by spot-checking rendered cards in a browser, not by reading all 114 end to end.
