(function () {
  var grid = document.getElementById("grid");
  var chips = [].slice.call(document.querySelectorAll(".chips button"));
  var groups = [].slice.call(document.querySelectorAll(".grp"));

  /* A card turns over rather than swapping pictures, because the two faces
     were designed as two sides of one object. aria-pressed carries the state
     so a screen reader knows which face is showing. */
  grid.addEventListener("click", function (e) {
    var b = e.target.closest(".flip");
    if (!b) { return; }
    var on = b.getAttribute("aria-pressed") === "true";
    b.setAttribute("aria-pressed", on ? "false" : "true");
    /* The label says which face a sighted person is looking at, so it has to
       change with the face. It carries the whole sentence rather than just a
       verb, because "Turn it over" alone tells a screen reader nothing about
       what is currently in front of them. */
    b.setAttribute("aria-label", b.getAttribute("aria-label")
      .replace(on ? "Back is showing" : "Front is showing",
               on ? "Front is showing" : "Back is showing"));
  });

  /* Filtering hides whole groups, so a heading never survives its cards. */
  function show(t) {
    groups.forEach(function (g) { g.hidden = t !== "all" && g.dataset.t !== t; });
    chips.forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.t === t ? "true" : "false");
    });
  }
  chips.forEach(function (b) {
    b.addEventListener("click", function () { show(b.dataset.t); });
  });
})();