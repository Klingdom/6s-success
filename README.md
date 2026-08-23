# 6S Success

**[6s-success.com](https://6s-success.com)** — a method for making a home work
better, one micro zone at a time.

Most organising advice starts with storage. This starts with function: what do
you want this space to do, what stops it doing that, and what is the smallest
change that fixes the cause rather than the symptom. Then it writes down the
standard, so the room does not quietly revert.

## The method

Six passes, taken in order, on one small zone at a time:

**Sort** what stays &middot; **Straighten** so what stayed has a reachable home
&middot; **Shine**, and read what the cleaning tells you &middot; **Safety**,
because a tidy room is not automatically a safe one &middot; **Standardize**,
writing down what good looks like &middot; **Sustain**, by attaching the reset
to something that already happens.

Safety is the fourth S, not an afterthought bolted onto the end.

The unit of work is the **micro zone**: the drop zone by the door, the medicine
cabinet, the under-sink cupboard. Small enough to finish in one sitting, and
specific enough to diagnose. Twenty rooms, 114 micro zones.

## Free things, no account needed

| | |
|---|---|
| [The Standards Pack](https://6s-success.com/standards.html) | One page per room. What each zone holds to, and the moment that triggers the reset. Print and post it. |
| [The Entryway Deck](https://6s-success.com/deck.html) | 46 cards taking one entryway through all six passes. Prints nine to a page. |
| [The Home Quest](https://6s-success.com/quest.html) | The whole method as a web app. Draw a card, do one job, put it down. |
| [Rooms and micro zones](https://6s-success.com/resources.html) | All 114 zones, each with the six passes written out. |

## What is in this repository

The site, the content pipeline, and the operations that run the business.

| Path | |
|---|---|
| `site/` | The static site, served by nginx in Docker |
| `content/manual/` | The Micro Zone Manual, and `source/content.json`, which is the spine every product is generated from |
| `ops/` | Build, audit, analytics, fulfilment and reporting scripts |
| `CLAUDE.md` | The operating rules this project runs under |

Everything the site sells is generated from `content/manual/source/content.json`,
so the book, the cards, the zone pages and the app cannot disagree with each
other about what a zone is.

## Running it

```
python ops/build_zone_pages.py      # 20 room pages, 114 zone pages
python ops/build_seo.py             # sitemap and robots
python ops/fingerprint_assets.py    # content hashes on css and js
python ops/audit_pages.py           # titles, descriptions, headings, links, alt text
```

The image is built and published by `.github/workflows/publish-image.yml`.

## Licence

The code here is available to read and learn from. The written content, the
card decks, the book and the artwork are not licensed for redistribution.
