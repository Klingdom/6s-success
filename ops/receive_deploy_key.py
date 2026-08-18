#!/usr/bin/env python3
"""
Take a public key out of the mailbox and put it into GitHub.

The VPS is reached through a browser terminal that text cannot easily be copied
out of, so the key it generated was stranded there. Rather than fight the
terminal, the VPS mails the key to support@6s-success.com, which we control, and
this reads it out and installs it as a read only deploy key using the gh CLI.

Nothing sensitive moves. A public key is safe in mail, safe in a repository, and
safe in a chat; only the private half on the VPS can use it.

Read only is deliberate. The VPS needs to pull this repository, never to write
to it, and a key that cannot push cannot be used to tamper with what deploys.

Run:  python ops/receive_deploy_key.py --check    show what is in the mailbox
      python ops/receive_deploy_key.py --install  add it to GitHub
"""
import email
import imaplib
import os
import re
import ssl
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")
REPO = "Klingdom/6s-success"
KEY_RE = re.compile(r"(ssh-(?:ed25519|rsa)|ecdsa-sha2-nistp\d+)\s+[A-Za-z0-9+/=]{40,}(?:\s+\S+)?")


def creds():
    env = {}
    if os.path.exists(SECRETS):
        with open(SECRETS, encoding="utf-8") as fh:
            env = dict(re.findall(r"^([A-Z_]+)=(.*)$", fh.read(), re.M))
    for k in ("IMAP_HOST", "IMAP_PORT", "IMAP_USER", "IMAP_PASS"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    if not env.get("IMAP_PASS"):
        raise SystemExit("No IMAP credentials in .env.secrets or the environment.")
    return env


def body_text(msg):
    """Flatten a message to searchable text, whatever parts it arrived in."""
    out = []
    for part in msg.walk():
        if part.get_content_type() in ("text/plain", "text/html"):
            payload = part.get_payload(decode=True) or b""
            text = payload.decode(part.get_content_charset() or "utf-8", "replace")
            out.append(re.sub(r"<[^>]+>", " ", text))
    return "\n".join(out)


def harvest():
    """Return [(subject, from, key)] for every public key found in the inbox."""
    env = creds()
    M = imaplib.IMAP4_SSL(env["IMAP_HOST"], int(env["IMAP_PORT"]),
                          ssl_context=ssl.create_default_context())
    M.login(env["IMAP_USER"], env["IMAP_PASS"])
    M.select("INBOX")
    _, nums = M.search(None, "ALL")
    found = []
    for num in nums[0].split():
        _, data = M.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        for m in KEY_RE.finditer(body_text(msg)):
            key = " ".join(m.group(0).split())
            found.append((msg.get("Subject", ""), msg.get("From", ""), key))
    M.logout()
    # de-duplicate on the key material itself, keeping the first sighting
    seen, unique = set(), []
    for subj, frm, key in found:
        material = key.split()[1]
        if material not in seen:
            seen.add(material)
            unique.append((subj, frm, key))
    return unique


def existing():
    out = subprocess.run(["gh", "api", f"repos/{REPO}/keys", "--jq",
                          ".[] | .key"], capture_output=True, text=True)
    return {l.split()[1] for l in out.stdout.splitlines() if len(l.split()) > 1}


def main(mode):
    keys = harvest()
    if not keys:
        print("No public key found in the support@ inbox.")
        print("Have the VPS session send one, then run this again:")
        print('  cat ~/.ssh/id_ed25519.pub | mail -s "VPS deploy key" support@6s-success.com')
        return 1

    have = existing()
    print(f"Found {len(keys)} public key(s) in the mailbox:\n")
    for subj, frm, key in keys:
        kind, material = key.split()[0], key.split()[1]
        label = key.split()[2] if len(key.split()) > 2 else "(no comment)"
        state = "already on the repo" if material in have else "not yet installed"
        print(f"  {kind}  ...{material[-12:]}  {label}")
        print(f"      from    {frm}")
        print(f"      subject {subj}")
        print(f"      status  {state}\n")

    if mode != "--install":
        print("Run with --install to add the missing ones as read only deploy keys.")
        return 0

    added = 0
    for subj, frm, key in keys:
        if key.split()[1] in have:
            continue
        title = (key.split()[2] if len(key.split()) > 2 else "vps")[:60]
        # read_only is not optional here. The VPS pulls; it never pushes.
        proc = subprocess.run(
            ["gh", "api", f"repos/{REPO}/keys", "-X", "POST",
             "-f", f"title=VPS: {title}", "-f", f"key={key}", "-F", "read_only=true"],
            capture_output=True, text=True)
        if proc.returncode == 0:
            print(f"  installed read only: {title}")
            added += 1
        else:
            print(f"  FAILED {title}: {proc.stderr.strip()[:160]}")
    print(f"\n{added} key(s) installed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "--check"))
