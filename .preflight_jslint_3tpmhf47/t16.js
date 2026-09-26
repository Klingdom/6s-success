(function () {
    if (!window.CATALOG || !window.renderProduct) return;
    function fill(id, filter) {
      var box = document.getElementById(id);
      if (!box) return;
      box.innerHTML = window.CATALOG.filter(filter).map(window.renderProduct).join("");
    }
    /* The Courses category was retired on 21 August because none of it could
       be delivered. This grid rendered empty under a heading promising every
       way to learn the method, so it now shows the ways that exist. */
    fill("courses", function (p) { return p.cat === "Books & Guides"; });
    fill("app", function (p) { return p.cat === "App"; });
    window.observeReveals && window.observeReveals();
  })();