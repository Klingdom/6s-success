/* Funnel instrumentation.
 *
 * WHY THIS BEFORE ANY A/B TEST
 * ----------------------------
 * The obvious next step after "we need experiments" is a split test. It would
 * be useless here. This site has had seven checkout sessions in its life and
 * one sale, and a comparative test needs hundreds of conversions per arm to say
 * anything at all. Running one now would produce a number with no meaning and,
 * worse, a decision made from it.
 *
 * The useful question at this traffic is not "which variant wins" but "does
 * anything happen at all". Nobody currently knows whether a stranger has ever
 * clicked a buy button, because six abandoned checkouts could equally have been
 * my own testing. That is a question about counting, not about statistics, and
 * counting works at n=1.
 *
 * So this records the funnel. When there is enough traffic for a split test the
 * events it needs will already be flowing and already trusted, which is the
 * opposite of the usual order and much less painful.
 *
 * WHAT IT SENDS, AND WHAT IT NEVER SENDS
 * --------------------------------------
 * Event names and a SKU or a zone slug. No email, no name, no address, no
 * photograph, no free text a person typed, and nothing from localStorage that
 * describes their home. Umami is already cookieless and stores no personal
 * identifier; nothing here changes that, and nothing here would be worth
 * anything if it did.
 */
(function () {
  "use strict";

  /* umami loads with defer, so it may not exist when this runs. Queue rather
     than drop: an event lost because a script had not parsed yet is a hole in
     the data that looks exactly like a visitor who did not click. */
  var queue = [];
  var flushing = false;

  function send(name, data) {
    if (window.umami && typeof window.umami.track === "function") {
      try { window.umami.track(name, data || {}); } catch (e) {}
      return true;
    }
    return false;
  }

  function flush() {
    if (flushing) { return; }
    flushing = true;
    var tries = 0;
    var tick = function () {
      while (queue.length && send(queue[0].n, queue[0].d)) { queue.shift(); }
      if (queue.length && tries++ < 40) { setTimeout(tick, 250); }
      else { flushing = false; }
    };
    tick();
  }

  function track(name, data) {
    if (!send(name, data)) { queue.push({ n: name, d: data }); flush(); }
  }

  window.Measure = { track: track };

  /* ---------------------------------------------------------------- funnel */

  document.addEventListener("click", function (ev) {
    var a = ev.target.closest ? ev.target.closest("a, button") : null;
    if (!a) { return; }
    var href = a.getAttribute("href") || "";

    /* The one event this business most needs and has never had: did a stranger
       click something that leads to money. */
    if (href.indexOf("buy.stripe.com") >= 0) {
      track("buy-click", { sku: a.getAttribute("data-sku") || skuFromLink(href),
                           from: page() });
      return;
    }

    /* A free artifact being taken is the closest thing to a conversion this
       site has while nothing is selling. */
    if (/\/downloads\/|print-and-play/.test(href)) {
      track("free-download", { what: href.split("/").pop().slice(0, 60),
                               from: page() });
      return;
    }

    if (href.indexOf("contact.html") >= 0 && href.indexOf("ref=") >= 0) {
      track("quote-click", { sku: href.split("ref=")[1].slice(0, 24), from: page() });
    }
  }, true);

  /* Which page types people actually reach. Umami records the URL already, but
     the type is what a decision gets made about, and deriving it from 176 paths
     afterwards is guesswork. */
  function page() {
    var p = location.pathname;
    if (p.indexOf("/zones/") === 0) { return p === "/zones/" ? "zone-index" : "zone"; }
    if (p.indexOf("/rooms/") === 0) { return "room"; }
    if (p.indexOf("/articles/") === 0) { return "article"; }
    if (p.indexOf("quest") >= 0) { return "quest"; }
    if (p.indexOf("shop") >= 0) { return "shop"; }
    if (p === "/" || p.indexOf("index") >= 0) { return "home"; }
    return p.replace(/^\//, "").replace(/\.html$/, "").slice(0, 30) || "other";
  }

  function skuFromLink(href) {
    /* Payment link ids are opaque, so map the ones we own back to a SKU. Any
       link not in this map reports as unknown rather than being guessed at. */
    var MAP = {
      "9B66oAgYedoC4ZA6VW0kE04": "PACK-HOUSE",
      "9B6fZafUaacqcs25RS0kE05": "BK-BUNDLE",
      "eVqeV637ocky8bMbcc0kE03": "MZ-MANUAL",
      "aFafZaazQ5Wacs2cgg0kE01": "CN-INHOME"
    };
    for (var k in MAP) {
      if (href.indexOf(k) >= 0) { return MAP[k]; }
    }
    return "unknown";
  }

  /* Scroll depth on the long pages, because a zone page is 1,200 words and
     whether anybody reaches the offer at the bottom is a real question that
     nothing currently answers. Fired once per page, at the deepest point
     reached, on the way out. */
  var deepest = 0;
  var LONG = ["zone", "room", "article"];
  if (LONG.indexOf(page()) >= 0) {
    addEventListener("scroll", function () {
      var h = document.documentElement.scrollHeight - innerHeight;
      if (h <= 0) { return; }
      var pct = Math.round((scrollY / h) * 100);
      if (pct > deepest) { deepest = Math.min(100, pct); }
    }, { passive: true });

    addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden" && deepest > 0) {
        /* Bucketed, not exact. An exact percentage per visitor is a fingerprint
           and tells nobody anything a bucket does not. */
        var b = deepest >= 90 ? "90-100" : deepest >= 70 ? "70-89"
              : deepest >= 40 ? "40-69" : deepest >= 15 ? "15-39" : "0-14";
        track("scroll-depth", { depth: b, type: page() });
        deepest = 0;
      }
    });
  }
})();
