# Chapter 8 Approach + Production Gates
*(Project knowledge. Built from a full editorial review of Chapters 4 to 7. The gates below are reusable for every remaining chapter; the Chapter 8 section is specific to "Sort: Remove What Does Not Belong.")*

## Where Chapters 4 to 7 landed
All four are genuinely good, warm, concrete, well-taught chapters, publishable after fixes, not filler. Instruments are rigorous (Ch 5's radar geometry and 14/30 arithmetic are correct), the friction meter ritual is executed correctly every time, hero devices are clear, and testimonials are properly marked placeholders throughout. The problems are systemic and process-level, not talent-level. Fix the process and the chapters get better and cheaper to trust.

## The seven systemic issues found (and the gate that stops each)

### 1. The dash rule was under-enforced (the big one)
The cardinal rule bans em (—), en (–), AND " - " (spaced hyphen) used as a dash. Every prior scan and every review file checked only em/en, which were genuinely zero, and then asserted a "clean dash scan." Meanwhile " - " as a dash-substitute is pervasive: candidate lines Ch4 ~17, Ch5 ~9, Ch6 ~38, Ch7 ~6. The designed `final.html` correctly renders these as the middot "·" ("Part Two · Prepare," "Chapter 8 · Sort"), which sets the house style. The manuscript source and the Markdown package assets never got the same treatment. One instance was reader-facing and reached [BLOCKER]: Ch 5 `video-audio/b-roll-and-visual-notes.md` line 102 series tag "6S Success: Home Edition - Part Two, Prepare".
- **GATE (widened dash scan):** flag `—`, `–`, and " - " / " -" / "- " used as punctuation across ALL files including the manuscript and signature, excluding Markdown list bullets (a line starting with "- " or "  - "). Standardize every label/separator on "·" (or a colon), matching the HTML. Run it before sign-off so the review can claim a clean scan truthfully.

### 2. Review files overstate and carry errors
- Asserted "zero dashes" while " - " was present (all four chapters).
- Wrong hard counts: Ch 6 review says the X thread is "12 posts"; it is 13. Ch 7 review says "10 / longest 265"; the thread is 12 posts, longest 263.
- Phantom evidence: Ch 4's `editorial-review.md` and `brand-voice-check.md` cite "a dollar latch" as a concrete noun that grounds the writing. "Latch" appears zero times in Chapter 4; it leaked from a template. This undercuts every "verified / publish-ready" claim in those files.
- "Verbatim" that is not byte-verbatim: Ch 5 `graphics/quote-card-copy.md` claims cards are "pulled verbatim," but Card 10 drops the "It is a map, and" clause.
- **GATE (honest review):** a review file may only (a) report the widened dash scan it actually ran, (b) cite a concrete noun or quote after grep-confirming it exists in THIS chapter's manuscript/HTML, (c) state a hard count only after counting it (count, then write), (d) use the word "verbatim" only for byte-identical strings, else "lightly trimmed."

### 3. Manuscript and HTML silently diverge
The HTML layer improves and sometimes corrects the manuscript, but the fixes are never back-ported, so the "manuscript of record" and the shipped HTML disagree, and sometimes the manuscript still carries the error the HTML fixed. Examples: Ch 5 "Chapter Close" became "A Number to Beat" in HTML only; Ch 7 manuscript line 67 says "five jobs" then lists six ("...the package staging area..."), and the HTML quietly dropped that sixth item to make five, in the very chapter whose device is "One Job Beats Five."
- **GATE (back-port):** the manuscript is the record. Any edit made while building the HTML (a retitle, a trim, a factual fix) is written back into the manuscript in the same session. Manuscript and HTML must agree on every fact, count, and section title.

### 4. Hero / reusable lines drift into variants
Ch 7's flagship worked sentence exists in two non-identical forms across 30+ package files and even splits body-vs-infographic inside one HTML spread ("...so that mornings start calm..." vs "...in the morning... so that the day starts calm...").
- **GATE (freeze canonical strings first):** before any packaging fan-out, lock a single source-of-truth string for every reusable artifact (hero device name, the decision rule wording, the worked example sentence, the friction-meter caption, the One Idea to Keep). Packaging agents copy these verbatim; they do not paraphrase them.

### 5. AI-detectable prose tics
Each chapter over-leans on one payoff word or one sentence shape: Ch 4 the clipped-fragment kicker ("It compounds." "Same effort. Wildly different payoff."), Ch 5 "relief" (about 7x) plus "measure twice, cut once" twice, Ch 6 "generous" used for both the villain (the eye) and the hero (the photo) plus "It is X, and a Y one" 3x, Ch 7 "quiet/quietly" 8x and "genuinely" 6x and "itch" 3x.
- **GATE (lexical + cadence pass):** count the top repeated payoff words and signature sentence patterns; cap any single payoff noun/adverb at roughly 3 to 4 uses; vary the recurring kicker cadence; never reuse a loaded praise-word on both sides of the chapter's central contrast; retire a stock metaphor (measure-twice) after one use.

### 6. The running example was never resolved to ONE target
Ch 4's First Target Map ends in a TIE (entryway drop zone +3 equals kitchen catch-all drawer +3) and the prose leans on the drawer, yet the drop zone is the intended running example. Ch 5's signature says "tied," a Ch 5 review says "winner." The throughline survived by luck, not design.
- **GATE (single named target before an action chapter):** the chapter before any action chapter must hand off ONE unambiguous named space. Resolve the Ch 4 tie so the entryway drop zone is the outright first target, then carry it verbatim (space, audit 14/30, weakest Standardize and Sustain, the before photo, the purpose sentence) into Ch 8.

### 7. Metaphor / tone fit is not audited
Mechanical scans passed while Ch 4's gun/targeting metaphor culminated in "Part 2 is where we start to pull the trigger" plus a gun-sight crosshair, which fights the book's anti-shame warmth.
- **GATE (tone/metaphor audit):** one explicit pass asking "does the imagery match the calm, anti-shame register?" This matters most in action chapters, where physical-effort and force language ("attack the pile," "purge," "trigger") is tempting.

---

## Chapter 8 specifics: "Sort: Remove What Does Not Belong"

Chapter 8 opens **Part 3 (Sort)** and is the **first action chapter in the book**. That creates one landmark and one scope discipline.

### The landmark: the friction meter MOVES for the first time
It has HELD for Ch 4 to 7 by design (choose, audit, photograph, define all build understanding without moving objects). Sort physically removes what does not belong from the drop zone, so per the design system ("move it when the chapter moved objects") the needle finally travels from the FRICTION side toward CALM, toward the GOAL crosshair that has been fully aimed since Ch 7. This first move is a genuine payoff and should read as an event, visually distinct from four chapters of "still holding." Freeze its caption as a canonical string and make the SVG needle position unmistakably different from the held state.

### Operationalize Ch 7's purpose as the judge
The keep-or-go decision rule is Ch 7's purpose made operational: "does this thing help the space do its job?" The purpose sentence the reader wrote in Ch 7 is the criterion. Use the exact frozen drop-zone purpose sentence from Ch 7.

### Scope discipline (do NOT pre-empt Ch 9 to 11)
Part 3 is four chapters. Ch 8 teaches only the first Sort pass: take out what plainly does not belong in this space, judged against its purpose.
- Ch 9 owns Necessary vs. Unnecessary (the finer keep/discard nuance). Do not resolve it here.
- Ch 10 owns Red Tags, Holding Areas, and Sorter's Remorse. **Do not introduce red tags or the holding-area mechanism in Ch 8** beyond, at most, a one-line promissory teaser; removal in Ch 8 should feel safe and non-final without yet naming the Ch 10 system.
- Ch 11 owns disposal routing (donate/sell/store/recycle/throw away). Ch 8 removes; it does not dispose.
- Just as Ch 7 set up the sort without doing it, Ch 8 sets up the sort's downstream decisions without doing them.

### Emotional / anti-shame job
Removing is not the same as throwing away. Keep the register calm and non-final so a nervous reader will actually pull things out. No "purge," no "attack," no force metaphors (see Gate 7).

### Continuity requirements
- Masthead: "Part Three · Sort" (new part), correct chapter eyebrow.
- Same single target: the entryway drop zone (resolve the Ch 4 tie first).
- The Part 2 trio (the number 14/30, the before photo, the purpose sentence) all pay off here: the number is what we will beat, the photo is the before, the purpose is the judge.
- Hand off cleanly to Ch 9 (Necessary vs. Unnecessary) without doing Ch 9's work.

### Hero device (freeze the name and terms before packaging)
A single clean "belongs here / has a better home elsewhere" sorting device driven by the purpose question, with one worked pass on the drop zone (e.g., the umbrella earns its place; the read magazines do not). Lock the exact verb set (recommend "keep" vs "remove", with removed items "going to a better home" rather than "the trash") and use it identically in prose, callouts, the infographic, and every package asset.

---

## Chapter 8 production sequence (revised)
1. **Resolve the target.** Fix the Ch 4 tie so the entryway drop zone is the outright first target; confirm the carried facts (14/30, weakest Standardize and Sustain, the before photo, the Ch 7 purpose sentence).
2. **Freeze canonical strings.** Write a small strings-of-record block: hero device name, keep/remove rule, worked-pass examples, friction-meter "first move" caption, One Idea to Keep, the exact drop-zone purpose sentence. Everything downstream copies these verbatim.
3. **Draft the three source files** (signature, manuscript, final.html) against the frozen strings and the design system. Build the friction-meter SVG in its new MOVED state.
4. **Back-port immediately.** Reconcile manuscript and HTML so every fact, count, and section title matches; the manuscript is the record.
5. **Run the widened validation gate:** em + en + spaced-hyphen dash scan (excluding list bullets), JSON/CSV validity, HTML balance and SVG count, social lengths, and standardize separators on "·".
6. **Lexical + cadence pass and tone/metaphor audit** (Gates 5 and 7).
7. **Package in two waves** (proven, avoids rate limits): wave 1 web, LinkedIn, Facebook, X, newsletter; wave 2 video-audio, slides, pdf-ebook, graphics; then canonical, workflow.
8. **Honest review files** (Gate 2): reviews report only the scans actually run and counts actually counted, grep-verify every cited noun/quote against this chapter, and reserve "verbatim" for byte-identical strings.
9. **Number/count integrity:** every number (items removed, before/after, the needle's move) agrees across prose, callout, infographic, and package.
10. **Copy to Desktop, update PROGRESS.md, stop for author review.**

## One recurring Facebook note
The Facebook longform post has run ~600+ words on Ch 5, 6, and 7 against a 300 to 450 target. Either raise the target for Facebook (long reads perform there) or instruct the Facebook agent to hard-cap at 450. Decide once and stop re-flagging it.
