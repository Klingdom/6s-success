(function () {
    /* Same composed-mailto pattern as contact.html's own form: no mail pipe
       exists yet, so a submission is packed into a mailto link one click
       delivers, with a copy-box fallback for a browser with no mail client
       attached. REVIEW-COMMERCE-2026-09-07.md C10. */
    var form = document.getElementById("intro-call-form");
    var ok = document.getElementById("intro-call-success");
    if (!form) { return; }

    /* Same ?from=<type>:<slug> origin convention offer()/room_offer() already
       set on the paid consult button, so the free path can be told apart
       from a cold arrival without adding a second convention. */
    var origin = null;
    try {
      var q = new URLSearchParams(location.search).get("from");
      if (q) {
        var parts = q.split(":");
        origin = { type: parts[0].slice(0, 20), slug: parts[1] ? decodeURIComponent(parts[1]).slice(0, 40) : null };
      }
    } catch (e) { origin = null; }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return false; }

      var val = function (id) {
        var el = document.getElementById(id);
        return el ? String(el.value || "").trim() : "";
      };
      var body = [
        origin ? "Came from: " + origin.type + (origin.slug ? " (" + origin.slug + ")" : "") : null,
        "Name: " + val("ic-name"),
        "Email: " + val("ic-email"),
        "Room: " + val("ic-room"),
        "",
        val("ic-message") || "(no extra detail given)"
      ].filter(function (x) { return x !== null; }).join("\n");

      var link = document.getElementById("intro-call-mailto");
      if (link) {
        link.href = "mailto:support@6s-success.com" +
          "?subject=" + encodeURIComponent("6S Success: free 15-minute call, which zone first") +
          "&body=" + encodeURIComponent(body);
        try { link.click(); } catch (e) { /* fallback is already on screen */ }
      }
      var copyBox = document.getElementById("intro-call-copy");
      if (copyBox) { copyBox.value = body; }

      /* Fixed-shape event only, never name/email/room/message: CLAUDE.md 47.
         "from" is the same bounded, already-sliced origin type the service-cta
         handler in measure.js records for the paid consult button, not free
         text typed by the visitor. */
      if (window.Measure) {
        window.Measure.track("intro-call-request", origin && origin.type ? { from: origin.type } : {});
      }

      if (ok) {
        ok.hidden = false;
        if (ok.scrollIntoView) { ok.scrollIntoView({ behavior: "smooth", block: "center" }); }
        if (link && link.focus) { link.focus(); }
      }
      return false;
    });

    var copyBtn = document.getElementById("intro-call-copy-btn");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var box = document.getElementById("intro-call-copy");
        if (!box) { return; }
        box.select();
        var done = function () {
          copyBtn.textContent = "Copied";
          setTimeout(function () { copyBtn.textContent = "Copy the message"; }, 2500);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(box.value).then(done, function () {});
        } else if (document.execCommand) {
          try { document.execCommand("copy"); done(); } catch (e) {}
        }
      });
    }
  })();