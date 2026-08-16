# Entryway Media Package — YouTube

Publish-ready YouTube metadata for the five Entryway episodes and their 23 Shorts. 2026-07-21.

Companion to the pilot scripts in `../pilot/`. Where the pilot is what you *shoot*, this is what you *paste into YouTube* when you upload.

## Contents

| File | What it is |
|---|---|
| `Entryway Media Package - YouTube.html` | The review document. One section per episode, every field in a copy box, then that episode's Shorts. Sticky nav across the five. |
| `paste/MZ-00N - <zone>.txt` | One plain-text file per episode with everything paste-ready: title, full description, tags, pinned comment, end screen, thumbnail, and all its Shorts. |
| `validation-report.txt` | Gate output, all passing. |
| `source/` | package.json (the copy as data) plus the collect/build/validate scripts. |

## What each episode includes

- **Title** (from the script)
- **Description** — a 2-line hook, body paragraphs, an estimated chapter block, the series blurb, link placeholders, and three series hashtags. Assembled and ready to paste.
- **Chapters** — labelled and timestamped
- **Tags** — 10 to 15, broad plus specific
- **Pinned comment** — seeds discussion with a real question
- **End screen** — what the last ~20 seconds features
- **Thumbnail** — the text and a headless visual (object or before/after, never a face)

## The 23 Shorts

Each of the 23 Shorts has its own title, caption, and hashtags, written from that segment's actual content. The set matches the pilot scripts exactly: only segments the scripts marked as standing alone became Shorts, so the five episodes carry 4, 6, 4, 4, and 5 Shorts rather than a flat six each.

## Before you publish

- **Chapter timestamps are estimated** from the script's segment targets, not from a real edit. Replace them with true timestamps once the video is cut, keeping the first at `0:00`. The chapter *labels* and order are correct; only the times are provisional.
- **Links are placeholders** in square brackets (`[link]`). Drop in your real channel, playlist, book, and manual URLs.
- **Publish in order**, and the README on the plan recommends the Door/Mat episode as the first upload (shortest, and it closes the room).

## Rebuilding

Edit `source/package.json`, then re-run `build_pkg.py` and `validate_pkg.py` from `source/`. The build reads the pilot scripts (`../pilot/source/pilot.json`) to compute chapters and to check the Shorts set. Paths are absolute to this session; update before running elsewhere.

## Gates

Em dashes zero · all metadata fields present · tag count 10 to 15 · Shorts set matches the scripts' stand-alone flags, 23 total, each complete · titles under 100 chars · hashtags well-formed · Safety 4th wherever the six S's are listed · no banned vocabulary, invented statistics, view promises, or clickbait · chapters start at 0:00 and are flagged estimated · HTML balanced, 5 paste files present.

## Caveats

- Scope is YouTube only, by request. No cross-platform social posts or newsletter copy are included.
- Clickbait and view-promise checks are text heuristics; they passed, but a human should still eyeball the titles before publishing.
- Reviewed by spot-checking the rendered document and one paste file, not by reading all five end to end.
