"""Check whether a keyword-demand query has already been investigated and
declined, before a cycle spends its one workstream re-deriving that by hand.

WHY THIS EXISTS
---------------
GitHub issue #42 names the recurring cost directly: the same room-guide
partial-tier candidates keep surfacing as "promising" on the mechanical
score alone, and the only way any cycle has ever confirmed they are not new
is to grep `ops/NIGHTLY-LOG.md` (2.2 MB) and its archive (13+ MB) by hand for
the exact phrase. At least four recent cycles (A270, A277, A279, A282, and
the entries at NIGHTLY-LOG.md lines ~818, ~1778, ~4231) did exactly that,
each describing it as the alternative to "the same wasted-cycle shape issue
#42 already names". This tool is that grep, automated and reusable, so the
next cycle calls one function instead of re-inventing the search.

It is a lookup aid, not a verdict. A hit means "this phrase (or a close
relative of it) appears in the operating history already" and the cycle
should read the actual surrounding text before concluding anything; a miss
means "nothing found by this search", not "definitely never discussed."

Usage:
    python ops/candidate_history.py "how to organize bulk snacks"
    from candidate_history import search_history
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Every file a prior cycle's own decline reasoning could be written into.
# Ordered roughly by how often a real hit has been found there in practice.
HISTORY_FILES = [
    "ops/NIGHTLY-LOG.md",
    "ops/NIGHTLY-LOG-ARCHIVE.md",
    "BACKLOG-2026-09-07.md",
    "BACKLOG-2026-09-07-ARCHIVE.md",
    "BACKLOG-2026-09-07-CLOSED-ARCHIVE.md",
    "BACKLOG-2026-09-07-SECTION2-ARCHIVE.md",
    "BACKLOG-2026-09-07-ITEMS-ARCHIVE.md",
    "BACKLOG-2026-09-07-SECTION1B-ARCHIVE.md",
    "BACKLOG-2026-09-07-SECTION3-ARCHIVE.md",
    "BACKLOG-2026-09-07-SECTION4-ARCHIVE.md",
    "BACKLOG-2026-09-07-B9-ARCHIVE.md",
    "CHECKIN-LOG.md",
    "CHECKIN-LOG-ARCHIVE.md",
]

# Leading words stripped one at a time when the exact phrase is not found,
# so "how to organise a car boot" can still match a precedent written down
# as just "car boot". Stripping only ever shortens from the front; a query
# that is already short (under 2 remaining words) is left alone rather than
# reduced to one word by this stage (the single-word fallback below handles
# that, explicitly marked weak).
STOP_LEAD = {
    "how", "to", "do", "i", "can", "you", "your", "a", "an", "the",
    "organize", "organise", "in", "for", "my", "of", "set", "up",
    "store", "storage",
}

MAX_HITS_PER_FILE = 3
MAX_LINE_CHARS = 220


def candidate_phrases(query):
    """Yield phrases to try, longest/most-specific first.

    Always tries the exact query first. Then progressively drops leading
    stopwords (never dropping below 2 remaining words). Finally yields the
    single longest content word as a last-resort weak signal.
    """
    query = " ".join(query.lower().split())
    yield query
    words = query.split()
    i = 0
    while i < len(words) and words[i] in STOP_LEAD and (len(words) - (i + 1)) >= 2:
        i += 1
        yield " ".join(words[i:])
    content = [w for w in words if w not in STOP_LEAD and len(w) >= 4]
    if content:
        yield max(content, key=len)


def _grep(phrase, path):
    """Case-insensitive fixed-string grep with line numbers. Returns up to
    MAX_HITS_PER_FILE (line_no, line_text) pairs, or [] on no match/no file.
    """
    if not os.path.exists(path):
        return []
    try:
        out = subprocess.run(
            ["grep", "-n", "-i", "-F", phrase, path],
            capture_output=True, text=True, timeout=30,
        ).stdout
    except (subprocess.TimeoutExpired, OSError):
        return []
    hits = []
    for line in out.splitlines():
        if ":" not in line:
            continue
        lineno, _, text = line.partition(":")
        if not lineno.isdigit():
            continue
        snippet = text.strip()
        if len(snippet) > MAX_LINE_CHARS:
            snippet = snippet[:MAX_LINE_CHARS] + "..."
        hits.append((int(lineno), snippet))
        if len(hits) >= MAX_HITS_PER_FILE:
            break
    return hits


def search_history(query, files=None):
    """Search the operating history for prior mentions of `query`.

    Returns None if nothing is found by any candidate phrase. Otherwise a
    dict: {"matched_on": str, "strength": "strong"|"weak", "hits": [
    {"file": relpath, "line": int, "snippet": str}, ...]}. "strength" is
    "weak" only when the match came from the single-word fallback; a strong
    match used the real query or a multi-word fragment of it.
    """
    files = files if files is not None else HISTORY_FILES
    for phrase in candidate_phrases(query):
        all_hits = []
        for rel in files:
            for lineno, snippet in _grep(phrase, os.path.join(ROOT, rel)):
                all_hits.append({"file": rel, "line": lineno, "snippet": snippet})
        if all_hits:
            strength = "weak" if " " not in phrase else "strong"
            return {"matched_on": phrase, "strength": strength, "hits": all_hits}
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="+", help="the query phrase to check, e.g. a room_guide_underperformance.py row")
    args = ap.parse_args()
    query = " ".join(args.query)
    result = search_history(query)
    if not result:
        print(f"No prior mention found for: {query!r} (checked {len(HISTORY_FILES)} history files)")
        return
    tag = "WEAK (single word only)" if result["strength"] == "weak" else "strong"
    print(f"Prior mention found, matched on {result['matched_on']!r} [{tag}]:")
    for h in result["hits"]:
        print(f"  {h['file']}:{h['line']}: {h['snippet']}")


if __name__ == "__main__":
    main()
