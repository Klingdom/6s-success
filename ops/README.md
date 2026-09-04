# ops/

Generators and the live dashboard. Nothing in here is hand-maintained output.

## Run order matters

`build_resources.py` rewrites `site/resources.html` from scratch, which strips the
SEO layer. `build_seo.py` re-applies that layer and is idempotent, so it must run
**after**:

```bash
python ops/build_resources.py   # rebuild the rooms page from content.json
python ops/build_seo.py         # re-apply canonical, OG, JSON-LD, sitemap
python ops/dashboard.py         # regenerate the dashboard last
```

Running `build_resources.py` alone silently drops the JSON-LD and Open Graph tags
from the rooms page. This happened once already.

`build_zone_pages.py` has the same trap one layer down and it is easy to miss,
because the script exits 0 either way. It rewrites all 134 room and zone pages
and chains eight wiring passes itself, but not `fingerprint_assets.py` and not
`build_pwa.py`, so running it alone leaves several hundred asset references
pointing at hashes the assets no longer carry, and `preflight.py` then fails
`fingerprints`, `image-coverage` and `nav-current` together. Measured
2026-09-03. The whole chain is:

```bash
python ops/build_zone_pages.py   # 20 room + 114 zone pages, ~8 minutes
python ops/build_seo.py          # canonical, OG, JSON-LD, robots, sitemap
python ops/fingerprint_assets.py # asset hashes the pages above just reset
python ops/build_pwa.py          # sw.js precache list, keyed on those hashes
```

Do not run any of it while `preflight.py` is running. `gate_tests` writes
fixture pages straight into `site/` and deletes them again, so a generator
globbing `site/**/*.html` at the wrong moment reads a file that no longer
exists and dies mid-chain. That happened on 2026-09-03 and left
`site/_audit_catalog_fixture.html` and `site/_gate_fixture_conflict.html`
sitting in the tree; neither is gitignored, unlike `_visual_probe.html`.

## Getting found: the two scripts that matter

Measured 2026-09-03: 52 visitors ever, one of them from a search engine.
Structured data, sitemap and robots.txt are all clean, so markup is not the
constraint. Being crawled at all is.

```bash
python ops/indexnow.py --status  # what has and has not been announced
python ops/indexnow.py --new     # announce only what has never been announced
python ops/build_seo.py          # emits ownership tags from site-verification.json
```

`indexnow.py` reaches Bing, Yandex, Seznam and Naver with no account at all.
It records every run in `ops/indexnow-log.json`, refuses to submit if the key
file is not live, and withholds any URL production answers with something other
than 200, because the sitemap is built from the repository and can list a page
that has not been deployed yet.

`site-verification.json` holds the Google, Bing, Pinterest and Yandex ownership
tokens. It is empty until Phil pastes one in (`OWNER-ACTIONS.md` item 1a), and
empty changes no byte of the site. Two preflight gates watch both:
`indexnow-current` warns about any sitemap URL never announced, and
`site-verification` fails if a token is set but the generator was never rerun.

## What each does

| Script | Writes | Reads |
|---|---|---|
| `dashboard.py` | `EXECUTIVE-DASHBOARD-LIVE.md`, `dashboard.html`, `state.json` | the repo, GitHub, `content/` |
| `build_resources.py` | `site/resources.html` | `content/manual/source/*.json`, `book_zone_names.json` |
| `build_seo.py` | SEO blocks in all `site/*.html`, `robots.txt`, `sitemap.xml` | the pages themselves |
| `build_epub.py` | `build/*.epub` | `content/book/` |
| `build_manual_print.py` | `content/manual/print/` | `content/manual/` |
| `build_zone_pages.py` | `site/rooms/*.html`, `site/zones/*.html` | `content/manual/source/content.json` |
| `canonical_links.py` | internal links in `site/**` | the pages' own canonical tags |
| `indexnow.py` | `ops/indexnow-log.json`, the key file in `site/` | `site/sitemap.xml`, production |

## Rules for anything added here

- **Never read an absolute local path.** The nightly agent runs in the cloud with
  only a git checkout. A Desktop path silently produces zeros there.
- **Never let a failed lookup render as a confident zero.** Distinguish UNKNOWN
  from none. A dashboard that reports "0 open P0" during an API outage is worse
  than one that reports nothing.
- **Never count something the repo deliberately excludes.** Card art is
  gitignored, so counting it reports a false zero rather than the truth.
