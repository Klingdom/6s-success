# Editorial Review: Chapter 15 Content Package

Reviewed against the checklist: repetition, AI-sounding phrasing, unsupported claims, hooks, CTAs, source alignment, overlong social posts, tone, formatting. This review reports only checks actually run; every count below was measured with LC_ALL=C scans, and every cited noun or quote was grep-verified present in the manuscript or final HTML before citing.

## Overall verdict
Publish-ready after author sign-off, with one standing caveat: the chapter is a draft (authored in the book voice, no source file supplied). The package holds the warm, quiet-pride, anti-shame voice across all channels, the facts trace cleanly to the manuscript and HTML, and the hooks are concrete (the row of separate good spots with a faint "?" over it, "Group by what you do, not by what things are," and "It was one zone all along"). Findings below are minor.

## Repetition
- Cross-asset repetition of the spine (the rule, the room-map definition, the zone definition, the launch-pad reveal, the shared-map pull-quote) is by design and staggered by the calendar.
- The hero vocabulary runs high ("map," "zone," "room," "home," "shared," "activity"), because it is the subject, not a tic. When excerpting, vary the surrounding language so a single post does not stack "whole," "picture," and "logic."

## AI-sounding phrasing
- None found. The writing leans on concrete images (the museum "you are here" diagram, morning coffee scattered across four cupboards, a napkin sketch of the rooms) rather than generic filler.
- Widened dash scan clean (em, en, spaced-hyphen, and dash HTML entities all zero). No hype words in any asset.

## Unsupported claims
- No invented statistics, names, or dates. The origin (the Straighten/Seiton idea of an overall workplace layout and activity zoning, home-scaled) is referenced lightly, not overclaimed.
- The "purge"/"attack" tokens flagged by the force-metaphor scan are confined to negated production notes in `video-audio/b-roll-and-visual-notes.md`; no reader-facing copy uses them.
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders.

## Hooks
- Strong and specific: the finished-but-scattered entryway with a pencilled "?" where a map would sit, the coffee-in-four-cupboards contrast, "It was one zone all along," and the private-map/shared-map turn.

## CTAs
- Every social post carries a soft CTA to the chapter or the online book. The hero action (pick one busy corner, name the activity in a single word, gather what it needs, and you have drawn your first zone) is concrete and free. Rotate wording before publishing; insert the live URL for "the online book."

## Source alignment
- Strong. The rule, the room-map definition, the zone definition, the launch-pad reveal (keys, leash, bag, umbrella, outgoing mail, shoes), the coffee/homework/charging/mail-and-admin zones, the draw-it-and-share-it move, and the STRAIGHTEN COMPLETE friction milestone all match the manuscript and HTML.

## Overlong social posts (measured)
- X thread: header states 14 posts; the file contains **14** posts, all at or under 280 characters INCLUDING the "N/" number line (**longest 261**, post 14, the friction-milestone close). Pass.
- X short posts: **10** standalone posts, all at or under 280 including the number line (**longest 266**, post 1). Pass.
- LinkedIn: **10** posts, each under 150 words of body copy (**longest 144**; with the "## N." heading line counted the max is 151, but the post body is 144). Pass.
- Facebook longform: **381** words in the post body (within the 300 to 450 target). Not a flag.

## Tone
- Correct platform-fit; the quiet-pride, anti-shame, honest-milestone register holds everywhere, and the goal is kept honestly ahead (four S's remain).

## Formatting
- Clean Markdown. Both JSON files parse (`canonical/chapter-metadata.json`, `web/schema-org-article.json`); the publishable HTML carries one JSON-LD block that parses. CSV `workflow/asset-inventory.csv` has 7 columns and 48 data rows. The publishable HTML has 4 balanced SVG figures; html/head/body/main and svg tags all balance.

## Recommended edits before publishing
1. Author approval of the authored chapter first.
2. Insert the real chapter URL for "the online book."
3. Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and `chapter-15-publishable.html`.
4. Rotate the LinkedIn and X CTA wording (several close on "Free online").
5. Replace or remove the back-cover testimonial placeholders.
6. Lead the visual production with the opener (scattered good spots plus the faint "?") and the zoned floor-plan graphic.
