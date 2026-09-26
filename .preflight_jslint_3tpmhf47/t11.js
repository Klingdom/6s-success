(function () {
  var form = document.getElementById("corp-form");
  if (!form) { return; }
  var ok = document.getElementById("corp-ok");
  var link = document.getElementById("corp-mailto");
  var copyBox = document.getElementById("corp-copy");
  var copyBtn = document.getElementById("corp-copy-btn");
  var assetLink = document.getElementById("corp-asset-link");

  /* The generic site-wide handler in measure.js already fires
     "free-download" for any /downloads/ link, with from:"corporate"
     (page()'s own fallback branch reads the path). This is the more
     specific event REVIEW-COMMERCE-2026-09-07.md C12 asks for, tracked
     alongside it rather than instead of it, the same way corporate-enquiry
     sits alongside quote-click for the enquiry form. */
  if (assetLink) {
    assetLink.addEventListener("click", function () {
      if (window.Measure && window.Measure.track) {
        window.Measure.track("corporate-asset-download", { sv: 1 });
      }
    });
  }

  function v(id) {
    var el = document.getElementById(id);
    return el ? String(el.value || "").trim() : "";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    /* Native validation rather than a hand-rolled check: it covers the three
       required fields AND the email format in one call, it announces itself to
       a screen reader, and it puts the message where the browser's own
       conventions put it. The hand-rolled version this replaced only tested
       for emptiness, so a typo'd address passed straight through and the reply
       bounced with nobody the wiser. Same pattern as contact.html. */
    if (form.checkValidity && !form.checkValidity()) {
      if (form.reportValidity) { form.reportValidity(); }
      return false;
    }

    var body = [
      "Service: Corporate Lean 6S",
      "",
      "Company: " + v("k-company"),
      "Name and role: " + v("k-name"),
      "Email: " + v("k-email"),
      "Phone: " + v("k-phone"),
      "Site or sites: " + v("k-sites"),
      "People in the area: " + v("k-people"),
      "Areas or zones wanted first: " + v("k-zones"),
      "Wants to start: " + v("k-when"),
      "Train their own people: " + v("k-train"),
      "Suggested time for a scoping call: " + v("k-time"),
      "",
      "What prompted this:",
      v("k-why")
    ].join("\n");

    var subject = "Corporate Lean 6S enquiry: " + v("k-company");
    var href = "mailto:support@6s-success.com?subject=" + encodeURIComponent(subject)
      + "&body=" + encodeURIComponent(body);

    /* Shown before the mail app is asked for, so a browser with no mail
       client attached still leaves the visitor holding their message. */
    if (copyBox) { copyBox.value = body; }
    if (ok) { ok.hidden = false; }
    if (link) {
      link.href = href;
      /* Opened on the submit itself. Being told "nothing has happened yet"
         after pressing a button reads as a failure, and the person who came
         here to hire somebody leaves. */
      try { link.click(); } catch (err) { /* the copy box is already shown */ }
    }
    if (ok && ok.scrollIntoView) {
      ok.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    /* The one number that says whether this page did anything. No company
       name, no address, nothing identifying: only that an enquiry was
       composed, and whether it named a time, which is the difference between
       a reply that can carry a calendar invite and one that has to ask. */
    if (window.Measure && window.Measure.track) {
      window.Measure.track("corporate-enquiry",
                           { timed: v("k-time") ? 1 : 0, sv: 1 });
    }
    return false;
  });

  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      if (!copyBox) { return; }
      copyBox.select();
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(copyBox.value);
        } else {
          document.execCommand("copy");
        }
        copyBtn.textContent = "Copied";
      } catch (err) {
        copyBtn.textContent = "Select the text above and copy it";
      }
    });
  }
})();