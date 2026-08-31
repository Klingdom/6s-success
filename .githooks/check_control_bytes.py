"""Refuse source files carrying control bytes. Called by .githooks/pre-commit.

A separate file rather than a heredoc inside the hook, for a reason that is
almost funny: the first version piped the file list into `python -`, and
`python -` reads its *program* from stdin, so the list and the script were
competing for the same channel. The script won, sys.stdin was already consumed,
the loop saw nothing, and the hook reported every commit clean. Third variant
of the same mistake in one sitting, and the third time the tool answered "I
found nothing" when the truth was "I never looked".

Usage: check_control_bytes.py <path> [<path> ...]
Exit 1 if any file carries a byte that does not belong in source.
"""
import io
import os
import sys

# Tab, newline and carriage return are legitimate. Everything else below 0x20,
# plus DEL, is not something a source file should carry.
BAD = (set(range(0, 32)) - {9, 10, 13}) | {127}

EXTS = (".py", ".js", ".css", ".html", ".md", ".yml", ".yaml",
        ".json", ".sh", ".conf")


def main(argv: list) -> int:
    problems = []
    looked = 0
    for path in argv:
        if not path.lower().endswith(EXTS) or not os.path.isfile(path):
            continue
        looked += 1
        try:
            raw = io.open(path, "rb").read()
        except OSError as e:
            problems.append((path, "could not be read (%s)" % e))
            continue
        hits = [(i, b) for i, b in enumerate(raw) if b in BAD]
        if hits:
            where = ", ".join("offset %d: 0x%02x" % (i, b) for i, b in hits[:4])
            problems.append((path, "%d control byte(s): %s"
                             % (len(hits), where)))

    if problems:
        for path, why in problems:
            print("  %s: %s" % (path, why))
        print("")
        print("  Refusing the commit. These are almost always a heredoc that")
        print("  ate a backslash: \\b became 0x08, \\1 became 0x01. The code")
        print("  may still compile, and the pattern will match nothing,")
        print("  silently, for ever.")
        print("")
        print("  Write the patch to a file and run it rather than piping a")
        print("  heredoc. If these bytes truly belong: git commit --no-verify")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
