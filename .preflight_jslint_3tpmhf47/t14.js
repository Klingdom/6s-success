(function () {
    var feat = ["BK-BUNDLE", "MZ-MANUAL", "PACK-HOUSE", "BK-EB"];
    var box = document.getElementById("featured");
    if (box && window.CATALOG) {
      box.innerHTML = feat.map(function (sku) {
        var p = window.CATALOG.find(function (x) { return x.sku === sku; });
        return p ? window.renderProduct(p) : "";
      }).join("");
      window.observeReveals && window.observeReveals();
    }
  })();