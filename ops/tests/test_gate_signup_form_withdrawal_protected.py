#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_signup_form_withdrawal_protected() catches a
silently restored, broken signup form, and prove ops/wire_signup.py itself
now refuses to restore one without --force.

Found 2026-09-18: ops/wire_signup.py's own docstring said nothing about the
fact that all six pages it touches carry a deliberate 2026-08-23 withdrawal
comment (the shared Listmonk SMTP identity 553s every 6S opt-in email, so the
form 500s on any visitor who submits it, issue #15, still open). A plain run
of the script, tried during a routine cold-read of this low-mention file,
silently overwrote that comment on all six pages with the real, broken form.
Caught only because the working tree was diffed before committing. Fixed
main() to refuse a page whose existing block says "withdrawn" unless --force
is passed; this file proves both the refusal and the gate that protects it.

Run:  python ops/tests/test_gate_signup_form_withdrawal_protected.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import wire_signup                                             # noqa: E402

WITHDRAWN_PAGE = (
    '<!doctype html><html><body>\n'
    '<!-- SIGNUP:BEGIN -->\n'
    '<!-- Signup withdrawn 2026-08-23: see issue #15. -->\n'
    '<!-- SIGNUP:END -->\n'
    '<footer class="site-footer"></footer>\n'
    '</body></html>'
)

LIVE_PAGE = (
    '<!doctype html><html><body>\n'
    '<!-- SIGNUP:BEGIN -->\n'
    '<section id="signup">a live form here</section>\n'
    '<!-- SIGNUP:END -->\n'
    '<footer class="site-footer"></footer>\n'
    '</body></html>'
)


def _run_gate(pages: dict) -> list:
    tmp = tempfile.mkdtemp()
    try:
        ops_dir = os.path.join(tmp, "ops")
        site_dir = os.path.join(tmp, "site")
        os.makedirs(ops_dir, exist_ok=True)
        os.makedirs(site_dir, exist_ok=True)
        shutil.copy(os.path.join(ROOT, "ops", "wire_signup.py"),
                    os.path.join(ops_dir, "wire_signup.py"))
        for rel, body in pages.items():
            p = os.path.join(site_dir, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            io.open(p, "w", encoding="utf-8").write(body)

        old_root, old_site = preflight.ROOT, preflight.SITE
        preflight.ROOT, preflight.SITE = tmp, site_dir
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_signup_form_withdrawal_protected()
            return list(preflight.FAIL)
        finally:
            preflight.ROOT, preflight.SITE = old_root, old_site
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A page still honestly withdrawn: no failure.
    r = _run_gate({"quest.html": WITHDRAWN_PAGE})
    if r:
        fails.append("withdrawn page wrongly flagged: %r" % (r,))

    # 2. The real, committed defect shape: a page silently restored to the
    # live form. Must be caught by name.
    r = _run_gate({"quest.html": LIVE_PAGE})
    if not r or not any("quest.html" in m for _, m in r):
        fails.append("restored page not caught: %r" % (r,))

    # 3. No site pages at all (none of the six exist here): nothing to
    # check, no false failure from the page scan, but the source guard
    # must still be intact, so this should pass.
    r = _run_gate({})
    if r:
        fails.append("no pages present wrongly flagged: %r" % (r,))

    # 4. The refusal guard itself removed from the source: caught even
    # with every page honestly withdrawn.
    tmp = tempfile.mkdtemp()
    try:
        ops_dir = os.path.join(tmp, "ops")
        site_dir = os.path.join(tmp, "site")
        os.makedirs(ops_dir, exist_ok=True)
        os.makedirs(site_dir, exist_ok=True)
        src = io.open(os.path.join(ROOT, "ops", "wire_signup.py"),
                     encoding="utf-8").read()
        stripped = src.replace('"withdrawn" in existing.lower()', "False")
        io.open(os.path.join(ops_dir, "wire_signup.py"), "w",
               encoding="utf-8").write(stripped)
        io.open(os.path.join(site_dir, "quest.html"), "w",
               encoding="utf-8").write(WITHDRAWN_PAGE)

        old_root, old_site = preflight.ROOT, preflight.SITE
        preflight.ROOT, preflight.SITE = tmp, site_dir
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_signup_form_withdrawal_protected()
            if not preflight.FAIL:
                fails.append("stripped guard not caught")
        finally:
            preflight.ROOT, preflight.SITE = old_root, old_site
    finally:
        shutil.rmtree(tmp)

    # 5. The real, committed pages: clean today.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_signup_form_withdrawal_protected()
    if preflight.FAIL:
        fails.append("the real committed pages failed: %r" % (preflight.FAIL,))

    # 6. wire_signup.py's own main(): given a withdrawn page and no
    # --force, it must not touch the file on disk.
    tmp = tempfile.mkdtemp()
    try:
        site_dir = os.path.join(tmp, "site")
        os.makedirs(os.path.join(site_dir, "assets", "css"), exist_ok=True)
        target = os.path.join(site_dir, "quest.html")
        io.open(target, "w", encoding="utf-8").write(WITHDRAWN_PAGE)
        io.open(os.path.join(site_dir, "assets", "css", "site.css"),
               "w", encoding="utf-8").write(".signup{}\n")
        before = io.open(target, encoding="utf-8").read()

        old_site, old_pages, old_argv = wire_signup.SITE, wire_signup.PAGES, sys.argv
        wire_signup.SITE = site_dir
        wire_signup.PAGES = ["quest.html"]
        sys.argv = ["wire_signup.py"]
        try:
            wire_signup.main()
        except SystemExit:
            pass
        finally:
            wire_signup.SITE, wire_signup.PAGES, sys.argv = old_site, old_pages, old_argv

        after = io.open(target, encoding="utf-8").read()
        if after != before:
            fails.append("main() overwrote a withdrawn page with no --force")
    finally:
        shutil.rmtree(tmp)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_signup_form_withdrawal_protected + wire_signup.py refusal, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
