/* Plain string builders pulled out of App.js so a JSX whitespace mistake
 * cannot silently ship again.
 *
 * Found 2026-09-05: the finish screen wrote
 *   {zonesHeld} of {CORPUS.zoneCount} zones in the house
 *   {zonesHeld === 1 ? "is" : "are"} holding.
 * across two JSX lines. Babel's JSX whitespace rule drops a line that is
 * only indentation between a text node and the next expression rather than
 * collapsing it to a space, so the compiled children array was
 * [..., "zones in the house", "is", " holding."] with no separator: the
 * screen every single completed zone lands on read "zones in the houseis
 * holding." (or "housearе holding."). ON-DEVICE-TEST.md check 6 would have
 * caught it, but nobody had run that check yet. Building the whole sentence
 * as one string here means there is exactly one place a line break can
 * hide, and it is testable with plain node.
 */

function zonesHoldingLine(zonesHeld, zoneCount) {
  return zonesHeld + " of " + zoneCount + " zones in the house " +
    (zonesHeld === 1 ? "is" : "are") + " holding.";
}

module.exports = { zonesHoldingLine };
