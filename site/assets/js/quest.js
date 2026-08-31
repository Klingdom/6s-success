/* The Home Quest.
 *
 * The card deck's loop, over all 114 micro zones: draw a card, do one thing,
 * put it down. Every card comes from window.QUEST, generated from the same
 * manual the book and the zone pages are built from.
 *
 * No account and no server. Progress lives in this browser and goes nowhere,
 * which is both the honest choice for a household app and the only one a
 * static site allows.
 */
(function () {
  "use strict";

  var Q = window.QUEST;
  if (!Q) { return; }

  var KEY = "6s.quest.v1";
  var $ = function (s) { return document.querySelector(s); };

  /* ---------------------------------------------------------------- state */

  function load() {
    try {
      var s = JSON.parse(localStorage.getItem(KEY) || "{}");
      if (!s.done) { s.done = {}; }
      return s;
    } catch (e) {
      /* A corrupt entry should cost somebody their progress, not the app. */
      return { done: {} };
    }
  }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }

  var state = load();
  var run = null;   /* the queue being worked right now, not persisted */

  function cardId(c) { return c.room + "|" + c.zone.zone + "|" + c.step.s; }
  function isDone(c) { return !!state.done[cardId(c)]; }

  /* ---------------------------------------------------------------- deck */

  function allCards() {
    var out = [];
    Q.rooms.forEach(function (r) {
      r.zones.forEach(function (z) {
        z.steps.forEach(function (st) {
          out.push({ room: r.room, roomSlug: r.slug, zone: z, step: st });
        });
      });
    });
    return out;
  }

  var DECK = allCards();

  /* 684 cards is not a number anybody finishes, and a bar toward it reads as
   * discouraging rather than motivating. A zone (six cards, one per S) is a
   * real, reachable unit, so it is the number the start screen leads with.
   * Total computed once from the same data the deck is built from, so it can
   * never drift from it. */
  var TOTAL_ZONES = Q.rooms.reduce(function (n, r) { return n + r.zones.length; }, 0);

  var reduceMotion = !!(window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches);

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /* Build the queue for a way of playing. Cards already done are filtered out
   * everywhere, because the point is what is left rather than what was. */
  function build(mode, roomName, zoneName, s) {
    var pool = DECK.filter(function (c) { return !isDone(c); });
    if (roomName) {
      pool = pool.filter(function (c) { return c.room === roomName; });
    }
    if (zoneName) {
      pool = pool.filter(function (c) { return c.zone.zone === zoneName; });
    }
    if (s) {
      pool = pool.filter(function (c) { return c.step.s === s; });
    }
    if (mode === "draw") {
      return shuffle(pool).slice(0, 1);
    }
    /* Zone and room runs stay in method order. The six S's only work in
     * sequence: straightening before sorting just rearranges what should have
     * left, and a standard written before the clean describes the wrong room. */
    return pool;
  }

  /* A zone page's own "Or draw a card free" link passes the same slug its
   * z.url already carries, so the visitor who was just reading about one
   * zone lands on that zone, not a random one across the whole house. */
  function findZoneBySlug(slug) {
    for (var i = 0; i < Q.rooms.length; i++) {
      var r = Q.rooms[i];
      for (var j = 0; j < r.zones.length; j++) {
        var z = r.zones[j];
        if (z.url && z.url.split("/").pop() === slug) {
          return { room: r.room, zone: z.zone };
        }
      }
    }
    return null;
  }

  /* A room page's own "Or draw a card free" link carries that room's slug,
   * the same one quest-data.js already stamps on every room, so the visitor
   * lands in that room's own run instead of the general start screen and its
   * two dropdowns. */
  function findRoomBySlug(slug) {
    for (var i = 0; i < Q.rooms.length; i++) {
      if (Q.rooms[i].slug === slug) { return Q.rooms[i].room; }
    }
    return null;
  }

  /* ---------------------------------------------------------------- views */

  function esc(t) {
    return String(t == null ? "" : t).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ------------------------------------------------------- sustain layer
   *
   * The app could take a zone through all six passes and then had nothing more
   * to say about it, which quietly dropped the S the whole method is built on.
   * Doing a zone is the easy half. Rooms revert, and an app that only ever
   * shows you what is left is an app you finish once and delete.
   *
   * So: a finished zone gets a date, and after that it has a standard to hold
   * and a trigger that brings it back. Nothing new is invented here, both
   * strings already ship in the card data. They were simply never shown after
   * the work was done, which is the exact moment they start mattering.
   *
   * DUE_DAYS is a default, not a measurement. Nobody has data on how fast a
   * real zone drifts, so it is stated here as an assumption rather than
   * buried, and it should be replaced the first time anybody does.
   */
  var DUE_DAYS = 30;
  var DAY = 86400000;

  function zoneKey(room, zone) { return room + "|" + zone; }

  /* A zone is held when every one of its cards is done. Derived rather than
     stored, so it stays true even if progress is edited or partly reset. */
  function heldZones() {
    var out = [];
    Q.rooms.forEach(function (r) {
      r.zones.forEach(function (z) {
        var stamps = z.steps.map(function (st) {
          return state.done[r.room + "|" + z.zone + "|" + st.s];
        });
        if (stamps.length && stamps.every(Boolean)) {
          out.push({ room: r.room, zone: z, at: Math.max.apply(null, stamps) });
        }
      });
    });
    return out.sort(function (a, b) { return a.at - b.at; });
  }

  function daysSince(t) { return Math.floor((Date.now() - t) / DAY); }

  /* Consecutive days with at least one card finished, counting back from today.
     Read from the timestamps already stored, so no new state and no way for a
     streak to disagree with the work behind it. */
  function streak() {
    var days = {};
    Object.keys(state.done).forEach(function (k) {
      var d = new Date(state.done[k]);
      days[d.getFullYear() + "-" + d.getMonth() + "-" + d.getDate()] = 1;
    });
    var n = 0, cur = new Date();
    /* Today not yet worked does not break a streak until tomorrow, so start
       from yesterday if today is empty. Otherwise every streak reads zero for
       most of the day, which is just discouraging and not true. */
    var key = function (d) {
      return d.getFullYear() + "-" + d.getMonth() + "-" + d.getDate();
    };
    if (!days[key(cur)]) { cur.setDate(cur.getDate() - 1); }
    while (days[key(cur)]) { n++; cur.setDate(cur.getDate() - 1); }
    return n;
  }

  function progress() {
    var done = DECK.filter(isDone).length;
    return { done: done, total: DECK.length,
             pct: DECK.length ? Math.round(done / DECK.length * 100) : 0 };
  }

  /* The zone with the fewest cards left, among zones somebody has already
   * started but not finished. This is the most reachable next win in the
   * whole house, so it is the default recommendation once nobody is overdue:
   * finishing it is close, and it is real progress rather than a random new
   * start. Ties go to whichever was touched most recently. */
  function nearestZone() {
    var best = null;
    Q.rooms.forEach(function (r) {
      r.zones.forEach(function (z) {
        var doneCount = 0, lastAt = 0;
        z.steps.forEach(function (st) {
          var t = state.done[r.room + "|" + z.zone + "|" + st.s];
          if (t) { doneCount++; if (t > lastAt) { lastAt = t; } }
        });
        var left = z.steps.length - doneCount;
        if (doneCount > 0 && left > 0) {
          if (!best || left < best.left || (left === best.left && lastAt > best.lastAt)) {
            best = { room: r.room, zone: z, doneCount: doneCount,
                     total: z.steps.length, left: left, lastAt: lastAt };
          }
        }
      });
    });
    return best;
  }

  /* What to recommend on the start screen for somebody who has done at least
   * one card before. In priority order: a standard slipping (overdue),
   * otherwise the closest zone to a finish line, otherwise (everything
   * caught up) a plain nudge to draw. A brand-new visitor gets none of this;
   * see renderRecommendation. */
  function computeRecommendation() {
    var due = heldZones().filter(function (h) { return daysSince(h.at) >= DUE_DAYS; })
      .sort(function (a, b) { return a.at - b.at; });
    if (due.length) {
      var h = due[0], d = daysSince(h.at);
      return {
        eyebrow: "Worth another look",
        title: "Refresh the " + h.zone.zone,
        body: "Last set " + d + " days ago in " + h.room + ". " +
          (h.zone.trigger || "A quick pass keeps the standard from sliding."),
        ctaLabel: "Refresh it",
        action: function () { startZoneRefresh(h.room, h.zone.zone); }
      };
    }
    var nz = nearestZone();
    if (nz) {
      return {
        eyebrow: "Almost there",
        title: "Finish the " + nz.zone.zone,
        body: (nz.left === 1 ? "One more card finishes it" : nz.left + " more cards finish it") +
          " in " + nz.room + ". " + (nz.zone.purpose || ""),
        ctaLabel: "Finish it",
        action: function () { begin("zone", { room: nz.room, zone: nz.zone.zone }); }
      };
    }
    return {
      eyebrow: "All caught up",
      title: "Nothing is due right now",
      body: "Every zone you have touched is holding. Draw a fresh card whenever you are ready for the next one.",
      ctaLabel: "Draw a card",
      action: function () { begin("draw"); }
    };
  }

  function startZoneRefresh(room, zoneName) {
    var key = zoneKey(room, zoneName);
    Object.keys(state.done).forEach(function (k) {
      if (k.indexOf(key + "|") === 0) { delete state.done[k]; }
    });
    save();
    begin("zone", { room: room, zone: zoneName });
  }

  /* One small line-art mark per room, drawn from the same visual language as
   * the header logo (currentColor strokes, no fill), so the map view reads
   * as a house rather than a list. Bedrooms and bathrooms of the same kind
   * intentionally share a mark: they are the same kind of room, and a forced
   * point of difference would be decoration for its own sake. */
  var ROOM_ICON = {
    "entryway": '<rect x="7" y="3" width="10" height="18" rx="1"/><circle cx="14.4" cy="12" r="1" fill="currentColor" stroke="none"/>',
    "kitchen": '<path d="M5 10h14v2a7 7 0 0 1-14 0z"/><path d="M4 10h1M19 10h1"/><path d="M9 10V6a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4"/>',
    "pantry": '<rect x="4" y="4" width="16" height="16" rx="1"/><path d="M4 10h16M4 16h16"/>',
    "dining-room": '<circle cx="14" cy="13" r="6"/><path d="M5 3v6M4 3v3M6 3v3M5 9v12"/>',
    "living-room": '<path d="M4 19v-4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/><path d="M4 19h16"/><path d="M4 15V9.5a1 1 0 0 1 1-1h1.2a1 1 0 0 1 1 1V13M16.8 15V9.5a1 1 0 0 1 1-1H19a1 1 0 0 1 1 1V13"/>',
    "family-room": '<rect x="4" y="4" width="16" height="10" rx="1"/><path d="M9 19h6M12 14v5"/>',
    "primary-bedroom": '<path d="M3 19v-5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v5"/><path d="M3 16h18"/><rect x="5" y="10" width="5.5" height="3" rx="1"/>',
    "guest-bedroom": '<path d="M3 19v-5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v5"/><path d="M3 16h18"/><rect x="5" y="10" width="5.5" height="3" rx="1"/>',
    "kids-bedroom": '<path d="M3 19v-5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v5"/><path d="M3 16h18"/><rect x="5" y="10" width="5.5" height="3" rx="1"/>',
    "nursery": '<path d="M12 3.5l1.8 4.6 4.9.4-3.7 3.2 1.1 4.8-4.1-2.6-4.1 2.6 1.1-4.8-3.7-3.2 4.9-.4z"/>',
    "primary-bathroom": '<path d="M12 3.5c2.6 3.6 5 7.3 5 10a5 5 0 0 1-10 0c0-2.7 2.4-6.4 5-10z"/>',
    "guest-bathroom": '<path d="M12 3.5c2.6 3.6 5 7.3 5 10a5 5 0 0 1-10 0c0-2.7 2.4-6.4 5-10z"/>',
    "laundry-room": '<circle cx="12" cy="13" r="6.5"/><circle cx="12" cy="13" r="2.6"/><path d="M9 6.3h.01M12 6.3h.01"/>',
    "home-office": '<rect x="4" y="5" width="16" height="10" rx="1"/><path d="M9 19h6M12 15v4"/>',
    "garage": '<path d="M4 20v-9l8-6 8 6v9"/><path d="M4 20h16"/><path d="M10 20v-6h4v6"/>',
    "workshop": '<path d="M15.3 6.4a3.6 3.6 0 0 0-4.9 4.9L5 16.7l2.3 2.3 5.4-5.4a3.6 3.6 0 0 0 4.9-4.9l-2.4 2.4-1.8-1.8z"/>',
    "mudroom": '<circle cx="12" cy="6" r="1.7"/><path d="M12 7.7V18M8 18h8"/>',
    "hall-closet": '<circle cx="12" cy="5" r="1.2"/><path d="M12 6.2v1.6M12 7.8 4 13.3h16z"/><path d="M4 16h16"/>',
    "stair-landing": '<path d="M4 20v-4h4v-4h4v-4h4V4h4"/>',
    "patio-or-deck": '<circle cx="12" cy="9" r="3.2"/><path d="M12 3.5v1.8M12 12.7v1.8M6.8 9h1.8M17.4 9h1.8M8.3 5.3l1.3 1.3M15.7 5.3l-1.3 1.3"/><path d="M3 19.5h18"/>'
  };
  var ROOM_ICON_DEFAULT = '<path d="M4 21V10l8-6 8 6v11"/><path d="M4 21h16"/>';

  function roomIcon(slug) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" ' +
      'stroke-linecap="round" stroke-linejoin="round">' + (ROOM_ICON[slug] || ROOM_ICON_DEFAULT) + '</svg>';
  }

  /* True once the first view has been shown, so the very first render on page
   * load does not steal focus away from the top of the document (the hero h1
   * a screen reader would otherwise start reading from). Every view change
   * after that is a real user action, and toggling `hidden` on the section
   * that held focus silently drops focus back to <body>, which is the same as
   * no announcement at all for a screen reader user and a lost tab position
   * for a keyboard user. Moving focus into the new section fixes both. */
  var everShown = false;

  function show(id) {
    var shown = null;
    ["start", "card", "finish", "map", "keep"].forEach(function (n) {
      var el = $("#view-" + n);
      if (el) {
        el.hidden = (n !== id);
        if (n === id) { shown = el; }
      }
    });
    window.scrollTo(0, 0);
    if (shown && everShown) { shown.focus({ preventScroll: true }); }
    everShown = true;
  }

  /* The Keep view: what you have already fixed, and what holds it there.
     This is the half of the method the app was missing. */
  function renderKeep() {
    var held = heldZones();
    var due = held.filter(function (h) { return daysSince(h.at) >= DUE_DAYS; });
    var el = $("#keep-body");
    if (!el) { return; }

    if (!held.length) {
      el.innerHTML = '<p class="lede">Nothing held yet. Take one zone through '
        + 'all six passes and it will appear here with the standard that keeps '
        + 'it, and the everyday moment that brings it back.</p>';
      show("keep");
      return;
    }

    var out = ['<p class="lede">' + held.length
      + (held.length === 1 ? ' zone is' : ' zones are') + ' standing. '
      + (!due.length
          ? 'Nothing is overdue.'
          : held.length === 1
            ? 'It has not been looked at in ' + DUE_DAYS + ' days.'
            : due.length + ' of them ' + (due.length === 1 ? 'has' : 'have')
              + ' not been looked at in ' + DUE_DAYS + ' days.')
      + '</p>'];

    held.forEach(function (h) {
      var d = daysSince(h.at);
      var over = d >= DUE_DAYS;
      out.push('<article class="keep-item' + (over ? ' due' : '') + '">'
        + '<div class="keep-head"><h3>' + esc(h.zone.zone) + '</h3>'
        + '<span class="keep-when">' + esc(h.room) + ' &middot; '
        + (d === 0 ? 'today' : d === 1 ? 'yesterday' : d + ' days ago')
        + '</span></div>'
        + (h.zone.standard
            ? '<p class="keep-std">' + esc(h.zone.standard) + '</p>' : '')
        + (h.zone.trigger
            ? '<p class="keep-trg"><b>Brings it back</b>'
              + esc(h.zone.trigger) + '</p>' : '')
        + '<div class="shots" data-shots="' + esc(zoneKey(h.room, h.zone.zone)) + '"></div>'
        + '<p class="keep-act"><a href="' + esc(h.zone.url || "#") + '">'
        + 'Read the zone</a>'
        + '<button type="button" class="linkish" data-reset-zone="'
        + esc(zoneKey(h.room, h.zone.zone)) + '">Run it again</button></p>'
        + '</article>');
    });
    el.innerHTML = out.join("");
    held.forEach(function (h) { paintShots(h.room, h.zone); });
    show("keep");
  }

  /* Photographs live in IndexedDB and are read asynchronously, so the slots are
     drawn empty and filled when each pair arrives. Object URLs are revoked on
     the next repaint: a page that takes a hundred of them and never lets go
     holds a hundred blobs in memory for the life of the tab. */
  var liveUrls = [];

  function releaseUrls() {
    liveUrls.forEach(function (u) { URL.revokeObjectURL(u); });
    liveUrls = [];
  }

  function slot(kind, rec, key) {
    var label = kind === "before" ? "Before" : "After";
    if (rec && rec.blob) {
      var u = window.QuestPhotos.objectUrl(rec);
      liveUrls.push(u);
      return '<figure class="shot has"><img src="' + u + '" alt="' + label
        + ' the reset" loading="lazy"><figcaption>' + label
        + '<button type="button" class="linkish shot-del" data-shot="' + esc(key)
        + '" data-kind="' + kind + '">Remove</button></figcaption></figure>';
    }
    /* class="sr-input" rather than the hidden attribute: hidden is display:none,
     * which drops an element from the tab order and the accessibility tree, so
     * this tile was mouse/touch only. sr-input (in quest.html) keeps the input
     * focusable and invisible instead, so Tab reaches it and Enter/Space opens
     * the file picker. The "+" is decorative, so it is hidden from the label's
     * accessible name rather than read aloud as a literal plus sign. */
    return '<label class="shot empty file-label"><input type="file" accept="image/*" '
      + 'capture="environment" data-shot-in="' + esc(key) + '" data-kind="'
      + kind + '" class="sr-input"><span class="shot-plus" aria-hidden="true">+'
      + '</span><span class="shot-lbl">' + label + '</span></label>';
  }

  function paintShots(room, zone) {
    if (!window.QuestPhotos || !window.QuestPhotos.supported()) { return; }
    var key = zoneKey(room, zone.zone);
    var box = document.querySelector('[data-shots="' + key.replace(/"/g, "") + '"]');
    if (!box) { return; }
    window.QuestPhotos.pair(room, zone.zone).then(function (p) {
      box.innerHTML = slot("before", p.before, key) + slot("after", p.after, key)
        + '<p class="shot-note">Kept on this device only. Never uploaded.</p>';
    }).catch(function () {
      box.innerHTML = '<p class="shot-note">Photographs are not available in '
        + 'this browser.</p>';
    });
  }

  /* Progress is the only thing this app holds and it lives in one browser.
     Clearing site data, a new phone or a private window all lose it silently,
     so there has to be a way to carry it out. */
  function backup() {
    var blob = new Blob([JSON.stringify(state, null, 1)],
                        { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "6s-home-quest-progress.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
  }

  function restore(text) {
    try {
      var incoming = JSON.parse(text);
      if (!incoming || typeof incoming.done !== "object") { return false; }
      /* Merge rather than replace, keeping the earlier timestamp for any card
         both sides have. Restoring a backup should never lose work done since
         it was taken. */
      Object.keys(incoming.done).forEach(function (k) {
        var a = state.done[k], b = incoming.done[k];
        state.done[k] = (a && b) ? Math.min(a, b) : (a || b);
      });
      save();
      return true;
    } catch (e) { return false; }
  }

  var currentRec = null;

  /* Shown only once somebody has finished at least one card. A first-time
     visitor has nothing yet to recommend from, and is better served by the
     plain "Draw one card" choice right below this. */
  function renderRecommendation(p) {
    var box = $("#rec-box");
    if (!box) { return; }
    if (p.done === 0) { box.hidden = true; currentRec = null; return; }
    currentRec = computeRecommendation();
    $("#rec-eyebrow").textContent = currentRec.eyebrow;
    $("#rec-title").textContent = currentRec.title;
    $("#rec-body").textContent = currentRec.body;
    $("#rec-go").textContent = currentRec.ctaLabel;
    box.hidden = false;
  }

  /* THE FIRST RUN GATE
   *
   * A stranger who has never done a card gets one sentence and one button.
   * Not a progress bar reading 0 of 114, not three modes to choose between,
   * not a map, not a Keep view with nothing in it, not an install prompt for
   * an app they have not used yet. Every one of those is a real feature and
   * every one of them is noise before the first win.
   *
   * The destination is fixed rather than random: the entryway door, mat and
   * floor. It is the shortest complete zone in the house at 15 to 30 minutes,
   * everyone has a front door, and its six passes are unusually legible as
   * six different actions, which is what makes it teach the method by doing.
   * It also carries no emotional weight, unlike a closet or a nursery.
   *
   * Derived from zones held, not stored. A visitor who clears their data is
   * a first time visitor again, which is correct: they have nothing to
   * return to either.
   */
  var FIRST_ZONE = { room: "Entryway", zone: "Door, Mat, and Immediate Floor" };

  function isFirstRun() { return heldZones().length === 0 && progress().done === 0; }

  var pendingInstall = null;

  function applyFirstRunGate() {
    var first = isFirstRun();
    /* An install prompt the browser offered while the gate was down is
       surfaced the moment somebody has something worth installing for. */
    var ib = $("#go-install");
    if (ib && !first && pendingInstall) { ib.hidden = false; }
    var box = $("#first-run");
    if (box) { box.hidden = !first; }
    /* Hidden rather than removed, so the moment the first card is done the
       full start screen is already there and does not need rebuilding. */
    var row = $("#go-map") && $("#go-map").parentNode;
    if (row) { row.hidden = first; }
    /* Both branches, explicitly. This used to read
         el.hidden = first ? true : el.hidden
       which only ever hid things, and worked only because the markup shipped
       them visible. The markup now ships the first-run screen instead, so
       that a first-time visitor is not shown the returning user's dashboard
       for as long as 372 KB of card data takes to parse. Leaving the old
       line would have left a returning visitor stuck on the first-run
       screen, which is the same defect pointing the other way. */
    ["#p-done-wrap", "#rec-box", "#mode-list", "#start-head",
     "#go-map", "#go-keep"].forEach(function (sel) {
      var el = $(sel);
      if (el) { el.hidden = first; }
    });
    /* The install prompt is the one exception: it is hidden for a first run
       and otherwise only shown when the browser has actually offered it. */
    var inst = $("#go-install");
    if (inst && first) { inst.hidden = true; }
    var track = $("#p-bar") && $("#p-bar").parentNode;
    if (track) { track.hidden = first; }
    var h = $("#start-head");
    if (h) { h.hidden = first; }
    var note = $("#p-note");
    if (note) { note.hidden = first; }
    return first;
  }

  function renderStart() {
    var p = progress();
    var held = heldZones();

    if (applyFirstRunGate()) {
      /* Nothing below this point has anything true to say to somebody with
         no history, and saying it anyway is what the gate exists to stop. */
      return;
    }

    /* The headline number is zones held, not cards done: 114 is still a lot,
       but each one is a real, reachable finish line, which 684 cards is not.
       The raw card count moves down to a supporting line instead. */
    $("#p-done").textContent = held.length;
    $("#p-total").textContent = TOTAL_ZONES;
    var zpct = TOTAL_ZONES ? Math.round(held.length / TOTAL_ZONES * 100) : 0;
    $("#p-bar").style.width = zpct + "%";
    var track = $("#p-bar").parentNode;
    track.setAttribute("aria-valuemax", String(TOTAL_ZONES));
    track.setAttribute("aria-valuenow", String(held.length));
    track.setAttribute("aria-valuetext", held.length + " of " + TOTAL_ZONES + " zones holding");

    $("#p-note").textContent = p.done === 0
      ? "Nothing done yet. Six cards finishes a zone, and one card is a real start."
      : p.done === p.total
      ? "Every card in the house is done. Reset a room to run it again."
      : p.done + " of " + p.total + " cards done, " +
        (p.pct === 0 ? "under 1 percent" : p.pct + " percent") + " of the house.";

    /* A streak and a due count give the start screen something to say to
       somebody returning, which it previously did not. Both are derived from
       the timestamps already stored, so neither can disagree with the work.
       Held count itself is no longer repeated here: it is now the headline. */
    var extra = $("#p-extra");
    if (extra) {
      var st = streak();
      var due = held.filter(function (h) { return daysSince(h.at) >= DUE_DAYS; });
      var bits = [];
      if (st > 1) { bits.push(st + " days in a row"); }
      if (due.length) { bits.push(due.length + " worth another look"); }
      extra.textContent = bits.join("  ·  ");
      extra.hidden = !bits.length;
    }

    renderRecommendation(p);

    var sel = $("#room-select");
    if (sel.options.length <= 1) {
      Q.rooms.forEach(function (r) {
        var left = DECK.filter(function (c) {
          return c.room === r.room && !isDone(c);
        }).length;
        var o = document.createElement("option");
        o.value = r.room;
        o.textContent = r.room + " (" + left + " left)";
        sel.appendChild(o);
      });
    }
    show("start");
  }

  var timer = null, elapsed = 0;

  function stopTimer() {
    if (timer) { clearInterval(timer); timer = null; }
  }

  function startTimer() {
    stopTimer();
    elapsed = 0;
    paint();
    timer = setInterval(function () { elapsed++; paint(); }, 1000);
    function paint() {
      var m = Math.floor(elapsed / 60), s = elapsed % 60;
      $("#t-clock").textContent = m + ":" + (s < 10 ? "0" : "") + s;
    }
  }

  function renderCard() {
    var c = run.queue[run.i];
    if (!c) { return renderFinish(); }

    var colour = Q.colours[c.step.s];
    document.documentElement.style.setProperty("--s-colour", colour);

    /* THE METHOD, TAUGHT BY DOING
     *
     * Nobody reads an explanation before starting, so the explanation lives
     * inside the work. Each pass says what it is for in plain verbs and
     * where it sits in the six. After running one zone start to finish a
     * person has done Sort before Straighten without ever being told to,
     * which is the only way this sticks.
     *
     * Shown on every card in every mode, not just to newcomers: the order
     * is the product, and repeating it costs one line. */
    var PASS_TEACH = {
      sort:        "decide what stays",
      straighten:  "give what stays a home",
      shine:       "clean it properly",
      safety:      "remove what could hurt somebody",
      standardize: "make the right state obvious",
      sustain:     "attach it to something you already do"
    };
    var teach = $("#c-teach");
    if (teach) {
      var idx = S_ORDER.indexOf(c.step.s);
      teach.textContent = idx >= 0
        ? "Pass " + (idx + 1) + " of 6, " + PASS_TEACH[c.step.s]
        : PASS_TEACH[c.step.s] || "";
    }

    $("#c-badge").textContent = c.step.s;
    $("#c-badge").style.background = colour;
    $("#c-where").textContent = c.room + "  >  " + c.zone.zone;
    $("#c-count").textContent = run.queue.length > 1
      ? (run.i + 1) + " of " + run.queue.length : "one card";
    $("#c-purpose").textContent = Q.purpose[c.step.s] || "";
    $("#c-do").textContent = c.step.text;
    /* The session length in the manual covers the whole zone, all six passes.
     * Printing it bare on a single card reads as "this one pass takes 45 to 75
     * minutes", which would make every card look like an afternoon and defeat
     * the point of drawing one. */
    $("#c-session").textContent = c.zone.session
      ? c.zone.session + " for the whole zone, six passes"
      : "";

    /* What done looks like is the only thing that answers "can I stop now",
     * so it sits with the instruction rather than behind a tap. */
    $("#c-done-look").textContent = c.zone.done || "";
    $("#c-done-wrap").hidden = !c.zone.done;

    /* Safety notes belong on the Safety card, and on Shine, because that is
     * the pass where somebody is reaching behind an appliance with a wet
     * cloth. Everywhere else they are noise that trains people to skip them. */
    var wrap = $("#c-watch");
    var showWatch = c.zone.watch.length && (c.step.s === "safety" || c.step.s === "shine");
    wrap.hidden = !showWatch;
    if (showWatch) {
      wrap.innerHTML = "<h3>Check before you start</h3>" +
        c.zone.watch.map(function (w) {
          return "<p><strong>" + esc(w.q) + "</strong> " + esc(w.t) + "</p>";
        }).join("");
    }

    /* The judgement call is what stalls a Sort, so it appears there. */
    var call = $("#c-call");
    var showCall = c.zone.call && c.step.s === "sort";
    call.hidden = !showCall;
    if (showCall) {
      call.innerHTML = "<h3>" + esc(c.zone.call.title) + "</h3><p>" +
                       esc(c.zone.call.text) + "</p>";
    }

    var std = $("#c-standard");
    var showStd = c.zone.standard && (c.step.s === "standardize" || c.step.s === "sustain");
    std.hidden = !showStd;
    if (showStd) {
      std.innerHTML = "<h3>The standard that keeps it</h3><p>" +
        esc(c.zone.standard) + "</p>" +
        (c.zone.trigger ? "<p><strong>Reset trigger:</strong> " +
                          esc(c.zone.trigger) + "</p>" : "");
    }

    $("#c-zone-link").href = c.zone.url;
    $("#c-skip").textContent = run.queue.length > 1 ? "Skip this one" : "Draw another";
    startTimer();
    show("card");
  }

  /* S names in the fixed method order, for a stable, meaningful order in the
   * recap strip rather than the order cards happened to be drawn in. */
  var S_ORDER = ["sort", "straighten", "shine", "safety", "standardize", "sustain"];

  function renderFinish() {
    stopTimer();
    var p = progress();
    var n = run ? run.completed : 0;
    $("#f-count").textContent = n === 0 ? "No cards finished this time."
      : n === 1 ? "One card done." : n + " cards done.";

    /* A small strip of coloured dots for what this session actually touched,
     * in method order. The dots are decorative (aria-hidden, colour only);
     * the sentence beside them carries the same counts in words, so nobody
     * has to tell six similar hues apart to know what got done. */
    var recap = $("#f-recap"), recapNote = $("#f-recap-note");
    var steps = run ? run.doneSteps : [];
    if (recap && recapNote) {
      if (steps.length) {
        var counts = {};
        steps.forEach(function (s) { counts[s] = (counts[s] || 0) + 1; });
        /* One dot per card finished (not one per distinct S), so six Sorts
         * in a room pass reads as six dots, ordered by the method rather
         * than by draw order. */
        recap.innerHTML = steps.slice().sort(function (a, b) {
          return S_ORDER.indexOf(a) - S_ORDER.indexOf(b);
        }).map(function (s) {
          return '<span style="background:' + Q.colours[s] + '"></span>';
        }).join("");
        recapNote.textContent = S_ORDER.filter(function (s) { return counts[s]; })
          .map(function (s) { return counts[s] + " " + s; }).join(", ");
        recap.hidden = false;
        recapNote.hidden = false;
      } else {
        recap.hidden = true;
        recapNote.hidden = true;
      }
    }

    $("#f-note").textContent = p.done + " of " + p.total +
      " across the house, " + (p.pct === 0 ? "under 1 percent" : p.pct + " percent") + ".";

    /* WHAT EARNS AN OFFER
     *
     * This used to fire on three cards in a session or ten overall. A raw
     * card count is the wrong signal: ten cards scattered across ten rooms
     * is somebody browsing, and six cards in one place is somebody who
     * finished something. The trigger is now what the person actually did.
     *
     * First zone ever held gets nothing at all. That screen stays free of
     * commerce by rule, because it is the moment the method finally landed
     * and an offer there reads as an interruption of the win.
     *
     * Everything offered here is either free or something we can actually
     * deliver today. The 155 generated zone, room, situation and area packs
     * are deliberately absent: they have no Stripe links yet, and listing a
     * product somebody cannot buy is worse than not listing it.
     */
    var held = heldZones();
    var rooms = {};
    held.forEach(function (h) { rooms[h.room] = 1; });
    var roomCount = Object.keys(rooms).length;

    var offer = $("#f-offer");
    var pitch = null;

    if (held.length >= 2 && roomCount >= 2) {
      /* Zones held in two different rooms means the habit is travelling,
         which is a far stronger signal than any card count. */
      pitch = {
        sku: "print-pack",
        body: "You have zones holding in " + roomCount + " different rooms, " +
          "which means this is becoming how you run the house rather than a " +
          "one off tidy. The printed pack is every card in the house on paper, " +
          "so the next one does not need a screen."
      };
    } else if (held.length >= 2) {
      /* Still inside one room. The free deck for that room is the honest
         next thing: it costs nothing, so it is a trust move rather than a
         sale, and it covers exactly where they already are. */
      pitch = {
        sku: "entryway-deck",
        body: "Two zones holding in " + held[0].room + ". The printable deck " +
          "is the same cards on paper for the rest of that room, free, no " +
          "email needed."
      };
    }

    /* The button has to match the sentence. It was hardcoded to the $19 pack,
       so a free deck pitch would have read "free, no email needed" above a
       button asking for nineteen dollars. That contradiction costs more
       trust than the offer could ever earn back. */
    var CTA = {
      "print-pack": { label: "The same cards on paper, $19",
                      href: "https://buy.stripe.com/00wdR223kfwK9fQ9440kF28" },
      "entryway-deck": { label: "Get the printable deck, free",
                         href: "deck.html" }
    };

    offer.hidden = !pitch;
    if (pitch) {
      var cta = $("#f-offer-cta"), spec = CTA[pitch.sku];
      if (cta && spec) {
        cta.textContent = spec.label;
        cta.setAttribute("href", spec.href);
      }
      $("#f-offer-body").textContent = pitch.body;
      m("quest-offer-shown", { offer: pitch.sku,
                               held: held.length,
                               rooms: roomCount });
    }
    show("finish");
  }

  /* Twenty rooms as plain text rows told you nothing about the house. Each
   * room is now a real button: a mark, a name, a fraction, a bar, and (for
   * anything not yet finished) a tap that starts working it, wired in the
   * delegated click handler below. A finished room is left as a plain
   * button that explains itself rather than one that quietly does nothing,
   * since resetting a whole room stays a deliberate choice made from the
   * select below, not a stray tap on a tile. */
  function renderMap() {
    var rows = Q.rooms.map(function (r) {
      var cards = DECK.filter(function (c) { return c.room === r.room; });
      var done = cards.filter(isDone).length;
      var complete = done === cards.length;
      var pct = Math.round(done / cards.length * 100);
      return '<li><button type="button" class="room-tile' + (complete ? " is-done" : "") +
        '" data-room="' + esc(r.room) + '">' +
        '<span class="room-icon">' + roomIcon(r.slug) + '</span>' +
        '<span class="room-name">' + esc(r.room) + '</span>' +
        '<span class="room-count">' + done + ' / ' + cards.length +
        (complete ? ' · held' : '') + '</span>' +
        '<span class="m-track"><span class="m-fill" style="width:' + pct + '%"></span></span>' +
        '</button></li>';
    }).join("");
    $("#m-list").innerHTML = rows;
    show("map");
  }

  /* ---------------------------------------------------------------- actions */

  /* opts lets a recommendation or a map tile start a specific room or zone
   * without touching the <select> elements on screen, which is what "room"
   * and "spass" modes read from when opts does not say otherwise. Mode
   * "zone" is a room-style run (method order, not shuffled) narrowed to one
   * zone by build()'s existing zoneName filter. */
  function begin(mode, opts) {
    opts = opts || {};
    var room = opts.room != null ? opts.room : ($("#room-select").value || null);
    var zone = opts.zone != null ? opts.zone : null;
    var s = opts.s != null ? opts.s : ($("#s-select").value || null);
    var queue = build(mode, mode === "draw" ? null : room, zone,
                      mode === "spass" ? s : null);
    if (!queue.length) {
      alertBox("Nothing left to draw with those choices. Try another room, or "
               + "reset one from the progress screen.");
      return;
    }
    run = { queue: queue, i: 0, completed: 0, doneSteps: [] };
    renderCard();
  }

  function alertBox(msg) {
    var b = $("#notice");
    /* role="status" (set in quest.html) only announces a change to content
     * that is already exposed to the accessibility tree. Unhiding first and
     * setting the text second, rather than the reverse, means the mutation a
     * screen reader needs to notice happens on a node that is already live. */
    b.hidden = false;
    b.textContent = msg;
    setTimeout(function () { b.hidden = true; }, 6000);
  }

  /* The one moment in the whole app that should feel like something: a card
   * finished. Previously "Done" just advanced, silently, which is the whole
   * emotional beat of the app doing nothing. This adds a quiet green halo on
   * the card and a checkmark that settles in, never a bounce, and the timer
   * freezes at the moment of completion rather than ticking through it.
   * Entirely skipped under prefers-reduced-motion: next() is called straight
   * away and no class or vibration is ever added, so nothing here can move a
   * pixel or buzz a phone for somebody who asked for less motion. */
  /* EXP-004 asks whether anybody finishes a second card. The app was just
     rebuilt around a completion moment, a streak and zones holding, all on the
     theory that people come back, and nothing tested that theory. These are the
     only events that can settle it. No zone name, no photograph, no progress
     detail: a count of cards and a count of zones is the whole question. */
  function m(name, data) {
    if (window.Measure) { window.Measure.track(name, data || {}); }
  }

  function done() {
    var c = run.queue[run.i];
    state.done[cardId(c)] = Date.now();
    run.completed++;
    m("quest-card-done", { s: c.step.s, nth: run.completed });
    /* A zone reaching six of six is the unit the app now counts, so it is the
       unit worth knowing about. */
    var zoneCards = c.zone.steps.filter(function (st) {
      return state.done[c.room + "|" + c.zone.zone + "|" + st.s];
    }).length;
    if (zoneCards === c.zone.steps.length) { m("quest-zone-held", {}); }
    run.doneSteps.push(c.step.s);
    save();
    stopTimer();

    if (reduceMotion) { next(); return; }

    var card = $(".q-card"), stamp = $("#c-stamp");
    if (card) { card.classList.add("q-settling"); }
    if (stamp) { stamp.classList.add("show"); }
    if (navigator.vibrate) { try { navigator.vibrate(12); } catch (e) {} }
    setTimeout(function () {
      if (card) { card.classList.remove("q-settling"); }
      if (stamp) { stamp.classList.remove("show"); }
      next();
    }, 420);
  }

  function next() {
    run.i++;
    if (run.i >= run.queue.length) { renderFinish(); } else { renderCard(); }
  }

  function resetRoom() {
    var room = $("#room-select").value;
    if (!room) { alertBox("Pick a room first."); return; }
    Object.keys(state.done).forEach(function (k) {
      if (k.indexOf(room + "|") === 0) { delete state.done[k]; }
    });
    save();
    alertBox(room + " cleared. Every card in it can be drawn again.");
    renderMap();
  }

  /* ---------------------------------------------------------------- wiring */

  document.addEventListener("DOMContentLoaded", function () {
    $("#go-draw").addEventListener("click", function () { begin("draw"); });

    /* The single first run button. A fixed zone rather than a random draw,
       because the whole point is that six cards in one place finish
       something, and a random card cannot promise that. */
    var goFirst = $("#go-first");
    if (goFirst) {
      goFirst.addEventListener("click", function () {
        m("quest-first-start", { zone: FIRST_ZONE.zone });
        begin("zone", { room: FIRST_ZONE.room, zone: FIRST_ZONE.zone });
      });
    }
    /* The escape hatch. Somebody who does not have an entryway, or does not
       want to start there, is one tap from the full screen. It reveals the
       modes rather than navigating, so nothing is lost. */
    var goOther = $("#go-other");
    if (goOther) {
      goOther.addEventListener("click", function () {
        var box = $("#first-run");
        if (box) { box.hidden = true; }
        ["#p-done-wrap", "#mode-list", "#go-map", "#go-keep", "#start-head",
         "#p-note"].forEach(function (sel) {
          var el = $(sel); if (el) { el.hidden = false; }
        });
        var r = $("#go-map") && $("#go-map").parentNode;
        if (r) { r.hidden = false; }
        var track = $("#p-bar") && $("#p-bar").parentNode;
        if (track) { track.hidden = false; }
        var sel = $("#room-select");
        if (sel) { sel.focus(); }
      });
    }
    $("#go-room").addEventListener("click", function () { begin("room"); });
    $("#go-spass").addEventListener("click", function () { begin("spass"); });

    var recGo = $("#rec-go");
    if (recGo) {
      recGo.addEventListener("click", function () {
        if (currentRec && currentRec.action) { currentRec.action(); }
      });
    }

    $("#c-done").addEventListener("click", done);
    $("#c-skip").addEventListener("click", next);
    $("#c-stop").addEventListener("click", renderFinish);

    $("#f-again").addEventListener("click", renderStart);
    $("#f-map").addEventListener("click", renderMap);
    $("#m-back").addEventListener("click", renderStart);
    $("#m-reset").addEventListener("click", resetRoom);
    $("#go-map").addEventListener("click", renderMap);

    /* Delegated for the same reason the Keep list is: the grid is rebuilt on
       every render. A finished room explains itself rather than resetting on
       a stray tap, since that stays a deliberate act from the select below. */
    var mList = $("#m-list");
    if (mList) {
      mList.addEventListener("click", function (ev) {
        var b = ev.target.closest(".room-tile");
        if (!b) { return; }
        var room = b.getAttribute("data-room");
        if (b.classList.contains("is-done")) {
          alertBox(room + " is fully held. Pick it from \"Work a room\" "
            + "below and clear it there if you want to run it again.");
          return;
        }
        begin("room", { room: room });
      });
    }

    var keepBtn = $("#go-keep");
    if (keepBtn) { keepBtn.addEventListener("click", renderKeep); }
    var kb = $("#k-back");
    if (kb) { kb.addEventListener("click", renderStart); }

    /* Delegated, because the Keep list is rebuilt on every render and rebinding
       a button per zone on each pass leaks listeners for no reason. */
    var keepBody = $("#keep-body");
    if (keepBody) {
      keepBody.addEventListener("click", function (ev) {
        var b = ev.target.closest("[data-reset-zone]");
        if (!b) { return; }
        var key = b.getAttribute("data-reset-zone");
        Object.keys(state.done).forEach(function (k) {
          if (k.indexOf(key + "|") === 0) { delete state.done[k]; }
        });
        save();
        /* The photographs are the record of the last time this zone was right.
           Running it again is a new pass, not a reason to destroy the evidence
           of the old one, so they are deliberately kept. */
        releaseUrls();
        renderKeep();
      });
    }

    /* Photograph capture and removal, delegated for the same reason the reset
       button is: the list is rebuilt on every render. */
    if (keepBody) {
      keepBody.addEventListener("change", function (ev) {
        var inp = ev.target.closest("[data-shot-in]");
        if (!inp) { return; }
        var f = inp.files && inp.files[0];
        if (!f) { return; }
        var parts = inp.getAttribute("data-shot-in").split("|");
        var kind = inp.getAttribute("data-kind");
        window.QuestPhotos.put(parts[0], parts[1], kind, f).then(function () {
          releaseUrls();
          renderKeep();
        }).catch(function (e) {
          alertBox(String(e && e.name) === "QuotaExceededError"
            ? "There is no room left on this device for another photograph. "
              + "Removing a few older ones will free it."
            : "That file could not be read as a photograph.");
        });
        inp.value = "";
      });

      keepBody.addEventListener("click", function (ev) {
        var del = ev.target.closest(".shot-del");
        if (!del) { return; }
        var parts = del.getAttribute("data-shot").split("|");
        window.QuestPhotos.del(parts[0], parts[1], del.getAttribute("data-kind"))
          .then(function () { releaseUrls(); renderKeep(); });
      });
    }

    var bk = $("#k-backup");
    if (bk) { bk.addEventListener("click", backup); }
    var rs = $("#k-restore");
    if (rs) {
      rs.addEventListener("change", function (ev) {
        var f = ev.target.files && ev.target.files[0];
        if (!f) { return; }
        var fr = new FileReader();
        fr.onload = function () {
          alertBox(restore(String(fr.result))
            ? "Progress restored and merged with what was already here."
            : "That file was not a Home Quest backup.");
          renderKeep();
        };
        fr.readAsText(f);
        ev.target.value = "";
      });
    }

    /* Android and desktop Chrome fire this when the app is installable. iOS
       never does, and there is no API for it, so that case is handled in the
       page copy rather than pretended at here. */
    var installBtn = $("#go-install");
    addEventListener("beforeinstallprompt", function (ev) {
      ev.preventDefault();
      if (!installBtn) { return; }
      /* The browser fires this whenever it likes, which on a cold landing is
         immediately. Asking somebody to install an app they have not used
         once is the worst version of this prompt, so it is held until a zone
         is actually holding. The event is kept, so nothing is lost: the
         button appears on the next start screen render after the first win.
         Testing caught this. The gate hid every element it listed and this
         handler simply unhid one of them afterwards. */
      pendingInstall = ev;
      if (isFirstRun()) { return; }
      installBtn.hidden = false;
      installBtn.addEventListener("click", function () {
        installBtn.hidden = true;
        ev.prompt();
      }, { once: true });
    });

    /* A zone page's "Or draw a card free" link carries the exact zone the
     * visitor was just reading about. Landing them in that zone's own run,
     * rather than the general start screen, is the whole point: the person
     * who finished the coffee station article is the one for whom drawing a
     * random card from the kitchen is a bait and switch. */
    var params = new URLSearchParams(location.search);
    var zoneSlug = params.get("zone");
    if (zoneSlug) {
      var target = findZoneBySlug(zoneSlug);
      if (target) {
        begin("zone", { room: target.room, zone: target.zone });
        if (run) { return; }
        /* Every card in this zone is already held; begin() already told the
         * visitor so via alertBox. Fall through to the normal start screen
         * rather than leaving the page blank. */
      }
    }

    /* Same idea, one level up: a room page's free link carries that room's
     * slug, so a visitor who has been reading about the whole Kitchen gets
     * that room's own run, in method order, rather than a dropdown asking
     * them to name the room they just came from. */
    var roomSlug = params.get("room");
    if (roomSlug) {
      var roomName = findRoomBySlug(roomSlug);
      if (roomName) {
        begin("room", { room: roomName });
        if (run) { return; }
        /* Every card in this room is already held; begin() already told the
         * visitor so via alertBox. Fall through to the normal start screen. */
      }
    }

    /* Launcher shortcuts and the manifest start_url land here with a hint. */
    var go = params.get("go");
    if (go === "draw") { begin("draw"); return; }
    if (go === "map") { renderMap(); return; }

    renderStart();
  });
})();
