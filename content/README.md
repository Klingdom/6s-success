# Content mirror

The text of every 6S Success product, mirrored here so autonomous agents can
read and edit it. **This exists because a cloud agent has no access to the local
Desktop**, and continuous overnight work is only possible on what lives in the
repository.

| Path | Source on disk | What it holds |
|---|---|---|
| `book/` | `Master\6S Success Home Edition\` | 50 chapters: manuscripts, final HTML, briefs, signatures, content packages |
| `manual/` | `Desktop\6S-Micro-Zone-Manual-Package\` | Micro Zone Field Manual v3 and its source JSON (20 rooms, 114 zones) |
| `decks/` | `Desktop\6S-Success-Card-Decks\` | Home Quest card lists, architecture, reviews, prompts |
| `games/` | `Desktop\6S-Success-Board-Game\` | Three board game prototypes and sell sheets |
| `appendix/` | `Desktop\6S-Product-Appendix\` | The 123-type product library |
| `video/` | `Desktop\6S-Video-Production-Plan\` | Production plan, tracker, Entryway pilot scripts |
| `app-spec/` | `Desktop\6S-Home-Reset-Product-Spec\` | Product spec, roadmap, review panel |
| `app-mvp/` | `Desktop\6S-Home-MicroZones-MVP-Beta\` | The runnable PWA prototype |

## What is deliberately not here

Images, PDFs, fonts, Office documents and archives. The full estate is about
1.78 GB; the text is 40 MB. Committing 1.74 GB of PNG masters would make the
repository unusable for the agents that need it. They stay on the Desktop.

If image work is ever needed in CI, use Git LFS rather than committing binaries.

## Direction of truth

Right now the Desktop copies are the originals and this is the mirror. Anything
an agent changes here must be treated as the newer version, since the agents can
only work here. Before doing local image work, pull first.
