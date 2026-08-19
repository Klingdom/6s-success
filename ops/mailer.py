#!/usr/bin/env python3
"""
Send mail as support@6s-success.com.

WHERE THIS MAY AND MAY NOT BE USED
----------------------------------
The website is a static bundle served by nginx. Everything under site/ is handed
verbatim to anybody who asks for it. An SMTP password placed there, in HTML, in
JavaScript, or in a JSON file, is published to the world the moment the site
deploys. So:

  ALLOWED   ops scripts on a trusted machine, and server side code running on
            the VPS that reads the credential from the environment.
  NEVER     anything under site/. There is no exception and no clever way to do
            it. A static page cannot hold a secret.

The credential lives in .env.secrets, which is gitignored. This module refuses to
run without it rather than falling back to anything weaker, and never prints it.

Usage:
    from ops.mailer import send, load
    send(to="support@6s-success.com", subject="...", text="...", html="...")

    python ops/mailer.py --check          authenticate only, send nothing
    python ops/mailer.py --test ADDRESS   send one plain test message
"""
import os
import re
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")
FROM_NAME = "6S Success"


def load():
    """Read credentials from the environment first, then .env.secrets.

    Environment wins so the VPS and any cloud runner can inject them without a
    file ever existing there.
    """
    env = {}
    if os.path.exists(SECRETS):
        with open(SECRETS, encoding="utf-8") as fh:
            env = dict(re.findall(r"^([A-Z_]+)=(.*)$", fh.read(), re.M))
    for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    missing = [k for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS")
               if not env.get(k)]
    if missing:
        raise SystemExit(
            "No mail credentials. Missing: " + ", ".join(missing) + ".\n"
            "Set them in the environment, or create .env.secrets (gitignored).")
    return env


def connect(env, timeout=30):
    """Open an authenticated connection. Port 465 is implicit TLS; anything else
    is STARTTLS. Certificates are verified in both cases."""
    ctx = ssl.create_default_context()
    port = int(env["SMTP_PORT"])
    if port == 465:
        server = smtplib.SMTP_SSL(env["SMTP_HOST"], port, context=ctx, timeout=timeout)
    else:
        server = smtplib.SMTP(env["SMTP_HOST"], port, timeout=timeout)
        server.ehlo()
        server.starttls(context=ctx)
        server.ehlo()
    server.login(env["SMTP_USER"], env["SMTP_PASS"])
    return server


def send(to, subject, text, html=None, reply_to=None, env=None, attachments=None):
    """Send one message. Returns the Message-ID so a send can be traced later."""
    env = env or load()
    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{env['SMTP_USER']}>"
    msg["To"] = to if isinstance(to, str) else ", ".join(to)
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="6s-success.com")
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")
    # attachments: [(filename, bytes, maintype, subtype)]. Added after the body
    # parts so the message stays multipart/alternative inside multipart/mixed,
    # which is what mail clients expect and what keeps the plain text readable
    # on a phone.
    for name, data, maintype, subtype in (attachments or []):
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=name)
    with connect(env) as server:
        server.send_message(msg)
    return msg["Message-ID"]


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    e = load()
    if mode == "--check":
        with connect(e):
            pass
        print(f"authenticated as {e['SMTP_USER']} on "
              f"{e['SMTP_HOST']}:{e['SMTP_PORT']}")
        sys.exit(0)
    if mode == "--test":
        if len(sys.argv) < 3:
            sys.exit("usage: python ops/mailer.py --test ADDRESS")
        mid = send(sys.argv[2], "6S Success mail check",
                   "Sending from support@6s-success.com works.\n\n"
                   "Sent by ops/mailer.py to verify the mailbox, nothing else.\n")
        print("sent", mid)
        sys.exit(0)
    sys.exit(f"unknown mode {mode}")
