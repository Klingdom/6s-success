(function () {
    var form = document.getElementById("contact-form");
    var ok = document.getElementById("contact-success");

    /* The product a visitor clicked through from, if any. Read from the query
       string against a fixed list of known SKUs rather than echoed straight
       into the page: ?ref= is attacker-controlled, and reflecting arbitrary
       text from a URL into the DOM is how a link becomes an injection. */
    var NAMES = {
      "CN-CORP": "Corporate Lean 6S",
      "CN-INHOME": "the In-Home Reset Day",
      "CN-VIRTUAL": "the Virtual Home Consult",
      "BK-BUNDLE": "the Complete Digital Bundle",
      "MZ-MANUAL": "the Micro Zone Manual",
      "PACK-HOUSE": "the Whole House Print Pack",
      "BK-EB": "the Home Edition eBook"
    };
    /* NOT named "ref": a later block in this same IIFE declares var ref for the
       topic prefill, and var is function scoped, so it would overwrite this at
       load time and the message would carry the raw query value instead of the
       validated name. Caught by grepping for the declaration rather than
       assuming the scopes were separate. */
    var refName = null;
    try {
      var q = new URLSearchParams(location.search).get("ref");
      if (q && Object.prototype.hasOwnProperty.call(NAMES, q)) { refName = NAMES[q]; }
    } catch (e) { refName = null; }

    /* There is no mail server behind this form. Rather than show a "Thanks" for
       something that did not happen and throw the message away, pack what they
       wrote into a mailto so one more click actually delivers it. When a real
       endpoint exists, POST here and drop the notice. */
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!form.checkValidity()) { form.reportValidity(); return false; }

        var val = function (id) {
          var el = document.getElementById(id);
          return el ? String(el.value || "").trim() : "";
        };
        var topic = val("c-topic") || "General question";
        /* Somebody who clicked "Request a quote" on a specific product arrived
           here with ?ref= naming it, and this page used to ignore that
           entirely, so they landed on a generic form and had to explain again
           what they had just told us by clicking. On the highest value products
           in the catalogue, that is the worst possible place to make somebody
           repeat themselves. */
        var body = [
          refName ? "About: " + refName : null,
          "Name: "  + val("c-name"),
          "Email: " + val("c-email"),
          "Topic: " + topic,
          "",
          val("c-message")
        /* Only nulls. filter(Boolean) would also eat the deliberate empty
           string above, which is the blank line separating the header from the
           message, and would run Topic straight into what the person wrote. */
        ].filter(function (x) { return x !== null; }).join("\n");

        var link = document.getElementById("contact-mailto");
        if (link) {
          link.href = "mailto:support@6s-success.com" +
            "?subject=" + encodeURIComponent("6S Success: " + topic) +
            "&body=" + encodeURIComponent(body);
          /* Open it on the submit itself rather than making the visitor find
             a second button. Pressing Send message and being told "nothing
             has been sent yet" reads as a failure, and the person who came
             here to hire somebody leaves. One click, then the copy box below
             is the fallback for anyone whose browser has no mail client. */
          try { link.click(); } catch (e) { /* fallback is already on screen */ }
        }
        /* A mailto link is not a delivery mechanism, it is a request that the
           visitor's operating system happens to have a mail client attached.
           When it does not, the link does nothing, the message is gone, and the
           person has no idea anything failed. So the composed text is also put
           somewhere they can copy it from. */
        var copyBox = document.getElementById("contact-copy");
        if (copyBox) { copyBox.value = body; }

        /* Counted the same way the newsletter form's mailto handoff is
           counted (site.js, "list-signup"): until now nothing anywhere
           recorded that a visitor tried to reach us through this form.
           Only the fixed dropdown topic travels, never name, email or the
           message itself, matching CLAUDE.md section 47. */
        if (window.Measure) { window.Measure.track("contact-submit", { topic: topic }); }

        if (ok) {
          ok.hidden = false;
          if (ok.scrollIntoView) ok.scrollIntoView({ behavior: "smooth", block: "center" });
          if (link && link.focus) link.focus();
        }
        return false;
      });
    }

    var copyBtn = document.getElementById("contact-copy-btn");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var box = document.getElementById("contact-copy");
        if (!box) { return; }
        box.select();
        var done = function () {
          copyBtn.textContent = "Copied";
          setTimeout(function () { copyBtn.textContent = "Copy the message"; }, 2500);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(box.value).then(done, function () {});
        } else if (document.execCommand) {
          /* Older browsers, and any context where the clipboard API is not
             permitted. Selecting the text above means a manual copy still
             works even if both of these fail. */
          try { document.execCommand("copy"); done(); } catch (e) {}
        }
      });
    }

    /* Prefill from ?ref=<sku> used by "Request a quote" buttons across the site. */
    function selectTopic(target) {
      var topic = document.getElementById("c-topic");
      if (!topic) return;
      for (var i = 0; i < topic.options.length; i++) {
        if (topic.options[i].value === target) { topic.selectedIndex = i; break; }
      }
    }

    try {
      var ref = new URLSearchParams(window.location.search).get("ref");
      if (ref && Array.isArray(window.CATALOG)) {
        var p = window.CATALOG.find(function (x) { return x.sku === ref; });
        if (p) {
          var msg2 = document.getElementById("c-message");
          var wantsQuote = (p.cat === "Consulting") || (p.price === null || p.price === undefined);
          selectTopic(wantsQuote ? "Consulting / quote" : "Book / product order");
          if (msg2 && !msg2.value) {
            msg2.value = "I'm interested in: " + p.name + " (" + p.sku + ").";
          }
        }
      }
    } catch (err) { /* stay quiet if ref is missing or unknown */ }
  })();