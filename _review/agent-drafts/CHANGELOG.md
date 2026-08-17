# 6S Success Changelog

> Concise, human readable history of what changed in 6S Success and what it meant. Newest first. Not a commit dump, and not a work diary.

## 1. Purpose

`CHANGELOG.md` answers one question quickly:

> What changed, when, and why should anyone care?

It is the readable layer above three things that already exist and are not readable:

| Source | What it holds | Why it is not enough |
|---|---|---|
| Git history | Every commit | Terse, granular, no business meaning |
| `RELEASES.md` | How a change becomes a verified release | Policy, not history |
| `ops/NIGHTLY-LOG.md` | Narrative of each unattended pass | A work diary, including work that shipped nothing |

Read with:

- `RELEASES.md`, which defines release identity and specifies the categories used below
- `DECISIONS.md` for why a change was chosen
- `INCIDENTS.md` for changes made under pressure
- `EXECUTIVE-DASHBOARD-LIVE.md` for current measured state

If a referenced file does not exist yet, do not invent its contents.

---

# 2. Core Rules

**One entry per meaningful change, not per commit.**

**Every entry states the customer or business consequence.** "Added resources.html" is a commit message. "The book now has an exit door" is a changelog entry.

**Never restate an entry.** Correct it in place with a note, or add a new entry.

**Do not claim a deployment that was not verified.** Building a page and serving it locally is not a release. Where deployment state is unverified, the entry says so.

---

# 3. Entry Format

```markdown
## YYYY-MM-DD  release_id (if released)

Short sentence on what this change was for.

**Added** ...
**Changed** ...
**Fixed** ...
**Performance** ...
**SEO/AEO** ...
**Commerce** ...
**Infrastructure** ...
**Security** ...

Deployed: yes with image digest, no, or UNVERIFIED.
```

Categories come from `RELEASES.md` section 22. Omit any category with nothing in it.

Release identity, when a release actually occurs, follows `RELEASES.md` section 4: `rel-YYYY-MM-DD-NNN`, with the commit SHA and the image digest, because a mutable `latest` tag is not proof of what is running.

---

# 4. History Before 2026-08-16

**UNKNOWN in detail, and not reconstructed here.**

The repository contains 16 commits in total, 10 of them in the seven days to 2026-08-17, per `ops/state.json`. File timestamps place the initial website build and the Docker and Traefik infrastructure in late July 2026.

Reconstructing that period would require reading `git log`, which has not been done. If it is worth having, generate it from the log rather than from memory, and mark it clearly as reconstructed.

Entries below start where written evidence starts.

---

# 5. Changelog

## 2026-08-17

Gave the book somewhere to send its readers.

**Added** `site/resources.html`, generated from the same 114 zone source the book uses, with one anchor per room, and a companion link inserted into all 50 chapters pointing at that chapter's own room anchor. Method chapters point at the page root.

**Fixed** The resources page originally used the Micro Zone Manual's zone names, but the book renames seven zones, so a reader holding both would have seen two names for one zone. Zone names now come from the chapter manuscripts.

**Fixed** nginx used `try_files $uri $uri/`, which would have returned 404 for the short `/resources` URL printed in all 50 chapters. It now tries `$uri.html` first.

**Why it mattered** Across 50 manuscripts and 50 chapter HTML files the book contained zero URLs and zero mentions of 6s-success.com. Roughly 233,000 words of demand generation sent the reader nowhere.

Verified: 20 sections and 20 table of contents links resolving, rendered in a browser, anchors spot checked for chapters 12, 31, 45 and 50, zero em or en dashes in the page or in any of the 50 inserted blocks.

Deployed: UNVERIFIED.

Source: `ops/NIGHTLY-LOG.md`.

---

## 2026-08-16

Closed the website half of the P0 list, and split the repository.

**Added** Four legal and safety pages: privacy, terms, accessibility, and the safety notice, wired into all 13 pages then live.

**Added** The safety disclaimer across the estate: 50 of 50 book chapters, the field manual, the decks, the board games, the product appendix, and the app material. Before this date no disclaimer existed anywhere.

**Changed** The website moved from the repository root into `site/`, with the infrastructure files staying at the root. The `Dockerfile` now copies `site/` and nothing else.

**Changed** The repository became private.

**Changed** The stated chapter count corrected from thirty to fifty, and the book download relabelled, because the file offered as the complete book contains chapters 1 to 30.

**Fixed** Dead links reduced from 24 to 0.

**Fixed** The site carried the same faux bold defect the book had: 22 font rules pointing at eight weight 400 files. The 14 missing weights were installed, so Fraunces 600 now loads as a real weight.

**Security** `invest.html` was the last page calling a font CDN, which disclosed visitor IP addresses to a third party. Fonts are now entirely self hosted and the site makes zero third party requests, which is what `site/privacy.html` promises.

**Infrastructure** The autonomous operating system was installed into this repository: 39 control documents at the root, 14 agent definitions, and 22 super prompts. See `_review/INSTALL-NOTES.md`.

**Known consequence, still open** Making the repository private broke the VPS's ability to pull it. A deploy key or a read only token is required before the next deploy. Tracked as GitHub issue #10 and `RISK-0002`.

Verified: the site was served locally and every new page loaded in a browser.

Deployed: UNVERIFIED.

Sources: `ops/NIGHTLY-LOG.md`, `DEPLOY.md`, `_review/INSTALL-NOTES.md`, `site/disclaimer.html`.

---

# 6. What Does Not Belong Here

- individual commits
- work that shipped nothing, which belongs in `ops/NIGHTLY-LOG.md`
- decisions and their reasoning, which belong in `DECISIONS.md`
- incident narratives, which belong in `INCIDENTS.md`
- plans and intentions, which belong in `ROADMAP.md` and `BACKLOG.md`

A changelog describes what is now true that was not true before.

---

# 7. Maintenance

Append a new entry when a change is released, or when a material change is made that a future reader would otherwise have to excavate from the commit log.

The `github-manager` agent keeps this file coherent with releases and tags. It does not own the content: the agent that made the change writes the entry.

If this file ever falls behind, do not backfill it from memory. Generate from git and mark it reconstructed.

---

# 8. Final Note

Two entries is a short history, and the honest reason is that most of the work in this business has been authoring rather than shipping.

The entry this changelog is waiting for is the one that records a customer being able to pay.
