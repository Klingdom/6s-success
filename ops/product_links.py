#!/usr/bin/env python3
"""
Retailer links for all 123 catalogue products, and the checker that keeps them
honest.

WHAT THIS SOLVES
----------------
ops/affiliate-catalogue.csv holds 123 product TYPES, not products. A row reads
"Compact vacuum with attachments", never a brand and a model. Every consumer of
that file (ops/zone_supplies.py on 114 zone pages, ops/build_kit_page.py on
site/kit.html) renders a product as plain text until the row carries both a URL
and a Link Status beginning "verified". Until today every row was Unverified
and empty, so the method told a reader to wipe the shelf with a neutral pH
cleaner and never told them where any such thing is sold.

WHY A SEARCH LINK AND NOT A PRODUCT LINK
----------------------------------------
Because a search link is the truth about what we know.

We know the TYPE of thing that removes a root cause. We do not know that any
particular SKU is in stock, still made, sold in your state, or the best of its
kind, and we cannot know it for long: a product URL verified today 404s or
turns into a different item without telling anyone. A retailer search for the
type never goes out of stock, never 404s, and swaps for an affiliate deep link
later without a single page changing.

It is also the only form that matches how the method recommends. See
CLAUDE.md section 48 and site/affiliate-disclosure.html: we recommend a kind of
thing, and often the honest answer is that you already own one.

A specific product URL is permitted by POLICY 3 below, and this tool supports
it, but nothing in the catalogue uses one today because nothing needed one.

WHAT VERIFIED MEANS HERE, EXACTLY
---------------------------------
Not HTTP 200. A 200 proves almost nothing on a retail site:

  walmart.com   returns 200 with a body titled "Robot or human?"
  target.com    returns 200 and an identical-length shell for a real search
                and for "zzqxwvxyzzy", because the results are rendered by
                JavaScript that a plain fetch never runs
  target.com    when actually rendered, returns 200 results for nonsense too,
                filled with unrelated recommendations

So a status code cannot distinguish working from broken here, which CLAUDE.md
section 0.3 says is exactly when you go and find a signal that can. This tool
renders the page in a real headless Chromium, extracts the product slugs the
retailer actually put in the grid, and requires that a keyword for the product
type appears in at least MIN_HITS of them. Measured against that test, the
"microfiber cleaning cloths" search returns 11 matching slugs out of the 24
checked and the nonsense search returns 0, its top results being canned coffee
and juice boxes.

The evidence, per link, is written to ops/product-links-evidence.json: the
slugs that matched, the number checked, and when. A claim of verification that
nobody can audit is not a verification.

FOUR STATES, AND THE THIRD IS THE POINT
---------------------------------------
  ok         rendered, and enough result slugs matched the product type
  weak       rendered, but only one or two matched. Not published.
  dead       rendered, and nothing matched, or the page is a real error
  unchecked  we could not look: no browser, a bot challenge, a timeout

"unchecked" is not "dead" and neither is "ok". CLAUDE.md section 0.4: a run
that could not look must say so and must never write its own ignorance over a
measurement. An unchecked link keeps whatever status it already had and is
reported separately in the summary, loudly.

Run:
  python ops/product_links.py --assign      verify every spec, write the CSV
  python ops/product_links.py --check       re-verify what the CSV publishes
  python ops/product_links.py --status      no network, just what the CSV says
  python ops/product_links.py --only MPL-00042[,MPL-00043...]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

CATALOGUE = os.path.join(ROOT, "ops", "affiliate-catalogue.csv")
EVIDENCE = os.path.join(ROOT, "ops", "product-links-evidence.json")

# How many of the retailer's own result slugs must name the product type.
# One match is a coincidence on a site that pads a bad query with unrelated
# recommendations; three in a row is the grid actually being about the thing.
MIN_HITS = 3
# How far down the grid to look. Retailers put sponsored and "related" tiles
# below the fold, so a deep scan flatters a bad query.
TOP_N = 24
RENDER_MS = 16000
WORKERS = 4


# ------------------------------------------------------------------ merchants
# Only merchants whose search results can actually be READ from this machine
# are here. Measured 2026-09-04:
#
#   target.com        renders headless, real slugs           USABLE
#   homedepot.com     403 to a plain fetch, renders fine     USABLE
#                     headless, real slugs, re-measured
#                     twice on 2026-09-04
#   ikea.com          renders headless, real slugs           USABLE
#   lowes.com         403 to fetch, "Access Denied" headless BLOCKED
#   containerstore    307 to fetch, "denied" headless        BLOCKED
#   walmart.com       200 "Robot or human?" both ways        BLOCKED
#   amazon.com        202 bot page for every URL             BLOCKED
#   uline.com         200 "Challenge Validation"             BLOCKED
#
# A blocked merchant is not listed as a link anywhere, because we could not
# verify it and POLICY 1 does not allow publishing what we did not check.
#
# HOME DEPOT IS THE ONE TO READ TWICE. A plain HTTP fetch of homedepot.com
# returns 403 for every URL including its own homepage, and on 2026-09-04 that
# 403 was taken as proof that its 37 links "were not verified by anything" and
# all 37 Link Status values were rewritten to say so. They had been verified,
# by the method this file exists to use: a headless Chromium render, from
# which 36 of 37 returned a real product grid on the first pass and the 37th
# on a retry. The 403 is real and it is about fetching, not about the link.
# Anything that concludes otherwise has tested the fetcher, not the URL.
MERCHANTS = {
    "target": {
        "name": "Target",
        "search": "https://www.target.com/s?searchTerm={q}",
        "slug": re.compile(r'href="/p/([a-z0-9\-]+)/-/A-\d+"'),
    },
    "homedepot": {
        "name": "The Home Depot",
        "search": "https://www.homedepot.com/s/{q}",
        "slug": re.compile(r'href="/p/([A-Za-z0-9\-]+)/\d+'),
    },
    "ikea": {
        "name": "IKEA",
        "search": "https://www.ikea.com/us/en/search/?q={q}",
        "slug": re.compile(r'/us/en/p/([a-z0-9\-]+)/'),
    },
}

BLOCKED_TITLES = ("robot or human", "access denied", "access to this page has "
                  "been denied", "challenge validation", "are you a human",
                  "pardon our interruption", "request unsuccessful",
                  "error page", "just a moment", "security check", "blocked")

# A real rendered results grid at any of these merchants is 300KB and up.
# Home Depot answers a burst of requests with a 2KB page titled "Error Page",
# which yields zero product slugs and would score as "nothing matched" if
# size were not checked. That is the exact failure CLAUDE.md section 0.4
# names: a run that could not look writing its ignorance over a measurement.
# Anything under this is treated as "we could not look", never as evidence.
MIN_RESULTS_BYTES = 60000


def search_url(merchant: str, query: str) -> str:
    m = MERCHANTS[merchant]
    if merchant == "homedepot":                    # path segment, not a param
        q = urllib.parse.quote(query)
    else:
        q = urllib.parse.quote_plus(query)
    return m["search"].format(q=q)


# ------------------------------------------------------------------- the spec
# merchant, search query, and the keywords that prove the grid came back about
# the right thing. A keyword is matched against the retailer's own product
# slug, lowercased, so "microfiber" matches "microfiber-dust-cloths-6pk".
#
# `why` is the recommendation's reason in the method's terms: the root cause it
# removes, not a description of the object. CLAUDE.md section 48 forbids
# dressing merchandising up as personalisation, and the test of that is whether
# the reason survives being read by somebody who pays us nothing. Every one of
# these has to answer "why this, for a person who has this problem".
#
# The reasons are deliberately about causes named in CLAUDE.md section 6: no
# assigned home, wrong location, excess quantity, poor accessibility, poor
# visibility, too many steps, unclear ownership, inadequate capacity,
# inconsistent standard, difficult cleaning, missing replenishment signal,
# unsafe placement.
S = lambda m, q, k, why: {"m": m, "q": q, "k": k, "why": why}       # noqa: E731

SPEC = {
    # ---------------------------------------------- 1 Universal Kit (8)
    "MPL-00008": S("target", "handheld vacuum with attachments", ["vacuum"],
        "Difficult cleaning is a root cause, and in a micro zone the obstacle "
        "is the seam, track and corner a broom cannot reach. The crevice "
        "attachment is the part that matters here, not the motor."),
    "MPL-00010": S("target", "storage totes with lids", ["tote", "storage", "bin"],
        "Sort is a decision and a decision needs somewhere to put the answer. "
        "Five labelled containers turn a vague clear-out into five finished "
        "piles, which is why this comes before any organiser."),
    "MPL-00012": S("target", "label maker", ["label"],
        "An inconsistent standard is a root cause: the zone only holds if the "
        "right state is obvious to somebody who was not there when you set it. "
        "A printed label survives that person; a memory does not."),
    "MPL-00009": S("target", "cleaning caddy", ["caddy"],
        "Too many steps is the reason cleaning stops happening. Walking back "
        "to the cupboard mid-zone costs more than the wipe does, so the inputs "
        "travel with you."),
    "MPL-00013": S("target", "removable write on labels", ["label"],
        "A first standard is usually slightly wrong. Removable labels let you "
        "correct it in a second, so people fix the system instead of living "
        "around it."),
    "MPL-00001": S("target", "ph neutral all purpose cleaner", ["cleaner"],
        "Excess quantity applies under the sink too. One neutral cleaner "
        "covers nearly every sealed surface in the house, which replaces six "
        "bottles and removes the choice that stalls the job."),
    "MPL-00006": S("target", "microfiber cleaning cloths", ["microfiber"],
        "Colour coding is a visual control. One colour per job stops the "
        "bathroom cloth reaching the kitchen counter without anybody having to "
        "remember a rule."),
    "MPL-00098": S("target", "moisture absorber damp",
                   ["moisture", "damprid", "dehumidifier"],
        "Damp is the root cause that turns a storage problem into a ruined "
        "one, and it is invisible until it is not. Enclosed zones get it "
        "measured rather than guessed."),

    # ------------------------------------------------------- 2 Core (26)
    "MPL-00016": S("homedepot", "safety glasses", ["safety-glass", "eye-protection"],
        "Unsafe placement in a garage reset is mostly overhead and mostly "
        "dust. Eye protection is the cheapest condition on doing the work at "
        "all."),
    "MPL-00003": S("target", "bathroom cleaner soap scum", ["bathroom", "scum", "shower", "tub"],
        "Soap film is difficult cleaning made routine: it rebuilds weekly, so "
        "the standard fails unless the right product is already in the zone."),
    "MPL-00004": S("target", "kitchen degreaser", ["degreaser", "grease"],
        "Grease is what makes a kitchen surface hard to clean, and hard to "
        "clean is what makes a standard slip. The neutral cleaner will not "
        "shift it."),
    "MPL-00002": S("target", "glass cleaner", ["glass"],
        "A mirror or a glass door shows its own standard. It is the one "
        "surface where the result is visible from across the room, so it "
        "carries the whole zone's appearance."),
    "MPL-00115": S("homedepot", "oily waste can", ["oily", "waste-can", "justrite"],
        "Oil-finish rags heat themselves as they cure and can ignite with "
        "nothing touching them. This is unsafe placement with a fire at the "
        "end of it, and the lid has to fall shut on its own weight."),
    "MPL-00118": S("homedepot", "entry door mat", ["mat"],
        "Grit at a threshold is wrong location: it is outdoor material that "
        "got in. Two mats stop it in two stages, scrape then soak, so the "
        "floor inside never has to be the filter."),
    "MPL-00104": S("homedepot", "multi purpose machine oil", ["oil"],
        "Bare steel and a stiff hinge are the same root cause, an unmaintained "
        "surface. A few drops at the end of a reset is what makes the next one "
        "shorter."),
    "MPL-00111": S("homedepot", "step ladder", ["ladder"],
        "Poor accessibility overhead is why the top shelf becomes a place "
        "things go to be forgotten. Stable access with both hands free is what "
        "makes high storage usable rather than nominal."),
    "MPL-00109": S("homedepot", "push broom", ["broom"],
        "A slab holds its standard only if clearing it is one pass. Anything "
        "that takes a dustpan and three trips will not be done weekly."),
    "MPL-00108": S("homedepot", "wire brush", ["wire-brush", "brush"],
        "Caked soil and rust are why a tool stops working, not why it looks "
        "bad. Scraping comes before any cleaner, or the cleaner just floats on "
        "top of the problem."),
    "MPL-00101": S("target", "screen cleaner electronics", ["screen", "electronic"],
        "A screen is the one surface in an office zone that a general cleaner "
        "damages. Without a safe option the honest instruction is to leave it "
        "dirty."),
    "MPL-00102": S("homedepot", "fireproof document safe", ["fireproof", "safe"],
        "Permanent originals have no assigned home in most houses, so they "
        "live in a drawer that a fire or a flood ends. One closed container is "
        "the whole standard."),
    "MPL-00116": S("homedepot", "fire extinguisher", ["extinguisher"],
        "Unsafe placement, in its most literal form. A workshop fire is small "
        "for about ninety seconds, and only if the extinguisher is on the wall "
        "you can reach from the door."),
    "MPL-00117": S("target", "first aid kit", ["first-aid"],
        "A working room produces cuts, splinters and burns as a matter of "
        "course. Treating them at the bench is the difference between a pause "
        "and an abandoned reset."),
    "MPL-00100": S("homedepot", "dryer vent cleaning brush", ["dryer", "vent", "lint"],
        "Packed lint is a capacity problem with a fire at the end of it. The "
        "screen is not the duct, and the duct is the part nobody has ever "
        "cleaned."),
    "MPL-00105": S("homedepot", "concrete degreaser", ["degreaser", "concrete", "cleaner"],
        "Oil in a slab is why a garage floor cannot be swept to a standard. "
        "Lift the staining once and sweeping starts to work."),
    "MPL-00113": S("homedepot", "saw blade cleaner",
                   ["blade-cleaner", "bladeclean", "pitch", "resin"],
        "A blade that has stopped cutting is usually not blunt, it is coated. "
        "This is the cleaning step that people replace tools instead of "
        "doing."),
    "MPL-00106": S("homedepot", "oil absorbent", ["absorbent", "oil-dri", "spill"],
        "A fresh spot on concrete is a five minute job and a two year stain "
        "otherwise. Absorbent granules make the fast option the available "
        "one."),
    "MPL-00099": S("target", "washing machine cleaner tablets", ["washing-machine", "affresh"],
        "A drum that smells is biofilm, not dirty laundry. It is the "
        "replenishment signal nobody set: it comes back on a schedule, so the "
        "cleaner belongs in the zone."),
    "MPL-00114": S("homedepot", "mineral spirits", ["mineral-spirits", "spirits", "solvent"],
        "A brush cleaned to the ferrule lasts years; one cleaned at the tip is "
        "ruined at the third use. This is the difference between the two."),
    "MPL-00112": S("homedepot", "plastic scraper", ["scraper"],
        "Dried glue on a bench is difficult cleaning that a metal blade turns "
        "into damage. Plastic lifts the residue and leaves the surface."),
    "MPL-00119": S("homedepot", "scrub brush", ["scrub"],
        "A boot tray or a bin that is never scrubbed becomes the reason the "
        "zone is avoided. Stiff bristles are what make caked mud a one minute "
        "job."),
    "MPL-00124": S("homedepot", "garden hose", ["hose"],
        "Outdoor grit is abrasive, so any cleaner applied over it grinds. "
        "Floating the loose material off first is the step that protects the "
        "surface."),
    "MPL-00122": S("homedepot", "deck scrub brush long handle", ["scrub", "deck"],
        "Anything that has to be done on your knees does not get done twice. "
        "Standing height is what turns a deck wash into a routine."),
    "MPL-00121": S("homedepot", "grill brush scraper", ["grill"],
        "Carbonised residue is the food-contact surface's real condition. A "
        "scraper or coil does it without leaving wire bristles behind, which "
        "is a genuine hazard and the reason the type is specified."),
    "MPL-00123": S("homedepot", "outdoor fabric cushion cleaner", ["fabric", "cushion", "upholstery"],
        "Outdoor fabric is water resistant until the wrong cleaner strips it, "
        "and then the cushion is finished. The compatibility is the whole "
        "recommendation."),

    # ------------------------------------------------------- 3 Room (88)
    "MPL-00093": S("target", "shelf labels adhesive", ["label"],
        "Unclear ownership of a shelf is what makes a system decay into "
        "wherever-it-fits. Naming locations makes the right place findable "
        "without asking anybody."),
    "MPL-00014": S("target", "waterproof labels", ["label"],
        "A label that peels in a damp or cold zone takes the standard with it. "
        "Permanent stock is for the standards you have already settled."),
    "MPL-00017": S("target", "step stool", ["step-stool", "stool"],
        "Poor accessibility is why the top of a cupboard fills with things "
        "nobody has looked at in years. Safe reach turns dead capacity back "
        "into storage."),
    "MPL-00096": S("target", "surge protector power strip", ["surge"],
        "Charging without one home means cords on every surface, and a daisy "
        "chain of unprotected strips underneath. One protected outlet fixes "
        "both the mess and the hazard."),
    "MPL-00005": S("target", "hardwood floor cleaner", ["floor"],
        "The wrong floor product is difficult cleaning you created: it hazes, "
        "or it strips a finish, and then the floor never looks clean again."),
    "MPL-00070": S("target", "bathroom towel storage basket", ["basket"],
        "A stack with no boundary slumps, and a slumped stack is refolded or "
        "ignored. A container is what holds the standard between uses."),
    "MPL-00061": S("target", "front facing bookshelf", ["book"],
        "Poor visibility is why children's books are never chosen. Spines "
        "mean nothing to a pre-reader; a cover facing out is the whole "
        "difference."),
    "MPL-00060": S("target", "toy storage bin", ["toy", "bin"],
        "Independence is the desired function here. A picture label lets a "
        "child put a thing away without an adult, which is what makes tidying "
        "survive the week."),
    "MPL-00042": S("target", "shoe rack", ["shoe"],
        "Shoes on the floor are the classic no assigned home. Off the path is "
        "the outcome; the rack is only the means."),
    "MPL-00020": S("target", "small clear storage bin with lid", ["clear", "storage", "bin"],
        "Small loose items are lost to poor visibility, not to lack of space. "
        "Clear sides mean the contents are the label."),
    "MPL-00027": S("target", "drawer organizer dividers", ["drawer", "divider"],
        "A shallow drawer with no divisions has one category, and that "
        "category is everything. Dividers create the subcategories a drawer "
        "cannot show on its own."),
    "MPL-00090": S("target", "removable inventory labels", ["label"],
        "A missing replenishment signal is why you run out of the thing you "
        "buy most. A minimum and maximum written on the shelf makes the "
        "reorder point visible instead of remembered."),
    "MPL-00055": S("target", "charging station multiple devices", ["charging", "charger", "dock"],
        "Devices with no assigned home charge wherever the cable is, which is "
        "every flat surface in the house. One controlled home ends the search "
        "and the clutter together."),
    "MPL-00092": S("homedepot", "floor marking tape", ["tape"],
        "A boundary that exists only in somebody's head is not a standard. "
        "Marked floor makes no-storage zones and equipment footprints obvious "
        "to everyone, including a visitor."),
    "MPL-00062": S("target", "laundry sorter hamper", ["laundry", "hamper", "sorter"],
        "Sorting at the machine is a step done every wash; sorting at the "
        "hamper is a step done once, by whoever undressed. The container "
        "decides which."),
    "MPL-00021": S("target", "clear storage box with lid", ["clear", "storage", "box"],
        "Shelf and closet items disappear into opaque containers. Clear sides "
        "are what stop a labelled box being opened to check."),
    "MPL-00063": S("target", "collapsible laundry basket", ["laundry", "basket"],
        "Clean laundry stalls between the dryer and the bedroom. Something "
        "that carries a load and then folds away removes the reason it is "
        "left in the hall."),
    "MPL-00069": S("target", "medicine lock box", ["lock"],
        "Medicines in an unlocked cabinet are unsafe placement, not untidy "
        "storage. Locking them is the intervention; organising them is not."),
    "MPL-00038": S("target", "over the door hook rack", ["door", "hook"],
        "Inadequate capacity in a rented or shared room. A door is unused "
        "vertical space and this borrows it without a fixing."),
    "MPL-00056": S("target", "small decorative tray", ["tray"],
        "Remotes are searched for daily because they have no home. One "
        "visible tray makes the standard state obvious at a glance from the "
        "sofa."),
    "MPL-00097": S("target", "cable labels", ["label"],
        "Unclear ownership of a cable is why nobody unplugs anything. "
        "Identifying the ends is what makes a cord nest safe to touch."),
    "MPL-00025": S("target", "small woven storage basket", ["basket"],
        "Soft daily-use items need a boundary, not a lid. Open weave keeps "
        "the one-motion access that makes a container get used."),
    "MPL-00007": S("target", "detail cleaning brush set", ["brush"],
        "Seams, tracks and hardware are where a zone actually fails "
        "inspection. A cloth cannot get into any of them."),
    "MPL-00074": S("target", "controller charging station", ["charging", "charger", "dock"],
        "Controllers live on the floor because charging and storing are two "
        "different places. Combining them removes the choice."),
    "MPL-00054": S("target", "cable management kit", ["cable", "cord"],
        "A cord nest is difficult cleaning, poor visibility and a trip hazard "
        "at once. Securing the run is what makes the surface under it "
        "cleanable."),
    "MPL-00036": S("target", "matching hangers set", ["hanger"],
        "Mixed hangers make a rail look chaotic even when it is not, and they "
        "waste depth. One type is a visual control that costs nothing to "
        "maintain."),
    "MPL-00086": S("homedepot", "hose reel", ["hose", "reel"],
        "A coiled hose on a path is a trip hazard and the reason the hose is "
        "never fully put away. The reel makes putting it away the fast "
        "option."),
    "MPL-00059": S("target", "craft storage tray organizer", ["tray", "caddy", "organizer"],
        "An active project spread across a table blocks the table's real "
        "function. Containing it lets the project pause without being packed "
        "away."),
    "MPL-00057": S("target", "jewelry valet tray", ["jewelry", "valet", "tray"],
        "Pocket contents land wherever the person lands. A defined tray is a "
        "single home for the small things that otherwise go missing."),
    "MPL-00091": S("target", "removable labels", ["label"],
        "Without a visible date, rotation is guesswork and the oldest item is "
        "always the one at the back. A date marker makes sequence visible."),
    "MPL-00075": S("target", "reclosable storage bags", ["bag"],
        "A board game is only complete until one piece is loose in the box. "
        "Bagging components is what keeps the game playable years later."),
    "MPL-00050": S("target", "airtight food storage containers", ["container", "canister", "airtight"],
        "Half-open packets are both a spoilage problem and a visibility one. "
        "Uniform containers show the level, which is also the reorder "
        "signal."),
    "MPL-00066": S("homedepot", "under sink drip tray", ["tray", "liner", "pan"],
        "A slow leak under a sink is invisible until the cabinet floor is "
        "ruined. A tray both protects the base and makes the leak show "
        "early."),
    "MPL-00068": S("target", "medicine cabinet organizer bins", ["organizer", "bin"],
        "Medicines grouped by nothing get taken by the wrong person or bought "
        "twice. Grouping by purpose and by user is the safety control here."),
    "MPL-00022": S("target", "latching storage tote", ["tote", "latch", "storage"],
        "Seasonal and bulk items need capacity that stacks and stays shut. A "
        "lid that latches is what makes vertical stacking safe."),
    "MPL-00033": S("target", "shelf dividers", ["divider"],
        "A tall stack collapses into its neighbour and the category is lost. "
        "Dividers hold the boundary a shelf cannot hold by itself."),
    "MPL-00026": S("target", "large woven storage basket", ["basket"],
        "Blankets and bulky soft items have no natural shape, so they take "
        "whatever shape the room allows. A large open container gives them "
        "one."),
    "MPL-00085": S("homedepot", "garden tool bag", ["garden", "tool-bag", "caddy", "tote"],
        "Small garden tools are abandoned where they were used. One carrier "
        "makes returning them a single motion rather than five."),
    "MPL-00065": S("homedepot", "broom holder wall mount", ["broom", "holder", "hook"],
        "Long-handled tools fall over, and a tool that falls over gets left "
        "leaning somewhere else. Vertical clips give each one a home that "
        "holds."),
    "MPL-00083": S("homedepot", "outdoor deck storage box", ["deck-box", "storage", "box"],
        "Cushions left out are ruined by one wet week, so they end up indoors "
        "in the wrong room. Weatherproof capacity outside fixes both."),
    "MPL-00024": S("target", "open front storage bin", ["bin"],
        "Every lid is a step. Where the item is used many times a day, "
        "one-motion access is what stops the container being bypassed."),
    "MPL-00082": S("homedepot", "glove dispenser wall mount", ["dispenser", "holder", "rack"],
        "Protective equipment that is in a drawer is not worn. Making it "
        "visible at the point of use is the difference between owning it and "
        "using it."),
    "MPL-00039": S("target", "wall mounted hook rail", ["hook", "rack", "rail"],
        "A labelled hook is the cheapest assigned home there is, and the only "
        "one a child can use without being taught."),
    "MPL-00048": S("target", "spice rack organizer", ["spice"],
        "Spices behind spices are bought again because they cannot be seen. "
        "Retrievability, not capacity, is the problem in this zone."),
    "MPL-00067": S("target", "plastic storage bin with handles", ["bin", "crate", "caddy"],
        "Household chemicals stored loose leak into each other and get picked "
        "up by the wrong hand. Containment is a safety control before it is "
        "an organising one."),
    "MPL-00023": S("target", "small open bin storage", ["bin"],
        "Frequently used small items are the ones a lid costs the most on. "
        "Open front is the standard for anything touched daily."),
    "MPL-00076": S("target", "sports ball storage bin", ["ball", "sport", "bin"],
        "Balls roll, so they have no stable home by nature and end up under "
        "the car. A deep container is the only thing that holds them."),
    "MPL-00044": S("target", "entryway umbrella holder", ["umbrella"],
        "A wet umbrella has to drain somewhere, and a hook makes it drip on "
        "the floor. Vertical containment handles the water and the home at "
        "once."),
    "MPL-00029": S("target", "cabinet shelf riser", ["shelf", "riser"],
        "A back row you cannot see is a back row you buy again. A riser turns "
        "one deep shelf into two visible ones."),
    "MPL-00081": S("homedepot", "flammable storage cabinet", ["flammable", "cabinet", "safety"],
        "Solvents and finishes stored on an open shelf are unsafe placement "
        "with a specific failure mode. A rated cabinet is the control, not a "
        "tidier shelf."),
    "MPL-00058": S("target", "file storage box hanging folders", ["file", "box"],
        "Household records are kept in a pile because filing them takes a "
        "system nobody built. A single box with hanging files is that system "
        "at its smallest."),
    "MPL-00035": S("target", "magazine file holder", ["magazine", "file"],
        "Slim items fall flat and then everything on the shelf leans. "
        "Vertical containment keeps them findable and keeps the shelf "
        "upright."),
    "MPL-00031": S("target", "2 tier pull out cabinet organizer", ["tier", "pull-out", "slide", "organizer"],
        "A deep cabinet has capacity you cannot reach, which is poor "
        "accessibility, not a shortage. Pulling the shelf out brings the back "
        "to you."),
    "MPL-00043": S("homedepot", "boot tray", ["boot", "tray"],
        "Wet and muddy boots are the reason an entry floor is never clean. "
        "A tray contains the water instead of spreading it."),
    "MPL-00053": S("target", "freezer labels", ["label"],
        "An undated leftover is thrown away on suspicion or eaten on hope. "
        "Dating removes the guess, which is what actually reduces waste."),
    "MPL-00080": S("homedepot", "lumber storage rack", ["rack", "lumber", "storage"],
        "Long material stored leaning falls, warps and blocks the floor. "
        "Horizontal support is a safety fix as much as a space one."),
    "MPL-00049": S("target", "can organizer rack pantry", ["can", "organizer", "rack"],
        "Cans stacked flat hide their own labels and defeat rotation. A "
        "stepped or gravity rack makes both visible."),
    "MPL-00084": S("homedepot", "grill tool holder hooks", ["grill", "hook", "tool", "holder"],
        "Hot tools put down on a rail or a table are a burn waiting to "
        "happen. A defined hanging home is the safe default."),
    "MPL-00032": S("target", "pull out cabinet organizer", ["pull-out", "slide", "organizer"],
        "In a low or narrow cabinet the barrier is kneeling and reaching "
        "blind. One sliding tier removes both motions."),
    "MPL-00079": S("homedepot", "small parts organizer drawers", ["drawer", "organizer", "parts", "bin"],
        "Fasteners mixed together are bought again rather than sorted "
        "through. Separation by type and size is what makes the stock "
        "usable."),
    "MPL-00064": S("target", "clothes drying rack", ["drying", "rack"],
        "Items that cannot go in a dryer end up over doors and radiators, "
        "which is wrong location by default. A rack gives the exception a "
        "home."),
    "MPL-00047": S("target", "bakeware organizer", ["bakeware", "pan"],
        "Nested pans mean lifting four to reach one. Standing them upright "
        "makes every one a single motion."),
    "MPL-00073": S("target", "toilet paper storage holder", ["toilet-paper", "toilet", "holder"],
        "The reserve is either invisible in a cupboard or a stack on the "
        "floor. A controlled visible reserve is also the replenishment "
        "signal."),
    "MPL-00034": S("target", "desktop file sorter", ["sorter", "file"],
        "Flat stacks are accessed from the top only, so the bottom is dead. "
        "Vertical storage makes every item in the set reachable."),
    "MPL-00095": S("target", "child safety cabinet latch", ["latch", "lock", "safety"],
        "Chemicals, medicines and sharp tools in a reachable drawer are "
        "unsafe placement. A latch is the control; teaching is not."),
    "MPL-00040": S("homedepot", "pegboard", ["pegboard", "peg-board"],
        "A tool in a drawer has no standard state, so nobody can tell whether "
        "it was put back. On a board, missing is visible from across the "
        "room."),
    "MPL-00077": S("homedepot", "bike wall mount rack", ["bike", "bicycle"],
        "Bikes on the floor take the space a car or a workbench needs and "
        "fall on things. Off the floor is the whole outcome."),
    "MPL-00046": S("target", "pot lid organizer", ["lid", "organizer", "rack"],
        "Lids are the single worst-behaved item in a kitchen because they do "
        "not stack with what they belong to. They need their own boundary."),
    "MPL-00015": S("homedepot", "nitrile gloves", ["nitrile", "glove"],
        "Hands are the reason a cleaning or sorting job gets cut short. "
        "Protection is what makes the unpleasant part of a reset finishable."),
    "MPL-00037": S("target", "velvet slim hangers", ["hanger"],
        "Crowding is inadequate capacity that looks like too many clothes. "
        "Slim non-slip hangers recover depth without anything being "
        "discarded."),
    "MPL-00041": S("homedepot", "garage wall track storage system", ["track", "rail", "storage", "wall"],
        "Long tools and sports equipment have no shape a shelf suits. An "
        "adjustable track lets the home match the item instead of the other "
        "way round."),
    "MPL-00078": S("homedepot", "tool battery storage rack", ["battery", "charger", "rack", "shelf"],
        "Batteries and chargers separate, and then nothing is charged when it "
        "is needed. One rack makes the charged state visible."),
    "MPL-00071": S("target", "shower caddy", ["shower", "caddy"],
        "Bottles on the shower floor are why the shower floor cannot be "
        "cleaned. Lifting them is a Shine fix disguised as storage."),
    "MPL-00072": S("target", "shower squeegee", ["squeegee"],
        "Limescale is difficult cleaning that you can prevent instead. Thirty "
        "seconds after use replaces a scrubbing job later."),
    "MPL-00103": S("target", "cross cut paper shredder", ["shredder"],
        "Paper that cannot be safely thrown away is not sorted, it is "
        "deferred. Destroying it at the point of decision is what lets the "
        "decision finish."),
    "MPL-00052": S("target", "produce keeper", ["produce"],
        "Produce is lost at the back of a drawer, which is a visibility "
        "problem with a cost attached to it every week."),
    "MPL-00045": S("target", "under bed storage bin", ["under-bed", "underbed", "storage"],
        "Under a bed is real capacity that becomes a dust trap when used "
        "loose. A closed rolling container makes it storage rather than a "
        "gap."),
    "MPL-00051": S("target", "refrigerator organizer bins", ["refrigerator", "fridge", "bin", "organizer"],
        "A fridge has no internal boundaries, so every category migrates. "
        "Grouped containers hold zones a shelf cannot."),
    "MPL-00030": S("target", "lazy susan turntable organizer", ["turntable", "lazy-susan"],
        "A deep corner is capacity you cannot reach without unloading it. "
        "Rotation brings the back to the front in one motion."),
    "MPL-00110": S("target", "extendable duster", ["duster"],
        "Overhead dust is the source that resettles on everything you just "
        "cleaned. Reaching it from the floor is what makes it part of the "
        "routine."),
    "MPL-00120": S("target", "garment brush", ["garment", "clothes-brush"],
        "Coat shoulders and bag straps carry street dust into the house. A "
        "soft brush at the door stops it at the threshold."),
    "MPL-00107": S("homedepot", "electrical contact cleaner", ["contact-cleaner", "contact", "electrical"],
        "A charger that stops working is usually a dirty contact, not a dead "
        "device. Residue-free cleaning is the whole requirement."),
    "MPL-00011": S("target", "manila shipping tags", ["tag"],
        "A genuine maybe stalls a Sort indefinitely. A dated tag time-boxes "
        "the decision so the item leaves or stays on a known date rather "
        "than never."),
    "MPL-00028": S("target", "deep drawer organizer bins", ["drawer", "bin", "organizer"],
        "A deep drawer becomes a well: items at the bottom are functionally "
        "gone. Bins hold categories at a depth you can still see into."),
    "MPL-00094": S("target", "printable label sheets", ["label"],
        "A zone standard that lives in a document nobody opens is not a "
        "standard. A durable code on the zone connects the place to its own "
        "instructions."),
    "MPL-00087": S("target", "kitchen timer", ["timer"],
        "An unbounded reset is the reason resets are avoided. A visible "
        "countdown is what turns a whole-room dread into a finishable "
        "fifteen minutes."),
    "MPL-00089": S("target", "dry erase pockets", ["dry-erase", "pocket"],
        "An audit that has to be remembered is not repeated. A reusable card "
        "in a wipeable sleeve makes the same six questions available in the "
        "zone every time."),
    "MPL-00088": S("target", "dry erase pockets", ["dry-erase", "pocket"],
        "Before and after is the only evidence a household reset produces. A "
        "consistent framing card is what makes two photographs comparable "
        "rather than just two photographs."),

    # ------------------------------------------------ 4 Situational (1)
    "MPL-00018": S("homedepot", "furniture anti tip anchor kit", ["anti-tip", "anchor", "furniture", "strap"],
        "Tall furniture tipping is the one household failure that kills "
        "children, and it is entirely preventable with a strap. This is not "
        "an organising product, it is the condition on storing anything high."),
}


# ----------------------------------------------------------------- rendering
def _browser():
    try:
        import browser
        return browser.find_browser()
    except Exception:                                          # noqa: BLE001
        return None


def render(url: str) -> tuple:
    """(html, note). html is "" when we could not look, and the note says why.

    A plain HTTP fetch is not enough for any of these merchants: the results
    are drawn by JavaScript. So this drives a real Chromium. If there is no
    browser on this machine the answer is "unchecked", never "dead".
    """
    b = _browser()
    if not b:
        return "", "no headless browser on this machine"
    exe, extra = b
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [exe, "--headless=new", "--disable-gpu", "--no-first-run",
               f"--user-data-dir={tmp}",
               f"--virtual-time-budget={RENDER_MS}", "--dump-dom", url] + extra
        try:
            p = subprocess.run(cmd, capture_output=True,
                               timeout=RENDER_MS / 1000 + 45)
        except subprocess.TimeoutExpired:
            return "", "render timed out"
        except Exception as e:                                 # noqa: BLE001
            return "", f"render failed: {type(e).__name__}"
    html = p.stdout.decode("utf-8", errors="ignore")
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    t = (title.group(1) if title else "").strip().lower()
    if any(b in t for b in BLOCKED_TITLES):
        return "", f"blocked or errored: page titled {t[:40]!r}"
    if len(html) < MIN_RESULTS_BYTES:
        return "", (f"render returned {len(html)} bytes, far short of a real "
                    f"results grid, so nothing was actually seen")
    return html, ""


def matches(slug: str, keyword: str) -> bool:
    """Does this retailer product slug actually name the product type.

    Not a substring test, which was the first version and was wrong. A slug is
    a hyphen-joined product name, so a bare substring makes "washer" match
    `clean-people-dishwasher-detergent-tablets` and "can" match a candle. That
    is a verification that certifies the wrong product, which is worse than no
    verification because it looks like evidence.

    So a single-word keyword must be a whole word of the name, allowing the
    ordinary plurals a retailer uses. A keyword written with a hyphen is a
    phrase ("safety-glass", "dry-erase") and is matched across the slug,
    because that is the only way to pin a two-word type.
    """
    kw = keyword.lower()
    if "-" in kw:
        return kw in slug
    return any(t == kw or t == kw + "s" or t == kw + "es"
               for t in slug.split("-"))


def judge(merchant: str, html: str, keywords: list) -> tuple:
    """(state, hits, slugs_checked, matched). state is ok / weak / dead."""
    pat = MERCHANTS[merchant]["slug"]
    seen, slugs = set(), []
    for m in pat.finditer(html):
        s = m.group(1).lower()
        if s and s not in seen:
            seen.add(s)
            slugs.append(s)
        if len(slugs) >= TOP_N:
            break
    matched = [s for s in slugs if any(matches(s, k) for k in keywords)]
    if not slugs:
        return "dead", 0, 0, []
    if len(matched) >= MIN_HITS:
        return "ok", len(matched), len(slugs), matched[:6]
    if matched:
        return "weak", len(matched), len(slugs), matched
    return "dead", 0, len(slugs), []


def verify(pid: str, merchant: str, url: str, keywords: list,
           tries: int = 3) -> dict:
    """Render, judge, and retry a failure to look.

    Retailers rate-limit bursts, so the first attempt at a link can come back
    blocked purely because of the attempt beside it. A retry distinguishes a
    busy server from a bad link; without one, "unchecked" would be reported so
    often that it would stop being read.
    """
    html, note = "", ""
    for attempt in range(tries):
        html, note = render(url)
        if html:
            break
        time.sleep(4 + 6 * attempt)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    if not html:
        return {"id": pid, "merchant": merchant, "url": url,
                "state": "unchecked", "why": note, "checked": now}
    state, hits, n, matched = judge(merchant, html, keywords)
    return {"id": pid, "merchant": merchant, "url": url, "state": state,
            "hits": hits, "of": n, "matched": matched, "checked": now,
            "keywords": keywords}


# --------------------------------------------------------------------- the CSV
COLUMNS_ADDED = ["Why Recommended"]


def read_catalogue() -> tuple:
    with io.open(CATALOGUE, encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        rows = list(r)
        return rows, list(r.fieldnames or [])


def write_catalogue(rows: list, fields: list) -> None:
    for c in COLUMNS_ADDED:
        if c not in fields:
            fields.append(c)
    with io.open(CATALOGUE, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def load_evidence() -> dict:
    if os.path.exists(EVIDENCE):
        try:
            return json.load(io.open(EVIDENCE, encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            return {}
    return {}


def save_evidence(ev: dict) -> None:
    ev["_what"] = ("How each retailer link in ops/affiliate-catalogue.csv was "
                   "verified. Written by ops/product_links.py. 'hits' is how "
                   "many of the first %d product slugs the retailer's own "
                   "search grid returned contained a keyword for the product "
                   "type; %d or more is required to publish. The grid is read "
                   "from a headless Chromium render, not an HTTP fetch: these "
                   "retailers draw results in JavaScript, and homedepot.com "
                   "returns 403 to a plain fetch of any URL including its own "
                   "homepage. A 403 from curl is not evidence about a link."
                   % (TOP_N, MIN_HITS))
    io.open(EVIDENCE, "w", encoding="utf-8", newline="").write(
        json.dumps(ev, indent=1, sort_keys=True) + "\n")


# ------------------------------------------------------------------ commands
def _targets(only: str | None) -> list:
    ids = [i.strip() for i in only.split(",")] if only else list(SPEC)
    missing = [i for i in ids if i not in SPEC]
    if missing:
        print(f"  no spec for {missing}")
    return [i for i in ids if i in SPEC]


def assign(only: str | None = None, dry: bool = False) -> int:
    """Verify every specified link and record the result in the catalogue."""
    rows, fields = read_catalogue()
    by_id = {r["Product ID"]: r for r in rows}
    ev = load_evidence()

    ids = _targets(only)
    jobs = {i: search_url(SPEC[i]["m"], SPEC[i]["q"]) for i in ids}
    print(f"  verifying {len(jobs)} links in a real browser, "
          f"{WORKERS} at a time. This is slow on purpose.")

    results = {}
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(verify, i, SPEC[i]["m"], jobs[i], SPEC[i]["k"]): i
                for i in ids}
        for done in cf.as_completed(futs):
            i = futs[done]
            r = done.result()
            results[i] = r
            mark = {"ok": "  ok  ", "weak": " weak ", "dead": " DEAD ",
                    "unchecked": " ---- "}[r["state"]]
            extra = (f'{r.get("hits",0)}/{r.get("of",0)} matched'
                     if r["state"] != "unchecked" else r["why"])
            print(f"  {mark} {i}  {r['merchant']:10} {extra}")

    n = {"ok": 0, "weak": 0, "dead": 0, "unchecked": 0}
    for i, r in results.items():
        n[r["state"]] += 1
        row = by_id.get(i)
        if row is None:
            continue
        row["Why Recommended"] = SPEC[i]["why"]
        ev[i] = r
        if r["state"] == "unchecked":
            # THE RULE THAT MATTERS. A run that could not look does not get to
            # overwrite what a run that could look wrote. The old status, old
            # URL and old date all stand, and the summary says it was skipped.
            continue
        if r["state"] == "ok":
            row["Merchant"] = r["merchant"]
            row["Affiliate URL"] = r["url"]
            row["Link Status"] = "Verified search"
            row["Last Checked"] = r["checked"]
            row["Notes"] = (f'Retailer search for the product type. '
                            f'{r["hits"]} of the first {r["of"]} results '
                            f'matched {"/".join(r["keywords"])} when rendered '
                            f'{r["checked"]}. No affiliate code.')
        else:
            # Publishing is refused, and the reason is recorded rather than
            # quietly dropped: zone_supplies.py only publishes a status that
            # begins "verified", so this row goes back to plain text.
            row["Merchant"] = ""
            row["Affiliate URL"] = ""
            row["Link Status"] = ("No results" if r["state"] == "dead"
                                  else "Too weak to publish")
            row["Last Checked"] = r["checked"]
            row["Notes"] = (f'{r["merchant"]} search "{SPEC[i]["q"]}" returned '
                            f'{r.get("hits",0)} matching results of '
                            f'{r.get("of",0)}. Not published.')

    if not dry:
        write_catalogue(rows, fields)
        save_evidence(ev)
    print(f"\n  ok {n['ok']}   weak {n['weak']}   dead {n['dead']}   "
          f"UNCHECKED {n['unchecked']}")
    if n["unchecked"]:
        print(f"  {n['unchecked']} link(s) could not be looked at at all. "
              f"They keep their previous status. Unchecked is not passing.")
    return 1 if n["dead"] or n["unchecked"] else 0


def checkable(rows: list) -> list:
    """Every row this tool must look at: any row carrying a URL.

    Status is an OUTPUT of checking, so it must never be an input to deciding
    what gets checked. Selecting on it is how a run ends up reporting
    "UNCHECKED 0" while 37 links sit unexamined, and it fails worst exactly
    when a row has been marked doubtful, which is when re-checking matters
    most.
    """
    return [r for r in rows if (r.get("Affiliate URL") or "").strip()]


def check() -> int:
    """Re-verify every link in the catalogue. Links rot.

    THE SCOPE BUG THIS FIXES, 2026-09-04
    ------------------------------------
    The first version selected only rows whose Link Status already began
    "verified", then printed

        re-checking 83 published links
        live 83   dead 0   UNCHECKED 0

    while 37 rows carried a URL that this run never looked at. "UNCHECKED 0"
    on a line that reads as a whole-catalogue verdict is false, and it is
    false in the most expensive direction: it says full coverage when the run
    silently narrowed its own scope to the part it found convenient. Worse,
    the excluded 37 were exactly the ones somebody had just marked
    unverifiable, so the tool would agree it had checked everything precisely
    when a row most needed re-checking.

    So the scope is now every row carrying a URL, whatever its status says,
    and the summary names what it skipped and why. A checker does not get to
    choose a denominator that flatters it.
    """
    rows, _ = read_catalogue()
    live = checkable(rows)
    no_url = [r for r in rows if r not in live]
    if not live:
        print("  the catalogue publishes no retailer link, so there is "
              "nothing to re-check")
        return 0

    print(f"  re-checking {len(live)} link(s), every row that carries a URL")
    if no_url:
        print(f"  {len(no_url)} row(s) carry no URL at all and are not links "
              f"to check: {[r['Product ID'] for r in no_url]}")
    ev = load_evidence()
    bad, unchecked = [], []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {}
        for r in live:
            pid = r["Product ID"]
            spec = SPEC.get(pid)
            kw = spec["k"] if spec else [
                # No spec: fall back to the words of the product name itself,
                # which is weaker but is still a real relevance test.
                w for w in re.findall(r"[a-z]{4,}",
                                      r["Product Standard Name"].lower())]
            futs[pool.submit(verify, pid, (r.get("Merchant") or "").strip(),
                             r["Affiliate URL"], kw)] = r
        for done in cf.as_completed(futs):
            row = futs[done]
            res = done.result()
            ev[res["id"]] = res
            if res["state"] == "unchecked":
                unchecked.append((row, res))
            elif res["state"] != "ok":
                bad.append((row, res))
            else:
                row["Last Checked"] = res["checked"]

    save_evidence(ev)
    for row, res in bad:
        print(f"  DEAD  {res['id']}  {row['Product Standard Name'][:44]}")
        print(f"        {res['url']}")
        print(f"        {res.get('hits',0)} of {res.get('of',0)} results "
              f"matched the product type")
    for row, res in unchecked:
        print(f"  ----  {res['id']}  {row['Product Standard Name'][:44]}")
        print(f"        UNCHECKED, not dead: {res['why']}")

    ok = len(live) - len(bad) - len(unchecked)
    print("")
    print(f"  of {len(rows)} catalogue rows: {len(live)} carry a URL and were "
          f"all looked at, {len(no_url)} carry none")
    print(f"  live {ok}   dead {len(bad)}   UNCHECKED {len(unchecked)}")

    # A row can be checkable and still not reach a reader, because
    # ops/affiliate.py holds back any host site/privacy.html has not named and
    # ops/zone_supplies.py holds back any status that does not begin
    # "verified". Reporting only the network result would let "live 120" be
    # read as "120 links on the site" on a day when the answer is nought.
    try:
        import affiliate as A
        rendering = sum(1 for r in live
                        if A.retailer_link(r)[1] in ("tracked", "plain"))
        print(f"  of those, {rendering} actually render on the site today")
        held = [r["Product ID"] for r in live
                if A.retailer_link(r)[1] not in ("tracked", "plain")]
        if held:
            print(f"  {len(held)} checked link(s) do NOT render: {held[:8]}")
    except Exception as e:                                     # noqa: BLE001
        print(f"  could not read the publish gate: {type(e).__name__}")

    if unchecked:
        names = [r["Product ID"] for r, _ in unchecked]
        print(f"  the {len(unchecked)} unchecked one(s) are {names}. Not dead, "
              f"not passing: nobody looked.")
    if unchecked and not bad:
        print("  Nothing failed, but this run did not prove every link works "
              "either. Do not read this as a pass.")
    return 1 if bad else 0


def status() -> int:
    """No network. What does the catalogue say about itself right now."""
    rows, _ = read_catalogue()
    by_state = {}
    no_why = []
    for r in rows:
        s = (r.get("Link Status") or "Unverified").strip() or "Unverified"
        by_state.setdefault(s, []).append(r)
        if (r.get("Link Status") or "").lower().startswith("verified") \
                and not (r.get("Why Recommended") or "").strip():
            no_why.append(r["Product ID"])

    print(f"  {len(rows)} products in ops/affiliate-catalogue.csv")
    for s, rs in sorted(by_state.items(), key=lambda kv: -len(kv[1])):
        merch = {}
        for r in rs:
            merch[r.get("Merchant") or "-"] = merch.get(r.get("Merchant") or "-", 0) + 1
        detail = ", ".join(f"{k} {v}" for k, v in sorted(merch.items()))
        print(f"    {len(rs):4}  {s:22} {detail}")

    # A row cannot both have been rendered and be unverifiable. On 2026-09-04
    # something rewrote the Link Status of all 37 Home Depot rows to "Search
    # URL, unverifiable here (retailer blocks bots)" while leaving each row's
    # own Notes reading "11 of the first 12 results matched ... when rendered
    # 2026-09-04". Home Depot does block a plain HTTP fetch, and does not
    # block a rendered browser, which is the entire reason this tool drives
    # one. Whatever wrote that status had not looked, and wrote its own
    # inability to look over a measurement that had. That is the failure
    # CLAUDE.md 0.4 exists for, and it is silent, so it gets a detector.
    contradicted = [r["Product ID"] for r in rows
                    if "when rendered" in (r.get("Notes") or "")
                    and not (r.get("Link Status") or "").lower()
                    .startswith("verified")]
    if contradicted:
        print("")
        print(f"  FAIL {len(contradicted)} row(s) carry rendered evidence in "
              f"Notes but a Link Status that denies it: {contradicted[:8]}")
        print(f"    Re-run --assign on them. Do not resolve this by deleting "
              f"the evidence.")

    spec_missing = [r["Product ID"] for r in rows if r["Product ID"] not in SPEC]
    if spec_missing:
        print(f"\n  {len(spec_missing)} product(s) have no link spec at all: "
              f"{spec_missing[:6]}")
    if contradicted:
        return 1
    if no_why:
        # Rule 3. A published recommendation with no stated reason is the
        # thing CLAUDE.md section 48 forbids, so it is a failure, not a note.
        print(f"\n  FAIL {len(no_why)} published product(s) carry no reason: "
              f"{no_why[:8]}")
        return 1

    # Verified is not the same as published, and the difference has an owner
    # action behind it. ops/affiliate.py and ops/zone_supplies.py both refuse
    # to render a link to a host site/privacy.html does not name, because that
    # page currently promises the only outbound links go to Stripe. A run that
    # printed "120 verified" and let a reader assume 120 are live would be
    # reporting an intention as a measurement.
    try:
        import affiliate as A
        pub = [r for r in rows if A.retailer_link(r)[1] in ("tracked", "plain")]
        held = [r for r in rows if A.retailer_link(r)[1] == "withheld"]
        hosts = sorted({(r.get("Merchant") or "").strip() for r in held})
        print(f"")
        print(f"  published on the site   {len(pub)}")
        if held:
            print(f"  verified but WITHHELD   {len(held)}")
            print(f"    site/privacy.html does not name the retailer hosts, "
                  f"so nothing renders. Merchants held: {', '.join(hosts)}.")
    except Exception as e:                                     # noqa: BLE001
        print(f"")
        print(f"  could not read the publish gate: {type(e).__name__}. "
              f"That is unchecked, not clear.")

    ev = load_evidence()
    dated = [v.get("checked") for k, v in ev.items()
             if isinstance(v, dict) and v.get("checked")]
    if dated:
        print(f"\n  evidence in ops/product-links-evidence.json, "
              f"{len(dated)} records, newest {max(dated)}")
    else:
        print(f"\n  no evidence file yet: nothing has been verified")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--assign", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    if a.assign:
        return assign(a.only, a.dry)
    if a.check:
        return check()
    return status()


if __name__ == "__main__":
    raise SystemExit(main())
