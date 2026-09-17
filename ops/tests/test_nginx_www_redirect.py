#!/usr/bin/env python3
"""
Prove site/nginx/default.conf still collapses duplicate URLs with 301s.

Added 2026-09-17. Until then every page answered 200 at up to four addresses:
www and apex, and for zones, rooms and articles both <path> and <path>.html.
The proxy log showed Googlebot fetching all 115 zone URLs in both forms on 23
to 27 August, and spending 29 of 143 fetches on www between 10 and 17 Sept.

Two rules are checked, by shape rather than comment text:

1. www -> apex. Host test matches www case-insensitively, the target is the
   hardcoded https apex (TLS terminates at the proxy, so $scheme inside the
   container is always http and would add a hop), and $request_uri is kept.

2. <section>/<page>.html -> <section>/<page> for zones|rooms|articles only.
   It must keep EXCLUDING index.html: /zones/ resolves internally to
   /zones/index.html through try_files, the internal redirect is matched
   against regex locations again, and without the exclusion /zones/ becomes
   a 301 to itself. That loop was caught in a test container before
   shipping. Top-level pages canonicalize WITH .html and must never match.

Run:  python ops/tests/test_nginx_www_redirect.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONF = os.path.join(ROOT, "site", "nginx", "default.conf")

WWW = re.compile(
    r"if\s*\(\s*\$host\s*~\*\s*\^www\\[.]\s*\)\s*\{\s*"
    r"return\s+301\s+https://6s-success\.com\$request_uri\s*;\s*\}"
)
HTML_RULE = re.compile(
    r"location\s*~\s*(\S+)\s*\{\s*return\s+301\s+"
    r"https://6s-success\.com/\$1/\$2\$is_args\$args\s*;\s*\}"
)

MUST = ["/zones/pantry-the-dry-goods-shelves.html", "/rooms/kitchen.html",
        "/articles/some-article.html"]
NEVER = ["/zones/index.html", "/articles/index.html", "/quest.html",
         "/shop.html", "/index.html", "/deck/entryway-print-and-play.html",
         "/downloads/6S-Standards-Pack.html",
         "/zones/pantry-the-dry-goods-shelves", "/zones/a/b.html"]


def strip_comments(text):
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def has_www(text):
    return bool(WWW.search(strip_comments(text)))


def html_rule_problems(text):
    m = HTML_RULE.search(strip_comments(text))
    if not m:
        return ["no .html -> extensionless 301 rule"]
    try:
        loc = re.compile(m.group(1))
    except re.error as e:
        return ["rule regex does not compile: %s" % e]
    out = ["rule does not redirect " + u for u in MUST if not loc.search(u)]
    out += ["rule would redirect " + u for u in NEVER if loc.search(u)]
    return out


def main():
    failures = []
    with open(CONF, encoding="utf-8") as f:
        real = f.read()
    if not has_www(real):
        failures.append("real default.conf has no www -> apex 301")
    failures += ["real default.conf: " + p for p in html_rule_problems(real)]

    # Negative controls: the checks must reject the defect shapes.
    good = r"if ($host ~* ^www\.) {" "\n" \
           "    return 301 https://6s-success.com$request_uri;\n}\n"
    if not has_www(good):
        failures.append("www matcher rejects the correct block")
    for name, text in {
        "removed": "server { listen 80; }\n",
        "commented out": "\n".join("# " + l for l in good.splitlines()),
        "302 not 301": good.replace("301", "302"),
        "scheme variable": good.replace("https://6s-success.com", "$scheme://6s-success.com"),
        "path dropped": good.replace("$request_uri", "/"),
    }.items():
        if has_www(text):
            failures.append("www matcher accepted defect shape: " + name)

    rule = (r"location ~ ^/(zones|rooms|articles)/(?!index\.html$)([^/]+)\.html$ {"
            "\n    return 301 https://6s-success.com/$1/$2$is_args$args;\n}\n")
    if html_rule_problems(rule):
        failures.append("html checker rejects the correct rule: %s" % html_rule_problems(rule))
    for name, text in {
        "no index exclusion (redirect loop)": rule.replace(r"(?!index\.html$)", ""),
        "unscoped (would hit quest.html)": rule.replace(r"^/(zones|rooms|articles)/", r"^/(.*)/?"),
        "removed": "server { listen 80; }\n",
    }.items():
        if not html_rule_problems(text):
            failures.append("html checker accepted defect shape: " + name)

    for f in failures:
        print("FAIL:", f)
    print("ok" if not failures else "%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
