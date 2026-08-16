# The Entryway Pilot — Shooting Scripts

Five full production scripts, the proof-of-format for **The 6S Micro Zone Reset**. 2026-07-21.

Open `Entryway Pilot - Shooting Scripts.html` in any browser. Sticky nav jumps to the fixed opener and each of the five episodes.

## What this is

The video plan gave 114 outlines. This takes the first room to something you can actually record. For each of the five Entryway zones you get:

- **Verbatim voiceover** — the exact words to read, for the cold open, all six S segments, the close, and the next teaser.
- **A synced shot table** — every setup numbered, tied to the line of VO it plays under, with an approximate length. Timings are targets, not measured.
- **On-screen text** with a cue for when each overlay appears.
- **The Short cut** for each segment — a standalone intro line and an end card, so it works as a Short with no prior context.
- **A consolidated shot list and shoot notes** for a one-person, one-session shoot.

Plus **the fixed opener** (beats 2 and 3), written once and reused on every episode in the whole series. Only its closing line changes per episode, where the zone name and session length swap in.

## Why a pilot

Before committing to 114 videos, five answer the questions that actually matter:

- Does headless carry a full reset on its own, with no presenter?
- Is sixty seconds the right opener length?
- Does a single segment really stand alone as a Short?

Shoot these five, watch how they land, and change the format **here** before it is baked into a hundred more.

## A finding worth noting

The scripts yield **23 Shorts, not 30**. The editing pass judged that 7 of the 30 segments do not genuinely stand alone (for example, the Landing Zone's Straighten only makes sense once you have seen its Sort). That is an honest editorial call surfaced early, and it is exactly the kind of thing the pilot exists to catch. If every zone loses roughly one Short this way, the series total is closer to 570 than 684. Worth confirming against the real cuts.

## Files

| File | What it is |
|---|---|
| `Entryway Pilot - Shooting Scripts.html` | The scripts. Open in a browser. |
| `validation-report.txt` | Gate output, all passing. |
| `source/pilot.json` | The five scripts as data, the editable source of truth. |
| `source/opener_asset.json` | The fixed opener (beats 2 and 3). |
| `source/entryway_source.json` | The merged outline + manual content the scripts were written from. |
| `source/*.py` | collect / build / validate scripts. |

## Rebuilding

Edit `source/pilot.json` (or `opener_asset.json`), then re-run `build_pilot.py` and `validate_pilot.py` from `source/`. Paths inside are absolute to this session; update before running elsewhere.

## Gates

Em dashes zero · six segments per episode in canonical order, Safety fourth · every VO field real spoken prose, not stubs · every shot's VO-sync phrase traces to its segment VO · no presenter on camera · one-person shoot only · no banned vocabulary, absolute timecodes, or invented statistics · HTML balanced with working nav.

## Caveats

- The headless gate is a text heuristic; it cleared false positives ("no second operator", "your head and shoulders") but cannot prove a presenter is absent. Skim the shot lists before shooting.
- The VO is written to be read aloud, but has not been read aloud on a stopwatch. The runtime and per-segment second targets are estimates; time a real read before locking the edit.
- Reviewed by spot-checking rendered episodes, not by reading all five end to end.
