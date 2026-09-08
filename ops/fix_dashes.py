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
#
# The bare-word branch originally allowed up to 45 characters of plain text
# with no other structure, which is not what "label" means in any of this
# rule's own examples (PHASE 1, L3, Level 0, PRD-XXX, 5 min: one to two
# words, always). Found 2026-09-07: "This is not deceptive" and "true and
# drawn from the page", ordinary clauses that happen to be short and
# punctuation-free, both matched it and both got a colon where a comma was
# needed ("not deceptive: ... but", a colon immediately followed by "but").
# Capped at 3 space-separated words. This cannot regress a file this tool
# already fixed: every em/en dash in a file this rule previously matched is
# gone from that file's text now, replaced by the colon or comma it chose,
# so a stricter rule here only changes behaviour for dashes not yet
# resolved, never one already shipped.
LABELISH = re.compile(r"""^(
      \#{1,6}\s.*                      # markdown heading
    | \*\*[^*]+\*\*                    # a bold label
    | `[^`]+`                          # a code-span label
    | [A-Za-z0-9][A-Za-z0-9_.\-/]{0,20}(?:\s[A-Za-z0-9][A-Za-z0-9_.\-/]{0,20}){0,2}
                                        # PHASE 1, L3, Level 0, PRD-XXX, 5 min
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

# A real label introduces its value; it is never followed by a word that
# continues a clause instead. Found 2026-09-07, still wrong after the
# word-count cap above: "and found none -- but the line item..." (head "and
# found none", 3 words, under the cap) and "**Yes -- and the tool..." (head
# "Yes", 1 word) both still read as labels, because a short ordinary clause
# fragment is exactly as short as a real label by word count alone; nothing
# about length distinguishes "L3" from "and found none". What does
# distinguish them is what comes next: a label's value is a description,
# never a bare coordinating conjunction or relative pronoun picking the
# sentence back up. Checked against every real label this file's own tests
# and docstring name (numbers, phase names, identifiers): none of their
# values start with one of these words.
CONTINUATION = re.compile(
    r"^(?:and|but|or|nor|so|yet|which|that|because|though|while|if)\b",
    re.I)

def is_continuation(tail):
    return bool(CONTINUATION.match(tail.lstrip()))

def fix_line(line):
    """Return the line with every spaced em dash resolved, and a per-rule tally."""
    counts = {"label": 0, "clause": 0, "cell": 0}

    # A table cell holding nothing but a dash means "not applicable". A comma
    # there would be nonsense and a colon worse, so it becomes a plain hyphen.
    if line.lstrip().startswith("|"):
        line, n = re.subn(r"(?<=\|)(\s*)—(\s*)(?=\|)", r"\1-\2", line)
        counts["cell"] += n

    # A dash with a leading space but nothing whitespace-shaped right after
    # it (either the line ends there, hard-wrapped mid-sentence, or the next
    # character is markup like a closing "*" with no space of its own)
    # never matches "\s+em-dash\s+", which requires whitespace on BOTH
    # sides, so it fell through to the "unspaced survivor" fallback below.
    # That fallback replaces only the dash character and leaves the genuine
    # leading space untouched. Found 2026-09-07, two shapes, both in
    # REVIEW-COMMERCE-2026-09-07.md: "...invite —" (end of line, sentence
    # continuing as "*\"When the customer..." on the next physical line)
    # became "...invite , " (stray space before the comma, stray trailing
    # space); "...a reason —* and" became "...a reason , * and" (same stray
    # leading space, and a space now sitting between the comma and "*" that
    # was never there).
    #
    # Always a comma, never is_label()'s colon: every real label in this
    # tool's own examples ("L1", "PHASE 1", "Level 0", "PRD-XXX") is
    # followed immediately by its value on the SAME line, with a normal
    # space; nothing here is a label whose value got pushed past a hard
    # line-wrap or glued to markup instead. Skipping the label test also
    # sidesteps a second, independent bug this same case exposed: a two-dash
    # aside split across a line-wrap ("This is not deceptive --\ntrue --\n
    # but...", each dash landing at its own line's end) never reaches the
    # same-line pair check below at all, and is_label() reads a short plain
    # clause like "This is not deceptive" as a label on its own, so both
    # ends of the aside got a colon independently: "not deceptive: ...
    # page: but the markup...", a colon immediately followed by "but".
    def comma(m):
        counts["clause"] += 1
        return ","

    line = re.sub(r"(?<=\S)\s+—(?!\s)", comma, line)

    # A pair of em dashes bracketing one aside ("X -- aside -- Y", one
    # sentence, nothing between them ending the sentence first) is a single
    # unit, not two independent breaks. Found 2026-09-07: is_label() reads
    # "This is not deceptive" as a label (it is short, plain words, no
    # trailing colon, and the generic bare-text branch of LABELISH does not
    # require anything more label-like than that), so the first dash of a
    # pair got a colon and the second got a colon too, printing
    # "not deceptive: every answer is true: but the markup...", a colon
    # immediately followed by "but" that a single-dash line would never
    # produce. Both dashes in a real pair become commas unconditionally;
    # is_label() is only trustworthy for a lone dash, where the label
    # reading (if wrong) still leaves a readable colon rather than this
    # double-break shape.
    #
    # Found 2026-09-08, live in STATUS.md: a THIRD spaced em dash later on
    # the same line (a separate aside earlier in the sentence, e.g.
    # "the cart (never reachable -- ...) and X -- which measured Y -- now
    # does") is invisible to the two-dash pair regex above, which pairs the
    # first two dashes it finds regardless of whether they actually bracket
    # one aside. `count=2` below correctly leaves that third dash spaced and
    # untouched, but the line that followed it, `out.replace("--", ", ")`,
    # replaced only the dash character and left both of its real spaces in
    # place: "`opacity` -- now" became "`opacity` ,  now", a stray leading
    # space before the comma and a stray double space after it. Every other
    # dash-handling path in this file (line 132's unspaced-survivor rule,
    # line 165's non-pair substitution) already consumes the surrounding
    # whitespace with `\s+`/`\s*`; only this one fallback used a bare
    # character replace. Changed to the same whitespace-consuming shape.
    pair = re.search(r"\s+—\s+[^.!?—]*\s+—\s+", line)
    if pair:
        counts["clause"] += 2
        out = re.sub(r"\s+—\s+", ", ", line, count=2)
        counts["clause"] += len(re.findall(r"\s*—\s*", out))
        out = re.sub(r"\s*—\s*", ", ", out)
        out = re.sub(r"\s*–\s*", "-", out)
        return out, counts

    def sub(m):
        before = line[:m.start()]
        # Only the text since the last sentence end matters for the label test.
        head = re.split(r"(?<=[.!?])\s+", before)[-1].rstrip()
        if is_label(head) and not is_continuation(line[m.end():]):
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
