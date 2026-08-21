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

  function progress() {
    var done = DECK.filter(isDone).length;
    return { done: done, total: DECK.length,
             pct: DECK.length ? Math.round(done / DECK.length * 100) : 0 };
  }

  function show(id) {
    ["start", "card", "finish", "map"].forEach(function (n) {
      var el = $("#view-" + n);
      if (el) { el.hidden = (n !== id); }
    });
    window.scrollTo(0, 0);
  }

  function renderStart() {
    var p = progress();
    $("#p-done").textContent = p.done;
    $("#p-total").textContent = p.total;
    $("#p-bar").style.width = p.pct + "%";
    $("#p-bar").parentNode.setAttribute("aria-valuenow", String(p.pct));
    $("#p-note").textContent = p.done === 0
      ? "Nothing done yet. One card is a real start."
      : p.done === p.total
      ? "Every card in the house is done. Reset a room to run it again."
      : p.done + " of " + p.total + " cards done, " +
        (p.pct === 0 ? "under 1 percent" : p.pct + " percent") + " of the house.";

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
      " across the house, " + p.pct + " percent.";
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
    b.textContent = msg;
    b.hidden = false;
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

    renderStart();
  });
})();
