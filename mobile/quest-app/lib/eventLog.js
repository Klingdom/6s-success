/* A small local record of what this install actually did.
 *
 * Prompt 9 (docs/future-state/) asks the app's own improvement loop to
 * "validate instrumentation before trusting it" and separate observed fact
 * from inference. Before this, the only evidence an on-device pass produced
 * was Phil's memory of what he tapped, in what order. That is exactly the
 * "unknown is not unused" gap CLAUDE.md warns about applied to this app's
 * own testing: a screen reader announcement can be correct and a control can
 * still do nothing (the "Not now" bug this file's sibling, pickCard.js, was
 * written to fix), and a log answers "did it actually happen" instead of "did
 * it feel like it happened."
 *
 * Fully local, exactly like everything else in this app: no network call
 * exists anywhere near this file, and nothing here changes that. Kept
 * separate from App.js for the same reason lib/pickCard.js and
 * lib/importProgress.js are: plain functions, testable with plain node.
 */

const MAX_EVENTS = 300;

/* Append one event, oldest dropped once the log passes MAX_EVENTS so an
 * install running for months cannot grow this without bound. `at` defaults
 * to now but takes an explicit value so tests are deterministic. */
function logEvent(log, type, detail, at) {
  const entry = { type: type, detail: detail == null ? null : detail,
                  at: at == null ? Date.now() : at };
  const next = (log || []).concat([entry]);
  return next.length > MAX_EVENTS ? next.slice(next.length - MAX_EVENTS) : next;
}

/* Counts and span, not just a raw dump: the summary is what answers "did
 * anything happen" at a glance, the raw entries answer "in what order." */
function summarize(log) {
  log = log || [];
  const byType = {};
  for (const e of log) byType[e.type] = (byType[e.type] || 0) + 1;
  return {
    count: log.length,
    byType: byType,
    firstAt: log.length ? log[0].at : null,
    lastAt: log.length ? log[log.length - 1].at : null,
  };
}

/* Plain text, safe to put in a <Text> and read or copy off the screen. Not
 * JSON: the point is a human reading a phone screen, not a machine. */
function formatForDisplay(log) {
  log = log || [];
  const sum = summarize(log);
  if (sum.count === 0) return "No activity recorded yet this install.";
  const lines = [sum.count + " event(s) recorded this install."];
  Object.keys(sum.byType).sort().forEach((t) => {
    lines.push("  " + t + ": " + sum.byType[t]);
  });
  lines.push("");
  const recent = log.slice(-15);
  lines.push("Most recent " + recent.length + ":");
  recent.forEach((e) => {
    const when = new Date(e.at).toISOString();
    lines.push(when + "  " + e.type + (e.detail ? "  " + e.detail : ""));
  });
  return lines.join("\n");
}

module.exports = { MAX_EVENTS, logEvent, summarize, formatForDisplay };
