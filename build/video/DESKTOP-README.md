# 6S Success zone videos

**912 files, 1.1 GB.** Every one of the 114 micro zones, silent and narrated, in
both shapes a viewer actually encounters, with captions and upload-ready text.

## This folder is the primary copy

As of 3 September 2026 the rendered video is no longer stored in git. It was
794 files and 785 MB inside the repository, `.git` had grown to 1.1 GB, and
every clone dragged the whole history for files a renderer reproduces from the
zone data. So this folder is not a convenience export any more. It is where the
finished work lives.

The renderer copies here automatically as each video finishes, and
`python ops/verify_media_delivery.py` in the repository reports anything that
exists only in `build/` and therefore in only one place.

Do not treat this folder as scratch. If it is moved or emptied, the videos have
to be re-rendered, which takes about four hours for the full set.

| Folder | Count | What it is |
|---|---|---|
| `narrated-9x16/` | 114 | 1080x1920. Narrated, Shorts and Reels. **Primary** |
| `narrated-16x9/` | 114 | 1920x1080. Narrated, YouTube proper. **Primary** |
| `narrated-captions/` | 228 | SRT timed to the spoken voice |
| `vertical-9x16/` | 114 | The earlier silent cut, 1080x1920 |
| `wide-16x9/` | 114 | The earlier silent cut, 1920x1080 |
| `captions/` | 114 | SRT for the silent cut, timed to the slides |
| `youtube-metadata/` | 114 + playlists | title, description, tags per video |

Filenames are `room--zone.mp4`, so `entryway--landing-zone.mp4` pairs with
`entryway--landing-zone.srt` and `entryway--landing-zone.json`. In the narrated
folders the 16:9 file carries a `-16x9` suffix.

**Publish the narrated set.** The silent cut is kept because ten of its videos
are already on YouTube and a published file cannot be replaced, so its captions
still need to match. For anything not yet uploaded, the narrated version is the
one to use.

## Uploading

Each JSON carries the title, description and tags for that video. The
description leads with what the zone is and what done looks like, lists the six
passes, and links to the free written steps on the site.

`playlists.json` groups the 114 into 20 playlists, one per room.

Upload the matching `.srt` as the caption track. The words are also burned into
the picture, but a text track is what YouTube indexes, what a screen reader can
speak, and what a translation can work from. Skipping it wastes most of the
reason the captions exist.

## Two things worth knowing

**The narrated set has a real voice, and its timing comes from that voice.**
Each beat is spoken, the audio is measured, and the slide is held for exactly as
long as the voice needs. That is why these run two to four minutes where the
silent cut ran under thirty seconds: the silent version showed each sentence for
less time than it takes to say.

**Every zone is uniquely named by room.** Three zone names repeat across rooms:
Dresser Drawers, Shower or Tub, and Toilet Area. Naming by zone alone produced
111 files for 114 zones and three rooms silently showed another room's video.
The `room--zone` prefix is what prevents that, so keep it.

## Verified before copying

All 456 videos were checked with ffprobe: correct dimensions, none under five
seconds or 50 KB. Every caption file parses, none is empty, none has fewer than
three cues, and every video has one.

Twelve narrated captions were regenerated on 3 September after being lost in an
earlier recovery. Ten of those twelve are already published, and a published
video file cannot be replaced, so each was re-rendered and its duration compared
against the published one first. All ten matched to the millisecond, which
confirms the regenerated captions are correctly timed for the videos that are
already live.
