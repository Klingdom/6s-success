#!/usr/bin/env python3
"""
Prove site/nginx/default.conf still sends www to the apex with a 301.

Added 2026-09-17. Until then www.6s-success.com answered 200 with the whole
site, so every page existed at two hostnames and Googlebot spent 29 of its
143 fetches between 10 and 17 September on the www copy. The fix is one
`if` block; this test exists because a config reflow or a copy of the block
into a new server stanza could drop it silently, and nothing else would
notice: both hostnames would go on answering 200.

Checks the shape that matters, not the comment text:
  - the host test matches www case-insensitively
  - the target is the hardcoded https apex (TLS terminates at the proxy, so
    $scheme inside this container is always http; redirecting to it would
    add a second hop)
  - the request URI is carried over, so deep links keep their path

Run:  python ops/tests/test_nginx_www_redirect.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONF = os.path.join(ROOT, "site", "nginx", "default.conf")

PATTERN = re.compile(
    r"if\s*\(\s*\$host\s*~\*\s*\^www\\\.\s*\)\s*\{\s*"
    r"return\s+301\s+https://6s-success\.com\$request_uri\s*;\s*\}"
)


def has_redirect(text: str) -> bool:
    code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    return bool(PATTERN.search(code))


def main() -> int:
    failures = []
    with open(CONF, encoding="utf-8") as f:
        real = f.read()
    if not has_redirect(real):
        failures.append("real default.conf has no www -> apex 301")

    # Negative controls: the matcher must reject the defect shapes.
    good = (r"if ($host ~* ^www\.) {" "\n"
            "    return 301 https://6s-success.com$request_uri;\n}\n")
    bad = {
        "removed": "server { listen 80; }\n",
        "commented out": "\n".join("# " + l for l in good.splitlines()),
        "302 not 301": good.replace("301", "302"),
        "scheme variable": good.replace("https://6s-success.com", "$scheme://6s-success.com"),
        "path dropped": good.replace("$request_uri", "/"),
    }
    if not has_redirect(good):
        failures.append("matcher rejects the correct block")
    for name, text in bad.items():
        if has_redirect(text):
            failures.append("matcher accepted defect shape: " + name)

    for f in failures:
        print("FAIL:", f)
    print("ok" if not failures else "%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
