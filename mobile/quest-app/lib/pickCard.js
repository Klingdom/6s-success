/* Which card is on top, and what "skip" actually does.
 *
 * The rule is simple on purpose: walk the corpus in its own order and hand
 * back the first pass nobody has finished. Predictable beats random, so
 * somebody coming back continues where the house was left rather than being
 * handed an unrelated room.
 *
 * Kept separate from App.js, the same reason lib/importProgress.js is: it can
 * be unit tested with plain node, no device and no React Native runtime.
 */

function cardId(zone, pass) {
  return zone.room + "|" + zone.zone + "|" + pass;
}

/* Whether a card is actually on screen for the player to act on, as opposed
 * to merely computed. `card` is recalculated from `done`/`skipped` on every
 * change regardless of which screen is showing, so `card` being non-null is
 * not the same as a card being drawn: the finished-zone recap and the
 * stopping screen both sit on top of it without a card visible underneath. */
function isCardVisible(finished, idle, card) {
  return !finished && !idle && !!card;
}

/* The card to show right now.
 *
 * `skipped` is a session-only set of card ids the player has already said
 * "not now" to. A skipped card is passed over in favour of the next
 * unfinished one, so pressing "Not now" actually changes what is on screen,
 * which is the whole point of the button. It is never treated as done, and
 * it is never lost: if every remaining unfinished card has been skipped,
 * the walk falls back to the first one rather than returning nothing, so a
 * player is never left on a blank screen just because they skipped
 * everything left in the house.
 */
function pickCard(corpus, done, skipped) {
  done = done || {};
  skipped = skipped || {};
  let fallback = null;
  for (const zone of corpus.zones) {
    for (const step of zone.steps) {
      const id = cardId(zone, step.s);
      if (done[id]) continue;
      if (!fallback) fallback = { zone, step };
      if (!skipped[id]) return { zone, step };
    }
  }
  return fallback; // null when every card in the house is done
}

module.exports = { cardId, pickCard, isCardVisible };
