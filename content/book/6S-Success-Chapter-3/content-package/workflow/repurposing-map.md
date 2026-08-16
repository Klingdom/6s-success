# Repurposing Map: One Chapter Becomes Everything

This shows how the single chapter, "The Six Steps That Transform Any Space", turns into every asset in the package. The chapter is the trunk. Everything else is a branch off it.

```
        CHAPTER 3: "The Six Steps That Transform Any Space"
              (signature + manuscript + final HTML)
                                   |
                                   v
                          canonical/ extracts
        (title, summary, outline, takeaways, quotes, CTA, SEO, metadata)
                                   |
   +-----------+-----------+-------+-------+-----------+-----------+
   |           |           |               |           |           |
   v           v           v               v           v           v
  WEB      SOCIAL      EMAIL          VIDEO/AUDIO    SLIDES     PRINT &
                                                              GRAPHICS
```

## Source moment to asset

The chapter has a handful of strong raw materials. Each one feeds several assets.

| Raw material in the chapter | Becomes |
|---|---|
| The cabinet that went feral | Web landing intro, LinkedIn post, X thread 1, FB longform, YouTube cold open, podcast intro, before/after graphic, image prompt, quote card |
| The 6S Loop (six nodes, handoffs) | Hero infographic, carousel, teaching deck spine, the loop card resource, LinkedIn carousel |
| "6S is a loop, not a menu" / the handoffs | LinkedIn post, X post, newsletter hook, quote card, One Idea to Keep |
| Shine is inspection / the hidden leak | LinkedIn post, FB post, short video, the Shine close-up graphic, "your sponge found it for free" quote card, discussion question |
| Safety: crouch to a toddler's height | LinkedIn post, FB post, the Safety-swap graphic, the Quick Win CTA, short video, discussion question |
| Standardize: photo inside the door | LinkedIn post, X post, short video, the standardize graphic |
| Sustain: ten-second reset, loops to Sort | LinkedIn post, X post, quote card, the loop-closes graphic |
| Find the skipped step | LinkedIn post, X post, the diagnostic diagram, discussion question |
| The fifteen-minute first lap | Primary CTA everywhere, the lap short-video, the checklist, the One-Space Lap Sheet resource |

## One to many, by channel

| Canonical asset | Direct children |
|---|---|
| `chapter-summary.md` | ebook description, newsletter version, landing intro, podcast outline |
| `chapter-quotes.md` | 10 quote cards, X short posts, LinkedIn hooks, slide pull-quotes |
| `chapter-key-takeaways.md` | LinkedIn posts, carousel slides, teaching deck bullets, discussion questions |
| `chapter-outline.md` | YouTube script structure, podcast structure, teaching deck flow |
| `chapter-cta.md` | every soft CTA, the fifteen-minute-lap primary CTA, lead-magnet copy |
| `chapter-seo.md` | SEO titles, meta descriptions, schema keywords, landing page |
| `chapter-metadata.json` | schema.org Article, navigation copy, all attribution lines |

## Sequencing logic

1. Lock `canonical/` first. If the title, slug, or "One Idea to Keep" changes, it ripples everywhere.
2. Build `web/` next, because the chapter URL is the destination every soft CTA points to.
3. Then social and email, which drive traffic to that URL.
4. Video, audio, slides, and graphics are higher-effort and can trail the text assets by a few days.
5. The 6S Loop graphic and the fifteen-minute-lap CTA are the two highest-value assets. Seed the loop early and repeat the lap CTA wherever it fits.
