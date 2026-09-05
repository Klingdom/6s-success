/* Merging a browser backup into on-device progress.
 *
 * The web Quest's own backup() writes { done: { cardId: timestamp } } from
 * site/assets/js/quest.js, and its restore() merges rather than replaces,
 * keeping the earlier timestamp for any card both sides have, so restoring
 * a backup can never lose work done since it was taken. cardId there is
 * room + "|" + zone.zone + "|" + step.s, and App.js's cardId() builds the
 * identical string from the same corpus, so a raw web backup file merges
 * into this app's own `done` object with no translation step.
 *
 * Kept separate from App.js so this can be unit tested with plain node,
 * with no device and no React Native runtime involved.
 */

function parseBackup(text) {
  let incoming;
  try {
    incoming = JSON.parse(text);
  } catch (e) {
    return null;
  }
  if (!incoming || typeof incoming.done !== "object" || incoming.done === null) {
    return null;
  }
  /* A card's value has to be a real completion timestamp. A malformed or
   * hand-edited backup can carry a string, NaN or a negative number for one
   * card without the whole file failing JSON.parse, and mergeDone's own
   * Math.min(a, b) turns that into NaN for any card both sides share, which
   * is falsy and silently erases a card the phone already had done. Drop
   * bad entries here instead, so mergeDone only ever sees valid timestamps. */
  const done = {};
  Object.keys(incoming.done).forEach((k) => {
    const v = incoming.done[k];
    if (typeof v === "number" && Number.isFinite(v) && v > 0) {
      done[k] = v;
    }
  });
  return { done };
}

/* Same rule as quest.js's restore(): a card in both sides keeps the earlier
 * timestamp, a card only on one side is kept as is. Returns the merged map
 * plus how many cards the import actually added or moved earlier, so the
 * app can tell someone what happened rather than a bare "done".
 *
 * Validates both sides itself rather than trusting a caller to have done it
 * first. `parseBackup` already drops a bad incoming value on the one path
 * that calls this today, but that made this function safe only in
 * combination with its one caller, not on its own, unlike quest.js's
 * restore(), which is self-contained. That is the same gap the 2.10 fix and
 * its 2026-09-05 correction found and closed for the existing-value side
 * one caller at a time; fixing it here at the source means a future caller
 * of mergeDone (a test, a different import path) cannot reintroduce the
 * exact same silent-corruption bug just by skipping parseBackup. */
function sanitizeTimestamp(v) {
  return typeof v === "number" && Number.isFinite(v) && v > 0 ? v : undefined;
}

function mergeDone(existingDone, incomingDone) {
  const next = { ...existingDone };
  let changed = 0;
  Object.keys(incomingDone).forEach((k) => {
    const rawA = existingDone[k];
    const a = sanitizeTimestamp(rawA);
    const b = sanitizeTimestamp(incomingDone[k]);
    const merged = a && b ? Math.min(a, b) : a || b;
    if (merged !== rawA) changed++;
    next[k] = merged;
  });
  return { done: next, changed };
}

module.exports = { parseBackup, mergeDone };
