/* The zone's own published video, as a URL or nothing.
 *
 * Pulled out of App.js so it can be tested with plain node, the same reason
 * format.js exists. Twelve of the 114 zones have a video published on
 * YouTube; ops/youtube-published.json is the record, ops/build_quest.py
 * copies each id into quest-data.js, and ops/build_mobile_corpus.py carries
 * it into this app's bundled corpus. Every other zone has none, and the
 * card must simply not offer a link rather than offering a dead one.
 *
 * A URL is built only from an id that looks like a YouTube id, so a
 * half-written corpus entry cannot become a link into nowhere. Returning a
 * URL rather than opening it keeps this pure: nothing is requested from
 * YouTube until somebody presses the link the app draws from it.
 */

const YOUTUBE_ID = /^[A-Za-z0-9_-]{11}$/;

function videoUrl(zone) {
  const id = zone && typeof zone.video === "string" ? zone.video.trim() : "";
  if (!YOUTUBE_ID.test(id)) {
    return null;
  }
  return "https://www.youtube.com/watch?v=" + id;
}

module.exports = { videoUrl };
