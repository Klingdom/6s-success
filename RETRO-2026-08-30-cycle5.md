# Retrospective, fifth cycle ending 2026-08-30

Six commits, and product work again after two cycles of instrumentation. The
Entryway deck went from 71 fronts to a complete 88 card deck with backs, laid
out as a print at home PDF.

---

## What went well

**Kept the promise made in the last retrospective.** That one set two
consecutive instrumentation cycles as the limit and named the work to do
instead. This cycle did that work rather than finding another measurement
problem to enjoy solving.

**Knew when to stop prompting.** A third photo pass recovered 5 of 12,
taking photographic heroes to 76 of 88. The remaining 12 fail structurally: five
name an idea with no object in it at all, and the rest need legible lettering
in the picture, which the negative prompt suppresses on purpose because that
suppression is what keeps garbled text off the deck. Asking the model for a
readable label is asking it to break the rule that makes the deck safe. A
fourth pass would have been superstition.

**The answer was a design decision, not a workaround.** Those 12 get a graphic
hero: six ascending marks in the card's own type colour with the type name
beneath. Card games have always drawn concept cards differently from object
cards, and a reader can tell at a glance which kind they hold. It never
pretends to be a photograph.

**Built the backs, which turned out to be half the product.** They were missing
entirely. On EE-001 the back carries best practices, the Home Quest challenge, a
fact, the next card, a progress tracker and the related path: more words than
the front. The corpus already had all seven fields on all 88 cards, checked
before building rather than discovered during. Shipping fronts only would have
been shipping half a deck for no reason at all.

**Treated duplex printing as the correctness problem it is.** Paper flipped on
its long edge reverses left and right, so a back printed in the same column as
its front lands on a different card and every card in the deck lies about
itself. Nobody would see it until they had printed, cut and sleeved ninety
cards. The placement is a tested function rather than two lines inside a loop.

---

## What did not go well

**I wrote a verification that could not fail and nearly believed it.** The first
duplex check compared the sorted set of x coordinates on the front and back
sheets. Those sets are identical whatever card sits where, so it was comparing
a number with itself. It reported six mismatches, all artefacts, and for a
moment I took that as evidence the mirroring was broken. The code was right and
the test was wrong. A check that cannot distinguish the two cases it exists to
distinguish is worse than no check, which is the same sentence I have now
written in four consecutive retrospectives about four different things.

**`want = sorted(allc)` nearly shipped another room's deck.** cards() merges
sources and the richest one also carries the Mudroom deck, so building "every
card with data" queued 180 cards and would have produced 92 unreviewed cards
from a room nobody asked for. Caught only because the count printed 180 and 88
was the number I expected. Had the merge added two cards instead of ninety two,
I would not have noticed.

**Committed before reading preflight.** The commit went in, then the gate
reported stale fingerprints across 186 pages. Harmless because the next commit
fixed it, and it is the second time this cycle that reading output after acting
rather than before cost a round trip.

**Two wrong versions of the concept panel before the right one.** The first
printed the card's tagline large, four centimetres under the same words as the
subtitle. The second was correctly composed and far too small, reading as a
picture that had failed to load. Both were obvious the moment the card was
opened and invisible in the code.

---

## What to change next cycle

**A test must be shown failing on the bug it is for.** Not merely "shown
failing", which the duplex check technically was. It has to fail when the
specific defect is present and pass when it is not, and the way to know is to
introduce the defect. The mirroring test now checks that mirroring is a real
swap and not a no-op, which is exactly the bug it exists to catch.

**Expect merged data sources to contain more than you asked for.** Anything
derived from `cards()`, `gather()` or a glob over a shared folder gets its
membership stated explicitly and its count asserted.

**The deck still is not linked anywhere a customer can reach.** The PDF exists
in build/. Putting it on the site is deploy gated like everything else, but
preparing the download and the page copy is not. That is next.

---

## Numbers

| | |
|---|---|
| Entryway deck, cards rendering | 88 of 88, fronts and backs |
| Photographic heroes | 76, after three passes |
| Designed concept heroes | 12, deliberately not photographs |
| Print and play PDF | 20 sheets, 25.2 MB, duplex, 2.5 by 3.5 inches exactly |
| Cards published on an unreviewed photograph | 0 |
| Tests now run by preflight | 3 |
| Verifications that were themselves wrong | 1, caught |
| Production still stale | 4 of 4 assets |
| Revenue | $19, unchanged |
