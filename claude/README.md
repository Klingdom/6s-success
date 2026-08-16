# Versioned copy of the agent definitions

These 14 files are the **source of truth under version control** for the 6S Success
agents. They are byte-identical to the installed copies.

## Where they actually run from

Claude Code loads agents from `~/.claude/agents/` (user scope) or `.claude/agents/`
(project scope). They are installed at **user scope**, so they work from any
working directory rather than only this repository.

This directory is deliberately named `claude/` and not `.claude/`. If it were
`.claude/agents/`, the same 14 agents would be defined twice whenever a session
runs in this repository, once at project scope and once at user scope. Keeping
the versioned copy here avoids that collision while still giving them history,
diffs and a backup.

## Keeping the two in sync

After editing an agent here, reinstall it:

```bash
cp claude/agents/*.md ~/.claude/agents/
```

After editing an installed agent, copy it back and commit:

```bash
cp ~/.claude/agents/*.md claude/agents/
```

`AUTONOMY.md` was removed from this directory because it duplicated the copy at
the repository root, which is the canonical one.
