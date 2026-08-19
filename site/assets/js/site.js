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
      '<p class="notice" style="margin:12px 0 0">Secure checkout arrives in v2. For now, review your order and we will send an invoice or booking link.</p>' +
      '</footer></aside>';
    document.body.appendChild(el);
    el.querySelectorAll("[data-close]").forEach(function (b) { b.addEventListener("click", function () { openDrawer(false); }); });
  }
  function openDrawer(open) {
    ensureDrawer();
    document.querySelector(".drawer-scrim").classList.toggle("open", open);
    document.querySelector(".drawer").classList.toggle("open", open);
  }
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
        return '<div class="citem"><img src="assets/img/' + i.img + '" alt=""><div>' +
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
    var action = (p.buy)
      ? '<a class="btn btn-sm btn-primary" href="' + p.buy + '" rel="noopener">Book and pay</a>'
      : (p.available === false)
      ? '<a class="btn btn-sm btn-ghost" href="contact.html?ref=' + p.sku + '">Notify me</a>'
      : (p.price === null)
      ? '<a class="btn btn-sm btn-ghost" href="contact.html?ref=' + p.sku + '">Request a quote</a>'
      : '<button class="btn btn-sm btn-primary" data-add-sku="' + p.sku + '">Add to cart</button>';
    var badge = (p.available === false)
      ? '<span class="badge">In development</span>'
      : (p.badge ? '<span class="badge">' + p.badge + '</span>' : '');
    return '<article class="product reveal"><div class="ph">' + badge +
      '<img src="assets/img/' + p.img + '" alt="' + p.name + '" loading="lazy"></div>' +
      '<div class="body"><span class="variant">' + (p.variant || p.cat) + '</span>' +
      '<h3>' + p.name + '</h3><p class="blurb">' + p.blurb + '</p>' +
      '<span class="chip ' + (p.phase || "All") + '">' + (p.phase || "All") + '</span>' +
      '<div class="foot">' + priceHtml + action + '</div></div></article>';
  };

  /* ---------- nav + reveal ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    wireNewsletter();
    ensureDrawer(); paint();
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
     There is no email provider yet, so there is no endpoint to POST to. What
     these forms did instead was nothing at all: you typed an address, clicked
     Join, and it vanished with no feedback. That is the worst of the options,
     because the reader believes they subscribed.

     Until a provider is chosen, say so plainly and hand the reader a prefilled
     message so the thing they wanted still happens in one click. When the
     provider exists, replace the body of subscribe() with the POST and delete
     the note. Nothing else here changes. */
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
      /* The markup keeps onsubmit="return false" deliberately. With scripting
         off it stops the form navigating to a bare query string and losing the
         page, which is the only sane no-JS behaviour available without a
         server. Here, where scripting is on, take it off and handle it. */
      form.removeAttribute("onsubmit");

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
        note.hidden = false;
        note.innerHTML = "The list is not connected yet, so this form cannot store your " +
          "address. <a href=\"" + mailtoJoin(addr) + "\">Send it to us in one click</a> " +
          "and we will add you by hand.";
        var link = note.querySelector("a");
        if (link && link.focus) link.focus();
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
