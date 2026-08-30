# Retrospective, sixth cycle ending 2026-08-30

Eight specialist agents, nine commits, and one finding that reframed
everything: the business has been unable to take money for days and nobody
knew.

---

## What went well

**Asking eight specialists at once was worth it.** The agents converged
independently on the same conclusion from six different directions, which is
what made it credible rather than a single opinion. Commerce found the dead
links by checking the Stripe account, analytics found them by comparing live
assets to the repository, and QA found them by crawling all 174 live URLs.
Three methods, one answer. I then verified it a fourth time myself before
repeating it to Phil, because a claim that large should not travel on
somebody else's word.

**The outage was invisible to every check that existed, and the reason is
worth keeping.** A deactivated Stripe link returns HTTP 200 and serves the
same 550 KB JavaScript shell as a working one, resolving to "no longer
active" only once a browser runs it. Every status check the repository had
was true. `check_sellable.py` looked at the repository, where the links are
correct, which is exactly what made it invisible. The new check asks Stripe's
API about the links the live site serves, and that is the only question that
distinguishes the two.

**Several things were fixed before they could ship, not after.** Terms said
six things are for sale while 155 are. Every surface promised delivery within
the hour against a measured median of 85 minutes and a longest gap of 12.4
hours. The privacy page's only mention of payments was a promise to update it
before payments went live, weeks after they did. All three would have become
public falsehoods the moment Phil clicked deploy.

**A gate caught something the moment it existed.** `gate_deck_count` compared
the advertised card count against the cards that actually render, and
immediately found the gallery still saying 90 after I had corrected the
catalogue and believed I was done.

**The long tail became reachable.** 109 zone packs existed, priced,
deliverable, each with a live Stripe link, and not one of the 114 zone pages
mentioned its own. A reader told exactly what was wrong with their mail
station was offered 684 cards for twenty rooms and nothing for the room they
were standing in.

---

## What did not go well

**I nearly shipped an nginx change I could not validate.** No nginx locally,
Docker daemon down, no CI check. A syntax error there does not slow the site,
it stops the container starting, which would have taken production down on
the very deploy meant to bring it back. I added `nginx -t` to CI before
committing the change, which was right, but the config had been written blind
and shipped on trust for the whole life of this project and I only noticed
because I was about to do it again.

**My first SKU derivation was tidier than the real one and therefore wrong.**
I stripped a trailing hyphen that the actual scheme keeps inside its truncated
segment. It produced SKUs matching nothing, so every zone page would have
silently offered no pack while looking exactly as intended. Caught by checking
the match count rather than by opening a page: 0 of 114 would have looked
identical to a page that simply had no pack.

**I let a subagent's assumption into my head before checking it.** One agent
flagged order fulfilment as a possible trust emergency on the basis that no
mail credentials exist. I checked the workflow's actual run log: it is switched
on and has delivered. Had I repeated that to Phil it would have sent him
chasing a problem that does not exist, on the day he has a real one.

**Three heredoc escaping failures again**, in the cycle right after a
retrospective that told me to stop writing Python with escapes through
heredocs. I switched to writing script files partway through, which worked.
The rule was right and I ignored it twice before applying it.

---

## What to change next cycle

**Every check must be able to distinguish "this is fine" from "I looked in the
wrong place".** That is now four consecutive retrospectives on the same theme,
but this cycle gave it the sharpest possible example: a check on the
repository cannot see a fault in production, and it reports clean while doing
so. Any new check states which artefact it examined, and if the artefact is
not the one a reader cares about, it says that too.

**Verify a claim before repeating it, especially a large one.** Both the
outage and the fulfilment scare came from agents. One was true and I confirmed
it four ways. One was false and I confirmed it in two commands. The cost of
checking is minutes; the cost of not checking is sending the owner after the
wrong thing.

**Write the script to a file when the code contains escapes.** Third time.

---

## Numbers

| | |
|---|---|
| Specialist audits run | 8, in parallel |
| Payment links dead on production | 6 of 6, confirmed four ways |
| Days the business could not take money | at least 3 |
| Public statements corrected before deploy | 4 |
| Zone pages now offering their own pack | 109 of 114, from 0 |
| Gates added | 3 (live links, deck count, nginx config) |
| Gates that caught something immediately | 1 |
| Preflight | every gate passes, 3 warnings, two of them the outage |
| Revenue | $19, unchanged, and now explained |
