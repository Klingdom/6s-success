# Installing the deploy key. Once, about two minutes.

This is the last thing standing between a commit and the live site. After it,
`python ops/deploy.py` deploys without anybody clicking anything, and the
Hostinger Redeploy button is never needed again.

**The key to install** (this is a *public* key, safe to paste anywhere, safe to
email, safe to put in a screenshot):

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGobKYWVBP1eg0rfeVfSqQn3yKL5jqzbNS0bq8CKLHp5 6s-success-vps-deploy-key
```

Its fingerprint, so you can confirm the right key landed:

```
SHA256:m6GB/nqwRWg4CZcQAUOZlVDjypFIJINoQw+J4m6zaQQ
```

The matching private key stays on this machine at `~/.ssh/6s_deploy` and is
never sent anywhere.

---

## Route A: Hostinger panel. No password needed.

1. Go to **https://hpanel.hostinger.com/vps** and click **Manage** on
   `srv1369835.hstgr.cloud`.
2. Left sidebar: **Settings → SSH keys**. (It currently says "Add an SSH key to
   your account" because there are none.)
3. Click **+ SSH key**.
4. Paste the key block above into **SSH key content**. Paste the whole line,
   including `ssh-ed25519` at the front and the label at the end.
5. Click **Save**.

That is the entire job. Nothing restarts, nothing goes down.

---

## Route B: The terminal, if you would rather not use the panel

Needs the VPS root password. In a terminal on your machine:

```bash
ssh root@187.77.25.50
```

Then, once you are logged in, paste this whole block and press Enter:

```bash
mkdir -p ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGobKYWVBP1eg0rfeVfSqQn3yKL5jqzbNS0bq8CKLHp5 6s-success-vps-deploy-key' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
exit
```

---

## Then tell me, and I will verify it myself

I check with `python ops/deploy.py --check`, which either prints the access it
found or says plainly that it is still blocked. You do not need to test
anything.

If you want to confirm it yourself first, this prints the server's hostname and
changes nothing:

```bash
ssh -i ~/.ssh/6s_deploy root@187.77.25.50 hostname
```

## What changes the moment it works

`python ops/deploy.py` pulls the published image, recreates the container, and
then reads the live catalogue to check the deploy actually changed production.
It refuses to report success it has not observed, so a deploy that silently
does nothing is reported as a failure rather than a win.

## If it does not take

- **"Permission denied (publickey)"** still, after Route A: Hostinger sometimes
  applies account keys only to newly built servers. Use Route B, which writes
  directly to the running machine.
- **Pasted key rejected as invalid:** the whole thing must be one line. If your
  editor wrapped it, rejoin it.
- **Wrong key installed:** compare against the fingerprint above with
  `ssh-keygen -lf ~/.ssh/6s_deploy.pub`.

## Why this is safe

An `ed25519` public key lets a holder of the matching private key log in. It
grants nothing to anybody else, it cannot be reversed into the private key, and
it can be revoked at any time by deleting the line from
`~/.ssh/authorized_keys` or removing it in hPanel.
