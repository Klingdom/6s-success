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
 * Event names, a page type, a scroll bucket, a Stripe payment link id that is
 * already public in the page's own href, and a SKU only where the page itself
 * declares one. No email, no name, no address, no
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

  /* WHY EVERY EVENT MAY CARRY who:"internal"
     ----------------------------------------
     EXP-001 asks whether anybody who is not us has ever clicked a buy button.
     On 2026-09-03 it could not be answered, and not for want of data: nine
     buy-clicks are recorded and not one of them can be shown to be a stranger
     or shown to be us. Umami is cookieless and stores no identity by design,
     so our own click and a customer's are the same row. The answer was
     ambiguous, and ambiguous it stays for those nine forever.

     This is the smallest thing that makes the NEXT nine answerable. Load any
     page once with ?6s-internal=1 and this browser stamps who:"internal" on
     what it sends, until ?6s-internal=0 clears it.

     Deliberately a label and not an off switch. Umami's own opt-out
     (localStorage umami.disabled) would silence the tracker completely, and a
     mechanism that can silently zero all analytics is the exact failure this
     repository keeps paying for. Labelling cannot lose data: at worst the
     property is missing and we are no worse off than today.

     Read it the honest way round. who:"internal" means we know it was us.
     Its ABSENCE means unattributed, which is not the same as "a stranger":
     every event recorded before this shipped lacks it, and so does any visit
     where we forgot to set the flag. */
  var INTERNAL = (function () {
    try {
      if (/[?&]6s-internal=1(&|$)/.test(location.search)) {
        localStorage.setItem("6s.internal", "1");
      } else if (/[?&]6s-internal=0(&|$)/.test(location.search)) {
        localStorage.removeItem("6s.internal");
      }
      return localStorage.getItem("6s.internal") === "1";
    } catch (e) { return false; }      /* private mode, blocked storage */
  })();

  function track(name, data) {
    if (INTERNAL) { (data = data || {}).who = "internal"; }
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
      var d = { plink: plinkId(href), from: page(), sv: 2 };
      /* Only when the page actually says so. A guessed SKU is worse than an
         absent one, because it reads as a measurement. */
      var declared = a.getAttribute("data-sku");
      if (declared) { d.sku = declared.slice(0, 32); }
      track("buy-click", d);
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
    /* The index of a section is not a page of that section. /articles/ was
       being reported as "article" and so counted itself into the scroll-depth
       denominator for articles; two of the eleven scroll-depth events ever
       recorded are the index, not an article. */
    if (p.indexOf("/zones/") === 0) { return p === "/zones/" ? "zone-index" : "zone"; }
    if (p.indexOf("/rooms/") === 0) { return p === "/rooms/" ? "room-index" : "room"; }
    if (p.indexOf("/articles/") === 0) {
      return p === "/articles/" || p === "/articles/index.html"
        ? "article-index" : "article";
    }
    if (p.indexOf("quest") >= 0) { return "quest"; }
    if (p.indexOf("shop") >= 0) { return "shop"; }
    if (p === "/" || p.indexOf("index") >= 0) { return "home"; }
    return p.replace(/^\//, "").replace(/\.html$/, "").slice(0, 30) || "other";
  }

  function plinkId(href) {
    /* WHY THE SKU MAP THAT USED TO LIVE HERE IS GONE
       ----------------------------------------------
       It was a hand-typed table of four payment link ids. The site carries 155,
       and Stripe reissues them: on 2026-08-27 a link was replaced and all four
       entries here went stale at once, silently breaking attribution site-wide
       until somebody read a diff. Then, of the nine buy-clicks ever recorded,
       seven came back `sku: "unknown"` because the link clicked was simply not
       one of the four.

       A table of opaque ids maintained by hand, in a file nobody edits when
       prices change, is the "no assigned home" root cause with a different
       hat on. So record the id itself, which is in the href and can never be
       stale, and resolve it to a SKU at analysis time against the generated
       catalogue in site/shop.html, which is rebuilt whenever the links are.
       ops/experiments.py does that resolution. */
    var m = /buy\.stripe\.com\/([A-Za-z0-9]+)/.exec(href);
    return m ? m[1] : "";
  }

  /* Scroll depth on the long pages, because a zone page is 1,200 words and
     whether anybody reaches the offer at the bottom is a real question that
     nothing currently answers. Fired once per page view, at the deepest point
     reached, on the way out.
   *
   * THE DENOMINATOR BUG THIS VERSION FIXES
   * --------------------------------------
   * EXP-002 asks for the SHARE of zone page views that reach the bottom. A
   * share needs a denominator, and v1 could not supply one. It fired only when
   * `deepest > 0`, so a visitor who landed and left without scrolling emitted
   * nothing at all, which in the database is indistinguishable from an event
   * that was lost. Fifty-four zone page views had produced six scroll-depth
   * events; the missing forty-eight were some unknowable mixture of "did not
   * scroll" and "we failed to record it", and no query could separate them.
   *
   * It also listened only for visibilitychange. That is the right primary
   * signal, but iOS Safari can go straight to pagehide on a back-navigation
   * without ever firing it, and iOS is most of this site's traffic.
   *
   * So: always send exactly one event per page view, including a genuine zero,
   * and listen on both signals behind a once-only guard. The denominator then
   * lives in the numerator's own table, and any remaining gap against
   * pageviews is a real transport loss rather than a design hole.
   *
   * `sv: 2` marks events emitted by this version. Events before it carry no
   * `sv` and must not be pooled with these, because "no event" meant something
   * different then. ops/experiments.py enforces that split. */
  var deepest = 0;
  var sent = false;
  var LONG = ["zone", "room", "article"];
  if (LONG.indexOf(page()) >= 0) {
    var measure = function () {
      var h = document.documentElement.scrollHeight - innerHeight;
      /* A page shorter than the viewport has been seen in full without any
         scrolling. Reporting that as 0 would libel the reader.
       *
         Never call this at parse time. This script loads from <head>, so the
         body has not been laid out yet and scrollHeight is still the height of
         nothing: an initial reading taken here returned 100 for a 6,000 pixel
         zone page, and the browser test caught it saying every unscrolled page
         had been read in full. Measure on scroll and again on the way out,
         when the layout is real. */
      if (h <= 0) { return 100; }
      return Math.min(100, Math.max(0, Math.round((scrollY / h) * 100)));
    };

    addEventListener("scroll", function () {
      var pct = measure();
      if (pct > deepest) { deepest = pct; }
    }, { passive: true });

    var report = function () {
      if (sent) { return; }
      sent = true;
      /* Bucketed, not exact. An exact percentage per visitor is a fingerprint
         and tells nobody anything a bucket does not. */
      var d = Math.max(deepest, measure());
      var b = d >= 90 ? "90-100" : d >= 70 ? "70-89"
            : d >= 40 ? "40-69" : d >= 15 ? "15-39" : "0-14";
      track("scroll-depth", { depth: b, type: page(), sv: 2 });
    };

    addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") { report(); }
    });
    /* iOS back-navigation reaches pagehide without visibilitychange. The guard
       above means whichever arrives first wins and the other is a no-op. */
    addEventListener("pagehide", report);
  }
})();
