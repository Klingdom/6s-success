# This directory is a dated snapshot, not the source of truth

These 78 files were copied here on **2026-08-16** by the commit "Mirror the text
of the whole estate into content/ so agents can work on it". They have not been
touched since. The originals they were copied from live at the repository root
and have moved on.

Measured on 2026-08-31: **123 of the 161 duplicated filenames across this
repository have drifted from their originals**, and most of that drift is here.
The differences are small, a separator character or a phrase, but small is not
the point. If you read `AGENT-ROUTING.md` or `AUTONOMY-API.md` in this
directory believing it is current, you are reading instructions that are two
weeks old.

## Where the current versions are

| Here | Authoritative |
|---|---|
| `AGENT-*.md`, `AUTONOMY-*.md`, and the other control docs | the repository root |
| `agents/*.md` | `claude/agents/`, and see `claude/README.md` |
| `super prompts/*.md` | `super prompts/` at the repository root |

## Why it is still here

It is indexed by `ops/corpus-index.json`, which `ops/corpus_posts.py` reads to
draw real social posts out of the corpus rather than inventing them. These files
are classified `kind: other` and `ready: false`, so two independent guards keep
them out of anything published. They are inert, not load bearing.

## What to do with it

Nothing automatic. Deleting 78 tracked files is Phil's call, not a maintenance
task, and the mirror costs nothing while it is labelled. What it must not do is
sit here unlabelled looking like a second, equally valid copy of the operating
system, which is what it was doing until this file was added.

If the mirror is ever wanted current again, it is a copy, so re-copy it. Do not
edit these files: an edit here goes nowhere, and widens the gap.
