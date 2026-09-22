# Everything-Claude-Code, integrated 2026-09-22

What was taken from `Klingdom/everything-claude-code` (a fork of the ECC agent
harness), what was deliberately left out, and why.

Owner: `6s-ceo`. Review when the fork updates.

---

## 1. What this adds

ECC is a library of agent definitions, slash commands, skills and rules for
Claude Code. It is a **capability library, not a second operating system**:
`CLAUDE.md` in this repository remains the authority on how this business is
run. Where ECC's own `RULES.md` overlaps (delegate to specialists, test before
shipping, never bypass security checks, never print secrets) it reinforces
`CLAUDE.md` rather than competing with it, which is why it was safe to take.

Installed to the user scope (`~/.claude/`), so every session on this machine
gets them, not just this repository:

| What | Installed | Left out | Where |
|---|---|---|---|
| Agents | **27** | 45 | `~/.claude/agents/` |
| Commands | **51** | 24 | `~/.claude/commands/` |
| Skills | **102** | 126 | `~/.claude/skills/` |
| Reference docs, rules, schemas | 16 docs + 110 rules + 10 schemas | the 891-file `docs/` tree, `src`, `tests`, `tradingagents`, `examples` | `~/.claude/ecc/` |

The 12 `trading-*` agents and `trade-analysis` command were already installed
from this same fork before today; they were left untouched.

## 2. What was left out, and why

**Anything for a stack this business does not use.** C++, C#, Dart, Django,
.NET, Flutter, F#, Go, Java, Kotlin, Laravel, NestJS, Next.js, Nuxt, Perl,
PyTorch, Quarkus, Rust, Spring Boot, Swift, Vite, Angular, Android, HarmonyOS.
This site is static HTML/CSS/JS with a Python operations layer, and 45
irrelevant agents would make agent selection worse, not better. The cost of a
wrong specialist is a confident answer about the wrong thing.

**Anything for a domain this business is not in.** Healthcare/HIPAA, DeFi,
trading security, customs and freight, Cisco and homelab networking, energy
procurement, production scheduling, scientific literature databases.

**The hooks. Deliberately, and this is the one worth reading.**

`hooks/hooks.json` defines **28 hooks**: 8 `PreToolUse`, 10 `PostToolUse`, 6
`Stop`, plus `SessionStart`, `SessionEnd`, `PreCompact` and
`PostToolUseFailure`. Several match `*`, so they run on **every single tool
call**, and `PreToolUse` hooks can block a tool outright.

They were not installed because of what this particular instance does: it runs
long autonomous sessions that deploy a live website, hold a live Stripe
credential, and write to production infrastructure. Adding 28 auto-executing
Node processes to that path buys linting and memory features at the cost of a
new way for production work to halt or a commit to be mangled, and it would be
a change whose failure mode is hard to attribute later. The repository already
has its own enforcement at exactly the moment it matters: `.githooks/pre-commit`
(control bytes, build id, sitemap currency) and `ops/preflight.py`'s gate set.

They are kept, unused, at `~/.claude/ecc/hooks/` so the decision is reversible.
If they are ever wanted, enable them **a few at a time**, never `*` matchers
first, and measure the tool-call latency before and after.

## 3. Verification actually performed

- Every installed file was parsed: 27 agents have frontmatter with a `name`
  matching the filename and a `description`; 51 commands have a `description`;
  102 skills have `SKILL.md` with a description. **0 malformed.** Two
  pre-existing folders (`skills/learned`, `skills/synced`) have no `SKILL.md`
  and are Claude Code's own sync directories, not ECC's and not broken.
- Name collisions were checked before copying. The only ones were the 12
  `trading-*` agents already installed from this fork. Nothing belonging to 6S
  Success (`6s-ceo`, `seo-aeo`, `security-auditor`, `commerce-manager` and the
  rest) was overwritten; ECC's nearest equivalents install alongside under
  different names (`seo-specialist`, `security-reviewer`).
- `~/.claude/{agents,commands,skills}` were backed up before anything was
  written, to `~/.claude/backups/pre-ecc-<timestamp>/` (249 files).

**The limit, stated plainly:** the session that installed these could not
dispatch a subagent, so "the agents load and run" has NOT been proved end to
end. What is proved is that the files are in the right place, in the right
format, with no collisions. First session that can dispatch one should invoke
`silent-failure-hunter` or `python-reviewer` against `ops/` and record the
result here.

Instead of claiming it worked, the installer applied one agent's method by
hand to real code as a content check: `silent-failure-hunter`'s criteria found
24 `except: pass` sites under `ops/`. The highest-risk one
(`check_live_links.py`, a swallowed `OSError` in the tool that reports payment
outages) was read and is **not** a defect: it returns a documented
`(None, None)` and its caller tests for it. The other 23 are unexamined and
are a real, small task for a future cycle, recorded here rather than converted
into a finding nobody checked.

## 4. The most useful pieces for this business

Agents: `silent-failure-hunter`, `python-reviewer`, `security-reviewer`,
`a11y-architect`, `seo-specialist`, `performance-optimizer`, `code-explorer`,
`doc-updater`, `planner`, `tdd-guide`, `pr-test-analyzer`.

Skills: `accessibility`, `seo`, `verification-loop`, `security-review`,
`browser-qa`, `click-path-audit`, `python-testing`, `production-audit`,
`content-engine`, `brand-voice`, `docker-patterns`, `deep-research`,
`content-hash-cache-pattern` (directly relevant to `ops/build_seo.py`'s
content-hash design).

Commands: `/code-review`, `/security-scan`, `/quality-gate`, `/test-coverage`,
`/update-docs`, `/plan`, `/prune`.

---

## 5. Wired into the operating model, not just dropped on disk

Installing files changes nothing on its own: the CEO agent delegates from a
list, and a specialist absent from that list is never chosen. So
`claude/agents/6s-ceo.md` section 6 (DELEGATE) now names the reinforcements
and, more importantly, what they are NOT:

> The eleven 6S specialists own the business. These are narrower tools to
> reach for inside a workstream, not replacements, and they do not have the
> business context the eleven carry.

Two cautions are recorded there with them. Their output is a proposal to
verify, not an instruction to follow, because they came from a third-party
library (`CLAUDE.md` section 33). And none of them knows this business: an ECC
reviewer does not know that a payment link is load-bearing, that production is
a live shop, or that `GOALS.md` says arrivals are the constraint.

**A drift risk found while doing this, worth knowing.** The live agent
definitions in `~/.claude/agents/` and the tracked copies in `claude/agents/`
are two copies of the same thing, and nothing checks that they agree. They were
compared: 13 of 14 were identical and the 14th differed only because of the
edit above, which has been copied back. So the copy is genuinely maintained
today, by hand, and would drift silently the first time somebody edits the
live one and forgets. A gate could compare them, but only on a machine that
holds both, so it would report UNCHECKED in CI the way the VPS-dependent gates
already do. Recorded rather than built.
