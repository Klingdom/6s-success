#!/usr/bin/env python3
"""
Bring the control layer into line with the house style it enforces.

The published estate carries zero em and en dashes. The control documents that
tell every agent to write that way carried 483 em and 53 en dashes, and agents
read those documents as authority, so the rule was being unwritten by the files
that stated it. That is the defect this fixes.

The substitution is not blind. Every em dash in these files is a spaced one, and
they fall into two jobs:

  label      "L1 - Instruction Compliance", "## Level 0 - Chat/Log History"
             A short name, then what it means. That is a colon.
  clause     ordinary prose where the dash interrupts a sentence.
             That is a comma.

En dashes are all numeric or ordinal ranges, so they become hyphens, which is
the same call the Micro Zone Manual already made for its session times.

Run:      python ops/fix_dashes.py --check     report only, exit 1 if any remain
          python ops/fix_dashes.py --apply     rewrite the files
"""
import glob, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def targets():
    return sorted(set(glob.glob(os.path.join(ROOT, "*.md"))
                      + glob.glob(os.path.join(ROOT, "claude", "**", "*.md"), recursive=True)))

# A label is short, has no sentence punctuation, and is the sort of thing that
# wants a colon after it: a heading, a bold run, an identifier, a numbered stage.
LABELISH = re.compile(r"""^(
      \#{1,6}\s.*                      # markdown heading
    | \*\*[^*]+\*\*                    # a bold label
    | `[^`]+`                          # a code-span label
    | [A-Za-z0-9][A-Za-z0-9_.\-/ ]{0,44}  # PHASE 1, L3, Level 0, PRD-XXX, 5 min
    | \d+\.\s+[^.]{0,44}               # 1. Commands
  )$""", re.X)

# List and blockquote markers are never part of the label, so they always come
# off before the test.
MARKER = re.compile(r"^\s*(?:[-*+]\s+|>\s*)*")
# Emphasis is different, and needs both readings. Usually the emphasis closes
# around the label alone, "**Commands** - request a state change", and the head
# must keep its markers so the bold-label rule can see a balanced pair. But it
# sometimes opens before the label and closes after the value, "**EXP-XXXX -
# Short title**", leaving the head unbalanced. Stripping unconditionally breaks
# the first case; never stripping breaks the second. So try it both ways.
OPENER = re.compile(r"^(?:\*\*|`|\*|_)\s*")

def is_label(head):
    head = MARKER.sub("", head).rstrip()
    if head.endswith(":"):
        return False
    return bool(LABELISH.match(head) or LABELISH.match(OPENER.sub("", head)))

def fix_line(line):
    """Return the line with every spaced em dash resolved, and a per-rule tally."""
    counts = {"label": 0, "clause": 0, "cell": 0}

    # A table cell holding nothing but a dash means "not applicable". A comma
    # there would be nonsense and a colon worse, so it becomes a plain hyphen.
    if line.lstrip().startswith("|"):
        line, n = re.subn(r"(?<=\|)(\s*)—(\s*)(?=\|)", r"\1-\2", line)
        counts["cell"] += n

    def sub(m):
        before = line[:m.start()]
        # Only the text since the last sentence end matters for the label test.
        head = re.split(r"(?<=[.!?])\s+", before)[-1].rstrip()
        if is_label(head):
            counts["label"] += 1
            return ": "
        counts["clause"] += 1
        return ", "

    out = re.sub(r"\s+—\s+", sub, line)
    # Any unspaced survivor (there are none today, but do not silently pass one).
    out = out.replace("—", ", ")
    # Ranges: en dash to hyphen, with the surrounding spacing left alone.
    out = re.sub(r"\s*–\s*", "-", out)
    return out, counts

def run(apply_it):
    total = {"label": 0, "clause": 0, "cell": 0, "en": 0}
    touched = []
    for path in targets():
        text = io.open(path, encoding="utf-8").read()
        if "—" not in text and "–" not in text:
            continue
        total["en"] += text.count("–")
        lines = text.split("\n")
        new = []
        for line in lines:
            fixed, c = fix_line(line)
            total["label"] += c["label"]
            total["clause"] += c["clause"]
            total["cell"] += c["cell"]
            new.append(fixed)
        result = "\n".join(new)
        if result != text:
            touched.append((os.path.relpath(path, ROOT), text, result))
            if apply_it:
                io.open(path, "w", encoding="utf-8", newline="").write(result)
    return total, touched

def remaining():
    bad = []
    for path in targets():
        t = io.open(path, encoding="utf-8").read()
        if "—" in t or "–" in t:
            bad.append((os.path.relpath(path, ROOT), t.count("—"), t.count("–")))
    return bad

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode == "--check":
        bad = remaining()
        for f, em, en in bad:
            print(f"  {f}: {em} em, {en} en")
        print(f"{len(bad)} control files still break the house style"
              if bad else "control layer is clean: 0 em dashes, 0 en dashes")
        sys.exit(1 if bad else 0)
    if mode == "--apply":
        total, touched = run(True)
        print(f"rewrote {len(touched)} files")
        print(f"  {total['label']} label separators became colons")
        print(f"  {total['clause']} clause breaks became commas")
        print(f"  {total['cell']} not-applicable table cells became hyphens")
        print(f"  {total['en']} en dash ranges became hyphens")
        sys.exit(0)
    # preview: show every changed line, grouped, so the call can be eyeballed
    total, touched = run(False)
    shown = 0
    for rel, old, new in touched:
        for a, b in zip(old.split("\n"), new.split("\n")):
            if a != b and shown < int(sys.argv[2] if len(sys.argv) > 2 else 40):
                print(f"{rel}\n  -  {a.strip()[:150]}\n  +  {b.strip()[:150]}")
                shown += 1
    print(f"\n{len(touched)} files, {total['label']} labels, {total['clause']} clauses, "
          f"{total['en']} ranges")
