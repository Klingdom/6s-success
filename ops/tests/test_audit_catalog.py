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
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
OPS = os.path.join(ROOT, "ops")
TOOL = os.path.join(OPS, "audit_catalog.py")
FIXTURE = os.path.join(SITE, "_audit_catalog_fixture.html")

sys.path.insert(0, OPS)
import audit_catalog as A                                     # noqa: E402

SHELL = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
         '<title>Temporary fixture</title></head><body><main>%s</main></body></html>')


def run(inner: str) -> str:
    io.open(FIXTURE, "w", encoding="utf-8", newline="").write(SHELL % inner)
    try:
        r = subprocess.run([sys.executable, TOOL], cwd=ROOT, capture_output=True,
                           text=True, timeout=600,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        return (r.stdout or "") + (r.stderr or "")
    finally:
        if os.path.exists(FIXTURE):
            os.remove(FIXTURE)


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
        out = run("<p>%s is $%d today.</p>" % (int_name, int(int_price) - 10))
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

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  drift compares money not leading digits, correct prices "
              "pass, wrong ones are caught, unknown buy links are caught")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
