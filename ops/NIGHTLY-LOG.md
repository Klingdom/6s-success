# Nightly log

One entry per unattended pass, newest first. Written to be read half awake.
Under 200 words each. Failures recorded as plainly as wins.

---

## 2026-08-19 (autonomous operator pass)

**Did:** Checked out `main`, found it 44 commits behind origin, and
fast-forwarded. Deployment and email were settled or blocked on values only
Phil holds, and no open P0 issue was free of `decision` or `blocked-on-art`, so
worked EXP-102 from `EXPERIMENT-PLAN.md`: the homepage hero and closing CTA
both sent visitors to `shop.html`, where 34 of 41 SKUs are unavailable, while
consulting, the only thing bookable today, sat two sections down. Both CTAs
now point at `consulting.html`. Also fixed a duplicate trailing
`</body></html>` in `resources.html`, the page all 50 book chapters link to.

**Verified:** All four required gates pass (EPUB 32/32, manual gates all pass,
dash check clean, dashboard runs). Both edited files parse to exactly one
`</html>` each, site wide. Every internal href in the two touched pages
resolves against the filesystem.

**Went well:** Reading the two closed decision issues (#11, #13) before picking
work. Both had reopened and closed since the templated prompt was written, so
its own priority list was stale. Checking GitHub first avoided duplicating
finished work.

**Did not go well:** Nothing this pass; the tree was clean once fast-forwarded.

**Changing next cycle:** None needed yet; one instance of a habit paying off is
not a pattern.

**Next:** Widening checkout to the book and manual is blocked on issue #3,
front matter and counsel review. Real email capture is blocked on a Listmonk
list UUID only Phil holds. Both need him, not more engineering.

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

---

## 2026-08-17 17:54 (cycle 1 of the four-hour loop)

**Did:** Took the defect the last retro called "the uncomfortable one". The
control layer carried 483 em dashes and 53 en dashes while the published estate
carried zero, so the documents that tell every agent the house style were the
only ones breaking it, and agents read them as authority. Built
`ops/fix_dashes.py` and converted all 536 across 52 files. Also stood up the
four-hour cloud routine and gave the command deck a real redesign.

**Verified:** `python ops/fix_dashes.py --check` reports the control layer clean.
`git diff --numstat` shows 535 added and 535 removed with added equal to removed
in every file, so nothing but punctuation moved. Dashboard now measures 0 em, 0
en. Book gates 32 of 32, Manual gates all pass.

**Went well:** Previewing the substitution before applying it. The first pass
classified 10 conversions as prose commas. Reading all 10 showed every one was a
label the classifier had missed, not prose. Had that run unreviewed it would have
put commas in 10 places a colon belonged. Preview, sample, then apply is the
habit worth keeping.

**Did not go well:** The classifier needed three corrections found only by
reading output: list markers on identifier labels, emphasis that wraps the whole
line rather than the label, and table cells where a lone dash means not
applicable. Writing the rules from a sample of six examples was too few. Also
inherited a tree that did not build, because a previous pass left a `ROOT`
symbol referenced but never defined.

**Changing next cycle:** Never apply a bulk text transform without first printing
every case of the minority class. The majority class is where the confidence is
and the minority class is where the errors are. And run the build before starting
new work, not after, so an inherited breakage is found in the first minute.

**Next:** The money path is still the constraint and still needs an email
provider. Front matter (#3) is the cheapest revenue unblock and needs Phil.

---

## 2026-08-18 08:30 (loop repair, run from the desk)

**Did:** Found the four-hour loop had fired four times overnight and committed
nothing. Every run did good work and then hung. Root cause: step 6 told it to
republish the hosted command deck, and the Artifact tool needs an interactive
approval that a headless cloud session cannot grant. All four sat on that
permission prompt until the run was abandoned, so steps 7 and 8, the
retrospective and the commit, were never reached. Rewrote the routine prompt and
saved it to `ops/routine-prompt.md` so it is reviewable in the repository rather
than only in the cloud.

**Verified:** `RemoteTrigger list_runs` shows all four runs `requires_action`.
`git log HEAD..origin/main` is empty, confirming nothing was pushed. The 12:50
run log shows all four gates passing and a real site change made and tested in a
headless browser, then the hang.

**Went well:** The runs themselves were good. The 12:50 one ran every gate first,
found the tree clean, tested its change in a real browser with a screenshot,
caught its own em dash, and diffed the EPUB byte change down to the build
timestamp before accepting it. The nine-step prompt is working. It just could not
finish.

**Did not go well:** I wrote that step. I gave a headless agent an instruction
that requires a human to click. Four cycles of work lost to one line I did not
think through.

**Changing next cycle:** Before putting any tool call in an unattended prompt,
ask whether it can complete with nobody watching. Added step 0, attach to main,
because the checkout arrives detached, and told it plainly that gh is absent so
UNKNOWN issue counts are correct rather than a bug to chase.

**Next:** 6s-success.com serves a Hostinger parking page. Nothing built so far is
reachable by anyone. Deployment is now second in the priority list, behind only
the money path.

---

## 2026-08-18 09:06 (forms pass, run from the desk)

**Did:** Made all 14 site forms do something. The 13 footer newsletter forms
accepted an address, discarded it, and gave no feedback at all, which is the
worst option because the reader believes they subscribed. They now say the list
is not connected and hand over a prefilled message so the person can be added in
one click. The contact form showed "Thanks" for a message it threw away; it now
says plainly that nothing has been sent and packs the name, email, topic and
message into a mailto so one more click delivers it.

**Verified:** Drove both forms in a real browser. Empty, malformed and valid
paths on the newsletter; empty and filled on contact; confirmed the mailto
carries the typed name, address, topic and message with real line breaks, that
focus moves to the link, and that the page does not scroll sideways. All four
gates pass and the site carries zero em and en dashes.

**Went well:** Testing in a browser rather than reading the diff. Nothing else
would have found either defect below.

**Did not go well:** I shipped a syntax error. My escaped newlines became literal
ones, leaving an unterminated string that killed the whole inline script block on
contact.html, including the pre-existing product prefill that had nothing to do
with my change. I also wrote CSS that lost a specificity fight with
`.site-footer .brand-col p` and silently rendered at the wrong size, twice,
because my first fix was still one class too weak.

**Changing next cycle:** When generating code through a Python here-doc, write it
in a raw string. Both defects were invisible in the diff and obvious in the
browser within seconds.

**Next:** Deployment. The domain is still parked.

---

## 2026-08-18 10:05 (sample PDF pass, run from the desk)

**Did:** Cut the free sample PDF from 50.7 MB to 40.0 MB with no loss of quality,
and corrected a claim it was making about itself. Five images had been stored in
a lossless format built for line art rather than for photographs, costing 8.7 MB
between them; re-encoding at identical pixel dimensions reclaimed 7.4 MB. The
sample also called itself "The Complete Book" while holding chapters 1 to 30 of
50, in the PDF metadata and twice in the HTML twin. Fixed in all three.

**Verified:** Page count identical at 492. Text extraction identical across 15
sampled pages. All 173 images still present and decodable. Measured the pixel
difference on every converted image, worst case a mean of 2.09 out of 255, and
looked at that worst case side by side with the original: no visible difference.
Served the file and opened it in a browser, where it renders and reports the
corrected title.

**Went well:** Measuring before deciding. The instinct was to recompress
everything; measurement showed the 168 JPEGs would give back only 6 percent while
adding a generation of loss, so they were left alone. The whole win came from 5
files.

**Did not go well:** I nearly committed a 50 MB backup copy. The file is tracked,
so git history already holds the original and the backup was pure waste. Caught
it in git status, not by thinking.

**Changing next cycle:** Before writing a backup, ask whether version control
already holds it. Now gitignored and documented in the script.

**Next:** The sample is still 89 percent of the deployable site. Going below
40 MB trades image quality, which is a product call, so issue #14 puts the
measured options in front of Phil rather than degrading the product quietly.

---

## 2026-08-18 (autonomous operator pass)

**Did:** Checkout landed detached, five commits ahead of the branch. Fast
forwarded main and pushed; a fetch showed origin already had them, nothing lost,
only the local branch pointer was stale. Fixed a money path bug: the cart's
"Request invoice" button links to contact.html?ref=cart, but the prefill only
looked up a single SKU, so ref=cart matched nothing and handed the customer an
empty message box. A filled cart now arrives itemised with subtotal, and the
mailto carries the same detail. Also corrected two stale STATUS.md claims,
disconnected forms and unverified deploy, both fixed by earlier passes today.

**Verified:** Drove it in a headless browser: added two catalogue items, clicked
cart to contact, confirmed prefill and topic, submitted, checked the mailto body
matched. Confirmed single-SKU quote links still work and an empty cart leaves
the message blank. All four gates pass.

**Went well:** Verifying with a fetch instead of assuming the detached commits
needed rescuing, proving no harm was done rather than just hoping.

**Did not go well:** Close call: had those commits not been on origin, the
checkout warning was the only thing between real work and permanent loss.

**Changing next cycle:** When instructions name a specific failure mode, verify
the actual state rather than assume it does not apply this time.

**Next:** Deployment stays blocked on issue #13, a VPS deploy key, needing
Phil's hands on the host. Until then, audit the site for the same defect class:
a handoff that looks connected but does nothing.

---

## 2026-08-18 11:40 (mail credential and a pricing defect, run from the desk)

**Did:** Two things. Phil supplied an app password for support@6s-success.com, so
the morning brief is now delivered rather than fetched: `ops/mailer.py` sends as
support@, `ops/send_brief.py` renders `ops/state.json` as a plain text and html
email and refuses to send if that state is over 12 hours old. Then, verifying the
cloud run's cart handoff, found a pricing misrepresentation and fixed it.

**Verified:** Authenticated on 465 and 587, sent the brief to support@, then read
the mailbox back over IMAP and confirmed the delivered Message-ID matched the one
SMTP returned with both parts intact. For the cart, drove a four item order
through the browser and read what the customer would actually send.

**Found:** `Cart.add` stored `price: p.price || 0`, which turned a null price into
zero, and `money(0)` renders "Free". So a corporate consulting engagement was
being offered as **Free** in the cart, in the drawer, and in the email the
customer sends, while the subtotal silently excluded it. The catalogue has both a
genuinely free item and a quote only item, so the distinction is real and was
being destroyed on the way into storage. Quote items now read "price on request"
and totals say "plus items we quote".

**Went well:** Not trusting the cloud run's work because it was well written. It
was well written, and it faithfully carried a defect that predated it.

**Did not go well:** Chrome served a cached `site.js` for three test rounds and I
read "not a function" as my own bug before checking. Also spent two failed
attempts patching a file by exact string match when the escaping made it fragile.

**Changing next cycle:** Hard reload before concluding a change did not take, and
patch by line predicate rather than by long exact strings.

**Next:** The credential unlocks a real form endpoint on the VPS, which would
capture a list without any third party. Blocked on deployment, issue #13.

---

## 2026-08-18 12:00 (deploy pipeline, run from the desk)

**Did:** Answered "how do I connect Docker to the private GitHub repo" by
removing the question. The host now pulls a published image rather than cloning
source, so no deploy key sits on the VPS and no token gets pasted into the
Hostinger panel. Built the Action, the compose file to paste, `DEPLOY-VPS.md`,
and `ops/verify_deploy.py`. Generated two SSH keypairs so no private half ever
crosses a chat.

**Verified:** The image built and published on the second attempt. Confirmed by
querying the registry directly rather than trusting the green tick: an anonymous
pull returns 403, which proves the package is still private and is exactly the
one step the deploy doc says Phil must do.

**Went well:** Running the verifier against the live parked domain before
trusting it. It scored 7 of 10, passing every page and asset check while failing
the three that test reality. That is the proof the tool works: a status-code-only
checker would have called a parked domain a healthy website.

**Did not go well:** The first Action run failed. I wrote `cache-to: type=gha`
without `docker/setup-buildx-action`, so buildx ran on the default docker driver
which cannot export a cache. Written from memory rather than checked.

**Changing next cycle:** When writing CI from memory, run it before saying it is
ready. The feedback loop is 40 seconds and I skipped it.

**Next:** Three panel clicks are now the only thing between the estate and being
reachable, listed at the bottom of DEPLOY-VPS.md. Stripe cannot be wired until
the site is actually served.

---

## 2026-08-18 (DNS diagnosis, run from the desk)

**Did:** Phil reported nginx and umami were configured for the domain on the VPS.
Checked, and the domain never reaches the VPS at all. Added a Host header
override to `ops/verify_deploy.py` so a virtual host can be proved correct
against a raw IP before any DNS record is touched.

**Verified:** `6s-success.com` and `www` both resolve to `2.57.91.91`, which
returns the Hostinger parking page **even when sent `Host: 6s-success.com`**. The
nameservers are still `aster` and `helios.dns-parking.com`. So the domain is on
parking nameservers and no record points at the VPS. Whatever is configured there
is correct and unreachable.

**Also found:** Phil flipped the **repository** public, not the **package**. They
are separate settings. The anonymous image pull still returns 403, so the deploy
is still blocked, and meanwhile 3,554 files including all 50 unpublished book
chapters and the strategy documents became publicly readable. Raised with him
immediately. No credential was exposed: nothing key shaped is tracked and the
tracked `.env` holds only DOMAIN and ACME_EMAIL.

**Did not go well:** I broke `verify_deploy.py` twice while adding six lines to
it, both times because escaped newlines in a generated patch became literal ones.
**I wrote a retro rule about this exact defect one cycle ago and then repeated
it.** The file did not parse for three attempts.

**Changing next cycle:** The rule was right and I ignored it, so the rule is not
the fix. From now on, any generated Python patch is followed immediately by
`python -c "import ast; ast.parse(open(f).read())"` in the same command, so a
broken file cannot survive the tool call that created it.

**Next:** Still the VPS public IP. Nothing about deployment can proceed without it.

---

## 2026-08-18 (autonomous operator, second look)

**Did:** Started from a checkout 17 commits behind origin and spent the first
half of this pass reconciling `STATUS.md` against issues #11 and #13 before
noticing how much had moved. Committed that reconciliation, then a push
rejection revealed the real state: desk sessions had already shipped a whole
deploy pipeline (publish an image, VPS pulls it, no deploy key), fixed a cart
pricing bug, and rewritten `STATUS.md` twice since my read of the tree. My
commit would have reverted real progress, so it was discarded and the branch
reset to `origin/main` rather than merged blind.

**Verified:** `git fetch` plus a full read of the new commits, not just the
diff stat. All four gates still pass on the synced tree.

**Found:** Issue #13 still asked for a deploy key, superseded hours earlier by
`DEPLOY-VPS.md`. Left it open for the owner, but commented with the current
ask: make the ghcr.io package public, paste the compose file, and point DNS,
still on Hostinger's parking nameservers.

**Went well:** Checking `git fetch` before pushing what looked like finished
work. Discarding a completed commit is unusual, and correct here.

**Did not go well:** Re-derived state three concurrent passes had already
established, by reading issues before checking whether origin had moved.

**Changing next cycle:** Fetch and compare against origin before analysis,
not only before pushing. A checkout goes stale in the minutes it takes to
read five files.

**Next:** DNS and the VPS's public IP are the last blockers on deployment.
Nothing else moves until `6s-success.com` resolves to the VPS.

---

## 2026-08-18 (deployment, run from the desk)

**Did:** Got the real site running on the VPS. Made the container package public
via the GitHub UI, then found and fixed two silent faults in the Docker Manager
compose and redeployed.

**Verified:** `ops/verify_deploy.py` against the running container with a Host
override now passes **10 of 10**. All four of today's fixes are present in the
served JavaScript, the homepage carries zero em dashes, and unknown paths return
404. Ledgerium on 3000 and Compassion Benchmark on 8080 both confirmed untouched
before and after.

**Found:** The container was serving 6S Success, but not our build. The compose
said `image: 6s-success:latest` with no registry, so Docker used a stale local
image of that name and never contacted ghcr. A volumes entry also mounted a
local nginx conf over the one in our image, which is why unknown paths returned
200. Both were invisible from the panel: the container was green and the site
looked right.

**Went well:** Not trusting a green container. The deploy reported success, the
title said 6S Success, and it was still wrong. The recency markers caught it in
one command.

**Did not go well:** My own checker listed a page called `rooms` that this site
has never had, so it reported a deployment failure that was really a list bug.
The tool that exists to prevent false signals produced one.

**Changing next cycle:** Generate the page list from `site/*.html` rather than
typing it, so the checker cannot drift from the site it checks.

**Next:** One step left. Port 80 is owned by Nginx Proxy Manager and has no host
entry for the domain, so it still answers "Default Site". DNS has already moved
to 187.77.25.50.

---

## 2026-08-19 (catalog trust pass, autonomous operator)

**Did:** Checkout looked detached with 22 commits ahead of the branch again.
Fetched origin first this time: everything was already there, only the local
pointer was stale, so nothing needed rescuing. All four gates were clean on
arrival. This session has no VPS or Stripe access, so the two top priorities,
money path and deployment, could not be advanced; both need a desk session.
Found a catalog integrity gap instead: 34 of 41 shop items, 4 reset kits, 4
courses, 24 tools and supplies, both app tiers, showed "Add to cart" exactly
like the 7 real items, despite STRIPE.md and PRODUCT-CATALOG.md already
recording that none of them have a supplier, a build, or a platform behind
them. Two, a course and a reset kit, are featured on the homepage. Added
`available: false` to those 34 entries and changed the one shared render
function so unavailable items show "In development" and link to an honest
interest form instead of a cart. `Cart.add` now refuses them even if called
directly. Also fixed two pre-existing dash violations in the files touched.

**Verified:** All four gates pass. A Playwright sweep loaded all 14 site pages
with zero console or page errors. Confirmed real items still add to cart,
confirmed a forced add of an unavailable SKU is rejected, confirmed the
notify link prefills contact.html correctly.

**Went well:** One shared render function meant the fix reached shop, home,
book, method, and consulting pages from a single edit.

**Did not go well:** Wrote a JSON patch script against a guess of the file's
structure instead of reading its head and tail first, and it failed twice on
the same wrong assumption before I checked.

**Changing next cycle:** Read a file's actual boundaries before writing a
script that parses it.

**Next:** Money path and deployment both need a desk session: Stripe
authentication for issue-11-adjacent invoicing, and the Nginx Proxy Manager
host entry that was the last blocker recorded in the prior entry.

---

## 2026-08-19 (record correction pass, autonomous operator)

**Did:** Started clean: main attached, all four gates passed on arrival, no
open P0 issues that were not blocked-on-art or decision, so nothing in that
category could be worked. Read every remaining decision issue and DEPLOY-VPS.md
against the actual 2026-08-18 deployment record and found both were stale in a
way that would cost the next session real time: issue #13's own tracking
comment still said the package was private and DNS unmoved, both fixed hours
later the same day, and DEPLOY-VPS.md still listed those two steps plus DNS as
outstanding. STATUS.md's priority list also still asked for a URL in the book,
already present in all 50 chapters since 2026-08-16. Corrected all three from
the verified nightly log record, not fresh verification, since this session has
no VPS or DNS access.

**Verified:** All three doc gates (`build_epub.py`, `validate.py`,
`fix_dashes.py --check`) pass after the edits. Confirmed the book's companion
link and the resources.html anchors it points to actually match, all 20 rooms.
Ran a static internal-link check across all 14 site pages: 0 broken.

**Went well:** Reading a linked source document (DEPLOY-VPS.md) instead of
trusting STATUS.md's summary of it surfaced a second stale document, not just
one.

**Did not go well:** Spent a long stretch confirming several things were
already fine, which is time not spent on new work, though it did find the two
real staleness defects.

**Changing next cycle:** When the top two priorities are both access-blocked
and no P0 issue is open, check operating docs against ops/NIGHTLY-LOG.md for
drift before searching for new content work. That is what actually paid off
this pass.

**Next:** Still the Nginx Proxy Manager host entry. Every other listed
blocker is now either resolved or accurately described as decision-pending.

---

## 2026-08-19 09:00 (risk register and sample rename, autonomous operator)

**Did:** Checkout was 24 commits behind again; fetched and fast-forwarded
first, so nothing this pass could revert. Gates clean on arrival. Money path
and deployment need access this session lacks, and no P0 issue is
unblocked, so worked category (d). The free sample's filename still read
"Complete Book" after an earlier pass fixed its title, so a saved download
still carried the claim the link text no longer made. Renamed the HTML and
PDF, plus a stale content/book mirror whose title fix was missed entirely,
to "Sample (Chapters 1-30)", and updated the links and scripts naming the
old file. Also found RISKS(1).md, which titles itself "RISKS.md" inside: an
unreconciled early upload beside the real, evidence-based RISKS.md. Removed
it. Reviewed RISKS.md: closed RISK-0002 (superseded by the ghcr.io deploy)
and RISK-0004 (fixed by relabeling, not adding chapters), and downgraded
RISK-0009 to MITIGATING, since "Set in Order" still appears roughly 135
times estate-wide, untriaged.

**Verified:** Four gates pass. Renamed-file links return 200 on a local
server; a link sweep of 14 pages, 462 hrefs, found 0 broken.

**Went well:** Fetching before analysis caught the stale checkout in
minutes, not after building on top of it.

**Did not go well:** Nearly spent the pass merging 1989 lines of generic
risk content into RISKS.md before checking it was superseded, not additive.

**Changing next cycle:** When two documents claim one canonical role, check
which has evidence-backed entries before assuming a merge.

**Next:** Deployment (NPM proxy host entry) and Stripe auth still need a
desk session. Otherwise, the RISK-0009 term triage is next.

---

## 2026-08-19 12:50 (RISK-0009 term triage, autonomous operator)

**Did:** Checkout started detached 25 commits behind origin/main with no
local record of why; fetched first and confirmed origin already held that
history, so nothing was at risk, and fast-forwarded to match. Gates clean on
arrival. Money path and deployment still need a desk session, no P0 issue is
unblocked, so did the RISK-0009 term triage the last entry queued up. Printed
and read every one of the 169 "Set in Order" lines across 72 files before
touching any of them, per the RISK's own mitigation and this run's standing
rule against bulk transforms. Found 14 real violations, all presenting the
term as this project's own rather than quoting or rejecting it, spanning
CLAUDE.md itself, seven other root control documents, one agent definition,
three super prompts, one social posting plan, and one deck planning
document. Fixed all 14 to "Straighten". Nine of them also had Safety sixth
instead of fourth in the same list; fixed that too, since it was the same
lines. Confirmed content/book/6s-success-claude-files/ is a stale, untouched
mirror, a separate finding, not swept.

**Verified:** All three gates pass. Independently confirmed zero remaining
"Set in Order" in every touched file, and that the two multi-section
super-prompt files still have exactly six "###" headings each, in the right
order, with no content dropped in the reorder.

**Went well:** Reading the minority class first, again. Of 169 lines, 155
were legitimate on inspection; the 14 real ones were only findable by
reading, not by a keyword count, and several were hiding behind "###" and
"##" headings a plain substitution would have handled correctly by accident
but a table cell or prose sentence would not have.

**Did not go well:** CLAUDE.md, the document every agent reads first and
that states "Write Straighten, never Set in Order" in its own text, was
itself violating that rule in its Core 6S Model list, with Safety sixth
too. Nobody had read it against its own rule before now.

**Changing next cycle:** When a rule and an example of the rule's violation
can both be true of the same document, check the document against its own
rule, not just against the content it governs.

**Next:** Deployment (NPM proxy host entry) and Stripe auth still need a
desk session. Otherwise: reconcile or retire content/book/6s-success-claude-
files/, and extend ops/dashboard.py's canon scan to the control layer so a
future regression here would show on the dashboard instead of waiting for
the next manual triage.

---

## 2026-08-19 (continuous delivery, run from the desk)

**Did:** Closed the last automatic gap in the pipeline. GitHub built images on
every push, but the VPS only ever pulled when a human clicked Deploy, because
`restart: unless-stopped` restarts a container without re-pulling it. Added a
Watchtower updater to the compose, scoped by label so it can only ever see this
one container.

**Verified:** 10 of 10 against the running container. Ledgerium on 3000,
Compassion Benchmark on 8080 and Nginx Proxy Manager on 81 all confirmed healthy
after the change. The registry's newest tag `60830af` matches the newest commit
that touched `site/`, and commits touching only documentation correctly build no
image.

**Went well:** Scoping the updater before running it. Watchtower's default is to
update every container on the host, which on this box would have included a live
product. `--label-enable` plus an explicit opt in label on our service makes the
neighbours invisible to it.

**Did not go well:** I nearly reported a false "stale build" finding. I compared
byte counts between the local file and the served one and saw 14,078 against
13,552. The difference was exactly 526, which is exactly the file's line count:
Windows CRLF locally against LF in the image. Comparing content after stripping
carriage returns showed them identical.

**Changing next cycle:** Never compare a Windows working copy to a served file
by byte count. Compare content with line endings normalised, or compare a hash
of the normalised bytes.

**Next:** One hop left and it is not ours to make from here. Port 80 belongs to
Nginx Proxy Manager, which has no host entry for the domain, so the public URL
still answers "Default Site". That panel needs a login.

---

## 2026-08-19 (LAUNCHED)

**Did:** 6s-success.com is publicly live. Phil added the proxy host in Nginx
Proxy Manager, which was the last hop. Verified the whole chain and taught the
dashboard to measure public reachability instead of asserting it.

**Verified:** Both DNS records resolve to 187.77.25.50, the apex directly and www
through a CNAME. NPM answers 301 on port 80 for both names and forwards to the
container. `ops/verify_deploy.py` passes **10 of 10 against
https://6s-success.com and 10 of 10 against www**. TLS is Let's Encrypt, issued
today, covering both names, expiring 17 November. Every page of a real reader
journey returns 200, and both free sample downloads resolve.

**Went well:** Having the verifier written and trusted before launch day. The
moment the proxy host existed, confirming the launch took one command rather
than an afternoon of clicking.

**Did not go well:** I reported the free sample as a 404 before checking why. It
was renamed by an earlier pass, correctly, from "Complete Book" to "Sample
(Chapters 1-30)", and every real link on the site resolves. I had tested a
hardcoded old path rather than the links the site actually contains. A false
alarm on launch day, from the tool that exists to prevent false alarms.

**Changing next cycle:** Check links by extracting them from the pages, never by
typing a path from memory. `verify_deploy.py` should read hrefs out of the served
HTML rather than carrying its own list, which is the same defect as the "rooms"
page it invented yesterday. Twice now, so this is the process fix, not a patch.

**Next:** The constraint is no longer reachability. It is that the site cannot
take money, and the front matter still blocks two finished products.

---

## 2026-08-19 (MCP connector, and an updater removed)

**Did:** Built and shipped a 6S Success MCP server. It exposes the 114 micro
zones as three tools so anybody using Claude can ask "my entryway is chaos" and
get the actual method rather than generic decluttering advice, with attribution
and a link back on every response. That is a distribution channel that does not
depend on search rankings, which matters when the site is six hours old. Also
connected the Stripe MCP, read only, and took live payments live.

**Verified:** All three tools driven against the real corpus. "keys always
missing" returns the Entryway Landing Zone first. All six passes render in
canonical order with Safety fourth and no "Set in Order" anywhere. The MCP
initialize handshake is clean over streamable HTTP. Image builds, publishes, and
pulls anonymously. CI fails the build if the copied corpus ever drifts from the
manual it came from.

**Did not go well:** I added a Watchtower auto updater to the website compose
earlier today and it went into a crash loop. The site itself stayed healthy at
10 of 10 throughout and the neighbours were untouched, but a container
restarting forever on a host that also runs two live products is not acceptable
to leave while investigating. Removed it and reverted to manual redeploy.

I also did not notice for some time. I checked the site and the neighbours after
deploying it, and both were fine, so I moved on. The thing I changed was the one
thing I did not check.

**Changing next cycle:** After adding a container, check that container, not
only the service it was meant to help. `verify_deploy.py` proves the site works
and says nothing about what else is running beside it.

**Next:** Deploy the MCP image as its own project on 8974 and put it behind the
proxy so it can be added as a connector.

---

## 2026-08-19 (front door, deployed and verified live)

**Did:** Stopped the homepage advertising things that do not exist, and gave the
one buyable offer a price and a claim that it is bookable. Deployed and
verified on the live domain.

**Verified:** Live homepage now returns zero occurrences of "self-paced course",
"live workshops" and "Reset kits," and one each of "250 dollars" and "Bookable
now". The method page no longer carries a "Get the video series" button and does
say none of it has been filmed. Site holds at 10 of 10, Ledgerium and Compassion
Benchmark untouched.

**Found:** The homepage offered three ways in with equal weight, and two of the
three sold nothing that exists. Consulting, the only line that can be delivered
and paid for today, was third of three with no price and no indication it was
available. A visitor who wanted help had two paths to things they could not buy
and none to the thing they could.

**Did not go well:** Two of my own errors, both caught before shipping but only
just. I repointed a footer link away from `method.html#videos` across 13 pages
believing the anchor was dead. It was not. The section existed and selling from
it was the real defect, so the repoint hid the problem rather than fixing it.
Then, correcting that section, I wrote that the series is "being filmed now",
which the tracker contradicts at 0 of 114 shot. I removed one false claim by
writing another.

**Changing next cycle:** Before repointing a link, fetch the target and read it.
And after writing replacement copy, check the new sentence against the data the
same way the old one was checked. The edit is not finished when the false claim
is gone; it is finished when the replacement is also true.

**Next:** The MCP connector needs a DNS record and a proxy host to go live.

---

## 2026-08-19 (money leak on the one live checkout, autonomous operator)

**Did:** Checkout arrived detached, 39 commits behind; attached to main and
fetched clean. Gates passed on arrival. Git history showed the money path had
already gone live since the last entry: two Stripe Payment Links for
consulting. But `consulting.html`'s own primary "Book a consult" button
linked to a dead-end contact form instead of the packages section holding the
real buy links, on the one page built to sell something that can now be
bought. Repointed it to `#packages`. Separately, `ops/dashboard.py` only
detected payment by looking for an embedded checkout script, so it kept
reporting "cannot take money" after the Payment Links went live; taught it to
also scan `assets/js/data.js` for `buy.stripe.com`. Also made its
site-reachability check return unknown rather than false when the request is
denied by this session's own sandboxed network, instead of folding a policy
403 into "the site is down". Updated `STATUS.md` to match.

**Verified:** All four gates pass, before and after. `ops/payment-links.json`
and `site/assets/js/data.js` agree on both live links. Confirmed the network
denial is a proxy policy, not a dead site, via the proxy's own
`/__agentproxy/status` endpoint, which logs a 403 for both `6s-success.com`
and `buy.stripe.com`.

**Went well:** Diffing the stale dashboard against recent git log, not just
trusting its RED, surfaced a real conversion leak already live in production.

**Did not go well:** Took real time confirming the network denial was a proxy
policy before trusting that fix, rather than just guessing.

**Changing next cycle:** When a dashboard says RED, check its own generation
logic against recent commits before trusting the number.

**Next:** Widen checkout to the book and the Field Manual, then reconnect an
email provider so the 14 forms stop dead-ending.

---

## 2026-08-19 (114 zone pages, live)

**Did:** Gave every micro zone a page. 134 new pages, 20 room hubs and 114 zone
pages, averaging 961 words of real method each, all live and verified on the
public domain. Sitemap went from 12 URLs to 146.

**Verified:** 8 of 8 randomly sampled zone pages return 200 on the live domain.
Site holds at 10 of 10. Every page carries the safety notice, a canonical, valid
schema.org HowTo, and the six passes in canonical order with Safety fourth.
5,793 internal references checked, none broken. Ledgerium and Compassion
Benchmark untouched.

**Found:** The site and the manual name the same 114 zones differently. The
manual says "Landing Zone", the site and book say "The Landing Spot". Shipping
in the manual's vocabulary would have put two names for one zone in front of one
reader. Display names now come from the site, content from the manual, mapped by
meaning rather than position, because the Workshop orders its zones differently
in each source.

**Did not go well:** Two deploys that I reported as done had not happened. The
Hostinger compose form silently reverts to a create-new state with an empty
application name, and my Deploy click hit a disabled button twice while I
watched 404s and assumed the deploy was slow. I only caught it by screenshotting
the panel rather than trusting the click result.

Underneath that was a second fault: `docker compose up -d` reuses whatever
`:latest` is already on the host, so even a real deploy would have shipped the
previous build. That is the same defect as the stale local image on 18 August,
wearing a different disguise, and it has now cost two sessions.

**Changing next cycle:** After clicking anything in that panel, read back the
state that proves it applied, not the click result. And `pull_policy: always` is
now in the compose so a deploy cannot quietly ship the old image again.

**Next:** The MCP connector still needs a DNS record and a proxy host.

---

## 2026-08-19 (Listmonk, and why the form is still not wired)

**Did:** Read the 6S Success list UUID out of Listmonk's public API without
needing any credential, wired the newsletter form to it, then deliberately
reverted that wiring and opened issue #15 instead.

**Verified:** Subscribed a real address end to end, then read the confirmation
out of the mailbox over IMAP rather than trusting the 200 that Listmonk
returned.

**Found, and this is why the revert:** the confirmation link is
`http://localhost:9000/subscription/optin/...`. Listmonk's Root URL is still the
default, so the link resolves to the subscriber's own machine and can never be
clicked by anybody. With double opt-in on, that is every signup unconfirmable
and a list of addresses that can never be mailed. The sender is also
`"Compassion Benchmark" <info@compassionbenchmark.com>`, because that business
shares the instance, so a 6S reader would get mail from an unrelated company.

Both settings are instance wide rather than per list, so they cannot be right
for two brands at once. Compassion Benchmark is live, so I did not touch it.

**Went well:** Not stopping at the 200. Listmonk accepted the subscription and
said a confirmation had been sent, and both of those were true. The thing that
was broken was only visible by reading the mail itself.

**Did not go well:** I nearly shipped it. The form was wired and would have gone
out with the next deploy, silently converting every future signup into a dead
end. What caught it was testing with an address I could actually read, rather
than a fake one.

**Changing next cycle:** When testing anything that sends mail, always send to a
mailbox we control and open the message. A send that reports success proves the
sender worked, never that the recipient got something usable.

**Next:** #15 is the blocker for email capture. Everything else on the money path
is already live.

---

## 2026-08-19 (search discovery)

**Did:** Submitted all 146 URLs to IndexNow. The domain was a parking page
yesterday and nothing on the internet links to it, so left alone a crawler might
have found the sitemap in days or weeks. Bing, Yandex and Seznam now know every
page exists.

**Verified:** Key file live at the site root and returning the key, then 146 of
146 URLs accepted with HTTP 202. The script refuses to submit at all when the
key file is unreachable, because an unverified submission is silently rejected
and would look like it had worked.

**Went well:** Finding an unblocked route to a blocked goal. Search Console needs
Phil's Google account and has been waiting three days. IndexNow needs no account
at all and covers everybody except Google, so the traffic clock starts now for
most of the web rather than whenever he gets to it.

**Did not go well:** Four Deploy attempts failed silently before I noticed the
pattern. Coordinate clicks on the Hostinger panel land on nothing while the page
is still settling, and my checks reported "clicked: false" without me reading
them properly the first two times. Clicking the button through the DOM instead
worked first try.

**Changing next cycle:** Drive that panel through the DOM, never by coordinates.
The button is findable by its text and clicking it that way is not sensitive to
layout or timing.

**Next:** Google still needs Search Console. Email capture still needs issue #15.

---

## 2026-08-20 (the free sample's broken images)

**Did:** All 9 open issues are `decision` or `blocked-on-art`, so I looked
for a real defect instead. A link sweep of every `site/**/*.html` file found
322 broken references, 172 of them the images in "Read chapters 1 to 30
free", the book page's main lead magnet: every figure showed a broken icon,
and both stylesheets 404'd too, so it also rendered unstyled. The source
images never ship here by design (`content/**/*.jpg` is gitignored, 1.78 GB
that stays on the Desktop). `ops/build_epub.py` already solved this for the
EPUB, degrade each image to its alt text in a labelled panel. Wrote
`ops/build_sample_html.py` to apply that same transform here and repoint the
fonts link at what the site already ships.

**Verified:** Re-ran the sweep, 5,849 references checked, zero broken except
the pre-existing `/stats/script.js`, a VPS route this session cannot reach
either way. Re-ran all four required gates, all pass.

**Went well:** Checking rather than assuming; the tree looked clean at
startup, the sweep is what surfaced this.

**Did not go well:** `git checkout main` reported "up to date" against a
stale cached ref, 49 commits behind actual `origin/main`. I would have
branched from the wrong base without a manual `git fetch` and compare.

**Changing next cycle:** Always `git fetch origin main` before trusting
checkout's report.

**Next:** This needs a VPS redeploy to reach a visitor; this session cannot
click through that. Check whether Phil answered any `decision` issue; if not,
keep auditing customer-facing pages for fixable defects.

---

## 2026-08-20 (the room pages were leaking their own template code)

**Did:** Fixed a bug in `ops/build_zone_pages.py` that made all 20 room pages
render raw Python dict text, `{'label': 'Where to start', 'text': '...'}`, in
the "For this room" section instead of formatted advice. It called `esc()` on
the whole tips dict rather than its label and text fields. Regenerated all 20
rooms, committed, pushed.

**Verified:** Grepped the repository for the artifact string, before and
after: zero remaining. Re-ran all four gates, all clean. Hand diffed one file
to confirm only the tips list moved. The Actions image build for the commit
succeeded. Could not load the live domain from this sandbox to see it
rendered; the outbound proxy denies 6s-success.com, the same limit the
previous pass recorded.

**Went well:** Running the gates first found nothing inherited broken, so the
session went straight to a real defect instead of repairing one.

**Did not go well:** This had been live on all 20 room pages, one tier above
the 114 zones in traffic priority, and nothing caught it until a manual read.

**Changing next cycle:** No gate checks built site HTML for garbage output.
Add one that greps `site/` for a Python-repr signature before calling the
tree clean.

**Next:** Traffic is still the constraint. Everything else on the money path
is live and waiting on Phil's two proxy paths.

---

## 2026-08-20 (four articles, live, and the overnight machinery made real)

**Did:** Published four long form articles, built an index so they are a cluster
rather than four orphans, wired them into the sitemap and the site's navigation,
deployed, and submitted all 151 URLs to IndexNow. Also built the thing that
actually delivers Phil's four hourly summary overnight, and retargeted the cloud
routine, which was still working from a picture of the world two days stale.

**Verified:** All five article URLs return 200 on the live domain. Site holds at
10 of 10. 151 of 151 URLs accepted by IndexNow. 5,961 internal references
checked, one flagged and it is the known JavaScript false positive in cart.html.
Every article independently regated by me rather than trusted from the agent
report: zero dashes, zero uses of "Set in Order", safety notice, canonical,
analytics tag and offer block on all four, and valid JSON-LD including FAQPage
on the two answer engine pieces.

**Went well:** Both writing agents independently flagged the same defect in
their own work, that the articles were orphans nothing linked to. That is the
kind of finding a brief should invite, and both briefs asked for it.

**Did not go well:** I committed a third agent's file while it was still
writing. The Kitchen script file has one episode heading where it should have
seven, and lopsided coverage of the six passes, because it is mid flight. No
harm, since it is repository content rather than anything served, but I should
not have swept it into a commit I had not verified.

**Changing next cycle:** Commit only what I have checked. `git add -A` picks up
whatever else is in the tree, including another agent's work in progress.

**Next:** Traffic is the constraint now. Everything else on the money path is
live and waiting on Phil's two proxy paths.

---

## 2026-08-20 (Kitchen scripts, and a safety gap they exposed)

**Did:** Committed seven Kitchen shooting scripts, 30,108 words, 42 Shorts, 203
shot rows each with a 9:16 framing note. Opened issue #16 on a safety gap the
scripting surfaced.

**Verified:** Zero dashes, zero uses of "Set in Order", Safety fourth in every
episode, product types only, nothing taught that needs a licensed trade.

**The find:** writing the safety segments forced a line by line read of the
Kitchen hazards, which reading them as a reader never would. The Cooking Zone
handles fire well and specifically, and mentions gas nowhere at all. Zero
occurrences in the safety pass, the hazards or the cleaning detail. That gap is
live on 114 pages. I did not write it in, because it is published safety copy
and the scope question is genuinely arguable, so it went to Phil with a
recommendation instead.

**Went well:** Not accepting the agent's report at face value. It also flagged
that the manual tells readers to combine three half empty bottles without a
caveat. Checking the source showed the text says "of the same spray" and the
same zone's safety pass already warns about mixing bleach with acid or ammonia.
That one was a false alarm and reporting it to Phil would have wasted his
attention and eroded trust in the real finding beside it.

**Did not go well:** Nothing new this pass. The previous pass's `git add -A`
error was confirmed from the other side: the agent noticed its half written file
had been committed out from under it.

**Changing next cycle:** Keep doing what caught the false alarm. Verify an
agent's finding against the source before passing it upward, especially a safety
claim, because a wrong safety alarm costs more than the finding is worth.

**Next:** Traffic. Everything else waits on Phil.

---

## 2026-08-20 (linking the zone and room pages back to the articles)

**Did:** All 10 open issues are `decision` or `blocked-on-art`. The 4
articles link out to specific zones and rooms, but none of the 134 zone and
room pages linked back. Added a Related reading block to both templates in
`ops/build_zone_pages.py` and regenerated all 134 pages. Also fixed step 0 of
`ops/routine-prompt.md` to fetch before checkout, a stale-ref defect that has
now cost two sessions the same surprise.

**Verified:** All four gates pass. Swept every local href in `site/`, 5,917
checked, zero broken, including the 268 new links. Zero dashes, zero uses of
the rejected term in the regenerated pages. The image build completed,
confirmed success against the GitHub API. Could not load the live domain
from this sandbox, same proxy limit as the last three entries, so IndexNow
resubmission was not run; it refuses without confirming the key is live.

**Went well:** Recognized the stale `main` ref immediately instead of
trusting `git checkout main`'s report, unlike the first time this happened.

**Did not go well:** Could not push the step 0 fix to the actual firing
routine. `update_trigger` refused it, since the routine was not created by a
Claude session. The fix is in the repo, not yet in what runs it.

**Changing next cycle:** Flagging for Phil: `trig_011oe2y7KR3AiPxUTd6b9P6c`
still runs the old step 0. Copying `ops/routine-prompt.md` in closes it.

**Next:** Traffic is still the constraint. Check for a resolved `decision`
issue first; otherwise keep strengthening internal links and technical SEO.
