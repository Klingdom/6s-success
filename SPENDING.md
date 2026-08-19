# How money gets spent

Written 2026-08-19. Owner: Phil.

## The short version

Claude cannot hold or use a payment card. Not a personal card, not a company
card, not a prepaid one, and not one loaded with a small amount. Entering a card
number into a payment field is something Claude will not do, and that does not
change if the owner authorises it or supplies the details.

That is a constraint, not a preference, so this document is about getting the
same outcome a different way.

## What the card was meant to solve

The real goal is that work should not stall waiting on a 30 dollar purchase. The
answer to that is not a card in Claude's hands. It is that Claude operates inside
accounts the owner has already paid for, and that anything genuinely new is
surfaced early with the cost and the reason, not discovered at the moment it
blocks something.

## The pattern that works

**The owner attaches payment once. Claude operates the account by API.**

That is already how everything here runs:

| Service | Who paid | How Claude works with it |
|---|---|---|
| Hostinger VPS | Phil, already | Docker Manager and the panel |
| Domain | Phil, already | DNS zone |
| Mailbox support@ | Phil, already | SMTP and IMAP with an app password |
| GitHub | free tier | gh CLI and API |
| Stripe | no upfront cost | restricted API key |
| Email provider, when chosen | free to 1,000 contacts | API key |

In none of those does Claude touch a card. In all of them Claude can do the work.

## What actually needs money today

Almost nothing, which is the useful finding.

- Domain, VPS and mailbox: **already paid**
- TLS, GitHub, Actions, the container registry: **free**
- Stripe: **no upfront cost**, a percentage per transaction
- Email provider: **free** to the first 1,000 contacts

Two things do cost money, and both are book related rather than infrastructure:

- **An ISBN**, roughly 125 dollars for a single one and much less per unit in a
  block of ten. Needed only to sell the book through retailers.
- **A print proof copy**, roughly 10 to 40 dollars, once there is a print file.

Neither blocks anything this week. Both belong to issue #3, which is already
waiting on the owner for the front matter.

## When Claude wants to spend

1. Say so before it blocks something, not when it does.
2. State the amount, what it buys, what it unblocks, and whether a free option
   was considered and rejected.
3. Anything recurring, or over 50 dollars, gets a `decision` issue rather than a
   sentence in passing, so it survives the conversation.
4. The owner pays. It takes a minute and it keeps the boundary clean.

## What Claude will never do

- Enter a card, bank or account number into any field
- Create an account that requires a payment method
- Accept terms or authorise a recurring charge
- Move money between accounts

If any of those is the next step, the work stops and the owner is told plainly.
