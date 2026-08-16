# Repurposing Map: One Chapter Becomes Everything

This shows how the single chapter, "The 6S Home Audit", turns into every asset in the package. The chapter is the trunk. Everything else is a branch off it.

```
              CHAPTER 5: "The 6S Home Audit"
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
| The audit as a flashlight, not a grade | Web landing intro, LinkedIn post, X thread 1, FB longform, YouTube open, podcast open, quote card |
| The 6S Snapshot (six-axis radar) | Hero infographic, carousel spine, teaching deck, the Snapshot card resource, LinkedIn carousel |
| Measure before you move / fixing the wrong thing | LinkedIn post, X post, newsletter hook, quote card, the before/after diagram |
| The six questions | The scorecard infographic, carousel, the Home 6S Audit Form resource, X posts, discussion questions |
| Reading the shape (buried, homeless, drifted) | The three-shapes diagram, LinkedIn post, short video, deck |
| A low score is good news | LinkedIn post, FB post, short video, quote card, the most shareable hook |
| The worked drop-zone example (14/30) | The scorecard graphic, the radar graphic, the article, the podcast |
| Take your baseline | Primary CTA everywhere, the baseline short video, the checklist |
| One Idea to Keep | Quote card, infographic footer, deck close, newsletter sign-off |

## One to many, by channel

| Canonical asset | Direct children |
|---|---|
| `chapter-summary.md` | ebook description, newsletter version, landing intro, podcast outline |
| `chapter-quotes.md` | 10 quote cards, X short posts, LinkedIn hooks, slide pull-quotes |
| `chapter-key-takeaways.md` | LinkedIn posts, carousel slides, teaching deck bullets, discussion questions |
| `chapter-outline.md` | YouTube script structure, podcast structure, teaching deck flow |
| `chapter-cta.md` | every soft CTA, the take-your-baseline primary CTA, lead-magnet copy |
| `chapter-seo.md` | SEO titles, meta descriptions, schema keywords, landing page |
| `chapter-metadata.json` | schema.org Article, navigation copy, all attribution lines |

## Sequencing logic

1. Lock `canonical/` first. If the title, slug, the six questions, or "One Idea to Keep" changes, it ripples everywhere.
2. Build `web/` next, because the chapter URL is the destination every soft CTA points to.
3. Then social and email, which drive traffic to that URL.
4. Video, audio, slides, and graphics are higher-effort and can trail the text assets by a few days.
5. The 6S Snapshot radar and the "a low score is good news" hook are the two highest-value assets. Seed the radar early and lead social with the counterintuitive hook.
