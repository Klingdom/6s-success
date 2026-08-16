# Repurposing Map: One Chapter Becomes Everything

This shows how the single chapter, "Photograph Before You Fix", turns into every asset in the package. The chapter is the trunk. Everything else is a branch off it.

```
            CHAPTER 6: "Photograph Before You Fix"
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
| Habituation (the pile you cannot see anymore) | Web landing intro, LinkedIn post, X thread 1, FB longform, YouTube open, podcast open, quote card |
| The Eye vs the Camera | Hero infographic, carousel spine, teaching deck, the standalone camera-side social graphic, LinkedIn carousel |
| The before is for the after | LinkedIn post, X post, newsletter hook, quote card, the before/after graphic |
| The embarrassing before is the valuable one | LinkedIn post, FB post, short video, quote card, the most shareable hook |
| The matched pair (same spot, mark it) | The Matched Pair diagram, carousel, the Before and After Photo Guide resource, short video, X posts |
| Do not tidy first | LinkedIn post, FB post, short video, quote card, discussion question |
| Keep it private if you wish | FB group post, LinkedIn post, discussion question (privacy angle) |
| Take the before photo | Primary CTA everywhere, the take-the-photo short video, the checklist |
| One Idea to Keep | Quote card, infographic footer, deck close, newsletter sign-off |

## One to many, by channel

| Canonical asset | Direct children |
|---|---|
| `chapter-summary.md` | ebook description, newsletter version, landing intro, podcast outline |
| `chapter-quotes.md` | 10 quote cards, X short posts, LinkedIn hooks, slide pull-quotes |
| `chapter-key-takeaways.md` | LinkedIn posts, carousel slides, teaching deck bullets, discussion questions |
| `chapter-outline.md` | YouTube script structure, podcast structure, teaching deck flow |
| `chapter-cta.md` | every soft CTA, the take-the-before-photo primary CTA, lead-magnet copy |
| `chapter-seo.md` | SEO titles, meta descriptions, schema keywords, landing page |
| `chapter-metadata.json` | schema.org Article, navigation copy, all attribution lines |

## Sequencing logic

1. Lock `canonical/` first. If the title, slug, or "One Idea to Keep" changes, it ripples everywhere.
2. Build `web/` next, because the chapter URL is the destination every soft CTA points to.
3. Then social and email, which drive traffic to that URL.
4. Video, audio, slides, and graphics are higher-effort and can trail the text assets by a few days.
5. The Eye vs the Camera split and the "embarrassing before is the valuable one" hook are the two highest-value assets. Seed the split early and lead social with the counterintuitive hook.
