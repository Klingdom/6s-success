/* What happens after payment genuinely differs by what was bought, and a page
   that says "we will be in touch" to everybody is the kind of confirmation
   that makes people write in to ask whether it worked. The sku arrives on the
   query string from the Stripe payment link. */
(function () {
  var PLANS = {
    "CN-VIRTUAL": {
      heading: "Your Virtual Home Consult",
      lede: "Your one hour consult is paid for. Here is what happens next.",
      steps: [
        ["We email you within one business day", "From support@6s-success.com, to agree a time that suits you. Reply with two or three that work."],
        ["You send photos beforehand", "Whatever rooms you want to cover. Photos let us spend the call on decisions rather than on looking."],
        ["The call itself, one hour, online", "Room by room, working from what you actually want each space to do."],
        ["A written plan afterwards", "The micro zones to work in order, the root cause behind each one, and a product list with types rather than brands."],
        ["Not useful? Tell us within 7 days", "We refund it in full, no argument."]
      ]
    },
    "CN-INHOME": {
      heading: "Your In-Home Reset Day",
      lede: "Your reset day is paid for. Here is what happens next.",
      steps: [
        ["We email you within one business day", "To confirm your address is inside the service area and agree a date. If we cannot reach you to book it, you get a full refund."],
        ["A short call before the day", "Fifteen minutes to agree which rooms matter most, so the day starts with the work rather than the discussion."],
        ["The day itself", "A full day on site, working the rooms you chose, zone by zone."],
        ["Standards left behind", "Every zone we finish gets a written standard, so the room can be put back in minutes rather than rebuilt."]
      ]
    },
    "BK-EB": {
      heading: "Your copy of the book",
      lede: "Paid. The book is on its way to your inbox.",
      steps: [
        ["Check your email within a few hours", "It arrives from support@6s-success.com with the EPUB attached. Deliveries go out on a schedule, so it is not instant."],
        ["Open it in any reader", "Apple Books, Google Play Books, Kobo, Calibre and most e-readers all take EPUB directly."],
        ["Start at chapter one, or at your worst room", "Part nine is twenty room playbooks. Skipping to yours is a perfectly good way to read it."]
      ]
    },
    "MZ-MANUAL": {
      heading: "Your Micro Zone Manual",
      lede: "Paid. The manual is on its way to your inbox.",
      steps: [
        ["Check your email within a few hours", "It arrives from support@6s-success.com as an HTML file you can open in any browser."],
        ["Print the room you are working on", "Use your browser's print dialog. There is no need to print all 114 zones."],
        ["Work one zone at a time", "Each carries the six passes in order, the safety checks, and the standard that keeps it fixed."]
      ]
    },
    "PACK-HOUSE": {
      heading: "Your Whole House Print Pack",
      lede: "Paid. All 684 cards are on their way to your inbox.",
      steps: [
        ["Check your email within a few hours", "It arrives from support@6s-success.com as an HTML file. Deliveries go out on a schedule, so it is not instant."],
        ["Print the room you are starting with", "Nine cards to a US Letter page across 76 pages, in room order. Print the pages for one room, not the lot."],
        ["Card stock if you have it", "Paper works. Card stock survives being carried around a kitchen."],
        ["Draw one card and do it", "That is the whole method. The card names one job and tells you when you can stop."]
      ]
    },
    "BK-BUNDLE": {
      heading: "Your Complete Digital Bundle",
      lede: "Paid. All three files are on their way to your inbox, together.",
      steps: [
        ["Check your email within a few hours", "One message from support@6s-success.com with three attachments: the book as an EPUB, the Micro Zone Manual and the Whole House Print Pack as HTML."],
        ["Nothing is being posted to you", "This bundle is entirely digital. There is no parcel and no tracking number to wait for."],
        ["Read, reference, carry", "The book is the method, the manual is the reference, and the pack is what you take into the room."]
      ]
    },
    "_generic": {
      heading: "Your order",
      lede: "Your payment went through and your receipt is on its way from Stripe.",
      steps: [
        ["We email you within one business day", "From support@6s-success.com, confirming what you bought and what happens next."],
        ["Anything digital arrives by email", "Usually within a few hours. Check spam if it has not appeared."]
      ]
    }
  };

  var sku = new URLSearchParams(location.search).get("sku") || "";
  /* Every product we sell is named above. An unrecognised sku falls to the
     generic plan, which promises nothing specific and therefore cannot promise
     the wrong thing. The old fallbacks guessed from the sku string and guessed
     wrong the moment the bundle stopped being a hardcover. */
  var plan = PLANS[sku];
  /* Falling through with no plan left the steps list empty, so a visit to
     /thanks.html with no sku showed a heading with nothing under it. A
     confirmation page that confirms nothing is worse than no page. */
  if (!plan) plan = PLANS._generic;

  document.getElementById("heading").textContent = plan.heading;
  document.getElementById("lede").textContent = plan.lede;
  document.getElementById("steps").innerHTML = plan.steps.map(function (s) {
    return "<li><strong>" + s[0] + "</strong>" + s[1] + "</li>";
  }).join("");

  /* REVIEW-COMMERCE-2026-09-07.md C9: the two appointment services collect no
     time anywhere on the money path. ops/service_orders.py can only attach a
     calendar invite when a customer names a time, and until this block
     existed nothing ever asked for one until Phil's own follow-up email, so
     every purchase became a manual round trip starting from zero. Shown only
     for the two services that are actually appointments; a digital product
     has nothing to schedule. Same composed-message, mailto handoff pattern
     as site/corporate.html's enquiry form (no ticket system, no new billing
     surface, no card data, no new Stripe object), and the "14 October at
     2pm" placeholder is not decoration: it is the exact shape
     ops/service_orders.py's find_time() parses, so a message sent unedited
     comes back with a real .ics attached rather than another "what time
     works" reply. */
  var SCHEDULED = { "CN-VIRTUAL": 1, "CN-INHOME": 1 };
  var scheduleBlock = document.getElementById("schedule-block");
  if (scheduleBlock && SCHEDULED[sku]) {
    var serviceName = plan.heading.replace(/^Your /, "");
    scheduleBlock.hidden = false;
    document.getElementById("schedule-heading").textContent =
      "Pick a time for your " + serviceName.toLowerCase();
    document.getElementById("schedule-intro").textContent =
      "Tell us when works and we will send a calendar invite for it, "
      + "rather than waiting for the usual back-and-forth by email.";

    var schedForm = document.getElementById("schedule-form");
    var schedOk = document.getElementById("sch-ok");
    var schedLink = document.getElementById("sch-mailto");
    var schedCopy = document.getElementById("sch-copy");
    var schedCopyBtn = document.getElementById("sch-copy-btn");

    function sv(id) {
      var el = document.getElementById(id);
      return el ? String(el.value || "").trim() : "";
    }

    schedForm.addEventListener("submit", function (e) {
      e.preventDefault();
      /* Native validation, same reasoning as corporate.html's form: it
         covers the one required field and announces itself to a screen
         reader without a hand-rolled emptiness check. */
      if (schedForm.checkValidity && !schedForm.checkValidity()) {
        if (schedForm.reportValidity) { schedForm.reportValidity(); }
        return false;
      }

      var body = [
        "Service: " + serviceName,
        "SKU: " + sku,
        "",
        "Preferred time: " + sv("sch-time"),
        "Second choice: " + (sv("sch-time2") || "none given"),
        "",
        "Anything to know beforehand:",
        sv("sch-notes") || "nothing noted"
      ].join("\n");

      var subject = "Scheduling: " + serviceName;
      var href = "mailto:support@6s-success.com?subject="
        + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);

      /* Shown before the mail app is asked for, so a browser with no mail
         client attached still leaves the visitor holding their message. */
      if (schedCopy) { schedCopy.value = body; }
      if (schedOk) { schedOk.hidden = false; }
      if (schedLink) {
        schedLink.href = href;
        try { schedLink.click(); } catch (err) { /* the copy box is already shown */ }
      }
      if (schedOk && schedOk.scrollIntoView) {
        schedOk.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      /* sku only, never the time or the notes: CLAUDE.md 47, and matching
         corporate.html's own corporate-enquiry event, which tracks whether a
         time was given rather than the time itself. */
      if (window.Measure && window.Measure.track) {
        window.Measure.track("service-schedule", { sku: sku, sv: 2 });
      }
      return false;
    });

    if (schedCopyBtn) {
      schedCopyBtn.addEventListener("click", function () {
        if (!schedCopy) { return; }
        schedCopy.select();
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(schedCopy.value);
          } else {
            document.execCommand("copy");
          }
          schedCopyBtn.textContent = "Copied";
        } catch (err) {
          schedCopyBtn.textContent = "Select the text above and copy it";
        }
      });
    }
  }
})();