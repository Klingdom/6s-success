#!/usr/bin/env bash
# Canonical way to run preflight.py in an agent sandbox with a short
# per-command foreground timeout (the harness default is commonly ~110-120s).
#
# Why this exists: preflight.py's own docstring has warned since before this
# script existed not to wrap the command in a foreground timeout shorter than
# about 1050 seconds, because a killed process leaves generators mid-chain
# (real incidents: an unfilled front-matter placeholder nearly shipped, an
# orphaned audit-catalog lockdir on 2026-09-11, -16 and twice on -23). The
# warning alone did not stop the mistake: "foreground timeout" appears
# dozens of times in ops/NIGHTLY-LOG.md as a caught-and-rerun incident. This
# script is the fix that does not depend on anyone remembering the warning:
# it always launches preflight.py detached (nohup, backgrounded, disowned)
# and polls for it, so the process itself can never be killed by a caller's
# foreground timeout, only this poll loop can, and re-running the poll finds
# the still-running (or by-then-finished) job rather than restarting it.
#
# Usage:
#   ops/run_preflight.sh [--deep] [--own]   same flags as preflight.py
#
# Prints preflight's own output as it runs and exits with preflight's own
# exit code. Safe to call from a shell tool with any foreground timeout,
# including one shorter than preflight.py's own runtime.

set -u
cd "$(dirname "$0")/.."

STATE="/tmp/.run_preflight_state"

# Attach to an already-running preflight.py from an earlier, interrupted
# call to this script rather than starting a second, concurrent one (the
# 2026-09-x incident this log records: two preflight runs against the same
# working tree at once). Only trust the recorded PID if that PID is still
# actually a live preflight.py process.
if [ -f "$STATE" ]; then
    read -r OLD_PID OLD_LOG < "$STATE" 2>/dev/null || true
    if [ -n "${OLD_PID:-}" ] && kill -0 "$OLD_PID" 2>/dev/null \
        && ps -p "$OLD_PID" -o args= 2>/dev/null | grep -q "ops/preflight.py"; then
        PID="$OLD_PID"
        LOG="$OLD_LOG"
    fi
fi

if [ -z "${PID:-}" ]; then
    LOG="$(mktemp /tmp/preflight_run.XXXXXX.log)"
    # setsid, not just nohup+disown: measured directly (2026-09-28) that a
    # caller killed by SIGTERM/SIGKILL takes a plain nohup'd, disowned child
    # down with it, because the signal targets the whole process group and
    # nohup/disown only stop SIGHUP and shell job-control cleanup, not a
    # group-wide signal. setsid puts preflight.py in its own session with
    # its own process group, so a signal aimed at this wrapper's group
    # cannot reach it.
    setsid nohup python ops/preflight.py "$@" >"$LOG" 2>&1 < /dev/null &
    PID=$!
    disown "$PID" 2>/dev/null || true
    printf '%s %s\n' "$PID" "$LOG" > "$STATE"
fi

DONE_MARKER="${LOG}.exitcode"

# Wait for the backgrounded process without imposing our own cap; a caller
# whose own foreground timeout fires while this loop is waiting kills only
# this wrapper, never the detached preflight.py, so a second call to this
# script (or a manual `wait`/tail on $LOG) picks up the same run.
while kill -0 "$PID" 2>/dev/null; do
    sleep 2
done
wait "$PID"
CODE=$?

cat "$LOG"
echo "$CODE" > "$DONE_MARKER"
rm -f "$STATE"
exit "$CODE"
