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

## What each does

| Script | Writes | Reads |
|---|---|---|
| `dashboard.py` | `EXECUTIVE-DASHBOARD-LIVE.md`, `dashboard.html`, `state.json` | the repo, GitHub, `content/` |
| `build_resources.py` | `site/resources.html` | `content/manual/source/*.json`, `book_zone_names.json` |
| `build_seo.py` | SEO blocks in all `site/*.html`, `robots.txt`, `sitemap.xml` | the pages themselves |
| `build_epub.py` | `build/*.epub` | `content/book/` |
| `build_manual_print.py` | `content/manual/print/` | `content/manual/` |

## Rules for anything added here

- **Never read an absolute local path.** The nightly agent runs in the cloud with
  only a git checkout. A Desktop path silently produces zeros there.
- **Never let a failed lookup render as a confident zero.** Distinguish UNKNOWN
  from none. A dashboard that reports "0 open P0" during an API outage is worse
  than one that reports nothing.
- **Never count something the repo deliberately excludes.** Card art is
  gitignored, so counting it reports a false zero rather than the truth.
