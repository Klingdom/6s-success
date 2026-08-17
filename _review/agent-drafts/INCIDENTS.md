# 6S Success Incident Register

> Durable record of things that actually went wrong: production outages, failed deploys, security events, data loss, and customer facing defects that reached the public. One entry per incident, kept permanently.

## 1. Purpose

`INCIDENTS.md` is the register. `RUNBOOK.md` is the procedure. `DISASTER-RECOVERY.md` is the plan for events that exceed ordinary response.

This file exists so the system can answer:

- What has broken before?
- How long did it last?
- What did the customer experience?
- What was the actual cause, not the first guess?
- What changed so it cannot happen the same way again?
- Did that change get verified?

`STATUS.md` holds the currently active incident. When it closes, it moves here and does not move again.

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `RUNBOOK.md`
- `DISASTER-RECOVERY.md`
- `SECURITY.md`
- `RISKS.md`
- `LEARNINGS.md`
- `STATUS.md`

If a referenced file does not exist yet, do not invent its contents.

---

# 2. Core Rule

**Record the incident even when nobody noticed.**

An outage at 3am on a site with UNKNOWN traffic is still an outage. The value of this register comes from completeness, and completeness is destroyed the first time an entry is skipped because it seemed unimportant or embarrassing.

Never delete an entry. Never quietly soften one. Correct it by adding to it.

---

# 3. Register State

**Zero incidents are recorded.**

This is the honest state on 2026-08-17, and it means exactly one thing: no incident has been recorded. It does not mean none has occurred.

Two facts about the current environment make that distinction important:

1. **No monitoring is known to exist.** Nothing in this repository configures uptime checks, alerting, or log shipping. The container has a Docker healthcheck, which restarts it and tells nobody. An outage would most likely be discovered by someone visiting the site. Whether any external monitor exists is UNKNOWN, and checking the Hostinger control panel and the DNS provider would establish it.
2. **The site has been live for a short time and changes rarely.** Sixteen commits exist in total. A thin incident history is plausible.

The first fact is the more likely explanation for an empty register. Treat this file as untested rather than as evidence of reliability.

---

# 4. What Counts As An Incident

Record any of these:

| Category | Examples for this system |
|---|---|
| Availability | Site unreachable, container down, host down, Traefik not routing |
| TLS | Certificate expired, renewal failed, browser warning shown |
| Deploy | A deploy failed, or a deploy shipped a broken page |
| Access | The VPS could not pull the repository, credentials lost or rotated wrongly |
| Security | Secret exposed, unauthorized access, dependency compromise |
| Data | Loss of product masters, loss of the certificate store, unrecoverable file |
| Customer facing defect | A published asset that misinforms or endangers a reader |
| Legal or IP exposure | Third party marks or unlicensed material reaching the public |
| Autonomous agent | An agent taking an unauthorized, destructive, or unverified action |
| Cost | Unexpected recurring or one time spend |

## Not incidents

- a risk that has not materialized, which belongs in `RISKS.md`
- a known gap that is simply unbuilt, which belongs in `BACKLOG.md`
- a defect found and fixed before publication
- a decision someone later disagreed with, which belongs in `DECISIONS.md`

Two current items are frequently mistaken for incidents and are correctly risks: the VPS cannot pull the private repository (`RISK-0002`), and safety notices did not exist before 16 August 2026 (`RISK-0006`). Neither has produced a recorded failure yet. If a deploy fails on the first, that failure is an incident and gets an entry here.

---

# 5. Incident ID

Use:

`INC-0001`

`INC-0002`

Sequential, never recycled, assigned when the incident is declared rather than when it is resolved.

---

# 6. Severity

| Level | Definition | Example |
|---|---|---|
| `SEV1` | Site down, data lost, or security compromise | 6s-success.com unreachable |
| `SEV2` | Major function broken or exposure likely | Certificate expired, browser warning |
| `SEV3` | Partial or cosmetic customer impact | One page broken, an asset 404s |
| `SEV4` | Internal only, no customer impact | A failed deploy caught before promotion |

Declare severity from customer impact, not from how difficult the fix is.

When uncertain between two levels, declare the higher one. Downgrading later is cheap. Discovering during the postmortem that it was worse than declared is not.

---

# 7. Lifecycle

```
DETECTED -> DECLARED -> MITIGATED -> RESOLVED -> REVIEWED -> CLOSED
```

An incident is not `CLOSED` when the site comes back. It is `CLOSED` when the review is written and the follow up actions exist as backlog items with owners.

Skipping the review is how the same incident happens twice.

---

# 8. Incident Record Template

```yaml
id: INC-0001
title: Short factual title, no blame
severity: SEV1|SEV2|SEV3|SEV4
status: DETECTED|DECLARED|MITIGATED|RESOLVED|REVIEWED|CLOSED
detected: YYYY-MM-DD HH:MM
detected_by: monitor, agent, owner, or visitor report
resolved: YYYY-MM-DD HH:MM
duration: total customer impact time
coordinator: which agent or the owner

customer_impact: >
  What a real person experienced. Not what was technically wrong.

detection: >
  How it was found, and how long after it started.

timeline:
  - "HH:MM what happened"
  - "HH:MM what was done"

cause: >
  The actual cause, established by evidence. If it is still a hypothesis,
  say so.

mitigation: >
  What restored service.

evidence:
  - commands run, log excerpts, image digests, commit hashes

follow_up:
  - action, owner, backlog reference

related:
  - RISK-nnnn or DEC-nnnn
```

---

# 9. During An Incident

Priority order, and it does not change under pressure:

1. **Restore the customer experience.** For a static site this is almost always a rollback to the last known good image, not a fix forward.
2. **Preserve evidence.** Capture logs and container state before pruning, recreating, or rebuilding anything. Evidence destroyed during recovery cannot be recovered afterward.
3. **Record the timeline as it happens.** Reconstructed timelines are wrong.
4. **Escalate on authority, not on difficulty.** Anything RED under `AUTONOMY.md` still needs the owner, mid incident included.

Do not begin a redesign during an incident.

`RUNBOOK.md` holds the operational detail. This file holds what happened.

---

# 10. Detection Reality

Honest assessment of what would currently be noticed, and how.

| Failure | Would it be detected? | How |
|---|---|---|
| Container crash loop | Partially | Docker healthcheck restarts it, silently |
| Host down | UNKNOWN | Nothing is known to watch it |
| Certificate renewal failure | Late | Discovered when a visitor sees a warning |
| Deploy shipped a broken page | No | No smoke test exists, see `RISK-0010` |
| Repository pull failure on the VPS | At deploy time | The deploy fails loudly, `RISK-0002` |
| Secret exposure | No | No scanning is configured |
| Loss of product masters | Late | They are outside the repository, `RISK-0011` |

Improving this table is worth more than improving this document. The cheapest meaningful step for a static site is a single external uptime check on the domain root plus a certificate expiry check.

---

# 11. Review Requirements

| Severity | Review required |
|---|---|
| `SEV1` | Always, written within one operating cycle |
| `SEV2` | Always |
| `SEV3` | If it recurs, or if it reached customers |
| `SEV4` | Optional, but record the entry regardless |

The review answers four questions:

1. What was the actual cause?
2. Why was it not caught earlier?
3. What would have made detection faster?
4. What specific change prevents this class of failure?

Blameless in the strict sense: the register names systems, changes, and gaps, never a person or an agent as the fault. "An agent deployed without verifying" is a missing gate, not a character flaw.

Durable lessons graduate to `LEARNINGS.md`. Follow up work goes to `BACKLOG.md`. Structural exposure goes to `RISKS.md`.

---

# 12. Relationship To Other Registers

| Question | File |
|---|---|
| What might go wrong? | `RISKS.md` |
| What went wrong? | `INCIDENTS.md` |
| What did we learn? | `LEARNINGS.md` |
| What did we decide because of it? | `DECISIONS.md` |
| What are we doing about it? | `BACKLOG.md` |
| What is happening right now? | `STATUS.md` and `EXECUTIVE-DASHBOARD-LIVE.md` |

One incident may touch all six. Write the incident here once and reference it from the others. Do not copy the narrative around.

---

# 13. Incident Log

No incidents recorded.

New entries are appended below in ID order, newest last, using the template in section 8.

---

# 14. Final Principle

An empty incident register is not an achievement, and it should never be presented as one.

Right now it means the system cannot see itself. Nothing watches the site, nothing tests a deploy, and nothing scans for exposure, so the honest reading of zero entries is that failures would pass unrecorded.

The first entry in this file will be a good sign. It will mean something noticed.
