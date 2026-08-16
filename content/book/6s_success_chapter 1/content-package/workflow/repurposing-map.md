# Repurposing Map: One Chapter Becomes Everything

This shows how the single chapter, "Why Some Homes Feel Effortless", turns into every asset in the package. The chapter is the trunk. Everything else is a branch off it.

```
                  CHAPTER 1: "Why Some Homes Feel Effortless"
                          (final HTML, canonical)
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
| The two Tuesdays (7:55 vs 8:09) | Web landing intro, LinkedIn post 1, X thread post 1, FB longform, YouTube cold open, podcast intro, the two-Tuesdays infographic, image prompt, quote card |
| "Effortless is a system, not a personality" | LinkedIn post, X short post, newsletter hook, short-video, quote card, deck title slide |
| "Fewer decisions, not more discipline" | LinkedIn post, FB post, X post, quote card, comment prompt |
| How a junk drawer forms one "for now" at a time | LinkedIn post, FB post, the junk-drawer-stages diagram, short-video, quote card |
| Cleaning vs organizing vs 6S | Pull quote, the shelf-life bars diagram, carousel slides, X posts, FAQ block |
| The six S's loop | Six-S loop diagram, carousel, teaching deck, Family Challenge post |
| Friction (the find-the-friction scene, 8 points) | The friction scene graphic, LinkedIn post, X posts, short-video, discussion question |
| "Rooms are not messy people" | LinkedIn post, FB group post, quote card, discussion question |
| The honest before photo (first move) | Primary CTA everywhere, the before-photo short-video, checklist, FB group post |
| One Idea to Keep | Quote card, infographic footer, deck close, newsletter sign-off |

## One to many, by channel

| Canonical asset | Direct children |
|---|---|
| `chapter-summary.md` | ebook description, newsletter version, landing intro, podcast outline |
| `chapter-quotes.md` | 10 quote cards, X short posts, LinkedIn hooks, slide pull-quotes |
| `chapter-key-takeaways.md` | LinkedIn posts, carousel slides, teaching deck bullets, discussion questions |
| `chapter-outline.md` | YouTube script structure, podcast structure, teaching deck flow |
| `chapter-cta.md` | every soft CTA, the before-photo primary CTA, lead-magnet copy |
| `chapter-seo.md` | SEO titles, meta descriptions, schema keywords, landing page |
| `chapter-metadata.json` | schema.org Article, navigation copy, all attribution lines |

## Sequencing logic

1. Lock `canonical/` first. If the title, slug, or "One Idea to Keep" changes, it ripples everywhere.
2. Build `web/` next, because the chapter URL is the destination every soft CTA points to.
3. Then social and email, which drive traffic to that URL.
4. Video, audio, slides, and graphics are higher-effort and can trail the text assets by a few days.
5. The before-photo CTA is the hero action for this chapter. Make sure it appears clearly in the highest-traffic assets.
