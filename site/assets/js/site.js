/* 6S Success shared site behavior: nav, cart (localStorage), drawer, reveals.
   Cart is fully functional for v1; checkout is staged for v2 (see cart.html). */
(function () {
  "use strict";
  /* Bumped from v1 when quote only items stopped being stored as price 0.
     A cart saved under v1 still holds that 0 and would render a quote only
     engagement as "Free" forever. Bumping the key retires those carts
     rather than migrating them, which is right while the site has no
     customers and no checkout. */
  var KEY = "sixs_cart_v2";
  var CATALOG = window.CATALOG || [];
  var bySku = {};
  CATALOG.forEach(function (p) { bySku[p.sku] = p; });

  /* ---------- money ---------- */
  /* A catalogue image is normally a bare filename in assets/img. The card
     artwork lives in assets/cards instead, so an entry may carry a path with
     a slash in it. Prefixing that with assets/img gave a 404 and a broken
     tile on the shop page. A value containing a slash is taken as already
     rooted at assets. */
  function imgSrc(v) {
    if (!v) { return ""; }
    return v.indexOf("/") >= 0 ? "assets/" + v : "assets/img/" + v;
  }

  function money(n) {
    if (n === null || n === undefined) return "Quote";
    if (n === 0) return "Free";
    return "$" + Number(n).toLocaleString("en-US");
  }
  window.money = money;

  /* ---------- cart store ---------- */
  function read() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function write(c) { localStorage.setItem(KEY, JSON.stringify(c)); paint(); }
  function count() { return read().reduce(function (s, i) { return s + i.qty; }, 0); }
  function subtotal() { return read().reduce(function (s, i) { return s + (i.price || 0) * i.qty; }, 0); }
  /* Null price means "we quote this", not zero. Anything rendering a line
     must ask here rather than multiplying, or quote items read as free. */
  function lineTotal(i) { return typeof i.price === "number" ? i.price * i.qty : null; }
  function hasQuoteItem() { return read().some(function (i) { return typeof i.price !== "number"; }); }
  window.lineTotal = lineTotal; window.hasQuoteItem = hasQuoteItem;

  var Cart = {
    add: function (sku, qty) {
      var p = bySku[sku]; if (!p) return;
      if (p.available === false) return;
      qty = qty || 1;
      var c = read(), row = c.find(function (i) { return i.sku === sku; });
      if (row) row.qty += qty;
      /* `p.price || 0` used to be here, which turned null into 0. money()
         renders 0 as "Free", so a quote only engagement was offered to the
         customer as free and left out of the subtotal. Keep null as null:
         APP-FREE really is 0, CN-CORP really is "ask us". */
      else c.push({ sku: sku, name: p.name, variant: p.variant || "",
                    price: (typeof p.price === "number" ? p.price : null),
                    img: p.img, qty: qty });
      write(c); toast(p.name + " added to cart"); openDrawer(true);
    },
    setQty: function (sku, q) {
      var c = read(), row = c.find(function (i) { return i.sku === sku; });
      if (!row) return; row.qty = Math.max(1, q); write(c);
    },
    remove: function (sku) { write(read().filter(function (i) { return i.sku !== sku; })); },
    items: read, count: count, subtotal: subtotal
  };
  window.Cart = Cart;

  /* ---------- drawer markup (injected once) ---------- */
  function ensureDrawer() {
    if (document.querySelector(".drawer")) return;
    var el = document.createElement("div");
    el.innerHTML =
      '<div class="drawer-scrim" data-close></div>' +
      '<aside class="drawer" role="dialog" aria-label="Your cart" aria-modal="true">' +
      '<header><h3>Your cart</h3><button class="btn btn-sm btn-ghost" data-close>Close</button></header>' +
      '<div class="items"></div>' +
      '<footer><div class="row"><span>Subtotal</span><span class="tot">$0</span></div>' +
      '<a class="btn btn-primary btn-lg" href="cart.html" style="width:100%;justify-content:center">Review order</a>' +
      '<p class="notice" style="margin:12px 0 0">Every priced item checks out through Stripe. Review your order to continue.</p>' +
      '</footer></aside>';
    document.body.appendChild(el);
    var d = el.querySelector(".drawer");
    d.setAttribute("inert", "");
    d.setAttribute("aria-hidden", "true");
    el.querySelectorAll("[data-close]").forEach(function (b) { b.addEventListener("click", function () { openDrawer(false); }); });
  }
  var lastFocus = null;
  function openDrawer(open) {
    ensureDrawer();
    var scrim = document.querySelector(".drawer-scrim");
    var draw = document.querySelector(".drawer");
    scrim.classList.toggle("open", open);
    draw.classList.toggle("open", open);
    // transform alone hides it from the eye and from nobody else. A closed
    // dialog must leave the tab order and the accessibility tree too.
    if (open) {
      lastFocus = document.activeElement;
      draw.removeAttribute("inert");
      draw.removeAttribute("aria-hidden");
      var first = draw.querySelector("button,a,input");
      if (first) first.focus();
    } else {
      draw.setAttribute("inert", "");
      draw.setAttribute("aria-hidden", "true");
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
  }
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var d = document.querySelector(".drawer.open");
    if (d) openDrawer(false);
  });
  window.openCart = function () { openDrawer(true); };

  /* ---------- paint counts + drawer ---------- */
  function paint() {
    document.querySelectorAll(".cart-count").forEach(function (b) {
      var n = count(); b.textContent = n; b.style.display = n ? "" : "none";
    });
    var box = document.querySelector(".drawer .items"); if (!box) return;
    var c = read();
    if (!c.length) { box.innerHTML = '<div class="empty-cart">Your cart is empty.<br>Every calm home starts with one room.</div>'; }
    else {
      box.innerHTML = c.map(function (i) {
        return '<div class="citem"><img src="' + imgSrc(i.img) + '" alt=""><div>' +
          '<div class="t">' + i.name + '</div><div class="v">' + (i.variant || "") + '</div>' +
          '<button class="rm" data-rm="' + i.sku + '">Remove</button></div>' +
          '<div style="text-align:right"><div class="qty"><button data-dec="' + i.sku + '">-</button>' +
          '<span style="min-width:26px;text-align:center;font-family:var(--sans);font-size:14px">' + i.qty + '</span>' +
          '<button data-inc="' + i.sku + '">+</button></div>' +
          '<div style="font-family:var(--display);font-weight:600;margin-top:6px">' + money(lineTotal(i)) + '</div></div></div>';
      }).join("");
    }
    var tot = document.querySelector(".drawer .tot");
    if (tot) tot.textContent = money(subtotal()) + (hasQuoteItem() ? " plus quotes" : "");
    window.renderCartPage && window.renderCartPage();
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-add-sku],[data-rm],[data-inc],[data-dec]"); if (!t) return;
    if (t.dataset.addSku) { Cart.add(t.dataset.addSku); }
    else if (t.dataset.rm) { Cart.remove(t.dataset.rm); }
    else if (t.dataset.inc) { var r = read().find(function (i) { return i.sku === t.dataset.inc; }); Cart.setQty(t.dataset.inc, r.qty + 1); }
    else if (t.dataset.dec) { var r2 = read().find(function (i) { return i.sku === t.dataset.dec; }); Cart.setQty(t.dataset.dec, r2.qty - 1); }
  });

  /* ---------- shared product card ---------- */
  window.renderProduct = function (p) {
    var priceHtml = (p.priceLo != null && p.priceHi != null && p.priceHi !== p.priceLo)
      ? '<span class="price">$' + p.priceLo + '<small> to $' + p.priceHi + '</small></span>'
      : (p.price === 0 && p.href)
      ? '<span class="price">Free</span>'
      : '<span class="price">' + money(p.price) + (p.variant === "Pro (annual)" ? '<small>/yr</small>' : '') + '</span>';
    /* available: false means no supplier, no stock, no platform, or no build behind
       the listing yet. Selling it would be taking money, or at least an order
       request, for something that does not exist. Route to the same interest
       capture as a quote, but say plainly that it is not ready rather than
       inviting an order the business cannot fill. */
    /* A buy link means Stripe can take money for this today. It is a hosted
       checkout on Stripe's own domain, so no card ever touches this site and no
       key is needed in this file. Only offers that can actually be delivered
       carry one. */
    /* An href means the thing is finished and free and lives at a URL on this
       site, so the useful action is to go and get it. Without this branch a
       free item falls through to Add to cart, which puts a zero on the cart
       badge and asks somebody to check out for nothing. */
    /* "Book and pay" is right for a consult and wrong for a book. The label
       follows what the thing is, because a button that describes the wrong
       action is a reason to hesitate at the exact moment you do not want one. */
    var buyLabel = (p.cat === "Consulting") ? "Book and pay"
                 : (p.price === 0) ? "Get it"
                 : "Buy it now";
    /* data-sku is the attribute measure.js reads when it fires buy-click. Every
       one of the 155 catalogue buttons was rendered without it, so of the nine
       buy-clicks this business has recorded, seven arrived with no SKU and had
       to be resolved backwards from the payment-link id. That resolution works,
       but it is a second step that can go stale, and the card already knows
       exactly which product it is drawing. */
    var action = (p.buy)
      ? '<a class="btn btn-sm btn-primary" data-sku="' + p.sku + '" href="' + p.buy + '" rel="noopener">' + buyLabel + '</a>'
      : (p.href)
      ? '<a class="btn btn-sm btn-primary" href="' + p.href + '">Open it</a>'
      : (p.available === false)
      ? '<a class="btn btn-sm btn-ghost" href="contact.html?ref=' + p.sku + '">Notify me</a>'
      : (p.price === null)
      ? '<a class="btn btn-sm btn-ghost" href="contact.html?ref=' + p.sku + '">Request a quote</a>'
      /* No cart. Every priced product has a direct Stripe link, so this
         branch was already unreachable, and a cart that cannot check out
         sitting beside 155 buttons that can is two purchase flows competing.
         Anything that somehow lands here has no way to be bought, so it says
         so rather than offering a basket that goes nowhere. */
      : '<a class="btn btn-sm btn-ghost" href="contact.html?ref=' + p.sku + '">Ask about this</a>';
    var badge = (p.available === false)
      ? '<span class="badge">In development</span>'
      : (p.badge ? '<span class="badge">' + p.badge + '</span>' : '');
    /* A real, tested fact stated at the exact point of hesitation: this is what
       STRIPE.md records ops/stripe_fulfil.py as actually doing, not a claim
       invented for the card. Only present on SKUs that carry it in data.js. */
    var fulfil = p.fulfil ? '<p class="fulfil">' + p.fulfil + '</p>' : '';
    /* THE SUPERSET, SAID OUT LOUD.
     *
     * 149 of the 159 catalogue entries carry a "super" field naming a product
     * that already contains all of them, and until now nothing rendered it.
     * That is a real trust problem, not a cosmetic one: the $19 Whole House
     * Print Pack holds all 684 cards, so an $16 area bundle is 84 percent of
     * the price for 20 percent of the content, and the shop grid sold the two
     * side by side as equals with nothing to tell the buyer.
     *
     * The 114 zone pages already state this comparison, in words, at the point
     * of sale. The shop page stripped that context off the identical product.
     * One surface being honest and another not is worse than neither, because
     * whichever one the buyer saw second is the one that reads as the trick.
     *
     * Both numbers are read from the catalogue, never typed, so this cannot
     * drift the way a hardcoded price would. It is a fact, not a nudge: no
     * urgency, no fake saving, no button. Somebody who wants only the room
     * they are standing in is still right to buy the room pack, and now they
     * are choosing rather than guessing. */
    var supr = '';
    if (p.super && p.super !== p.sku) {
      var whole = CATALOG.find(function (x) { return x.sku === p.super; });
      if (whole && whole.price != null && p.price != null && whole.price > p.price) {
        /* The card count comes off the superset's own variant string rather
           than being typed as 684 here, so it cannot outlive a change to the
           pack the way a hardcoded number would. */
        var n = /(\d[\d,]*)\s+cards/.exec(whole.variant || '');
        supr = '<p class="fulfil">Part of ' + whole.name + ', ' + money(whole.price)
             + (n ? ' for all ' + n[1] + ' cards' : '') + '.</p>';
      }
    }
    return '<article class="product reveal"><div class="ph">' + badge +
      '<img src="' + imgSrc(p.img) + '" alt="' + p.name + '" loading="lazy"></div>' +
      '<div class="body"><span class="variant">' + (p.variant || p.cat) + '</span>' +
      '<h3>' + p.name + '</h3><p class="blurb">' + p.blurb + '</p>' +
      '<span class="chip ' + (p.phase || "All") + '">' + (p.phase || "All") + '</span>' +
      fulfil + supr +
      '<div class="foot">' + priceHtml + action + '</div></div></article>';
  };

  /* ---------- nav + reveal ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    wireNewsletter();
    // Deliberately not ensureDrawer(): the drawer is built the
    // first time something actually opens it. See ensureDrawer.
    paint();
    var tog = document.querySelector(".nav-toggle");
    if (tog) tog.addEventListener("click", function () {
      var nav = document.querySelector(".nav"); nav.classList.toggle("open");
      tog.setAttribute("aria-expanded", nav.classList.contains("open"));
    });
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.12 });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
    setTimeout(function () {
      var vh = window.innerHeight || document.documentElement.clientHeight;
      document.querySelectorAll(".reveal:not(.in)").forEach(function (el) {
        var r = el.getBoundingClientRect(); if (r.top < vh * 0.92 && r.bottom > 0) el.classList.add("in");
      });
    }, 200);
  });

  /* reveal any element already within the viewport (belt-and-suspenders so
     first-screen content is never left invisible if the observer is slow) */
  function revealInView() {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    document.querySelectorAll(".reveal:not(.in)").forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < vh * 0.92 && r.bottom > 0) el.classList.add("in");
    });
  }
  /* re-observe reveals added later (e.g. shop render) */
  window.observeReveals = function () {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.12 });
    document.querySelectorAll(".reveal:not(.in)").forEach(function (el) { io.observe(el); });
    revealInView();
    setTimeout(revealInView, 250);
  };

  /* ---------- footer newsletter ----------

     WHY THE LIST DOES NOT WORK
     --------------------------
     Listmonk itself returns HTTP 500 on subscribe; it is not our reverse
     proxy. The cause is measured, not inferred, and is written up in
     OWNER-ACTIONS.md item 7 with the log lines.

     The detail deliberately does NOT live here. This file is served to every
     visitor, and the diagnosis named our VPS's IP address and another
     company's SMTP username. Neither belongs in shipped JavaScript. A useful
     comment in the wrong file is still a disclosure.

     WHY THIS FORM STILL EXISTS, AND WHY IT NOW SAYS SO FIRST
     --------------------------------------------------------
     The previous version asked for an address and only then admitted it could
     not store it. That is the worst possible order: it takes the effort first
     and spends the trust second, and the sentence a visitor is left holding is
     "this site is broken". The mechanism has not changed, because a static
     site with no server has exactly one honest way to collect an address, but
     it is now stated before the ask rather than confessed after it.

     support@6s-success.com is a real mailbox that is really read, so an address
     that arrives there really does get added. Nothing here claims a
     subscription that has not happened, nothing pre-ticks a consent, and there
     is no list to be quietly added to. */
  var LIST_INBOX = "support@6s-success.com";

  function mailtoJoin(addr) {
    return "mailto:" + LIST_INBOX +
      "?subject=" + encodeURIComponent("Add me to the 6S Success list") +
      "&body=" + encodeURIComponent("Please add this address to the list: " + addr);
  }

  function wireNewsletter() {
    document.querySelectorAll("form.foot-newsletter").forEach(function (form) {
      if (form.dataset.wired) return;
      form.dataset.wired = "1";
      form.removeAttribute("onsubmit");

      /* The offer and the mechanism, above the field, before anybody types.
         One paragraph, not two: the .newsletter-offer line already sitting
         above this form carries the free thing, and a third block of small
         type around a two-field form is its own kind of friction.

         Inserted from here rather than into 187 pages of footer markup, which
         is also why the no-JS case degrades to a form that does nothing rather
         than to a form that lies. */
      var ask = document.createElement("p");
      ask.className = "newsletter-note";
      ask.textContent = "Told when there is something new: another room's cards, " +
        "another zone guide, or a correction when we got something wrong. The " +
        "list software is not connected yet, so this opens your email app with " +
        "a one-line message ready to send, and a person adds you by hand.";
      form.parentNode.insertBefore(ask, form);

      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.textContent = "Email us your address"; }

      var note = document.createElement("p");
      note.className = "newsletter-note";
      note.setAttribute("role", "status");
      note.setAttribute("aria-live", "polite");
      note.hidden = true;
      form.parentNode.insertBefore(note, form.nextSibling);

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var input = form.querySelector('input[type="email"]');
        var addr = (input && input.value || "").trim();
        if (!addr) {
          note.hidden = false;
          note.textContent = "Enter an email address first.";
          return;
        }
        if (!input.checkValidity()) {
          note.hidden = false;
          note.textContent = "That does not look like an email address. Check it and try again.";
          return;
        }
        var url = mailtoJoin(addr);
        note.hidden = false;
        note.innerHTML = "Your email app should be opening. If nothing happened, " +
          "<a href=\"" + url + "\">use this link</a>, or write to " +
          "<a href=\"mailto:" + LIST_INBOX + "\">" + LIST_INBOX + "</a> yourself.";
        /* Counted, because until now nothing anywhere recorded whether a single
           person has ever tried to join the list, and "the list is at zero" and
           "nobody has ever asked" are different problems. The event carries no
           address and never will: only that somebody wanted on. */
        if (window.Measure) { window.Measure.track("list-signup", { via: "mailto" }); }
        try { window.location.href = url; } catch (err) {}
      });
    });
  }

  /* ---------- toast ---------- */
  var tEl;
  function toast(msg) {
    if (!tEl) { tEl = document.createElement("div"); tEl.className = "toast"; document.body.appendChild(tEl); }
    tEl.textContent = msg; tEl.classList.add("show");
    clearTimeout(tEl._t); tEl._t = setTimeout(function () { tEl.classList.remove("show"); }, 1900);
  }
})();
