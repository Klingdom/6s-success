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
  return incoming;
}

/* Same rule as quest.js's restore(): a card in both sides keeps the earlier
 * timestamp, a card only on one side is kept as is. Returns the merged map
 * plus how many cards the import actually added or moved earlier, so the
 * app can tell someone what happened rather than a bare "done". */
function mergeDone(existingDone, incomingDone) {
  const next = { ...existingDone };
  let changed = 0;
  Object.keys(incomingDone).forEach((k) => {
    const a = existingDone[k];
    const b = incomingDone[k];
    const merged = a && b ? Math.min(a, b) : a || b;
    if (merged !== a) changed++;
    next[k] = merged;
  });
  return { done: next, changed };
}

module.exports = { parseBackup, mergeDone };
