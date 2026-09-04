"""Build the narrated version of a zone video: real voice, matched timing, captions.

Phil asked for audio and captions on every video. The silent cut could not
simply have a soundtrack laid over it, because the timings do not fit: the
Landing Zone's video runs 27.8 seconds and its own on-screen words take about
two and a half minutes to say. Every one of its eleven beats was shorter than
the sentence it displays.

So the narration drives the timing rather than the other way round. Each beat
is spoken, the audio is measured, and the slide is held for exactly as long as
the voice needs plus a breath. The result is the two to four minute
instructional video the media plan described, instead of a caption reel.

Voice is Microsoft's neural TTS through edge-tts. I previously told Phil that
narration was blocked because Windows SAPI sounds robotic. That was true of
SAPI and false as a conclusion: these voices are natural, free, and needed no
decision from him.

Captions are regenerated from the same measured durations, so the SRT matches
the spoken audio exactly rather than approximately.

    python ops/video_narrated.py --zone "Landing Zone" --room Entryway
    python ops/video_narrated.py --all
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

OUT = os.path.join(ROOT, "build", "video", "zones-narrated")
WORK = os.path.join(ROOT, "build", "video", "_narr")
# Rendered video is no longer committed (Phil, 2026-09-03), so the Desktop
# folder is the only place a finished video survives outside this machine's
# build directory. Copying has to happen as part of rendering rather than as
# something somebody remembers, or a render that is never copied is a render
# that did not happen.
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop", "6s-success-videos")
VOICE = "en-US-AvaNeural"
RATE = "-4%"          # a touch under default; instructions need room to land
TAIL = 0.6            # a breath after each beat, so slides do not snap
FPS = 30


def probe_duration(path: str) -> float:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True, timeout=60)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


async def _speak(text: str, path: str) -> None:
    import edge_tts
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)


def narrate(lines: list, work: str) -> list:
    """Speak each line, return [(mp3, seconds)] in order.

    A beat with no words still gets a silent placeholder, because dropping it
    would slide every later caption out of sync with the picture.
    """
    import time
    os.makedirs(work, exist_ok=True)
    out = []
    for i, text in enumerate(lines):
        mp3 = os.path.join(work, "b%03d.mp3" % i)
        if not text.strip():
            subprocess.run(
                ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                 "-t", "1.2", mp3], capture_output=True, timeout=60)
        else:
            # The voice service throttles under sustained use. A first run of
            # 228 videos produced 20 and then failed 198 times with
            # NoAudioReceived, which is a rate limit rather than bad input.
            # Back off and retry instead of losing the whole batch.
            last = None
            for attempt in range(5):
                try:
                    asyncio.run(_speak(text, mp3))
                    if probe_duration(mp3) > 0:
                        last = None
                        break
                    last = "empty audio"
                except Exception as e:                          # noqa: BLE001
                    last = "%s: %s" % (type(e).__name__, str(e)[:60])
                time.sleep(3 * (attempt + 1))
            if last:
                raise SystemExit("voice failed for beat %d after 5 tries: %s"
                                 % (i, last))
            # A short pace between beats keeps a long batch under the limit
            # rather than sprinting into it.
            time.sleep(0.7)
        d = probe_duration(mp3)
        if d <= 0:
            raise SystemExit("no audio produced for beat %d" % i)
        out.append((mp3, d))
    return out


def srt_from(durations: list, lines: list) -> str:
    def stamp(t):
        ms = int(round(t * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return "%02d:%02d:%02d,%03d" % (h, m, s, ms)
    import video_srt
    cues, t, n = [], 0.0, 0
    for (_, d), text in zip(durations, lines):
        start, end = t, t + d + TAIL
        t = end
        if not text.strip():
            continue
        # span is computed ONCE, before the loop. Recomputing it inside used the
        # already-advanced start, so each cue got a shorter slice than the last
        # and the captions ran ahead of the voice: the first beat produced
        # 2.99s then 1.49s instead of two equal halves.
        parts = video_srt.split_beat(text)
        span = (end - start) / max(1, len(parts))
        for part in parts:
            n += 1
            cues.append("%d\n%s --> %s\n%s\n"
                        % (n, stamp(start), stamp(start + span),
                           video_srt.wrap_two_lines(part)))
            start += span
    return "\n".join(cues)


def build(room: str, z: dict, wide: bool) -> str:
    import video_srt
    import video_zone as vz

    slug = vz.zone_slug(room, z["zone"])
    work = os.path.join(WORK, slug)
    os.makedirs(work, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    bs = vz.beats(room, z)
    lines = [video_srt.BRAND.sub("", video_srt.visible_text(h)).strip()
             for _, h, _ in bs]
    audio = narrate(lines, work)

    exe, extra = vz.browser()
    listing, pngs = [], []
    for i, ((secs, html, _dark), (_mp3, dur)) in enumerate(zip(bs, audio)):
        png = os.path.join(work, "b%03d.png" % i)
        vz.shot(exe, extra, html, png)
        if not os.path.exists(png):
            raise SystemExit("beat %d did not render" % i)
        pngs.append(png)
        hold = dur + TAIL
        listing.append("file '%s'\nduration %.3f"
                       % (png.replace(os.sep, "/"), hold))
    listing.append("file '%s'" % pngs[-1].replace(os.sep, "/"))
    lst = os.path.join(work, "list.txt")
    io.open(lst, "w", encoding="utf-8", newline="").write("\n".join(listing))

    # Concatenate the spoken beats with the same trailing pad the pictures use,
    # so the voice and the slide change together instead of drifting apart.
    alist = os.path.join(work, "audio.txt")
    padded = []
    for i, (mp3, dur) in enumerate(audio):
        p = os.path.join(work, "p%03d.mp3" % i)
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", mp3,
             "-af", "apad=pad_dur=%.3f" % TAIL, "-c:a", "libmp3lame", p],
            capture_output=True, timeout=120)
        padded.append(p)
    io.open(alist, "w", encoding="utf-8", newline="").write(
        "\n".join("file '%s'" % p.replace(os.sep, "/") for p in padded))
    voice = os.path.join(work, "voice.mp3")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "concat", "-safe", "0", "-i", alist,
                    "-c", "copy", voice], capture_output=True, timeout=300)

    out_path = os.path.join(OUT, slug + ("-16x9" if wide else "") + ".mp4")
    W, H = (1920, 1080) if wide else (1080, 1920)
    p = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", lst, "-i", voice,
         "-vf", "scale=%d:%d,fps=%d,format=yuv420p" % (W, H, FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         # -14 LUFS is the streaming loudness standard. Getting this wrong is
         # the most common reason amateur video sounds amateur.
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         # 48 kHz is the standard sample rate for video audio. The first build
         # came out at 96 kHz, which is needless and resamples badly on some
         # players.
         "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest", out_path],
        capture_output=True, text=True, timeout=900)
    if not os.path.exists(out_path):
        raise SystemExit("ffmpeg produced nothing: %s" % p.stderr[-400:])

    io.open(out_path.replace(".mp4", ".srt"), "w",
            encoding="utf-8", newline="").write(srt_from(audio, lines))
    deliver(out_path, wide)
    return out_path


def deliver(mp4: str, wide: bool) -> None:
    """Copy the finished video and its captions to the Desktop folder.

    This is delivery, not backup. Since video left git, this folder is the only
    copy outside build/, and it is the folder the files are actually used from.
    A failure here is reported rather than raised: the render succeeded, and
    losing that to a copy error would be worse than a missing copy.
    """
    import shutil
    sub = "narrated-16x9" if wide else "narrated-9x16"
    try:
        for dest, src in ((os.path.join(DESKTOP, sub), mp4),
                          (os.path.join(DESKTOP, "narrated-captions"),
                           mp4.replace(".mp4", ".srt"))):
            if not os.path.exists(src):
                continue
            os.makedirs(dest, exist_ok=True)
            shutil.copy2(src, os.path.join(dest, os.path.basename(src)))
    except Exception as e:                                      # noqa: BLE001
        print("  WARNING: rendered but not delivered to Desktop: %s"
              % type(e).__name__)


def main() -> int:
    import video_zone as vz
    wide = "--wide" in sys.argv
    zs = vz.zones()
    want_z = sys.argv[sys.argv.index("--zone") + 1] if "--zone" in sys.argv else None
    want_r = sys.argv[sys.argv.index("--room") + 1] if "--room" in sys.argv else None
    todo = [(r, z) for r, z in zs
            if (want_z is None or z["zone"] == want_z)
            and (want_r is None or r == want_r)]
    if not todo:
        print("  no zone matched"); return 1

    made = 0
    for room, z in todo:
        out = build(room, z, wide)
        d = probe_duration(out)
        size = os.path.getsize(out) / 1048576
        print("  %-44s %5.1fs  %4.1f MB" % (os.path.basename(out), d, size))
        made += 1
    print("  narrated videos built: %d" % made)
    return 0


if __name__ == "__main__":
    sys.exit(main())
