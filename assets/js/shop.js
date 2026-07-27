/* 6S Success — shop page: render catalog into #grid, wire category filters.
   Relies on window.CATALOG (data.js) and window.renderProduct / window.observeReveals (site.js). */
(function () {
  "use strict";

  var grid = document.getElementById("grid");
  if (!grid) return;

  var CATALOG = window.CATALOG || [];
  var buttons = Array.prototype.slice.call(document.querySelectorAll(".filters button"));

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
