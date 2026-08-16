# Chapter 49 Editorial Review: The Stair Landing

An honest read of the chapter as built, not a summary of intent.

## What works

**"A staircase is not a task" is the best sentence in Part Nine.** It does an enormous amount in six words: it explains why stair hazards are categorically different from workshop hazards, it removes any implication that the reader is careless, and it justifies the entire safety weighting of the chapter. Everything else in the layer follows from it.

**The attended-versus-unattended distinction is genuinely new.** Chapter 46 already claimed the workshop was the room where a bad standard costs a finger. A lesser chapter would have repeated that claim here and blunted both. Instead this one draws the line precisely: a workshop hazard has your attention, a stair hazard has nobody's. That sharpens Chapter 46 retrospectively rather than competing with it.

**"The trap is a reasonable sentence" is the kindest diagnosis in the book.** Naming the mechanism as "I will take it up next time I go", and then explicitly saying nobody is lying and the trip genuinely was going to happen, is a real piece of understanding. And the response follows from the diagnosis rather than contradicting it: you do not argue with the sentence, you give it a basket.

**The dead bulb passage is the most useful paragraph in Part Nine.** It identifies a serious hazard, explains precisely why it goes unnoticed (invisible from the landing, invisible from halfway up), names the single position it is visible from, and ends in a ten-minute fix. That is the complete shape of a good safety note.

**A route needing almost nothing is carried into the kit itself.** The kit list is the shortest in the book and the infographic spec explicitly says it should look sparse on the page. Letting the design carry the argument rather than restating it is the right instinct.

**The close is the only one in Part Nine that is not a photograph.** A check you stand in, from the two positions nobody occupies on purpose. It is well argued and it catches the one fault a photograph cannot.

## What is weaker

**A length-model refinement was attempted at the brief stage and was wrong, which is worth recording rather than hiding.** Observing that every chapter carries one hard call per zone, the frame looked like it should scale with zone count, giving `2,940 + 570 per zone`. That model fitted Chapters 45 to 48 more tightly than the original, so it was adopted and the target set at 4,650.

The chapter then landed at 4,985: **+7.2% against the refined model, +0.1% against the original.**

| | Ch 45 | Ch 46 | Ch 47 | Ch 48 | **Ch 49** |
|---|---|---|---|---|---|
| Original model | +3.4% | +1.0% | +1.3% | -0.6% | **+0.1%** |
| Refined model | +1.7% | +1.0% | +1.3% | +1.3% | **+7.2%** |

The refinement had been fitted to the four points that produced it, and the fifth disproved it. The original model is now five-for-five within -0.6% to +3.4%. **The lesson generalises beyond this book: do not re-fit a model on the sample that generated it, and do not adopt a refinement until an out-of-sample point has tested it.**

**Per-zone words rose again, to 587, and the cause has moved.** Chapter 48's overrun was step count (a default of ten). Here step count is correct at ten for eight surfaces, per the rule added after Ch 48, but the steps themselves are longer: 59 words per step against Chapter 48's 51. So the metric is drifting for a second reason, and fixing one driver revealed the other. **For Chapter 50, budget words per step, not just steps per zone.**

**Three calls is thin, and one of them repeats a shape.** With only three zones there are only three hard calls, which makes the section noticeably shorter than any other in Part Nine. That is faithful to the Manual. But "the runner that has already lifted once" and the deferred-repair logic in Chapter 48's broken vacuum are close cousins, and this is now the fourth Part Nine chapter to contain a variant of the postponed-repair decision.

**The chapter is short enough to feel slight.** At 4,985 words it is the shortest room playbook by nearly 900 words. That is correct for a three-zone space and the chapter argues for its own brevity convincingly. It is still worth Phil knowing that a reader coming from the 7,500-word Laundry Room will feel the drop.

## Verdict
Ready for Phil's review as a draft. The best-written chapter in Part Nine on a sentence-by-sentence basis, and the one that produced the most useful process lesson, which was a model correction rather than a content fix.
