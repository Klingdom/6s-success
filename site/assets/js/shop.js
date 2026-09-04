/* 6S Success: shop page. Renders the catalog into #grid, wires category filters.
   Relies on window.CATALOG (data.js) and window.renderProduct / window.observeReveals (site.js). */
(function () {
  "use strict";

  var grid = document.getElementById("grid");
  if (!grid) return;

  var CATALOG = window.CATALOG || [];
  var buttons = Array.prototype.slice.call(document.querySelectorAll(".filters button"));

  /* THE FILTER ROW IS BUILT FROM THE CATALOGUE, NOT TYPED INTO THE PAGE.
   *
   * It used to be four hardcoded buttons. The catalogue then grew from ten
   * products to 159 across seven categories, and four of those categories had
   * no button, so 149 products could only be reached by scrolling past every
   * other one. Anything hardcoded beside a generated list eventually
   * disagrees with it.
   *
   * Order is fixed rather than alphabetical, and it is deliberately the same
   * order the catalogue array itself is in (see site/assets/js/data.js), so
   * the filter row and the "All" grid tell the same story instead of two.
   *
   * Books & Guides leads, then Room Packs. Six varied tiles before nineteen
   * near-identical ones, on purpose: a person on the shop page has not told us
   * a room, so the first thing they need is orientation, and $19 for the whole
   * house next to two genuinely free things answers "what is this?" better
   * than nineteen tiles that differ only by a room name.
   *
   * Room Packs come second because the room is the unit people actually name.
   * Nobody says "my shoe zone is a mess", they say "my kitchen is a mess", so
   * the $9 room pack is the entry offer (DECISIONS.md D-016). It leads on the
   * 20 room pages, where the visitor HAS named a room, rather than here where
   * they have not.
   *
   * The 109 micro zone packs are our unit of diagnosis rather than the
   * customer's complaint, and they are best found from the zone page that has
   * just explained that zone, not from a wall of 109 near-identical tiles.
   *
   * Area Bundles sit last of the paid groups because they are the one tier
   * that maps to no job anybody names out loud: they group rooms by function
   * ("every wet room"), which is how we think, not how a person with a messy
   * bathroom thinks. PRICING.md 0.3 recommends retiring or repricing them;
   * until somebody decides, they are demoted rather than hidden. */
  var CAT_ORDER = ["Books & Guides", "Room Packs", "App", "Situation Kits",
                   "Micro Zone Packs", "Area Bundles", "Consulting"];

  function buildFilters() {
    var row = document.querySelector(".filters");
    if (!row || !window.CATALOG) { return; }
    var present = {};
    CATALOG.forEach(function (p) { if (p.cat) { present[p.cat] = (present[p.cat] || 0) + 1; } });
    var cats = CAT_ORDER.filter(function (c) { return present[c]; })
      .concat(Object.keys(present).filter(function (c) {
        return CAT_ORDER.indexOf(c) < 0;
      }).sort());

    row.innerHTML = '<button type="button" data-cat="All" aria-pressed="true">All</button>'
      + cats.map(function (c) {
          var safe = c.replace(/&/g, "&amp;").replace(/</g, "&lt;");
          /* The count is shown because "Micro Zone Packs" gives no sense of
             whether that is three products or a hundred and nine. */
          return '<button type="button" data-cat="' + safe + '" aria-pressed="false">'
            + safe + ' <span class="n">' + present[c] + '</span></button>';
        }).join("");
  }

  buildFilters();
  /* buildFilters replaces the whole row, so the node list captured above now
     points at buttons that are no longer in the document. Every click handler
     bound below would attach to a detached element and the filter would
     silently do nothing, which is exactly what it did until this line. */
  buttons = Array.prototype.slice.call(document.querySelectorAll(".filters button"));

  function render(cat) {
    var list = (cat && cat !== "All")
      ? CATALOG.filter(function (p) { return p.cat === cat; })
      : CATALOG.slice();

    if (!list.length) {
      grid.innerHTML = '<p class="lede">Nothing to show here yet. Try another category.</p>';
      return;
    }

    grid.innerHTML = list.map(function (p) {
      return (typeof window.renderProduct === "function") ? window.renderProduct(p) : "";
    }).join("");

    if (typeof window.observeReveals === "function") window.observeReveals();
  }

  function select(cat) {
    buttons.forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.cat === cat ? "true" : "false");
    });
    render(cat);
  }

  buttons.forEach(function (b) {
    b.addEventListener("click", function () { select(b.dataset.cat); });
  });

  /* initial category from ?cat= in the URL, if it matches a filter button */
  var requested = null;
  try { requested = new URLSearchParams(location.search).get("cat"); } catch (e) { requested = null; }

  var valid = requested && buttons.some(function (b) { return b.dataset.cat === requested; });
  select(valid ? requested : "All");
})();
