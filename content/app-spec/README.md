# 6S Home Reset — Product Specification & Store Release Plan (rebuilt)

An improved rebuild of the uploaded `6S Home Reset Product Specification.pdf`, now with **Part III: MVP Beta Build Plan**. 2026-07-22.

## Visual product roadmap

`roadmap/6S Home Micro Zones - Product Roadmap.html` is a one-page visual roadmap: a seven-phase timeline (Phase 0 the verified prototype through Phase 6 growth) with a "you are here" marker, phase cards with milestones, a workstream swimlane grid (Core app / AI / Data / Privacy / Growth across the phases), a deferred-beyond-v1.0 rail, and the roadmap principles. Built from this spec, the MVP beta plan, and the review panel. Durations are planning estimates.

## Latest update: Part IV (Usability, Data & Visualization)

A seven-discipline panel (product, QA, front-end, back-end, marketing, customer success, support) reviewed the running MVP and this spec and produced 59 findings (27 high-severity). Their synthesis is a new **Part IV: Usability, Data & Visualization** (6 sections): usability improvements, a data-collection plan (on-device loop instrumentation + a health/reliability event family), user-facing and team-facing visualization (five discipline dashboards on one shared pipeline), corrections to earlier parts, and a tiered do-next list. The full panel report is in `review-panel/`. The document is now **42 sections across four parts, 25 marked *new***.

Headline the panel converged on: the beta emits **zero analytics events**, never shows the **before/after transformation**, and keeps **AI unreachable to testers** — instrument the loop, show the change, and turn AI on, or the beta demos without learning. The panel also caught a real build bug: the app's "items released" stat sums relocate too (should be donate + discard only).

## Part III (MVP Beta)

Four parallel code-analysis subagents inspected the v2.4 app (`6s-home-reset-app-v2.jsx`), and their findings became a new **Part III: MVP Beta Build Plan** (9 sections) preparing the app now provisionally titled **6S Success Home Micro Zones: Organization & Housekeeping** (store listing) / **6S Home Reset** (short app name). Part III covers: MVP scope and the cut line, what the code confirmed and corrected, the two decoupling workstreams (device storage + AI proxy), the port plan and module structure, a build-ready feature backlog, beta compliance and privacy gates, acceptance criteria, the beta test plan and timeline, and an explicitly-deferred list. See `analysis/README.md` for the code-analysis findings behind it. The document is now 36 sections across three parts, 19 marked *new*.


## What this is

A redesigned, navigable version of your two-part product plan for the **6S Home Reset** app. Part I documents the validated v2.4 Claude-artifact build; Part II is the committed App Store / Google Play release scope. The content is preserved and extended; the layout is rebuilt in the 6S Success book design system so it matches the manual, the video plan, and the appendices.

## Contents

| File | What it is |
|---|---|
| `6S Home Reset - Product Specification and Store Release Plan.html` | The document. Open in a browser. Sticky sidebar table of contents with scroll-spy, grouped Overview / Part I / Part II. |
| `6S Home Reset - Product Specification and Store Release Plan.pdf` | Print rendering (sidebar hidden, single column). |
| `review/validation-report.txt` | Gate output, all passing. |
| `source/` | The rebuild pipeline: PDF text extraction, cleanup, collect, build, validate, plus `spec.json` (the content as data) and `spec_source.txt` (the cleaned original text). |

## What changed

**Layout.** The original was a working-draft PDF (and a plain Arial/navy library export). This rebuild is in the book design system (Fraunces / Newsreader, terracotta, warm paper), with a grouped sidebar TOC, scroll-spy highlighting, a headline stat band, readable tables, and callouts. It reads as part of the same product family as the book, manual, and video materials.

**Content: everything preserved, plus 10 new sections** (marked *new* in the TOC), addressing the gaps in the original:

- **Executive Summary** — a front-page framing the whole document.
- **Pricing & Packaging** — concrete tier structure (Free / 6S Plus monthly + annual / Household / future Pro). Every price is labeled a recommendation to validate.
- **Go-to-Market & the Content Funnel** — the acquisition story the original lacked, built on your own ecosystem: the 114-episode / 684-Short video series maps one-to-one onto the app's 114 zones, so each Short funnels to that zone in the app; the book and manual are top-of-funnel and credibility.
- **Competitive Landscape & Moat** — the real category (Sortly, Tody, Home Routines, checklist/habit apps) and the durable differentiator (a professional SOP + AI plans from the user's own photos + three-way sourced products).
- **Backend Data Model** — a proposed entity model (household, member, room, zone, progress, photo, catalog, product, subscription, AI usage) with ownership and row-level-security rules.
- **Accessibility** — VoiceOver/TalkBack, Dynamic Type, contrast beyond the step colors, tap targets, reduced motion.
- **Localization & International** — US-first retailers/catalog, metric/imperial units, language, phased expansion.
- **Analytics & Instrumentation** — a privacy-respecting event taxonomy traced to the success metrics.
- **Unit Economics** — a per-activated-user revenue/cost sketch, all figures marked illustrative assumptions to validate.
- **Explicitly Deferred** — a clear v1.0 scope line (Pro tier, web app, AI vision v2, non-US markets).

## Honest notes

- **The rebuild was reconstructed from the PDF's extracted text**, since no HTML source was uploaded. The extraction had font-encoding artifacts; these were decoded to clean text, but a pass against your original source is worth doing to confirm no fact was mis-transcribed. All original numbers (114 zones, 684 activities, 97 products, 291 picks, ~98h, phase durations, targets) were carried through deliberately.
- **Every price, cost, and conversion figure introduced in the new sections is flagged as a recommendation or illustrative assumption**, not a decided fact. A validation gate enforces that no such figure is stated as fact. Store fees, testing gates, and AI pricing must be re-verified at build/submission time.
- **Brand alignment note:** the original app spec declared the old navy Field-Manual identity; this rebuild restates the design system as the current book system (terracotta/Fraunces) for ecosystem consistency. If the app itself is meant to keep the navy identity, tell me and I will realign.
- Reviewed by spot-checking the rendered document, not by reading all 27 sections line by line.

## Relationship to the other product docs

This supersedes the plain `..._Current_State_Specification.html` export as the human-facing spec. The product **library** appendices (Appendix A and B, in the Micro Zone Manual package) remain the catalog reference and sourcing sheet; this document is the app product plan that consumes that catalog.

## Rebuilding

From `source/`: `pdf_text.py` (extract) → `clean_spec.py` (decode artifacts) → *(workflow authors sections)* → `collect_spec.py` → `build_spec.py` → `validate_spec.py`. Edit `spec.json` and re-run `build_spec.py` + `validate_spec.py` to revise without re-running agents. Paths are absolute to this session.
