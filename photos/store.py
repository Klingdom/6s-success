"""Private storage for before and after photos.

Privacy rules, written as code rather than as a promise (CLAUDE.md section 47,
AUTONOMY.md section 27: household photos are private by default):

- No accounts. A session is a capability: a random id plus a random token,
  returned once at creation. Only the token's SHA-256 is stored, so a copy of
  the disk is not a copy of anybody's access.
- Every image is decoded and RE-ENCODED. That drops EXIF, including GPS, and
  anything else riding in the file. A file that does not decode as an image
  is refused, so nothing but pixels is ever stored.
- Nothing is public. There is no listing across sessions and no URL that works
  without the token. A wrong token and a missing session give the same answer.
- The owner of a session can delete a photo or the whole session, and
  sessions untouched for RETENTION_DAYS are purged.
"""
from __future__ import annotations

import hashlib
import hmac
import io
import json
import os
import re
import secrets
import shutil
import threading
import time
import warnings

from PIL import Image, ImageOps

# Our own MAX_PIXELS check below runs first and raises before Pillow's internal
# decompression-bomb check would even warn; suppress the now-redundant warning
# rather than let a container log fill up with it on every oversized attempt.
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)

MAX_BYTES = 12 * 1024 * 1024
MAX_SIDE = 2048
MAX_PIXELS = 25_000_000   # checked before decode; see reencode()'s own comment
RETENTION_DAYS = int(os.environ.get("PHOTOS_RETENTION_DAYS", "90"))
MAX_PHOTOS_PER_SESSION = 200
MAX_SESSION_BYTES = 150 * 1024 * 1024   # well above one household's real use, well below the unbounded worst case
MIN_FREE_BYTES = 1 * 1024 * 1024 * 1024  # refuse new uploads once the shared disk has less than this free
KINDS = ("before", "after", "progress")
_ID = re.compile(r"^[A-Za-z0-9_-]{16,64}$")

# ThreadingHTTPServer hands every request its own thread with no cap, so
# MAX_PIXELS alone still lets enough concurrent uploads add up past the
# container's 256 MB limit. This bounds how many decodes can run at once,
# independent of how many requests arrive at once.
_decode_slots = threading.Semaphore(2)


class StoreError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def _h(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class Store:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        os.makedirs(self.root, exist_ok=True)
        self._rate_lock = threading.Lock()
        self._rate_path = os.path.join(self.root, "rate.json")
        self._rate = self._load_rate()

    # rate limiting ------------------------------------------------------
    # In-process-only counters silently rearm on every restart (a deploy, a
    # crash, an OOM kill), which is routine on this host, not rare, so the
    # limits below would protect nothing for the first hour after most
    # restarts. Persisting them costs one small JSON file and a lock.
    def _load_rate(self):
        try:
            return json.load(io.open(self._rate_path, encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _save_rate(self):
        tmp = self._rate_path + ".tmp"
        io.open(tmp, "w", encoding="utf-8").write(json.dumps(self._rate))
        os.replace(tmp, self._rate_path)

    def allow(self, bucket, key, limit, window_seconds):
        """True, and records one hit, if `key` has had fewer than `limit`
        hits in `bucket` over the last `window_seconds`. `bucket` keeps
        independent counters (e.g. "sessions" vs "analyze_ip") in one file."""
        now = time.time()
        with self._rate_lock:
            b = self._rate.setdefault(bucket, {})
            hits = [t for t in b.get(key, []) if now - t < window_seconds]
            if len(hits) >= limit:
                b[key] = hits
                return False
            hits.append(now)
            b[key] = hits
            self._save_rate()
            return True

    # sessions ---------------------------------------------------------
    def _dir(self, sid):
        if not _ID.match(sid or ""):
            raise StoreError(404, "not found")
        d = os.path.join(self.root, sid)
        if os.path.dirname(d) != self.root:
            raise StoreError(404, "not found")
        return d

    def create_session(self):
        sid = secrets.token_urlsafe(18)
        token = secrets.token_urlsafe(32)
        d = self._dir(sid)
        os.makedirs(d)
        self._write(d, {"token_sha256": _h(token), "created": time.time(),
                        "touched": time.time(), "photos": {}, "analyses": {}})
        return sid, token

    def _meta_path(self, d):
        return os.path.join(d, "meta.json")

    def _read(self, d):
        try:
            return json.load(io.open(self._meta_path(d), encoding="utf-8"))
        except (OSError, ValueError):
            raise StoreError(404, "not found")

    def _write(self, d, meta):
        tmp = self._meta_path(d) + ".tmp"
        io.open(tmp, "w", encoding="utf-8").write(json.dumps(meta))
        os.replace(tmp, self._meta_path(d))

    def open(self, sid, token):
        """Authorise. Same 404 for unknown session and wrong token."""
        d = self._dir(sid)
        if not os.path.isdir(d):
            raise StoreError(404, "not found")
        meta = self._read(d)
        if not token or not hmac.compare_digest(meta["token_sha256"], _h(token)):
            raise StoreError(404, "not found")
        meta["touched"] = time.time()
        self._write(d, meta)
        return d, meta

    def delete_session(self, sid, token):
        d, _ = self.open(sid, token)
        shutil.rmtree(d)

    # photos -----------------------------------------------------------
    def add_photo(self, sid, token, data, zone, kind, note=""):
        if kind not in KINDS:
            raise StoreError(400, "kind must be one of %s" % ", ".join(KINDS))
        if not data:
            raise StoreError(400, "empty body; send the image bytes")
        if len(data) > MAX_BYTES:
            raise StoreError(413, "image larger than %d MB" % (MAX_BYTES // 1048576))
        free = shutil.disk_usage(self.root).free
        if free < MIN_FREE_BYTES:
            raise StoreError(503, "storage temporarily full; try again later")
        d, meta = self.open(sid, token)
        if len(meta["photos"]) >= MAX_PHOTOS_PER_SESSION:
            raise StoreError(409, "session photo limit reached")
        used = sum(p.get("bytes", 0) for p in meta["photos"].values())
        if used + len(data) > MAX_SESSION_BYTES:
            raise StoreError(409, "session storage limit reached")
        with _decode_slots:
            jpeg, w, h = reencode(data)
        pid = secrets.token_urlsafe(12)
        io.open(os.path.join(d, pid + ".jpg"), "wb").write(jpeg)
        meta["photos"][pid] = {"id": pid, "zone": zone, "kind": kind,
                               "note": (note or "")[:500], "width": w, "height": h,
                               "bytes": len(jpeg), "created": time.time()}
        self._write(d, meta)
        return meta["photos"][pid]

    def list_photos(self, sid, token):
        _, meta = self.open(sid, token)
        return sorted(meta["photos"].values(), key=lambda p: p["created"])

    def photo_bytes(self, sid, token, pid):
        d, meta = self.open(sid, token)
        if pid not in meta["photos"]:
            raise StoreError(404, "not found")
        return io.open(os.path.join(d, pid + ".jpg"), "rb").read(), meta["photos"][pid]

    def delete_photo(self, sid, token, pid):
        d, meta = self.open(sid, token)
        if pid not in meta["photos"]:
            raise StoreError(404, "not found")
        os.remove(os.path.join(d, pid + ".jpg"))
        del meta["photos"][pid]
        self._write(d, meta)

    def save_analysis(self, sid, token, result):
        d, meta = self.open(sid, token)
        aid = secrets.token_urlsafe(9)
        result = dict(result, id=aid, created=time.time())
        meta["analyses"][aid] = result
        self._write(d, meta)
        return result

    def analyses_today(self, sid, token):
        _, meta = self.open(sid, token)
        cut = time.time() - 86400
        return sum(1 for a in meta["analyses"].values() if a.get("created", 0) > cut)

    def purge(self, now=None):
        now = now or time.time()
        gone = 0
        for sid in os.listdir(self.root):
            d = os.path.join(self.root, sid)
            try:
                meta = json.load(io.open(self._meta_path(d), encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if now - meta.get("touched", 0) > RETENTION_DAYS * 86400:
                shutil.rmtree(d, ignore_errors=True)
                gone += 1
        return gone


def reencode(data):
    """Decode, orient, downscale, and write a fresh JPEG with no metadata.

    The size check below runs BEFORE `.load()`, on purpose. `Image.open()`
    only reads the header, so checking `im.size` there is nearly free; a
    compressed image well under MAX_BYTES can still unpack to an enormous
    pixel buffer (a few hundred KB of flat-colour PNG decodes to hundreds of
    MB of RGB), and this container has a 256 MB limit. Pillow's own
    decompression-bomb guard only raises past roughly 2x its default
    threshold (about 179 megapixels) and merely warns below that, which is
    already enough to exceed this container's memory on its own, so MAX_
    PIXELS is a separate, tighter bound, not a duplicate of Pillow's.
    """
    try:
        im = Image.open(io.BytesIO(data))
        w, h = im.size
    except Exception:                                     # noqa: BLE001
        raise StoreError(415, "not a readable image (JPEG, PNG, WebP or HEIC converted to JPEG)")
    if w * h > MAX_PIXELS:
        raise StoreError(413, "image dimensions too large (%dx%d)" % (w, h))
    try:
        im.load()
    except Exception:                                     # noqa: BLE001
        raise StoreError(415, "not a readable image (JPEG, PNG, WebP or HEIC converted to JPEG)")
    im = ImageOps.exif_transpose(im)        # keep the picture upright, then drop the tags
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    im.thumbnail((MAX_SIDE, MAX_SIDE))
    out = io.BytesIO()
    im.save(out, "JPEG", quality=86, optimize=True)   # no exif= argument: nothing carried over
    return out.getvalue(), im.width, im.height
