# Nightly log

One entry per unattended pass, newest first. Written to be read half awake.
Under 200 words each. Failures recorded as plainly as wins.

---

## 2026-08-16 (setup pass, run by Claude with Phil awake)

**Did:** Closed the website half of the P0 list. Built privacy, terms,
accessibility and safety-notice pages and wired them into all 13 pages, taking
dead links from 24 to 0. Injected the safety disclaimer estate-wide: 50/50
chapters, the Field Manual, decks, board games, appendix and app. Corrected the
chapter count from thirty to fifty and relabelled the download, which claims to
be the complete book but is chapters 1 to 30.

**Verified:** Served the site locally and loaded every new page in a browser.
Confirmed Fraunces 600 now loads as a real weight, and that the site makes zero
third-party requests.

**Found:** The site had the same faux-bold bug the book had, 22 font rules all
pointing at eight weight-400 files. Fixed by installing the 14 missing weights.
`invest.html` was the only page still calling a font CDN, which leaked visitor
IPs to Google. Now self-hosted.

**Next:** The nightly loop cannot start until the GitHub account is connected
for cloud routines. See `LOOP.md`. After that, the money path: connect the nine
dead forms to an email service.

---

## 2026-08-17 (money-path pass)

**Did:** Gave the book an exit door. It contained zero URLs and zero mentions of
6s-success.com across all 50 manuscripts and all 50 chapter HTML files, so
233,000 words of demand generation sent the reader nowhere. Built
`site/resources.html`, generated from the same 114-zone source the book uses, one
anchor per room, then added a companion link to all 50 chapters pointing at their
own room's anchor. Method chapters point at the page root.

**Verified:** 20 sections, 20 table-of-contents links, all resolving. Rendered in
a browser. Zero em or en dashes in the page or in any of the 50 inserted blocks.
Spot-checked anchors for chapters 12, 31, 45 and 50.

**Found and fixed two things that would have shipped broken.** The page used the
Manual's zone names, but the book renames seven zones, so a reader holding both
would have seen two names for one zone. It now reads names from the chapter
manuscripts. And nginx used `try_files $uri $uri/`, which would have 404'd the
short `/resources` URL printed in all 50 chapters. Now tries `$uri.html`.

**Next:** Still no email capture, so the resources page cannot convert a reader
into a contact. That is the next money-path step and it needs an email provider
account.

---

## 2026-08-17 (four-agent parallel pass)

**Did:** Ran four specialist agents on disjoint paths. Shipped an **EPUB** of all
50 chapters (0.67 MB, deterministic, 55 spine items, 0 dashes, all 50 safety
notices intact) and reconstructed **Chapter 1's missing manuscript**, the one
chapter that could not previously be rebuilt from source. Prepared the **Micro
Zone Manual for print** at 7x10 with real print CSS and rebuilt its appendix from
97 to the current 123 product types. Wrote **7 missing control documents** and
proved 8 others were redundant rather than writing them. Ran an **SEO pass**:
robots, sitemap, canonicals, 18 valid JSON-LD blocks, and the rooms page went
from 13 inbound links to 66.

**Verified:** 14/14 pages return 200, 18/18 JSON-LD blocks parse, 0 em and 0 en
dashes across the site, EPUB zip structure checked independently of the agent
that built it.

**Found:** The SEO agent removed a **fabricated testimonial** ("Dana R.") and two
unsupported badges ("Bestseller", "Most popular") from the live site. It also
found `--rule`, a CSS variable used by five pages but never defined, so those
borders silently never rendered.

**The uncomfortable one:** the control layer carries **457 em dashes and 42 en
dashes** across 65 files while the published site carries zero. The documents
that enforce the house style are the only ones breaking it, and agents read them
as authority. Now measured on the dashboard.

**Next:** money path still blocked on an email provider. GitHub connection still
500s, so the nightly loop cannot be created yet.

---

## 2026-08-17 (cover and packaging pass)

**Did:** Finished the half-built cover work the previous pass left in the tree.
The EPUB now carries a cover: `ops/build_cover.py` generates a 1600x2560
typographic cover from the book's own design system, and `ops/build_epub.py`
embeds it as the first spine item with both the EPUB 3 `cover-image` property and
the EPUB 2 `meta name="cover"` that KDP and Kobo still read. Rebuilt: 32 of 32
gates pass, 56 spine items, zero em and en dashes. Also ran the Micro Zone Manual
gates after the print work: all pass, 20 rooms, 114 zones.

**Verified:** Opened the zip independently of the builder and confirmed the cover
image, the cover page and all four OPF declarations. Rendered the cover and
looked at it.

**Found and fixed three things.** The tree did not build at all: the cover code
referenced `ROOT`, which does not exist in that file. The cover used the general
palette rather than the site's per-S ramp, so **Safety was blue on the cover and
amber everywhere else**. And the dashboard's "can the site take money" was
`... and False`, a hardcoded NO wearing the costume of a measurement, which would
have kept saying NO on the day a checkout went live. It now looks for a real
payment processor.

**New on the dashboard:** a "Book, sellable?" row. It reads **NO**. The manuscript
is finished and packaged, but 13 front-matter fields are still bracketed, so
there is no byline and no copyright holder. That is issue #3, and it is the only
thing between the book and a retailer.

**Next:** money path unchanged, still no email capture and no processor.
