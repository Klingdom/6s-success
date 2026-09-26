(function () {
    var box = document.getElementById("book-editions");
    if (box && window.CATALOG) {
      box.innerHTML = window.CATALOG
        .filter(function (p) { return p.cat === "Books & Guides"; })
        .map(function (p) { return window.renderProduct(p); })
        .join("");
      window.observeReveals && window.observeReveals();
    }
  })();