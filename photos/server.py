#!/usr/bin/env python3
"""HTTP API for before/after photos and their analysis. Standard library only.

Meant to sit behind the site's nginx at https://6s-success.com/api/photos/ ,
which strips that prefix, so routes here start at /v1. Usable the same way by
the web app, a phone app, or an AI agent; the contract is /v1/openapi.json.

    POST   /v1/sessions                          -> {session_id, token}  (token shown once)
    PUT    /v1/sessions/{sid}/photos?zone=&kind= -> store one image (raw bytes in the body)
    GET    /v1/sessions/{sid}/photos             -> list
    GET    /v1/sessions/{sid}/photos/{pid}       -> the JPEG
    DELETE /v1/sessions/{sid}/photos/{pid}
    DELETE /v1/sessions/{sid}                    -> everything, immediately
    POST   /v1/sessions/{sid}/analyze            -> {"photo_id": .., "compare_to": ..?}
    GET    /v1/zones                             -> public zone list
    GET    /v1/zones/{zone}/method               -> public method for one zone
    GET    /v1/openapi.json, /v1/health

Auth on every /sessions/{sid}/ route: "Authorization: Bearer <token>".

    python photos/server.py --port 8975 --data ./photo-data
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A                                        # noqa: E402
import methodology as M                                    # noqa: E402
from store import KINDS, MAX_BYTES, Store, StoreError     # noqa: E402

ANALYSES_PER_DAY = int(os.environ.get("PHOTOS_ANALYSES_PER_DAY", "20"))
SESSIONS_PER_IP_HOUR = int(os.environ.get("PHOTOS_SESSIONS_PER_IP_HOUR", "10"))
ALLOW_ORIGIN = os.environ.get("PHOTOS_ALLOW_ORIGIN", "https://6s-success.com")

_rate = {}
_rate_lock = threading.Lock()


def _allow_session(ip):
    now = time.time()
    with _rate_lock:
        hits = [t for t in _rate.get(ip, []) if now - t < 3600]
        if len(hits) >= SESSIONS_PER_IP_HOUR:
            _rate[ip] = hits
            return False
        hits.append(now)
        _rate[ip] = hits
        return True


def openapi():
    sess = {"name": "sid", "in": "path", "required": True, "schema": {"type": "string"}}
    auth = [{"bearer": []}]
    return {
        "openapi": "3.1.0",
        "info": {"title": "6S Success photos", "version": "1.0",
                 "description": "Private before/after photos of one micro zone, and an analysis "
                 "that comments on next steps using that zone's published 6S method. Photos are "
                 "re-encoded (all metadata, including GPS, is removed), never public, deletable, "
                 "and purged after 90 days untouched. If no vision provider is configured, "
                 "analysis returns the zone's method with image_analyzed=false."},
        "servers": [{"url": "https://6s-success.com/api/photos"}],
        "components": {"securitySchemes": {"bearer": {"type": "http", "scheme": "bearer"}}},
        "paths": {
            "/v1/zones": {"get": {"summary": "List the 114 micro zone ids (page slugs)"}},
            "/v1/zones/{zone}/method": {"get": {"summary": "The published method for one zone",
                "parameters": [{"name": "zone", "in": "path", "required": True, "schema": {"type": "string"}}]}},
            "/v1/sessions": {"post": {"summary": "Create a private session; returns session_id and a token shown once"}},
            "/v1/sessions/{sid}": {"delete": {"summary": "Delete the session and every photo in it", "parameters": [sess], "security": auth}},
            "/v1/sessions/{sid}/photos": {
                "get": {"summary": "List photos", "parameters": [sess], "security": auth},
                "put": {"summary": "Store one photo; body is the raw image bytes (JPEG/PNG/WebP), max %d MB" % (MAX_BYTES // 1048576),
                        "parameters": [sess,
                            {"name": "zone", "in": "query", "required": True, "schema": {"type": "string"}},
                            {"name": "kind", "in": "query", "required": True, "schema": {"enum": list(KINDS)}},
                            {"name": "note", "in": "query", "required": False, "schema": {"type": "string"}}],
                        "requestBody": {"content": {"image/*": {}}}, "security": auth}},
            "/v1/sessions/{sid}/photos/{pid}": {
                "get": {"summary": "The stored JPEG", "parameters": [sess, {"name": "pid", "in": "path", "required": True, "schema": {"type": "string"}}], "security": auth},
                "delete": {"summary": "Delete one photo", "parameters": [sess, {"name": "pid", "in": "path", "required": True, "schema": {"type": "string"}}], "security": auth}},
            "/v1/sessions/{sid}/analyze": {"post": {
                "summary": "Analyze a photo against its zone's method. Body: {photo_id, compare_to?}. "
                           "A before photo gets next steps; an after photo is checked against "
                           "done-looks-like; compare_to (a before photo id) compares the two.",
                "parameters": [sess], "security": auth}},
        },
    }


class Handler(BaseHTTPRequestHandler):
    store = None
    analyze_call = None          # test hook: replaces the vision provider
    server_version = "6s-photos/1"
    sys_version = ""

    def log_message(self, fmt, *args):     # no paths, no tokens, no IPs in logs
        pass

    # helpers ---------------------------------------------------------
    def _send(self, status, obj=None, body=None, ctype="application/json"):
        data = body if body is not None else json.dumps(obj or {}).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Access-Control-Allow-Origin", ALLOW_ORIGIN)
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(data)

    def _err(self, status, msg):
        self._send(status, {"error": msg})

    def _token(self):
        h = self.headers.get("Authorization", "")
        return h[7:].strip() if h.lower().startswith("bearer ") else ""

    def _body(self, limit):
        n = int(self.headers.get("Content-Length") or 0)
        if n > limit:
            raise StoreError(413, "body too large")
        return self.rfile.read(n) if n else b""

    def _ip(self):
        """The visitor's address, for rate limiting only (never logged or stored).

        Two proxies sit in front: Nginx Proxy Manager, then the site's own
        nginx, which forwards $proxy_add_x_forwarded_for. So the list ends
        "..., <visitor as seen by NPM>, <NPM>". The second-to-last entry is
        the one NPM wrote; anything before it is client-supplied and spoofable.
        """
        xff = [x.strip() for x in (self.headers.get("X-Forwarded-For") or "").split(",") if x.strip()]
        if len(xff) >= 2:
            return xff[-2]
        return self.headers.get("X-Real-IP") or self.client_address[0]

    def _route(self, method):
        u = urlparse(self.path)
        parts = [p for p in u.path.split("/") if p]
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            return self._dispatch(method, parts, q)
        except StoreError as e:
            return self._err(e.status, e.message)
        except A.AnalysisError as e:
            return self._err(502 if "provider" in str(e) else 400, str(e))
        except Exception:                                  # noqa: BLE001
            return self._err(500, "internal error")

    def _dispatch(self, method, p, q):
        S = self.store
        if p[:1] != ["v1"]:
            return self._err(404, "not found")
        p = p[1:]
        if method == "GET" and p == ["health"]:
            return self._send(200, {"ok": True, "zones": len(M.zone_slugs()),
                                    "vision": bool(os.environ.get("ANTHROPIC_API_KEY"))})
        if method == "GET" and p == ["openapi.json"]:
            return self._send(200, openapi())
        if method == "GET" and p == ["zones"]:
            return self._send(200, {"zones": M.zone_slugs()})
        if method == "GET" and len(p) == 3 and p[0] == "zones" and p[2] == "method":
            m = M.method(p[1])
            return self._send(200, m) if m else self._err(404, "unknown zone")
        if method == "POST" and p == ["sessions"]:
            if not _allow_session(self._ip()):
                return self._err(429, "too many sessions from this address; try later")
            sid, tok = S.create_session()
            return self._send(201, {"session_id": sid, "token": tok,
                                    "note": "Keep the token. It is shown once and cannot be recovered."})
        if len(p) >= 2 and p[0] == "sessions":
            sid, tok, rest = p[1], self._token(), p[2:]
            if method == "DELETE" and rest == []:
                S.delete_session(sid, tok)
                return self._send(200, {"deleted": True})
            if rest == ["photos"] and method == "GET":
                return self._send(200, {"photos": S.list_photos(sid, tok)})
            if rest == ["photos"] and method in ("PUT", "POST"):
                zone, kind = q.get("zone", ""), q.get("kind", "")
                if M.method(zone) is None:
                    return self._err(400, "zone must be one of GET /v1/zones")
                S.open(sid, tok)                     # authorise before reading a big body
                return self._send(201, S.add_photo(sid, tok, self._body(MAX_BYTES), zone, kind,
                                                   q.get("note", "")))
            if len(rest) == 2 and rest[0] == "photos":
                if method == "GET":
                    data, _ = S.photo_bytes(sid, tok, rest[1])
                    return self._send(200, body=data, ctype="image/jpeg")
                if method == "DELETE":
                    S.delete_photo(sid, tok, rest[1])
                    return self._send(200, {"deleted": True})
            if rest == ["analyze"] and method == "POST":
                S.open(sid, tok)
                try:
                    req = json.loads(self._body(10000) or b"{}")
                except ValueError:
                    return self._err(400, "body must be JSON")
                if S.analyses_today(sid, tok) >= ANALYSES_PER_DAY:
                    return self._err(429, "daily analysis limit reached for this session")
                img, meta = S.photo_bytes(sid, tok, str(req.get("photo_id", "")))
                images, mode = [img], ("after" if meta["kind"] == "after" else "before")
                if req.get("compare_to"):
                    before, bmeta = S.photo_bytes(sid, tok, str(req["compare_to"]))
                    if bmeta["zone"] != meta["zone"]:
                        return self._err(400, "both photos must be of the same zone")
                    images, mode = [before, img], "compare"
                res = A.analyze(meta["zone"], images, mode, call=self.analyze_call)
                res["photo_id"] = meta["id"]
                if req.get("compare_to"):
                    res["compare_to"] = req["compare_to"]
                return self._send(200, S.save_analysis(sid, tok, res))
        return self._err(404, "not found")

    def do_GET(self): self._route("GET")
    def do_POST(self): self._route("POST")
    def do_PUT(self): self._route("PUT")
    def do_DELETE(self): self._route("DELETE")
    def do_OPTIONS(self): self._send(204, body=b"")


def make_server(data_dir, port=8975, host="127.0.0.1"):
    Handler.store = Store(data_dir)
    return ThreadingHTTPServer((host, port), Handler)


def main():
    a = sys.argv
    port = int(a[a.index("--port") + 1]) if "--port" in a else 8975
    data = a[a.index("--data") + 1] if "--data" in a else os.environ.get("PHOTOS_DATA", "/data")
    host = a[a.index("--host") + 1] if "--host" in a else os.environ.get("PHOTOS_HOST", "127.0.0.1")
    srv = make_server(data, port, host)
    gone = Handler.store.purge()
    print("6s-photos on %s:%d, data %s, purged %d expired session(s), vision %s"
          % (host, port, data, gone, "on" if os.environ.get("ANTHROPIC_API_KEY") else "OFF"))
    srv.serve_forever()


if __name__ == "__main__":
    main()
