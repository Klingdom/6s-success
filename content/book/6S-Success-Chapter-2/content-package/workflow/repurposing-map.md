# Repurposing Map: One Chapter Becomes Everything

This shows how the single chapter, "What Is 6S?", turns into every asset in the package. The chapter is the trunk. Everything else is a branch off it.

```
                         CHAPTER 2: "What Is 6S?"
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
| The bottle-opener drawer scene | Web landing intro, Facebook longform, X thread post 1, YouTube cold open, podcast intro, infographic hero, image prompt 1, quote cards |
| "Findability, not tidiness" | LinkedIn post, X short post, newsletter teaser, short-video script, quote card |
| The Toyota / postwar origin | LinkedIn post, FB post, X thread, podcast segment, the "Factory Floor to Front Hall" diagram, slide 3 |
| The five Japanese words mapped to English | Bilingual mapping diagram, carousel slides, teaching deck, X short posts, quote card on "the words are handles" |
| How 5S became 6S (Safety) | LinkedIn post, FB post, the Quick Win safety walk (secondary CTA), short-video, "5S + Safety = 6S" diagram |
| "Borrow the logic, not the look" | LinkedIn post, FB longform, newsletter, factory-vs-counter diagram, quote card |
| "One method, any size" | LinkedIn post, X post, scale-targets diagram, slide, podcast aside |
| The one-sentence definition | Meta description, schema headline, quote card, infographic footer, deck closing slide |
| "Your home has you" (Safety) | FB group post, X post, discussion question, quote card |

## One to many, by channel

| Canonical asset | Direct children |
|---|---|
| `chapter-summary.md` | ebook description, newsletter version, landing intro, podcast outline |
| `chapter-quotes.md` | 10 quote cards, X short posts, LinkedIn hooks, slide pull-quotes |
| `chapter-key-takeaways.md` | LinkedIn posts, carousel slides, teaching deck bullets, discussion questions |
| `chapter-outline.md` | YouTube script structure, podcast structure, teaching deck flow |
| `chapter-cta.md` | every soft CTA across social, the two book CTAs, lead-magnet copy |
| `chapter-seo.md` | SEO title options, meta descriptions, schema keywords, landing page |
| `chapter-metadata.json` | schema.org Article, navigation copy, all attribution lines |

## Sequencing logic

1. Lock `canonical/` first. If the title, slug, or definition changes, it ripples everywhere.
2. Build `web/` next, because the chapter URL is the destination every soft CTA points to.
3. Then social and email, which drive traffic to that URL.
4. Video, audio, slides, and graphics are higher-effort and can trail the text assets by a few days.
5. Quote cards and diagrams are the easiest wins to seed across the 14 days.
