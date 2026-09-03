/* 6S Success Home Quest, mobile.
 *
 * The core loop and nothing else: draw one card, do one bounded job, mark it
 * done, stop without guilt or continue by choice. That is the loop the web
 * Quest was functionally tested against, and it is the whole product until
 * there is evidence a native app earns more than the installable web one.
 *
 * Deliberately absent, and each for a reason rather than an omission:
 *   no account, because a user must get real value before creating one
 *   no network calls at all, because a garage has no signal and a photograph
 *     of somebody's home must not leave the device
 *   no streak pressure, no fake urgency, no manufactured engagement
 *
 * Safety is the fourth S. The order is fixed in the corpus and this file never
 * reorders it.
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  SafeAreaView, ScrollView, StatusBar, StyleSheet, Text, View, Pressable,
  ActivityIndicator,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as DocumentPicker from "expo-document-picker";
import * as FileSystem from "expo-file-system";

import CORPUS from "./assets/quest-corpus.json";
import { parseBackup, mergeDone } from "./lib/importProgress";
import { cardId, pickCard } from "./lib/pickCard";
import { logEvent, formatForDisplay } from "./lib/eventLog";

/* The same key the web app uses, so a future import can recognise its shape. */
const KEY = "6s.quest.v1";

/* A local-only record of what this install did: cards drawn, done, skipped,
 * zones finished, stops and imports, each with a timestamp. Never sent
 * anywhere. It exists so an on-device test pass produces a fact ("the log
 * shows Not now was pressed and the card changed") instead of a memory of
 * what was tapped, see ON-DEVICE-TEST.md's Diagnostics section. */
const DIAG_KEY = "6s.quest.diag.v1";

/* Method order. The corpus already stores steps in this order; this exists so
 * the finish recap can name passes in method order rather than draw order. */
const S_ORDER = ["sort", "straighten", "shine", "safety", "standardize", "sustain"];

const C = {
  deep: "#1A272E",
  panel: "#22323C",
  line: "#33474F",
  ink: "#EDE4D2",
  soft: "#A9B7BE",
  accent: "#BC4B2A",
  honey: "#DDA63A",
  good: "#6E8B5B",
};

/* Border and dot colour. These are non-text UI components (WCAG 1.4.11,
 * 3:1 floor against the screen background), not body text, and every value
 * here clears that floor against C.deep. Kept exactly as the brand's pass
 * colours: nothing here needed correcting. */
const PASS_COLOUR = {
  sort: "#CB4B36",
  straighten: "#D98A2B",
  shine: "#DDA63A",
  safety: "#BC4B2A",
  standardize: "#6E8B5B",
  sustain: "#4E7A57",
};

/* Badge TEXT colour, deliberately separate from PASS_COLOUR above.
 *
 * Found 2026-09-03: the badge reuses PASS_COLOUR for its text too, and the
 * badge word ("sort", "safety", ...) is 12px bold, well under the WCAG 2.2
 * large-text threshold (14pt/~18.7px bold or 18pt/24px regular) that would
 * excuse a 3:1 floor. Ordinary text needs 4.5:1. Computed against C.deep with
 * the real relative-luminance formula rather than assumed: four of six
 * PASS_COLOUR values fall short (sort 3.35, safety 3.04, standardize 4.01,
 * sustain 3.09), the same 3.04 a prior cycle recorded in BACKLOG-2026-H2.md
 * 5B.9 as "passing... against a 3.0 floor" (the large-text floor, applied to
 * text that does not qualify as large). Each shortfall lightened along its
 * own hue until it clears 4.5:1 with margin (>=4.6), verified by
 * ops/preflight.py's gate_mobile_badge_contrast rather than eyeballed;
 * straighten and shine were already clear and are unchanged. The border and
 * dots keep the original brand colour above: both are decorative or
 * non-text, and the pass name itself is also plain text content, so colour
 * was never the only carrier of which S is showing (the mobile prompt's own
 * "colour cannot be the only carrier of S identity" rule). */
const BADGE_TEXT_COLOUR = {
  sort: "#D67161",
  straighten: "#D98A2B",
  shine: "#DDA63A",
  safety: "#D87152",
  standardize: "#789763",
  sustain: "#639B6E",
};

export default function App() {
  const [done, setDone] = useState(null);      // null until storage has been read
  const [session, setSession] = useState([]);  // passes finished this sitting
  const [finished, setFinished] = useState(null);
  const [importMsg, setImportMsg] = useState(null);
  const [skipped, setSkipped] = useState({});  // session-only, cleared on reset
  const [idle, setIdle] = useState(false);     // true after "Stop here, this counts"
  const [log, setLog] = useState([]);
  const [showDiag, setShowDiag] = useState(false);

  useEffect(() => {
    let alive = true;
    AsyncStorage.getItem(KEY)
      .then((raw) => {
        if (!alive) return;
        let parsed = {};
        try { parsed = raw ? (JSON.parse(raw).done || {}) : {}; } catch (e) { parsed = {}; }
        setDone(parsed);
      })
      .catch(() => alive && setDone({}));
    AsyncStorage.getItem(DIAG_KEY)
      .then((raw) => {
        if (!alive) return;
        try { setLog(raw ? JSON.parse(raw) : []); } catch (e) { setLog([]); }
      })
      .catch(() => {});
    return () => { alive = false; };
  }, []);

  const persist = useCallback((next) => {
    setDone(next);
    AsyncStorage.setItem(KEY, JSON.stringify({ done: next })).catch(() => {});
  }, []);

  const record = useCallback((type, detail) => {
    setLog((prev) => {
      const next = logEvent(prev, type, detail);
      AsyncStorage.setItem(DIAG_KEY, JSON.stringify(next)).catch(() => {});
      return next;
    });
  }, []);

  /* The next card is the first unfinished, unskipped pass of the first zone
   * that has any, walking the corpus in its own order. Predictable beats
   * random: somebody coming back should continue where the house was left,
   * not be handed an unrelated room. A skipped card is passed over rather
   * than shown again immediately, see lib/pickCard.js. */
  const card = useMemo(() => {
    if (!done) return null;
    return pickCard(CORPUS, done, skipped);
  }, [done, skipped]);

  const zoneProgress = useMemo(() => {
    if (!done || !card) return { finished: 0, total: 0 };
    const total = card.zone.steps.length;
    const fin = card.zone.steps.filter((s) => done[cardId(card.zone, s.s)]).length;
    return { finished: fin, total };
  }, [done, card]);

  const zonesHeld = useMemo(() => {
    if (!done) return 0;
    return CORPUS.zones.filter(
      (z) => z.steps.every((s) => done[cardId(z, s.s)])
    ).length;
  }, [done]);

  function markDone() {
    if (!card) return;
    const id = cardId(card.zone, card.step.s);
    const next = { ...done, [id]: Date.now() };
    const zoneNowComplete = card.zone.steps.every(
      (s) => next[cardId(card.zone, s.s)]
    );
    record("card_done", id);
    setSession(session.concat(card.step.s));
    persist(next);
    if (zoneNowComplete) {
      record("zone_finished", card.zone.zone);
      setFinished({ zone: card.zone, passes: session.concat(card.step.s) });
    }
  }

  function skip() {
    /* Skipping does not mark anything done. It moves the card to the back of
     * this session's own order by name, so the next unfinished card is shown
     * instead, and this one comes back once nothing else is left. Honest,
     * and it keeps "done" meaning done. */
    if (!card) return;
    const id = cardId(card.zone, card.step.s);
    record("card_skipped", id);
    setSkipped((prev) => (prev[id] ? prev : { ...prev, [id]: true }));
  }

  /* Somebody who already worked the web Quest and now installs the app should
   * not start over. The web app's own backup() writes { done: {...} } with
   * the identical cardId shape this app already uses, so a raw browser
   * backup file merges straight in, same rule as the web restore(): the
   * earlier timestamp wins, so importing can never erase work done on the
   * phone since the backup was taken. */
  async function importBackup() {
    setImportMsg(null);
    let picked;
    try {
      picked = await DocumentPicker.getDocumentAsync({
        type: "application/json",
        copyToCacheDirectory: true,
      });
    } catch (e) {
      record("import_failed", "picker error");
      setImportMsg("Could not open the file picker.");
      return;
    }
    if (picked.canceled || !picked.assets || !picked.assets[0]) return;
    let text;
    try {
      text = await FileSystem.readAsStringAsync(picked.assets[0].uri);
    } catch (e) {
      record("import_failed", "read error");
      setImportMsg("Could not read that file.");
      return;
    }
    const incoming = parseBackup(text);
    if (!incoming) {
      record("import_failed", "not a Home Quest backup");
      setImportMsg("That file was not a Home Quest backup.");
      return;
    }
    const { done: merged, changed } = mergeDone(done, incoming.done);
    persist(merged);
    record("import_ok", changed + " changed");
    setImportMsg(
      changed === 0
        ? "Already up to date with that backup."
        : changed + (changed === 1 ? " card" : " cards") + " imported from the browser."
    );
  }

  if (done === null) {
    return (
      <SafeAreaView style={[s.screen, s.centre]}>
        <StatusBar barStyle="light-content" />
        <ActivityIndicator color={C.honey} />
      </SafeAreaView>
    );
  }

  if (finished) {
    const counts = {};
    finished.passes.forEach((p) => { counts[p] = (counts[p] || 0) + 1; });
    const words = S_ORDER.filter((p) => counts[p])
      .map((p) => counts[p] + " " + p).join(", ");
    return (
      <SafeAreaView style={s.screen}>
        <StatusBar barStyle="light-content" />
        <ScrollView contentContainerStyle={s.pad}>
          <Text style={s.eyebrow}>THAT IS A ZONE</Text>
          <Text style={s.h1}>{finished.zone.zone}</Text>
          <Text style={s.body}>
            All six passes are done. {finished.zone.done}
          </Text>
          <View style={s.dots} importantForAccessibility="no-hide-descendants"
                accessibilityElementsHidden={true}>
            {finished.passes.slice().sort(
              (a, b) => S_ORDER.indexOf(a) - S_ORDER.indexOf(b)
            ).map((p, i) => (
              <View key={i} style={[s.dot, { backgroundColor: PASS_COLOUR[p] }]} />
            ))}
          </View>
          <Text style={s.note}>{words}</Text>
          <Text style={s.note}>
            {zonesHeld} of {CORPUS.zoneCount} zones in the house
            {zonesHeld === 1 ? "is" : "are"} holding.
          </Text>
          <Pressable style={s.primary} accessibilityRole="button"
                     accessibilityLabel="Draw the next card"
                     accessibilityHint="Opens the next card in the house"
                     onPress={() => { setSession([]); setSkipped({}); setFinished(null); }}>
            <Text style={s.primaryText}>Draw the next card</Text>
          </Pressable>
          <Pressable style={s.ghost} accessibilityRole="button"
                     accessibilityLabel="Stop here, this counts"
                     accessibilityHint="Saves what you finished and stops without showing another card"
                     onPress={() => { record("stopped", null); setSession([]); setSkipped({}); setFinished(null); setIdle(true); }}>
            <Text style={s.ghostText}>Stop here, this counts</Text>
          </Pressable>
        </ScrollView>
      </SafeAreaView>
    );
  }

  /* "Stop here, this counts" has to actually stop: showing the next open
   * card the moment it is pressed would mean there is never a way to put
   * the house down, only two buttons that both say "keep going" in
   * different words. Progress is already persisted (persist() ran inside
   * markDone before this screen ever showed), so idle has nothing left to
   * save; it exists purely to not draw another card until asked. */
  if (idle) {
    return (
      <SafeAreaView style={[s.screen, s.centre]}>
        <StatusBar barStyle="light-content" />
        <Text style={s.h1}>Good stopping point.</Text>
        <Text style={s.body}>
          {zonesHeld} of {CORPUS.zoneCount} zones in the house holding.
          Nothing here expects you back at any particular time.
        </Text>
        <Pressable style={s.primary} accessibilityRole="button"
                   accessibilityLabel="Draw a card"
                   accessibilityHint="Opens the next card in the house"
                   onPress={() => setIdle(false)}>
          <Text style={s.primaryText}>Draw a card</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  if (!card) {
    return (
      <SafeAreaView style={[s.screen, s.centre]}>
        <StatusBar barStyle="light-content" />
        <Text style={s.h1}>Every card is done.</Text>
        <Text style={s.body}>
          All {CORPUS.cardCount} cards across {CORPUS.zoneCount} zones are
          finished. The house is holding.
        </Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={s.screen}>
      <StatusBar barStyle="light-content" />
      <ScrollView contentContainerStyle={s.pad}>
        <View style={s.row}>
          <View style={[s.badge, { borderColor: PASS_COLOUR[card.step.s] }]}
                accessibilityRole="text"
                accessibilityLabel={"Pass " + (zoneProgress.finished + 1) +
                  " of " + zoneProgress.total + ", " + card.step.s}>
            <Text style={[s.badgeText, { color: BADGE_TEXT_COLOUR[card.step.s] }]}>
              {card.step.s}
            </Text>
          </View>
          <Text style={s.count}>
            {zoneProgress.finished + 1} of {zoneProgress.total}
          </Text>
        </View>

        <Text style={s.where}>{card.zone.room} &gt; {card.zone.zone}</Text>
        <Text style={s.h1}>{card.zone.purpose}</Text>
        <Text style={s.body}>{card.step.text}</Text>

        <View style={s.panel}>
          <Text style={s.panelHead}>DONE LOOKS LIKE</Text>
          <Text style={s.panelBody}>{card.zone.done}</Text>
        </View>

        <Text style={s.note}>About {card.zone.session} for the whole zone.</Text>

        <Pressable style={s.primary} accessibilityRole="button"
                   accessibilityLabel="Mark this card done"
                   accessibilityHint="Records this pass and moves to the next card"
                   onPress={markDone}>
          <Text style={s.primaryText}>Done</Text>
        </Pressable>
        <Pressable style={s.ghost} accessibilityRole="button"
                   accessibilityLabel="Not now"
                   accessibilityHint="Leaves this card unfinished and keeps it for next time"
                   onPress={skip}>
          <Text style={s.ghostText}>Not now</Text>
        </Pressable>

        <Text style={s.foot}>
          {zonesHeld} of {CORPUS.zoneCount} zones holding. Progress is on this
          device only, and nothing is sent anywhere.
        </Text>

        <Pressable style={s.importLink} accessibilityRole="button"
                   accessibilityLabel="Import progress from the web Quest"
                   accessibilityHint="Opens a file picker for a Home Quest backup file"
                   onPress={importBackup}>
          <Text style={s.importLinkText}>
            Already used the web Quest? Import your progress
          </Text>
        </Pressable>
        {importMsg ? <Text style={s.importMsg}>{importMsg}</Text> : null}

        <Pressable style={s.importLink} accessibilityRole="button"
                   accessibilityLabel="Diagnostics"
                   accessibilityHint="Shows a local record of what this install has done, kept on this device only"
                   onPress={() => setShowDiag((v) => !v)}>
          <Text style={s.importLinkText}>
            {showDiag ? "Hide diagnostics" : "Diagnostics"}
          </Text>
        </Pressable>
        {showDiag ? (
          <Text selectable style={s.diagText}>{formatForDisplay(log)}</Text>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: C.deep },
  centre: { alignItems: "center", justifyContent: "center", padding: 24 },
  pad: { padding: 22, paddingBottom: 48 },
  row: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  badge: {
    borderWidth: 1.5, borderRadius: 999, paddingVertical: 5, paddingHorizontal: 12,
  },
  badgeText: { fontSize: 12, fontWeight: "700", letterSpacing: 1.2, textTransform: "uppercase" },
  count: { color: C.soft, fontSize: 13, letterSpacing: 0.6 },
  where: { color: C.soft, fontSize: 13, marginTop: 18, letterSpacing: 0.4 },
  eyebrow: { color: C.honey, fontSize: 12, fontWeight: "700", letterSpacing: 2 },
  h1: { color: C.ink, fontSize: 26, fontWeight: "700", marginTop: 8, lineHeight: 33 },
  body: { color: C.ink, fontSize: 17, lineHeight: 26, marginTop: 14 },
  panel: {
    backgroundColor: C.panel, borderColor: C.line, borderWidth: 1,
    borderRadius: 14, padding: 16, marginTop: 20,
  },
  panelHead: { color: C.soft, fontSize: 11, fontWeight: "700", letterSpacing: 1.4 },
  panelBody: { color: C.ink, fontSize: 15, lineHeight: 23, marginTop: 8 },
  note: { color: C.soft, fontSize: 14, marginTop: 16, lineHeight: 21 },
  primary: {
    backgroundColor: C.accent, borderRadius: 999, paddingVertical: 16,
    alignItems: "center", marginTop: 26,
  },
  primaryText: { color: "#fff", fontSize: 17, fontWeight: "700" },
  ghost: {
    borderColor: C.line, borderWidth: 1, borderRadius: 999, paddingVertical: 14,
    alignItems: "center", marginTop: 12,
  },
  ghostText: { color: C.ink, fontSize: 15, fontWeight: "600" },
  foot: { color: C.soft, fontSize: 13, lineHeight: 20, marginTop: 26 },
  importLink: { marginTop: 18, alignItems: "center" },
  importLinkText: {
    color: C.soft, fontSize: 13, textDecorationLine: "underline",
  },
  importMsg: {
    color: C.honey, fontSize: 13, textAlign: "center", marginTop: 8,
  },
  diagText: {
    color: C.soft, fontSize: 11, lineHeight: 16, marginTop: 12,
    fontFamily: "monospace",
  },
  dots: { flexDirection: "row", flexWrap: "wrap", marginTop: 18 },
  dot: { width: 14, height: 14, borderRadius: 7, marginRight: 7, marginBottom: 7 },
});
