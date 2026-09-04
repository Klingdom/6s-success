#!/usr/bin/env python3
"""
Build site/corporate.html: the page Corporate Lean 6S never had.

WHY THIS PAGE EXISTS
--------------------
Measured 2026-09-04 (REVENUE-REVIEW-2026-09-04.md): $19 of gross revenue in
this business's life, one charge, from 52 visitors in thirty days and zero
arrivals from Google. 97% of the 159 SKUs are priced between $4 and $19. At a
generous 2% conversion the $4 packs would need a quarter of a million visitors
a month to reach the goal. The catalogue cannot get there.

CN-CORP, "Corporate Lean 6S", is the one line in that catalogue that needs no
consumer traffic at all: a corporate buyer with a budget closes at a scale the
rest of the shop cannot reach in a month. And its whole presence on the live
site was one sentence on consulting.html saying it is quoted per engagement, a
`price: null` record with no page behind it, and a "Request a quote" badge that
led to a generic contact form. Somebody who arrived ready to buy the highest
value thing here had nothing to read and nowhere to go.

So: a page for a business buyer. Not a homeowner page with the word "team"
substituted in.

WHAT IS DELIBERATELY NOT ON IT
------------------------------
No price, and no range. Corporate Lean 6S is scoped per engagement. Every
figure this repository holds for that kind of work ($5,000 to $15,000 in
REVENUE-REVIEW-2026-09-04.md) is a market range read off the industry, NOT a
quote we have given or received, and that review says so in its own honest
limits section. Printing it would turn somebody else's benchmark into our
price. What the page does instead is name the nine things that actually
determine the scope, which is more use to a buyer working out whether they can
afford us than an invented number would be. main() asserts that no dollar
figure of any kind reaches the page.

No client names, no logos, no case studies, no testimonials, no count of
engagements delivered. We have none, and a corporate buyer is precisely the
reader most likely to check. CLAUDE.md section 8 is absolute and this is the
page where breaking it would cost the most.

What the page DOES claim is Phil's own career record, which is already
published on about.html and is his own work, framed as exactly that: work
delivered inside those organizations before 6S Success existed, not client
outcomes of this offer. See CREDENTIAL SOURCING below for where each item
comes from.

THE ENQUIRY ROUTE IS A MAILTO, AND THE PAGE SAYS SO FIRST
---------------------------------------------------------
Listmonk returns HTTP 500 (Hostinger rejects the sender), so there is no
delivery mechanism on this site that can be trusted with a lead. A mailto is
not a delivery mechanism either, it is a request that the visitor's operating
system happens to have a mail client attached, so the page states the mechanism
BEFORE it asks, and puts the composed message in a copyable box for anyone
whose browser has none. That is the pattern cro-growth established on
contact.html and it is matched here rather than reinvented.

The composed message is then picked up by machinery that already exists:
ops/service_orders.py watches the support@ inbox for unread mail matching one
of three services, forwards it to the owner, and attaches a real .ics calendar
invite when the sender named a time. Three consequences bind this file to that
one, and all three are asserted at the end of main():

  1. The subject line must contain a phrase service_orders.which_service()
     routes to "Corporate Lean 6S". It does: "Corporate Lean 6S enquiry".
  2. The composed body must contain no phrase belonging to the other two
     services, or a corporate lead could be forwarded as a home booking.
  3. The date example on the form must be a shape find_time() can parse, or
     the calendar invite the page promises never gets attached.

The scoping call is described as one hour because service_orders.DURATION says
sixty minutes for this service: the copy follows the tool, not the reverse.

OWNERSHIP
---------
This file owns site/corporate.html completely. Hand editing that file creates
the drift issue #26 exists for, so it is registered in preflight's
gate_generator_ownership list. It also chains the same seven whole-site wiring
passes every other single page generator here chains, for the same reason: an
unchained wiring pass is drift waiting for the next rebuild.

Run:  python ops/build_corporate.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "corporate.html")
DATA_JS = os.path.join(SITE, "assets", "js", "data.js")
BASE = "https://6s-success.com"
URL = BASE + "/corporate.html"

# The chrome is lifted from resources.html rather than retyped, because
# preflight's gate_footer_consistent compares every page's footer against that
# one byte for byte. A hand-copied footer is a gate failure waiting for the
# next time a link is added to the real one.
CHROME_SRC = os.path.join(SITE, "resources.html")

SUBJECT = "Corporate Lean 6S enquiry"
TO = "support@6s-success.com"
DATE_EXAMPLE = "14 October at 2pm"

# CREDENTIAL SOURCING. Nothing on this page is stated that is not either
# already published on the live site or Phil's own written assertion about
# himself, and the distinction is recorded here so nobody has to re-derive it.
#
#   Lean Six Sigma Master Black Belt   about.html #founder, live on the site.
# PMP WAS REMOVED FROM THIS PAGE, 2026-09-04.
#
# The brief said it was already published in the book's author block. It is
# not. It appears nowhere on the live site, nowhere in the book front matter,
# and nowhere in the print-and-play PDF: only in our own internal strategy
# documents, which are not evidence about a real person's certification.
#
# "Lean Six Sigma Master Black Belt" stays, because it IS already published on
# about.html and has been for weeks.
#
# An unverified professional credential on a page selling five-figure
# engagements is the highest-cost place in the whole business to be wrong, and
# it is a claim about Phil rather than about us. Put it back only when he
# confirms it, and then publish it on about.html too so the two pages agree.
#   PMP                                Phil's own documents:
#                                      6S_Success_20K_Month_Revenue_Strategy.md
#                                      and super prompts/Claude_Code_Super_
#                                      Prompt_6S_Success_Grow.md. Searched
#                                      2026-09-04: it is NOT currently printed
#                                      on the site or in the book front matter,
#                                      so this page is the first published
#                                      surface carrying it.
#   Twenty years, Idaho DHW, McKinstry,
#   Amazon, Process Kaizen             about.html #founder, live and published.
#
# The career figures are written in words rather than digits, as about.html
# already writes them. Not decoration: preflight's gate_unsourced_stats flags a
# digit beside a results word with no source nearby, and these are a personal
# record rather than a claim about what this offer will do for a buyer.

# The nine things that actually move a scope. This is the honest substitute for
# a price, and it is a list a buyer can answer for themselves in a minute.
SCOPE_DRIVERS = [
    ("How many people are in the room",
     "A kaizen event with six people on one cell and one with thirty across "
     "three shifts are different weeks of work, not the same week charged "
     "differently."),
    ("How many sites",
     "One building is one engagement. Four buildings is either four "
     "engagements or one plus a rollout, and those scope differently."),
    ("How many areas or zones in the baseline",
     "The assessment is scoped by what gets walked, scored and photographed. "
     "One stockroom is not one plant."),
    ("How much of it is on site",
     "Assessment, standards writing and audit coaching all work over video. "
     "The event days do not; they happen where the work happens."),
    ("Travel",
     "Engagements are run from Boise, Idaho. Anywhere else, travel and "
     "lodging sit in the scope at cost, named before you agree to anything."),
    ("Whether we train your trainers",
     "Teaching two or three of your own people to run the next event and hold "
     "the audit adds days, and it is usually the difference between an "
     "improvement and a capability."),
    ("Who writes the standards",
     "Written with your team costs more time in the room and holds far "
     "better. Written for you is faster and decays faster. Both are real "
     "choices, and we will tell you which one we think you need."),
    ("How long we stay for sustain",
     "The audit either becomes yours or it stops when we leave. Staying for a "
     "few audit cycles is what makes the difference, and it is scoped "
     "separately so you can decline it."),
    ("Shifts, unions and language",
     "An event that has to run once per shift runs more than once. If the "
     "floor does not work in English, the standards cannot either."),
]

# The four components. Concrete on purpose: a buyer should be able to tell
# whether they are being sold a workshop or a piece of work.
COMPONENTS = [
    ("Assessment",
     "Two days",
     "We walk the area with the people who work in it and produce a zone map, "
     "a scored 6S baseline for every zone, and photographs of the current "
     "state. Then we name where the time actually goes: searching, walking, "
     "waiting, rework, and anything standing on the safety line. You get the "
     "baseline in writing whether or not you go further, because a scope "
     "argued from a walk-through nobody wrote down is how these engagements "
     "go wrong."),
    ("Kaizen event",
     "Two or three consecutive days",
     "On the floor, with the people who do the work, not in a conference "
     "room. Sort runs against a red-tag area with a written disposition rule "
     "and a named person who can approve a skip. Straighten places what is "
     "left at the point of use and marks it. Shine is run as inspection, so "
     "cleaning finds the leak instead of hiding it. The area is different at "
     "the end of the week, and your team is the one that changed it."),
    ("Standards",
     "Written during and after the event",
     "One page per zone: a photograph of the correct state, what belongs there "
     "and how much, the named owner, the trigger that starts the reset, and "
     "the replenishment signal. Posted in the zone, not filed. A standard "
     "nobody can see from where they stand is a document, not a control."),
    ("Audit and sustain",
     "Set up in the last week, then yours",
     "A layered audit: the team leader checks daily or per shift, the "
     "supervisor weekly, the manager monthly, each against the same scoring "
     "sheet the baseline used, so the trend line is comparable to day one. We "
     "train your auditors and run the first two audits with them. This is the "
     "part most 5S programmes skip, and skipping it is why most 5S programmes "
     "get run twice."),
]

FOR_YOU = [
    "Operations, EHS, quality and facilities leaders who own a physical area "
    "and a budget.",
    "Manufacturing cells, warehouses and stockrooms, maintenance shops, "
    "service bays, labs, clinical supply and med rooms, commercial kitchens, "
    "and offices where shared physical work actually happens.",
    "Teams with an audit, a customer visit or a certification coming, who need "
    "the area to hold up and to keep holding up afterwards.",
    "Teams who ran 5S once, got a good week out of it, and watched it decay. "
    "That decay has a cause, and it is nearly always the missing sixth S.",
    "New lines, new buildings and relocations, where the standard is cheapest "
    "to set before anybody has developed a habit.",
]

NOT_FOR_YOU = [
    "If what you need is a tidy-up before a visit, hire cleaners. It will cost "
    "less and we would be the wrong spend.",
    "If nobody with authority to approve disposal and to move equipment will "
    "be in the room, the event stalls on day one. We would rather say so now "
    "than invoice you for it.",
    "If the people who do the work cannot be released for the event days, "
    "there is no engagement. A standard written over their heads is one they "
    "will be right to ignore.",
    "If you want a certificate rather than a changed area, there are cheaper "
    "ways to get one.",
]

WEEKS = [
    ("Before we start",
     "You pick one area, name one sponsor, and name the team. We agree in "
     "writing what is in scope, what the measure is, and what better will look "
     "like when we are done. Scope and fee are agreed here, before any work "
     "begins."),
    ("Week one",
     "Assessment. We walk and score every zone in the area, photograph the "
     "current state, and write the baseline. You see the score before the "
     "event, so the after has something to be compared against."),
    ("Week two",
     "The kaizen event. Two or three consecutive days on the floor with the "
     "team: Sort against the red-tag rule, Straighten to the point of use, "
     "Shine as inspection, and the safety pass that falls out of both."),
    ("Week three",
     "Standards. Every zone gets its one-page visual standard, its owner and "
     "its reset trigger. Labels, shadow boards and floor marking go in. The "
     "area now tells you when it is wrong without anybody having to notice."),
    ("Week four",
     "Audit and handover. The layered audit is stood up, your auditors are "
     "trained, and we run the first two audits alongside them. You keep the "
     "scoring sheet, the standards, the photographs and the baseline."),
    ("After",
     "Either we come back for a few audit cycles while the habit sets, or we "
     "scope the next area, or you run it yourselves with what you now hold. "
     "All three are fine outcomes. Only one of them is more revenue for us, "
     "which is why it is worth saying out loud that it is not the default."),
]

YOU_SUPPLY = [
    ("A sponsor with authority",
     "Somebody who can approve disposal, authorise moving equipment, and "
     "release people for the event days. Without that, the event becomes a "
     "meeting."),
    ("The people who do the work",
     "Released for the event days. This is the largest real cost of the "
     "engagement and it is usually larger than our fee. Better you hear it "
     "here than discover it in week two."),
    ("One named area",
     "Agreed before we start. The whole plant is not a first engagement, it is "
     "a programme, and it is scoped differently."),
    ("A red-tag holding area, and somebody who can decide",
     "Somewhere items can sit while their fate is settled, and a person who is "
     "allowed to settle it."),
    ("Site access and safety induction",
     "Whatever your visitor process, PPE and training requirements are, told "
     "to us up front, so the first morning is not spent in an induction room."),
    ("A decision about photography",
     "Standards work best with a photograph of the correct state. If your site "
     "does not allow cameras, say so at the start and we will use drawings "
     "instead. Nothing gets photographed that you have not agreed to."),
    ("An owner for every standard",
     "Named, before we leave. A standard with no owner decays, and we will say "
     "that at the time rather than let you find out a quarter later."),
    ("A small materials budget, bought by you",
     "Labels, tape, shadow board stock, bins. You buy them locally and we tell "
     "you what and how much. We do not mark up materials."),
    ("Two hours of leadership time",
     "One at the start to agree the measure, one at the end to walk the area "
     "and accept the standard. If leadership never walks it, the floor learns "
     "what the programme is worth."),
]

# Questions a real buyer asks, answered on the page and mirrored into FAQPage
# markup. build_seo.py's DECLINED note records that no page on this site
# carried a genuine question and answer block; this one does, which is the only
# reason the markup is defensible here.
FAQ = [
    ("What does a Corporate Lean 6S engagement include?",
     "Four parts: an assessment that scores and photographs every zone in the "
     "area, a kaizen event of two or three consecutive days on the floor with "
     "your team, a one-page visual standard for each zone with a named owner "
     "and a reset trigger, and a layered audit your own people are trained to "
     "run."),
    ("How much does it cost?",
     "It is scoped per engagement and quoted in writing before any work "
     "starts. No rate is published, because the same headcount can be a very "
     "different piece of work. What moves it: how many people are in the room, "
     "how many sites, how many zones are in the baseline, how much is on site, "
     "travel, whether we train your trainers, who writes the standards, how "
     "long we stay for the audit, and whether the event has to run once per "
     "shift."),
    ("How long does a first engagement take?",
     "About four weeks in the usual shape: assessment, then the event, then "
     "standards, then the audit handover. The event itself is two or three "
     "consecutive days. The actual dates and the scope are agreed in writing "
     "before anything starts."),
    ("What do we have to provide?",
     "A sponsor who can approve disposal and release people, the people who "
     "actually do the work for the event days, one named area, a red-tag "
     "holding area, site access and safety induction, a decision about "
     "photography, an owner for every standard, a small materials budget you "
     "buy locally, and about two hours of leadership time."),
    ("Do you have client references or case studies?",
     "Not for this offer. No corporate engagement has been sold through 6S "
     "Success, so any logo, testimonial or case study on this page would be "
     "invented. What is real is Phil Kling's own record: twenty years "
     "installing continuous improvement systems, a statewide process redesign "
     "for the Idaho Department of Health and Welfare, a company-wide Lean "
     "transformation at McKinstry, and six years building continuous "
     "improvement systems at Amazon. That record is set out in full on the "
     "About page."),
    ("Where do you deliver it?",
     "Engagements are run from Boise, Idaho. On-site work anywhere else is "
     "possible with travel and lodging agreed in the scope at cost. The "
     "assessment, the standards writing and the audit coaching can all be done "
     "over video; the event days cannot, because they happen where the work "
     "happens."),
    ("Who actually turns up?",
     "Phil Kling. This is not a bench of consultants with a partner on the "
     "cover, so the person who scopes the work is the person on your floor. "
     "That is the limit as much as the selling point: capacity is one "
     "practitioner, so dates are agreed rather than assumed."),
]

# The enquiry body, as data rather than as a JavaScript string, so the routing
# assertion in main() checks the thing that actually ships. Label first,
# element id second.
BODY_FIELDS = [
    ("Company", "k-company"),
    ("Name and role", "k-name"),
    ("Email", "k-email"),
    ("Phone", "k-phone"),
    ("Site or sites", "k-sites"),
    ("People in the area", "k-people"),
    ("Areas or zones wanted first", "k-zones"),
    ("Wants to start", "k-when"),
    ("Train their own people", "k-train"),
    ("Suggested time for a scoping call", "k-time"),
]


# ------------------------------------------------------------------ chrome ---

def chrome() -> tuple:
    src = io.open(CHROME_SRC, encoding="utf-8").read()
    hdr = src[src.index("<header"):src.index("</header>") + 9]
    ftr = src[src.index("<footer"):src.index("</footer>") + 9]
    return hdr, ftr


# ----------------------------------------------------------------- markup ----

def cards(items) -> str:
    return "".join(
        '<div class="card reveal"><span class="badge-soft">%s</span>'
        '<h3 style="margin-top:12px">%s</h3><p>%s</p></div>'
        % (when, name, body) for name, when, body in items)


def bullets(items) -> str:
    return "".join("<li>%s</li>" % i for i in items)


def deflist(items) -> str:
    return "".join('<li><b>%s.</b> %s</li>' % (n, b) for n, b in items)


def weeks() -> str:
    return "".join(
        '<li class="wk"><p class="wk-when">%s</p><p class="wk-what">%s</p></li>'
        % (label, body) for label, body in WEEKS)


def faq_html() -> str:
    return "".join(
        '<details class="faq"><summary>%s</summary><p>%s</p></details>'
        % (q, a) for q, a in FAQ)


# --------------------------------------------------------------- structured --

def jsonld() -> str:
    provider = {
        "@type": "Organization",
        "@id": BASE + "/corporate.html#nova",
        "name": "Nova Consulting",
        "url": URL,
        "email": TO,
        "description": "The Lean and workplace 6S practice behind 6S Success.",
    }

    person = {
        "@type": "Person",
        "@id": BASE + "/about.html#founder",
        "name": "Philip Kling",
        "url": BASE + "/about.html#founder",
        "jobTitle": "Lean Six Sigma Master Black Belt",
        "worksFor": {"@id": provider["@id"]},
        "knowsAbout": ["Lean", "Six Sigma", "6S", "5S", "Kaizen",
                       "Visual management", "Continuous improvement"],
        # Certifications Phil states for himself. No issuing body is named,
        # because naming one nobody here has verified would be the fabricated
        # authority signal CLAUDE.md section 11 rules out. The credential
        # itself is his own assertion and is presented as exactly that.
        "hasCredential": [
            {"@type": "EducationalOccupationalCredential",
             "credentialCategory": "certification",
             "name": "Lean Six Sigma Master Black Belt"},
        ],
    }

    service = {
        "@type": "Service",
        "@id": URL + "#service",
        "name": "Corporate Lean 6S",
        "serviceType": "Lean 6S workplace improvement consulting",
        "url": URL,
        "description":
            "A workplace 6S engagement for one area: a scored assessment of "
            "every zone, a kaizen event of two or three consecutive days with "
            "the team that works there, a one-page visual standard per zone "
            "with a named owner, and a layered audit your own people are "
            "trained to run. Scoped and quoted per engagement.",
        "provider": {"@id": provider["@id"]},
        "brand": {"@id": BASE + "/#organization"},
        "audience": {"@type": "BusinessAudience",
                     "audienceType": "Operations, EHS, quality and facilities "
                                     "leaders"},
        "areaServed": [
            {"@type": "City", "name": "Boise, Idaho"},
            {"@type": "AdministrativeArea", "name": "United States"},
        ],
        "availableChannel": [
            {"@type": "ServiceChannel", "name": "On site",
             "serviceLocation": {
                 "@type": "Place",
                 "name": "Your site, travel agreed in the scope"}},
            {"@type": "ServiceChannel", "name": "Remote",
             "serviceUrl": URL,
             "description": "Assessment, standards writing and audit coaching "
                            "can be delivered over video."},
        ],
        # An OfferCatalog with no price on any Offer, on purpose. This service
        # is quoted per engagement and no figure has ever been charged for it,
        # so a price or a priceRange here would be an invented number in
        # machine-readable form, which is worse than one in prose because it is
        # the form an answer engine repeats verbatim.
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "What a Corporate Lean 6S engagement contains",
            "itemListElement": [
                {"@type": "Offer",
                 "itemOffered": {"@type": "Service", "name": n,
                                 "description": b}}
                for n, _when, b in COMPONENTS
            ],
        },
        "termsOfService": BASE + "/terms.html",
    }

    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Consulting",
             "item": BASE + "/consulting.html"},
            {"@type": "ListItem", "position": 3, "name": "Corporate Lean 6S",
             "item": URL},
        ],
    }

    faq = {
        "@type": "FAQPage",
        "@id": URL + "#faq",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQ
        ],
    }

    return json.dumps({"@context": "https://schema.org",
                       "@graph": [crumbs, service, provider, person, faq]},
                      indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ script ---

def script() -> str:
    """The submit handler.

    Same shape as contact.html's, for the same reasons, and with the same
    fallback: a mailto is a request that the visitor's OS has a mail client
    attached, and when it does not the message is silently lost, so the
    composed text is also put somewhere it can be copied from.

    The body is ordered so the FIRST line names the service.
    ops/service_orders.py routes an inbound message by which service phrase it
    finds, reading subject and body together, so putting the service on line
    one under a subject that also says it means routing never depends on what
    the sender happens to write further down.
    """
    lines = ['"Service: Corporate Lean 6S"', '""']
    lines += ['"%s: " + v("%s")' % (label, fid) for label, fid in BODY_FIELDS]
    lines += ['""', '"What prompted this:"', 'v("k-why")']
    arr = ",\n      ".join(lines)
    return """<script>
(function () {
  var form = document.getElementById("corp-form");
  if (!form) { return; }
  var ok = document.getElementById("corp-ok");
  var link = document.getElementById("corp-mailto");
  var copyBox = document.getElementById("corp-copy");
  var copyBtn = document.getElementById("corp-copy-btn");

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
      %s
    ].join("\\n");

    var subject = "%s: " + v("k-company");
    var href = "mailto:%s?subject=" + encodeURIComponent(subject)
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
</script>
""" % (arr, SUBJECT, TO)


# ------------------------------------------------------------------- style ---

STYLE = """
.wk-list{list-style:none;padding:0;margin:0}
.wk{display:grid;grid-template-columns:170px 1fr;gap:22px;padding:20px 0;
  border-top:1px solid var(--line)}
.wk:last-child{border-bottom:1px solid var(--line)}
.wk-when{font-family:var(--sans);font-size:12px;font-weight:700;
  letter-spacing:.14em;text-transform:uppercase;color:var(--terra);margin:0}
.wk-what{margin:0;max-width:66ch}
.plain{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;
  gap:14px}
.plain li{max-width:72ch;padding-left:20px;position:relative}
.plain li:before{content:"";position:absolute;left:0;top:.62em;width:8px;
  height:8px;border-radius:2px;background:var(--honey)}
.faq{border-top:1px solid var(--line);padding:16px 0}
.faq:last-of-type{border-bottom:1px solid var(--line)}
.faq summary{cursor:pointer;font-family:var(--sans);font-weight:600;
  font-size:16px;color:var(--ink)}
.faq p{margin:12px 0 0;max-width:72ch;color:var(--soft)}
.howto{border:1px solid var(--line);background:var(--panel);border-radius:14px;
  padding:22px 26px;margin:0 0 26px}
.howto p{margin:0 0 10px;font-size:16px;line-height:1.55}
.howto p:last-child{margin-bottom:0}
.enq{max-width:760px}
.enq .two{display:grid;grid-template-columns:1fr 1fr;gap:0 20px}
.hint{font-family:var(--sans);font-size:12.5px;color:var(--soft);
  margin:-10px 0 20px}
@media (max-width:640px){
  .enq .two{grid-template-columns:1fr}
  .wk{grid-template-columns:1fr;gap:6px}
}
"""


# ------------------------------------------------------------------- page ----

def build() -> str:
    hdr, ftr = chrome()
    return "".join([
        '<!doctype html>\n<html lang="en">\n<head>\n',
        '<meta charset="utf-8">\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
        # Both of these are length-checked by ops/audit_pages.py: 60 and 155
        # characters, which is roughly where Google truncates. The first
        # version of this page overran both (87 and 236) and would have been
        # cut mid-sentence in results, on the one page meant to be found by a
        # buyer searching for exactly this.
        '<title>Corporate Lean 6S: workplace 6S engagements | 6S '
        'Success</title>\n',
        '<meta name="description" content="Workplace 6S for one area: a scored '
        'assessment, a kaizen event with your team, a visual standard per '
        'zone, and an audit your own people run.">\n',
        '<link rel="canonical" href="%s">\n' % URL,
        '<meta property="og:type" content="website">\n',
        '<meta property="og:site_name" content="6S Success">\n',
        '<meta property="og:title" content="Corporate Lean 6S: assessment, '
        'kaizen event, standards, audit">\n',
        '<meta property="og:description" content="Workplace 6S for one area, '
        'end to end: baseline, event, standards, and an audit your own people '
        'run. Scoped per engagement.">\n',
        '<meta property="og:url" content="%s">\n' % URL,
        '<meta property="og:image" content="%s/assets/img/standard.jpg">\n' % BASE,
        '<meta name="twitter:card" content="summary_large_image">\n',
        '<meta name="twitter:title" content="Corporate Lean 6S">\n',
        '<meta name="twitter:description" content="Workplace 6S for one area: '
        'baseline, kaizen event, standards, and an audit your own people '
        'run.">\n',
        '<meta name="twitter:image" content="%s/assets/img/standard.jpg">\n' % BASE,
        '<link rel="stylesheet" href="assets/css/site.css">\n',
        '<style>%s</style>\n' % STYLE,
        '<script type="application/ld+json">\n%s\n</script>\n' % jsonld(),
        '</head>\n<body>\n',
        hdr,
        '\n<main>\n',

        # ---------------------------------------------------------- hero ---
        '<section class="section">\n  <div class="wrap">\n',
        '    <p class="crumbs"><a href="index.html">Home</a> &rsaquo; '
        '<a href="consulting.html">Consulting</a> &rsaquo; '
        '<span aria-current="page">Corporate Lean 6S</span></p>\n',
        '    <div class="head">\n',
        '      <p class="eyebrow">Corporate Lean 6S &middot; Nova Consulting</p>\n',
        '      <h1>Workplace 6S, run on your floor and left working without '
        'us</h1>\n',
        '      <p class="lede">One area, about four weeks, four things you '
        'keep: a scored baseline for every zone, a kaizen event with the '
        'people who do the work, a visual standard per zone with a named '
        'owner, and a layered audit your own team is trained to run.</p>\n',
        '    </div>\n',
        '    <p style="max-width:72ch">This is the industrial method, not the '
        'household version of it. Sort, Straighten, Shine, Safety, '
        'Standardize, Sustain, run the way they are run in a plant: against a '
        'red-tag rule, at the point of use, with the standard posted where the '
        'work happens and an audit that produces a trend line rather than a '
        'feeling.</p>\n',
        '    <p style="max-width:72ch"><b>It is scoped per engagement.</b> '
        'There is no published rate, because two engagements with the same '
        'headcount can be very different weeks of work. '
        '<a href="#scope">What determines the scope</a> is set out below in '
        'nine items you can answer for yourself in about a minute. '
        '<a href="#enquiry">Send us those nine answers</a> and you get a '
        'written scope and a fixed fee, not a brochure.</p>\n',
        '    <p style="margin-top:22px">'
        '<a class="btn btn-primary btn-lg" href="#enquiry">Start a scoping '
        'conversation</a> '
        '<a class="btn btn-ghost btn-lg" href="#engagement">See what is in '
        'it</a></p>\n',
        '  </div>\n</section>\n',

        # ----------------------------------------------------- components ---
        '<section class="section" id="engagement">\n  <div class="wrap">\n',
        '    <div class="head"><p class="eyebrow">What the engagement is</p>\n',
        '    <h2>Four parts, in this order, for one area</h2>\n',
        '    <p>Each one produces something you keep. The order is not '
        'decoration: standards written before the sort is finished describe a '
        'mess, and an audit with no standard behind it scores an opinion.</p>'
        '</div>\n',
        '    <div class="grid g-4">%s</div>\n' % cards(COMPONENTS),
        '  </div>\n</section>\n',

        # ------------------------------------------------------------ fit ---
        '<section class="section" id="fit">\n  <div class="wrap split">\n',
        '    <div><h2>Who it is for</h2><ul class="plain">%s</ul></div>\n'
        % bullets(FOR_YOU),
        '    <div><h2>When we are the wrong call</h2><ul class="plain">%s</ul>'
        '<p style="margin-top:18px;color:var(--soft)">A consultant who has '
        'never told you not to hire them has not been paying attention to your '
        'problem.</p></div>\n' % bullets(NOT_FOR_YOU),
        '  </div>\n</section>\n',

        # -------------------------------------------------------- outcome ---
        '<section class="section band">\n  <div class="wrap">\n',
        '    <div class="head"><p class="eyebrow on-deep">What changes</p>\n',
        '    <h2 style="color:#fff">What your team holds at the end that it '
        'does not hold now</h2></div>\n',
        '    <div class="grid g-3">\n',
        '      <div class="card reveal"><h3>A number you can repeat</h3>'
        '<p>A 6S score per zone, taken before and after against the same '
        'sheet, and the photographs both were taken from. Your next audit is '
        'comparable to your first one, which is the only way anybody can tell '
        'whether this held.</p></div>\n',
        '      <div class="card reveal"><h3>A standard with a name on it</h3>'
        '<p>Every zone has a posted one-page standard, an owner, a reset '
        'trigger and a replenishment signal. Nobody has to remember the rule, '
        'because the area shows it.</p></div>\n',
        '      <div class="card reveal"><h3>People who can run the next '
        'one</h3><p>Your auditors are trained and have run audits with us '
        'watching. If you never call us again the method still works, which is '
        'what the sixth S is for.</p></div>\n',
        '    </div>\n',
        '    <p class="notice" style="max-width:72ch;margin:26px auto 0">'
        '<b>What is deliberately not promised here: a percentage.</b> No '
        'figure for space recovered, time saved or defects avoided appears on '
        'this page, because we have not run this engagement for you and any '
        'number printed here would be somebody else&rsquo;s result borrowed to '
        'sell you ours. The baseline in week one is what makes your own number '
        'measurable, and it is yours either way.</p>\n',
        '  </div>\n</section>\n',

        # ---------------------------------------------------------- weeks ---
        '<section class="section" id="weeks">\n  <div class="wrap">\n',
        '    <div class="head"><p class="eyebrow">A first engagement</p>\n',
        '    <h2>Week by week</h2>\n',
        '    <p>This is the usual shape rather than a fixed product. The '
        'actual dates, scope and fee are agreed in writing before the first '
        'day.</p></div>\n',
        '    <ol class="wk-list">%s</ol>\n' % weeks(),
        '  </div>\n</section>\n',

        # -------------------------------------------------------- supply ----
        '<section class="section" id="supply">\n  <div class="wrap">\n',
        '    <div class="head"><p class="eyebrow">Your side of it</p>\n',
        '    <h2>What you have to supply</h2>\n',
        '    <p>None of it is unusual, and all of it is the difference between '
        'an engagement that holds and one that photographs well. It is listed '
        'before you buy rather than in a kickoff deck afterwards.</p></div>\n',
        '    <ul class="plain">%s</ul>\n' % deflist(YOU_SUPPLY),
        '  </div>\n</section>\n',

        # --------------------------------------------------------- scope ----
        '<section class="section" id="scope">\n  <div class="wrap">\n',
        '    <div class="head"><p class="eyebrow">Scope and fee</p>\n',
        '    <h2>What determines the scope</h2>\n',
        '    <p>Corporate Lean 6S is quoted per engagement and there is no '
        'published rate. That is not a negotiating position. It is that two '
        'engagements with the same headcount can be very different weeks of '
        'work, and these nine things are what move it.</p></div>\n',
        '    <ul class="plain">%s</ul>\n' % deflist(SCOPE_DRIVERS),
        '    <p class="notice" style="max-width:72ch;margin-top:26px">You get '
        'a written scope and a fixed fee before any work starts, with what is '
        'excluded written down beside it. If the scope changes, the fee is '
        're-agreed in writing before the work changes, not invoiced '
        'afterwards.</p>\n',
        '  </div>\n</section>\n',

        # ----------------------------------------------------------- who ----
        '<section class="section" id="who">\n  <div class="wrap split">\n',
        '    <div>\n',
        '      <p class="eyebrow">Who delivers it</p>\n',
        '      <h2>Philip Kling</h2>\n',
        '      <p class="lede">Lean Six Sigma Master Black Belt. '
        'Twenty years installing continuous improvement systems inside '
        'organizations, trading as Nova Consulting.</p>\n',
        '      <p>In 2007 he led a statewide operational redesign for the '
        'Idaho Department of Health and Welfare, taking a benefit process from '
        'thirty two days to under seven. In 2008 he became principal Lean Six '
        'Sigma consultant at McKinstry, where he ran a company-wide Lean '
        'transformation and trained more than two hundred people. Redesigning '
        'that warehouse as a flow-based system cut inventory and space '
        'requirements by eighty percent, and it did it through 6S '
        'standardization rather than more shelving. He then spent six years '
        'building continuous improvement systems at Amazon across a forty '
        'thousand person organization, training over a thousand people a year, '
        'and wrote <i>Process Kaizen</i> in 2012.</p>\n',
        '      <p><a href="about.html#founder">The full record is on the '
        'About page &rarr;</a></p>\n',
        '    </div>\n',
        '    <div>\n',
        '      <div class="howto">\n',
        '        <h3 style="margin-top:0">What you will not find on this '
        'page</h3>\n',
        '        <p>No client logos. No testimonials. No case studies. No '
        'count of engagements delivered.</p>\n',
        '        <p>No corporate engagement has been sold through 6S Success, '
        'so every one of those would have to be invented, and a corporate '
        'buyer is exactly the reader who checks. The work described here is '
        'Phil&rsquo;s own, delivered inside those organizations before 6S '
        'Success existed. It is a career record, not a client reference, and '
        'it is written that way on purpose.</p>\n',
        '        <p>If you want references before committing to anything, ask '
        'in your enquiry and you will get a straight answer about what can and '
        'cannot be provided.</p>\n',
        '      </div>\n',
        '      <p style="color:var(--soft)">Phil turns up himself. Capacity is '
        'one practitioner, so dates get agreed rather than assumed, and the '
        'person who scopes the work is the person on your floor.</p>\n',
        '    </div>\n',
        '  </div>\n</section>\n',

        # ------------------------------------------------------- enquiry ----
        '<section class="section" id="enquiry">\n  <div class="wrap">\n',
        '    <div class="head"><p class="eyebrow">Start here</p>\n',
        '    <h2>Tell us enough to scope it</h2></div>\n',
        '    <div class="enq">\n',
        '    <div class="howto">\n',
        '      <p><b>How this works, before you type anything.</b> There is no '
        'ticket system behind this form. Pressing the button opens your own '
        'mail app with the message already written and addressed to '
        '<b>%s</b>. You press send there.</p>\n' % TO,
        '      <p>Phil reads it himself, usually within one working day. If '
        'your browser has no mail app attached, the same text appears in a box '
        'you can copy and send yourself. Nothing is stored on this site and '
        'nobody is added to a mailing list.</p>\n',
        '      <p>Put a date and time in the last field and a calendar invite '
        'for a one-hour scoping call comes back attached to the reply.</p>\n',
        '    </div>\n',
        '    <form id="corp-form">\n',
        '      <div class="two">\n',
        '        <div class="field"><label for="k-company">Company</label>'
        '<input id="k-company" name="company" required '
        'autocomplete="organization"></div>\n',
        '        <div class="field"><label for="k-name">Your name and role'
        '</label><input id="k-name" name="name" required '
        'autocomplete="name"></div>\n',
        '        <div class="field"><label for="k-email">Work email</label>'
        '<input id="k-email" name="email" type="email" required '
        'autocomplete="email"></div>\n',
        '        <div class="field"><label for="k-phone">Phone, if you would '
        'rather talk</label><input id="k-phone" name="phone" type="tel" '
        'autocomplete="tel"></div>\n',
        '        <div class="field"><label for="k-sites">Site or sites, and '
        'where they are</label><input id="k-sites" name="sites" '
        'placeholder="One plant, Nampa ID"></div>\n',
        '        <div class="field"><label for="k-people">People in the area '
        'we would work</label><input id="k-people" name="people" '
        'placeholder="14 across two shifts"></div>\n',
        '        <div class="field"><label for="k-zones">Areas or zones you '
        'would want first</label><input id="k-zones" name="zones" '
        'placeholder="Stockroom and the maintenance shop"></div>\n',
        '        <div class="field"><label for="k-when">When you would want to '
        'start</label><input id="k-when" name="when" '
        'placeholder="Before the end of the quarter"></div>\n',
        '      </div>\n',
        '      <div class="field"><label for="k-train">Do you want your own '
        'people trained to run it after we go?</label>'
        '<select id="k-train" name="train">'
        '<option>Not sure yet</option>'
        '<option>Yes, train our auditors</option>'
        '<option>Yes, train trainers to run their own events</option>'
        '<option>No, just this area</option></select></div>\n',
        '      <div class="field"><label for="k-why">What prompted this now?'
        '</label><textarea id="k-why" name="why" rows="4" '
        'placeholder="An audit, a customer visit, an incident, a 5S that '
        'decayed, a new line, a move, or something else."></textarea></div>\n',
        '      <div class="field"><label for="k-time">A date and time that '
        'suits for a one-hour scoping call</label><input id="k-time" '
        'name="time" placeholder="%s"></div>\n' % DATE_EXAMPLE,
        '      <p class="hint">Written like that example, a calendar invite '
        'comes back with the reply. Leave it blank and we will suggest times '
        'instead.</p>\n',
        '      <button class="btn btn-primary btn-lg" type="submit">'
        'Open this in my mail app</button>\n',
        '      <div class="notice" id="corp-ok" role="status" '
        'aria-live="polite" style="margin-top:18px" hidden>\n',
        '        <b>Your mail app should have opened with the message '
        'ready.</b> Press send there. '
        '<a id="corp-mailto" href="mailto:%s">Open it again</a> if nothing '
        'happened, or copy the message below and send it to <b>%s</b>.\n'
        % (TO, TO),
        '        <details style="margin-top:12px" open>'
        '<summary style="cursor:pointer">Copy the message instead</summary>'
        '<textarea id="corp-copy" readonly rows="10" aria-label="Your enquiry, '
        'ready to copy" style="width:100%;font:inherit;font-size:15px;'
        'padding:10px;border:1px solid #E2D8C4;border-radius:8px;'
        'background:#fff"></textarea>'
        '<button type="button" class="btn btn-ghost btn-sm" '
        'id="corp-copy-btn" style="margin-top:8px">Copy the message</button>'
        '</details>\n',
        '      </div>\n',
        '    </form>\n',
        '    <p class="notice" style="margin-top:18px">Would rather write it '
        'yourself? <a href="mailto:%s?subject=%s">%s</a>. Say which company, '
        'how many people, and what prompted it, and the first reply will be a '
        'question rather than a brochure.</p>\n'
        % (TO, SUBJECT.replace(" ", "%20"), TO),
        '    </div>\n',
        '  </div>\n</section>\n',

        # ----------------------------------------------------------- next ---
        '<section class="section" id="more">\n  <div class="wrap">\n',
        '    <div class="grid g-3">\n',
        '      <div class="card"><span class="badge-soft">The method</span>'
        '<h3 style="margin-top:12px">See it before you buy it</h3>'
        '<p>The six S&rsquo;s, what each one asks of a space, and the order '
        'that works. Free, and the same method the engagement runs.</p>'
        '<p><a href="method.html">Read the method &rarr;</a></p></div>\n',
        '      <div class="card"><span class="badge-soft">Home</span>'
        '<h3 style="margin-top:12px">Consulting for a house</h3>'
        '<p>A video walkthrough or a full day on site, for a home rather than '
        'a workplace. Both are priced openly.</p>'
        '<p><a href="consulting.html">See home consulting &rarr;</a></p>'
        '</div>\n',
        '      <div class="card"><span class="badge-soft">The book</span>'
        '<h3 style="margin-top:12px">How the method is written down</h3>'
        '<p>Fifty chapters and twenty room playbooks. A fair sample of how we '
        'write a standard, if you want to read before you talk.</p>'
        '<p><a href="book.html">See the book &rarr;</a></p></div>\n',
        '    </div>\n',
        '  </div>\n</section>\n',

        # ------------------------------------------------------------ faq ---
        '<section class="section" id="faq">\n  <div class="wrap narrow">\n',
        '    <div class="head"><p class="eyebrow">Questions</p>'
        '<h2>Asked before, answered here</h2></div>\n',
        '    %s\n' % faq_html(),
        '  </div>\n</section>\n',

        '</main>\n',
        ftr,
        '\n<script defer src="/stats/script.js"\n'
        '  data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a"\n'
        '  data-host-url="https://6s-success.com/stats"></script>\n',
        script(),
        '</body>\n</html>\n',
    ])


# ------------------------------------------------------------------- main ----

def main() -> int:
    doc = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(doc)

    import service_orders as SO

    # 1. No price, anywhere, in any form. The single most important property of
    #    this page and the easiest thing for a later edit to break.
    money = re.findall(r"\$\s?\d", doc)
    assert not money, "a price appeared on the corporate page: %r" % money[:3]

    # 2. The subject line must route to Corporate Lean 6S, not to one of the
    #    two home services, or a corporate lead is forwarded as a household
    #    booking with a household invite attached.
    assert SO.which_service(SUBJECT) == "Corporate Lean 6S", \
        "the subject line does not route to Corporate Lean 6S"

    # 3. No label in the composed body may carry another service's phrase.
    body_text = " ".join(label for label, _ in BODY_FIELDS) + " " + SUBJECT
    for name, keys in SO.PHRASES:
        if name == "Corporate Lean 6S":
            continue
        for k in keys:
            assert k not in body_text.lower(), \
                "the enquiry body carries %r, which routes to %s" % (k, name)

    # 4. The example date must be one find_time() can actually read, or the
    #    calendar invite this page promises never gets attached.
    assert SO.find_time(DATE_EXAMPLE) is not None, \
        "the date example %r cannot be parsed by service_orders" % DATE_EXAMPLE

    # 5. The catalogue record must still point here, must still have no price
    #    and must still have no payment link. All three live in another file
    #    and all three are load-bearing.
    js = io.open(DATA_JS, encoding="utf-8").read()
    cat = json.loads(js[js.index("["):js.rindex("]") + 1])
    corp = [p for p in cat if p.get("sku") == "CN-CORP"]
    assert corp, "CN-CORP is missing from the catalogue"
    assert corp[0].get("price") is None, "CN-CORP has acquired a price"
    assert corp[0].get("quote") == "corporate.html", \
        "CN-CORP does not point at this page"
    assert "buy" not in corp[0], "CN-CORP has acquired a payment link"

    print("  wrote site/corporate.html  (%d KB)" % (len(doc) // 1024))
    print("  no dollar figure on the page; CN-CORP still price: null, no link")
    print("  subject %r routes to %r" % (SUBJECT, SO.which_service(SUBJECT)))
    print("  date example %r parses to %s"
          % (DATE_EXAMPLE, SO.find_time(DATE_EXAMPLE)))
    print("  %d scope drivers, %d engagement parts, %d supplied by client, "
          "%d FAQ" % (len(SCOPE_DRIVERS), len(COMPONENTS), len(YOU_SUPPLY),
                      len(FAQ)))

    # The same whole-site wiring passes every other single page generator here
    # chains. Issue #26: a generator whose own template does not carry the skip
    # link, the main landmark, the progressive marker, the PWA icons,
    # measure.js, aria-current and the canonical form silently strips all of
    # them on the next rebuild.
    import canonical_links
    import prune_catalog_js
    import wire_landmarks
    import wire_progressive
    import wire_measure
    import wire_pwa
    import wire_aria_current
    import build_avif
    canonical_links.main()
    prune_catalog_js.main()
    wire_landmarks.main()
    wire_progressive.main()
    wire_measure.main()
    wire_pwa.main()
    wire_aria_current.main()
    build_avif.wire()

    # AND THEN THE FINGERPRINTER, WHICH IS NOT OPTIONAL HERE.
    # wire_measure rewrites the measurement block as a bare
    # `assets/js/measure.js`, dropping the ?v= content hash it does not know
    # how to restore. Running the wiring chain standalone therefore strips the
    # cache-busting fingerprint off every page on the site, which is exactly
    # what happened the first time this generator was run: 188 pages quietly
    # lost it. preflight hides that by running fingerprint_assets.py after the
    # generators, so the gate stays green while a standalone run ships the
    # drift. It is chained here instead of documented, for the same reason
    # fingerprint_assets.py itself chains build_pwa.py: writing the order down
    # was not enough three times running. It is idempotent, so preflight
    # running it again afterwards changes nothing.
    import fingerprint_assets
    fingerprint_assets.main(False)

    # The sitemap, and only the sitemap. build_seo's __main__ also rewrites the
    # <head> of every page in its PAGES table, which is not this generator's
    # business and would trample pages another agent is editing this cycle.
    # build_sitemap() finds corporate.html through scan_extra_pages, which
    # reads the tree rather than a hand list, so nothing has to be registered.
    import build_seo
    print("  sitemap.xml rebuilt: %d URLs" % build_seo.build_sitemap())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
