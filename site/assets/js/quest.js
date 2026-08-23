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

  function renderStart() {
    var p = progress();
    $("#p-done").textContent = p.done;
    $("#p-total").textContent = p.total;
    $("#p-bar").style.width = p.pct + "%";
    $("#p-bar").parentNode.setAttribute("aria-valuenow", String(p.pct));
    $("#p-bar").parentNode.setAttribute("aria-valuetext", p.done + " of " + p.total + " cards");
    $("#p-note").textContent = p.done === 0
      ? "Nothing done yet. One card is a real start."
      : p.done === p.total
      ? "Every card in the house is done. Reset a room to run it again."
      : p.done + " of " + p.total + " cards done, " +
        (p.pct === 0 ? "under 1 percent" : p.pct + " percent") + " of the house.";

    /* A streak and a held count give the start screen something to say to
       somebody returning, which it previously did not. Both are derived from
       the timestamps already stored, so neither can disagree with the work. */
    var extra = $("#p-extra");
    if (extra) {
      var st = streak(), held = heldZones();
      var due = held.filter(function (h) { return daysSince(h.at) >= DUE_DAYS; });
      var bits = [];
      if (st > 1) { bits.push(st + " days in a row"); }
      if (held.length) {
        bits.push(held.length + (held.length === 1 ? " zone holding" : " zones holding"));
      }
      if (due.length) {
        bits.push(due.length + " worth another look");
      }
      extra.textContent = bits.join("  ·  ");
      extra.hidden = !bits.length;
    }

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

  function renderFinish() {
    stopTimer();
    var p = progress();
    var n = run ? run.completed : 0;
    $("#f-count").textContent = n === 0 ? "No cards finished this time."
      : n === 1 ? "One card done." : n + " cards done.";
    $("#f-note").textContent = p.done + " of " + p.total +
      " across the house, " + (p.pct === 0 ? "under 1 percent" : p.pct + " percent") + ".";

    /* The offer appears only once somebody has done real work. Under three
     * cards in a session and under ten overall, they are still deciding
     * whether this is for them, and a pitch at that moment is an interruption
     * rather than an answer. */
    var earned = n >= 3 || p.done >= 10;
    var offer = $("#f-offer");
    offer.hidden = !earned;
    if (earned) {
      $("#f-offer-body").textContent =
        "You have finished " + p.done + " card" + (p.done === 1 ? "" : "s") +
        ", which is real work on a real room. The book walks the whole method " +
        "in order and goes deeper than a card can. A consult is somebody doing " +
        "it with you, room by room, and leaving the standards behind.";
    }
    show("finish");
  }

  function renderMap() {
    var rows = Q.rooms.map(function (r) {
      var cards = DECK.filter(function (c) { return c.room === r.room; });
      var done = cards.filter(isDone).length;
      var pct = Math.round(done / cards.length * 100);
      return '<li><div class="m-top"><span>' + esc(r.room) + "</span><span>" +
        done + " / " + cards.length + "</span></div>" +
        '<div class="m-track"><div class="m-fill" style="width:' + pct + '%"></div></div></li>';
    }).join("");
    $("#m-list").innerHTML = rows;
    show("map");
  }

  /* ---------------------------------------------------------------- actions */

  function begin(mode) {
    var room = $("#room-select").value || null;
    var s = $("#s-select").value || null;
    var queue = build(mode, mode === "draw" ? null : room, null,
                      mode === "spass" ? s : null);
    if (!queue.length) {
      alertBox("Nothing left to draw with those choices. Try another room, or "
               + "reset one from the progress screen.");
      return;
    }
    run = { queue: queue, i: 0, completed: 0 };
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

  function done() {
    var c = run.queue[run.i];
    state.done[cardId(c)] = Date.now();
    run.completed++;
    save();
    next();
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
    $("#go-room").addEventListener("click", function () { begin("room"); });
    $("#go-spass").addEventListener("click", function () { begin("spass"); });

    $("#c-done").addEventListener("click", done);
    $("#c-skip").addEventListener("click", next);
    $("#c-stop").addEventListener("click", renderFinish);

    $("#f-again").addEventListener("click", renderStart);
    $("#f-map").addEventListener("click", renderMap);
    $("#m-back").addEventListener("click", renderStart);
    $("#m-reset").addEventListener("click", resetRoom);
    $("#go-map").addEventListener("click", renderMap);

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
      installBtn.hidden = false;
      installBtn.addEventListener("click", function () {
        installBtn.hidden = true;
        ev.prompt();
      }, { once: true });
    });

    /* Launcher shortcuts and the manifest start_url land here with a hint. */
    var go = new URLSearchParams(location.search).get("go");
    if (go === "draw") { begin("draw"); return; }
    if (go === "map") { renderMap(); return; }

    renderStart();
  });
})();
