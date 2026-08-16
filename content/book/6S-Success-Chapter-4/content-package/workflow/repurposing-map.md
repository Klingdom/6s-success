# Repurposing Map: One Chapter Becomes Everything

This shows how the single chapter, "How to Choose Your First Target Area", turns into every asset in the package. The chapter is the trunk. Everything else is a branch off it.

```
        CHAPTER 4: "How to Choose Your First Target Area"
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
| The tempting garage (Saturday morning) | Web landing intro, LinkedIn post, X thread 1, FB longform, YouTube cold open, podcast intro, the garage og:image, image prompt, quote card |
| The First Target Map (friction vs effort) | Hero infographic, carousel spine, teaching deck, the worksheet resource, LinkedIn carousel |
| Proof, not the room / the win compounds | LinkedIn post, X post, newsletter hook, quote card |
| Guilt is a bad compass, friction is a good one | LinkedIn post, FB group post, quote card, discussion question, the compass diagram |
| Why not the garage | LinkedIn post, FB post, short video, X post, the garage-in-the-wrong-quadrant graphic |
| Win where you will see it (three filters) | LinkedIn post, short video, the daily-touch diagram, discussion question |
| The Target Scorecard (friction minus effort) | The scorecard infographic, carousel, the printable resource, X post |
| Write it down | Primary CTA everywhere, the write-it-down short video, the checklist |
| One Idea to Keep | Quote card, infographic footer, deck close, newsletter sign-off |

## One to many, by channel

| Canonical asset | Direct children |
|---|---|
| `chapter-summary.md` | ebook description, newsletter version, landing intro, podcast outline |
| `chapter-quotes.md` | 10 quote cards, X short posts, LinkedIn hooks, slide pull-quotes |
| `chapter-key-takeaways.md` | LinkedIn posts, carousel slides, teaching deck bullets, discussion questions |
| `chapter-outline.md` | YouTube script structure, podcast structure, teaching deck flow |
| `chapter-cta.md` | every soft CTA, the choose-your-target primary CTA, lead-magnet copy |
| `chapter-seo.md` | SEO titles, meta descriptions, schema keywords, landing page |
| `chapter-metadata.json` | schema.org Article, navigation copy, all attribution lines |

## Sequencing logic

1. Lock `canonical/` first. If the title, slug, or "One Idea to Keep" changes, it ripples everywhere.
2. Build `web/` next, because the chapter URL is the destination every soft CTA points to.
3. Then social and email, which drive traffic to that URL.
4. Video, audio, slides, and graphics are higher-effort and can trail the text assets by a few days.
5. The First Target Map and the "should you start with the garage" hook are the two highest-value assets. Seed the map early and lead social with the garage question.
