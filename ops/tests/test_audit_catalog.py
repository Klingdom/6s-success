"""Prove ops/audit_catalog.py reports each of the three faults it claims to catch.

It prints three PASS lines and is a CI gate that refuses to publish on drift,
but the catalogue is currently clean, so a working audit and a broken one
produce identical output. This plants each fault in turn and requires it to be
reported, and plants correct copy and requires it to be left alone.

The false positive this was written for: the drift check captured only the
leading digits of a price, so a page stating the correct $9.99 price of the
ebook was read as "$9" and reported as drift. That would have failed the build
on correct copy the first time anyone wrote that price beside that name.
"""
import inspect
import io
import os
import subprocess
import time
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
OPS = os.path.join(ROOT, "ops")
TOOL = os.path.join(OPS, "audit_catalog.py")
# Suffixed with this process's own pid. Found 2026-09-05: preflight's own
# gate_tests() and a second, separately launched run of this same file both
# scan the whole site/ tree at once, and a fixed fixture name meant the two
# collided, one process's write or cleanup landing between another's write
# and its subprocess read of audit_catalog.py. That produced a real-looking
# gate failure ("a buy.stripe.com link absent from data.js was not
# reported") with no actual product defect behind it, reproduced by rerunning
# alone and watching it pass clean. A per-pid name makes two concurrent runs
# structurally unable to share a path, rather than relying on nobody ever
# overlapping them.
FIXTURE = os.path.join(SITE, "_audit_catalog_fixture_%d.html" % os.getpid())
# The per-pid name only stops two runs from overwriting the SAME file. It does
# not stop audit_catalog.py's own pages(), which globs the whole site/ tree,
# from seeing BOTH fixtures at once when two runs' write/scan/cleanup windows
# overlap, mixing one run's planted fault into another's clean-copy check.
# Found 2026-09-08 exactly this way (preflight's own gate_tests() overlapped
# a separately launched run of this file): "the correct price $19 of 'The
# Whole House Print Pack' was reported as drift," reproduced on demand by
# starting two copies at once, and gone the moment they run one at a time.
# A shared lock around the write-run-cleanup window serializes any number of
# concurrent instances of this file against each other, so at most one
# fixture ever exists in site/ while audit_catalog.py is reading it.
LOCK = os.path.join(SITE, "_audit_catalog_fixture.lockdir")

sys.path.insert(0, OPS)
import audit_catalog as A                                     # noqa: E402

SHELL = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
         '<title>Temporary fixture</title></head><body><main>%s</main></body></html>')


# The lock was fcntl.flock when it was written, which is Unix only, so this
# file could not even IMPORT on Windows and took the whole test gate red with
# ModuleNotFoundError. That matters more than it looks: Windows is the only
# machine here that can reach production, so a Unix-only test blocks the one
# environment that deploys.
#
# os.mkdir is atomic on both platforms and needs no dependency, so the lock is a
# directory. Same guarantee, same window, no import that only exists on one
# operating system.
STALE_AFTER = 900


# Found live 2026-09-16: a killed run's orphaned lockdir (this exact file's
# own comment two lines below anticipates it) blocked the very next waiter
# forever in practice, because its default timeout (600) was shorter than
# STALE_AFTER (900). A waiter that starts right as the orphan is created
# always hits its own timeout before the lock is old enough to break, so the
# self-heal this was written for could never fire on the first retry; only a
# second, later-arriving waiter (or a human clearing the directory by hand,
# as happened on 2026-09-11 and again on 2026-09-16) ever got past it. The
# margin below guarantees any single waiter's own timeout outlasts
# STALE_AFTER, so the lock it is waiting on is always stale, and therefore
# broken, before that waiter gives up.
def _lock(path: str, timeout: int = STALE_AFTER + 120) -> None:
    start = time.time()
    while True:
        try:
            os.mkdir(path)
            return
        except FileExistsError:
            # A run that was killed leaves its directory behind and would
            # otherwise block every later run forever. Break a lock that is
            # older than any legitimate hold.
            try:
                if time.time() - os.path.getmtime(path) > STALE_AFTER:
                    os.rmdir(path)
                    continue
            except OSError:
                pass
            if time.time() - start > timeout:
                raise RuntimeError("could not take %s within %ss" % (path, timeout))
            time.sleep(0.2)


def _unlock(path: str) -> None:
    try:
        os.rmdir(path)
    except OSError:
        pass


def _check_lock_self_heals() -> str:
    """A killed run's orphaned lockdir must not block the very next waiter.

    Two checks, because either one alone misses the real 2026-09-16 bug:

    1. The constant relationship itself. A waiter only ever lives long enough
       to see a lock go stale if its own timeout exceeds STALE_AFTER; with
       the old default (600 < STALE_AFTER's 900) this was false, so a waiter
       starting right as the orphan was created always raised first. Checked
       directly against the real, un-overridden default, since a check that
       passes an explicit timeout would not have caught that bug at all.
    2. The break-and-retry mechanism itself, on a fake orphan of its own
       (never the real LOCK, so this cannot collide with a concurrent real
       run), backdated past STALE_AFTER, called with a short explicit
       timeout so a regression here fails in seconds rather than hanging.
    """
    default_timeout = inspect.signature(_lock).parameters["timeout"].default
    if default_timeout <= STALE_AFTER:
        return ("_lock()'s default timeout (%ss) does not exceed STALE_AFTER "
                 "(%ss), so a waiter that starts right as an orphaned lock is "
                 "created will always time out before the lock is old enough "
                 "to break" % (default_timeout, STALE_AFTER))

    path = LOCK + ".selfheal_check_%d" % os.getpid()
    os.mkdir(path)
    old = time.time() - STALE_AFTER - 5
    os.utime(path, (old, old))
    try:
        _lock(path, timeout=5)
    except RuntimeError as e:
        return "an orphaned lock older than STALE_AFTER was not broken: %s" % e
    finally:
        _unlock(path)
    return ""


def run(inner: str) -> str:
    _lock(LOCK)
    try:
        io.open(FIXTURE, "w", encoding="utf-8", newline="").write(SHELL % inner)
        try:
            r = subprocess.run([sys.executable, TOOL], cwd=ROOT, capture_output=True,
                               text=True, timeout=600,
                               env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            return (r.stdout or "") + (r.stderr or "")
        finally:
            if os.path.exists(FIXTURE):
                os.remove(FIXTURE)
    finally:
        _unlock(LOCK)


def pick(decimal: bool):
    for c in A.load_catalog():
        p = c.get("price")
        if not p:
            continue
        is_dec = float(p) != int(float(p))
        if is_dec == decimal:
            return c["name"], float(p)
    return None, None


def main() -> int:
    bad = []
    heal_failure = _check_lock_self_heals()
    if heal_failure:
        bad.append(heal_failure)
    dec_name, dec_price = pick(True)
    int_name, int_price = pick(False)
    retired = A.load_retired()

    def drift_count(out: str) -> int:
        return sum(1 for l in out.splitlines() if "shown, catalogue price" in l)

    # Correct copy must not be reported. This is the regression that matters:
    # a gate that fails on correct copy is worse than no gate.
    if dec_name:
        out = run("<p>%s is $%s today.</p>" % (dec_name, ("%.2f" % dec_price)))
        if drift_count(out):
            bad.append("the correct price $%.2f of %r was reported as drift"
                       % (dec_price, dec_name))
        out = run("<p>%s is $%.2f today.</p>" % (dec_name, dec_price - 1))
        if not drift_count(out):
            bad.append("a wrong price for %r was not reported" % dec_name)

    if int_name:
        out = run("<p>%s is $%d today.</p>" % (int_name, int(int_price)))
        if drift_count(out):
            bad.append("the correct price $%d of %r was reported as drift"
                       % (int_price, int_name))
        # Plus ten, not minus ten. pick() returns the first integer priced
        # item in catalogue order, and on 2026-09-03 that became the $9 Kitchen
        # Pack when the catalogue was reordered to lead with room packs.
        # Minus ten made the fixture read "$-1", which is not a price, so the
        # drift check correctly found nothing and this test reported the audit
        # as broken. The test was only ever passing because the first integer
        # priced SKU happened to cost more than ten dollars, which is not a
        # property anybody guaranteed. Adding keeps the wrong price a real
        # price whatever the catalogue costs.
        out = run("<p>%s is $%d today.</p>" % (int_name, int(int_price) + 10))
        if not drift_count(out):
            bad.append("a wrong price for %r was not reported" % int_name)

    # A retired SKU offered for sale. The rule distinguishes two cases, so
    # both are exercised: a retired SKU whose name is unique is flagged on
    # buy-intent language alone, while one that shares a name with a live
    # sibling needs something specific to the retired configuration, its own
    # price or variant, before buy-intent counts. Asserting only the first
    # would leave the harder branch untested.
    live_names = {c["name"].strip().lower() for c in A.load_catalog()}
    unique = next((r for r in retired
                   if not r["sku"].startswith("MPL-")
                   and r["name"].strip().lower() not in live_names), None)
    shared = next((r for r in retired
                   if not r["sku"].startswith("MPL-")
                   and r["name"].strip().lower() in live_names
                   and r.get("price")), None)

    if unique:
        out = run('<p>Buy the %s now. Add to cart.</p>' % unique["name"])
        if unique["sku"] not in out:
            bad.append("a retired SKU with a unique name (%s) offered for sale "
                       "was not reported" % unique["sku"])
    if shared:
        out = run('<p>Buy the %s, %s, for $%s. Add to cart.</p>'
                  % (shared["name"], shared.get("variant", ""), shared["price"]))
        if shared["sku"] not in out:
            bad.append("a retired SKU sharing a name with a live one (%s), sold "
                       "at its own retired price, was not reported"
                       % shared["sku"])

    # A buy link that is not in the catalogue at all.
    out = run('<a href="https://buy.stripe.com/notARealSlug0000">Buy</a>')
    if "not in data.js" not in out:
        bad.append("a buy.stripe.com link absent from data.js was not reported")

    # shop.html's own prerendered snapshot: a wrong price inside it must be
    # caught even though check_price_drift's narrow window cannot reach a
    # shop card's price past the blurb, chip and fulfil text between the
    # name and it. Built positionally, the same way prerender_shop.py's own
    # real output is: one <article> per catalogue entry, in catalogue order.
    catalog = A.load_catalog()

    def prerendered(cards: list[str]) -> str:
        return (A.PRERENDER_START + "\n" + "\n".join(cards) + "\n" + A.PRERENDER_END)

    def card(sku: dict, price_text: str) -> str:
        return ('<article class="product"><span data-sku="%s"></span>'
                '<span class="price">%s</span></article>'
                % (sku["sku"], price_text))

    def price_text_for(price):
        if price is None:
            return "Quote"
        if price == 0:
            return "Free"
        return "$%g" % price

    good_cards = [card(c, price_text_for(c.get("price"))) for c in catalog]

    out = run(prerendered(good_cards))
    if "prerendered card shows" in out or "prerendered shop snapshot" in out:
        bad.append("a prerendered snapshot matching the catalogue was reported as drift")

    priced = next(c for c in catalog if c.get("price"))
    bad_cards = [card(c, "$99999" if c is priced else price_text_for(c.get("price")))
                 for c in catalog]
    out = run(prerendered(bad_cards))
    if priced["sku"] not in out or "prerendered card shows" not in out:
        bad.append("a wrong price in the prerendered shop snapshot (%s) was not "
                    "reported" % priced["sku"])

    short_cards = good_cards[:-1]
    out = run(prerendered(short_cards))
    if "prerendered shop snapshot has" not in out:
        bad.append("a prerendered snapshot short of the catalogue's own card "
                    "count was not reported")

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  drift compares money not leading digits, correct prices "
              "pass, wrong ones are caught, unknown buy links are caught")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
