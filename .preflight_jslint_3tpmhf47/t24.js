(function () {
  var grid = document.getElementById("zgrid");
  var count = document.getElementById("zcount");
  var empty = document.getElementById("zempty");
  var roomSel = document.getElementById("zroom");
  var chips = [].slice.call(document.querySelectorAll(".zchip"));
  var cards = [].slice.call(grid.querySelectorAll(".zcard"));
  var bucket = "all";

  function apply() {
    var room = roomSel.value;
    var n = 0;
    cards.forEach(function (c) {
      var ok = (bucket === "all" || c.getAttribute("data-bucket") === bucket) &&
               (room === "all" || c.getAttribute("data-room") === room);
      c.hidden = !ok;
      if (ok) { n++; }
    });
    /* role=status on the count means a screen reader hears the result of a
       filter, which is otherwise a silent change to a long list. */
    count.textContent = n + (n === 1 ? " zone" : " zones");
    empty.hidden = n > 0;
  }

  chips.forEach(function (b) {
    b.addEventListener("click", function () {
      chips.forEach(function (x) { x.classList.remove("is-on"); });
      b.classList.add("is-on");
      bucket = b.getAttribute("data-filter");
      apply();
    });
  });
  roomSel.addEventListener("change", apply);
})();