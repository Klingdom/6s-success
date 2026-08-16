# Repurposing Map: One Chapter Becomes Everything

This shows how the single chapter, "Define the Purpose of the Area", turns into every asset in the package. The chapter is the trunk. Everything else is a branch off it.

```
          CHAPTER 7: "Define the Purpose of the Area"
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
| Messy because it is failing to be any one thing | Web landing intro, LinkedIn post, X thread 1, FB longform, YouTube open, podcast open, quote card |
| The everything-space (five jobs at once) | The One Job Beats Five infographic, carousel, LinkedIn post, FB group post, short video |
| The one-job rule | LinkedIn post, X post, the definition box, quote card |
| The Purpose Statement template | Hero infographic, the worksheet resource, carousel, teaching deck, short video |
| A plain true sentence beats a vague pretty one | LinkedIn post, X post, quote card |
| Match it to your real life (not an ideal) | LinkedIn post, FB post, quote card, discussion question, the kindest-version angle |
| Purpose sets the limits / a bouncer at the door | LinkedIn post, X post, the limits diagram, discussion question |
| Write your purpose | Primary CTA everywhere, the write-it short video, the checklist |
| One Idea to Keep | Quote card, infographic footer, deck close, newsletter sign-off |

## One to many, by channel

| Canonical asset | Direct children |
|---|---|
| `chapter-summary.md` | ebook description, newsletter version, landing intro, podcast outline |
| `chapter-quotes.md` | 10 quote cards, X short posts, LinkedIn hooks, slide pull-quotes |
| `chapter-key-takeaways.md` | LinkedIn posts, carousel slides, teaching deck bullets, discussion questions |
| `chapter-outline.md` | YouTube script structure, podcast structure, teaching deck flow |
| `chapter-cta.md` | every soft CTA, the write-your-purpose primary CTA, lead-magnet copy |
| `chapter-seo.md` | SEO titles, meta descriptions, schema keywords, landing page |
| `chapter-metadata.json` | schema.org Article, navigation copy, all attribution lines |

## Sequencing logic

1. Lock `canonical/` first. If the title, slug, the Purpose Statement template, or "One Idea to Keep" changes, it ripples everywhere.
2. Build `web/` next, because the chapter URL is the destination every soft CTA points to.
3. Then social and email, which drive traffic to that URL.
4. Video, audio, slides, and graphics are higher-effort and can trail the text assets by a few days.
5. The Purpose Statement template and the "a space cannot be good at everything" hook are the two highest-value assets. Seed the template early and lead social with the counterintuitive hook.
