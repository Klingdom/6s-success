"""End-to-end tests for the photo service, over real HTTP.
Run: python ops/tests/test_photos_service.py"""
import io, json, os, shutil, sys, tempfile, threading, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "photos"))
os.environ.pop("ANTHROPIC_API_KEY", None)
import server as SV
import store as ST
from PIL import Image

ZONE = "entryway-the-landing-spot"
OTHER = "kitchen-the-cooking-zone"
tmp = tempfile.mkdtemp()
srv = SV.make_server(tmp, 0)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:%d/v1" % port
fails, n = [], 0


def req(method, path, body=None, token=None, ctype=None):
    r = urllib.request.Request(BASE + path, data=body, method=method)
    if token:
        r.add_header("Authorization", "Bearer " + token)
    if ctype:
        r.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if resp.headers.get("Content-Type") == "application/json" else raw)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def check(name, cond):
    global n
    n += 1
    if not cond:
        fails.append(name)


def jpeg_with_gps():
    im = Image.new("RGB", (640, 480), (180, 120, 90))
    ex = Image.Exif()
    ex[0x010F] = "PhoneMaker"                                     # Make
    ex[0x8825] = {1: "N", 2: (43.0, 36.0, 0.0), 3: "W", 4: (116.0, 12.0, 0.0)}  # GPS IFD
    b = io.BytesIO(); im.save(b, "JPEG", exif=ex); return b.getvalue()


src = jpeg_with_gps()
check("fixture-has-gps", Image.open(io.BytesIO(src)).getexif().get_ifd(0x8825) != {})

st, s = req("POST", "/sessions"); sid, tok = s["session_id"], s["token"]
check("create", st == 201 and sid and tok)

st, p = req("PUT", "/sessions/%s/photos?zone=%s&kind=before" % (sid, ZONE), src, tok, "image/jpeg")
check("upload", st == 201 and p["zone"] == ZONE)
st, raw = req("GET", "/sessions/%s/photos/%s" % (sid, p["id"]), token=tok)
stored = Image.open(io.BytesIO(raw))
check("exif-stripped", len(stored.getexif()) == 0 and b"Exif" not in raw[:4096])
check("gps-gone", stored.getexif().get_ifd(0x8825) == {})

st, e = req("PUT", "/sessions/%s/photos?zone=%s&kind=before" % (sid, ZONE), b"<script>x</script>", tok)
check("non-image-refused", st == 415)

# A flat-colour PNG compresses to a few hundred KB (well under MAX_BYTES) but
# decodes to hundreds of MB of RGB; must be rejected on dimensions, not decoded.
def _bomb():
    im = Image.new("RGB", (13000, 13000), (120, 120, 120))
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return b.getvalue()
bomb = _bomb()
check("bomb-fixture-under-max-bytes", len(bomb) < SV.MAX_BYTES)
st, e = req("PUT", "/sessions/%s/photos?zone=%s&kind=before" % (sid, ZONE), bomb, tok, "image/png")
check("decompression-bomb-refused", st == 413)
st, e = req("PUT", "/sessions/%s/photos?zone=nowhere&kind=before" % sid, src, tok)
check("unknown-zone-refused", st == 400)
st, e = req("PUT", "/sessions/%s/photos?zone=%s&kind=sideways" % (sid, ZONE), src, tok)
check("bad-kind-refused", st == 400)

st1, _ = req("GET", "/sessions/%s/photos" % sid, token="wrong-token")
st2, _ = req("GET", "/sessions/%s/photos" % ("A" * 24), token=tok)
st3, _ = req("GET", "/sessions/%s/photos" % sid)
check("wrong-token-same-as-missing", st1 == st2 == st3 == 404)
st, _ = req("GET", "/sessions/..%2F..%2Fetc/photos", token=tok)
check("traversal-404", st == 404)

disk = "".join(io.open(os.path.join(tmp, sid, "meta.json"), encoding="utf-8").read())
check("token-not-on-disk", tok not in disk)

# No provider configured: honest method-only answer.
st, a = req("POST", "/sessions/%s/analyze" % sid, json.dumps({"photo_id": p["id"]}).encode(), tok)
check("method-only", st == 200 and a["image_analyzed"] is False and a["provider"] is None
      and len(a["steps"]) == 1 + 7 and all("method" in s for s in a["steps"][1:]))

# A provider that wanders: invented cause, invented pass, invented surface.
SV.Handler.analyze_call = staticmethod(lambda imgs, txt: {
    "zone_visible": "yes", "summary": "Tray full of mail.",
    "items_seen": [{"item": "keys", "status": "belongs"}, {"item": "mail", "status": "stray"}],
    "frictions": [{"observed": "mail beside tray", "causes": ["RC-015", "XX-999"]}],
    "steps": [{"pass": "polish", "action": "buff"},
              {"pass": "shine", "surface_id": "s4", "action": "clean tray", "because": "grit"},
              {"pass": "sort", "surface_id": "s99", "action": "verdict the mail", "because": "x"}],
    "safety": [], "confidence": "medium"})
st, a = req("POST", "/sessions/%s/analyze" % sid, json.dumps({"photo_id": p["id"]}).encode(), tok)
check("grounded-ok", st == 200 and a["image_analyzed"] is True)
check("invented-dropped", a["dropped_as_outside_method"] == 3)
check("cause-kept-and-named", [c["id"] for c in a["frictions"][0]["causes"]] == ["RC-015"])
check("pass-order", [s["pass"] for s in a["steps"]] == ["sort", "shine"])
check("published-method-attached", "Lift the tray right out" in a["steps"][1].get("method", ""))

# Compare must stay inside one zone.
st, q = req("PUT", "/sessions/%s/photos?zone=%s&kind=after" % (sid, OTHER), src, tok, "image/jpeg")
st, e = req("POST", "/sessions/%s/analyze" % sid, json.dumps({"photo_id": q["id"], "compare_to": p["id"]}).encode(), tok)
check("compare-same-zone-only", st == 400)

st, d = req("DELETE", "/sessions/%s/photos/%s" % (sid, q["id"]), token=tok)
check("delete-photo", st == 200 and not os.path.exists(os.path.join(tmp, sid, q["id"] + ".jpg")))
st, d = req("DELETE", "/sessions/%s" % sid, token=tok)
check("delete-session", st == 200 and not os.path.exists(os.path.join(tmp, sid)))
st, _ = req("GET", "/sessions/%s/photos" % sid, token=tok)
check("deleted-is-gone", st == 404)

st, z = req("GET", "/zones"); check("zones-public", st == 200 and len(z["zones"]) == 114)
st, o = req("GET", "/openapi.json"); check("openapi", st == 200 and "/v1/sessions/{sid}/analyze" in o["paths"])

# Per-session-per-day alone does nothing against an attacker who just opens
# more sessions or more addresses; these bound actual vision-API spend.
st, s2 = req("POST", "/sessions"); sid2, tok2 = s2["session_id"], s2["token"]
st, p2 = req("PUT", "/sessions/%s/photos?zone=%s&kind=before" % (sid2, ZONE), src, tok2, "image/jpeg")
SV.ANALYSES_PER_IP_HOUR = 0
st, _ = req("POST", "/sessions/%s/analyze" % sid2, json.dumps({"photo_id": p2["id"]}).encode(), tok2)
check("analyze-ip-rate-limit", st == 429)
SV.ANALYSES_PER_IP_HOUR = 20
SV.ANALYSES_GLOBAL_PER_HOUR = 0
st, _ = req("POST", "/sessions/%s/analyze" % sid2, json.dumps({"photo_id": p2["id"]}).encode(), tok2)
check("analyze-global-rate-limit", st == 503)
SV.ANALYSES_GLOBAL_PER_HOUR = 100

# A compressed file well under MAX_BYTES must still be refused once a
# session's own cumulative storage would cross its quota, independent of
# MAX_PHOTOS_PER_SESSION (set far higher, so this is the quota actually firing).
old_quota = ST.MAX_SESSION_BYTES
ST.MAX_SESSION_BYTES = len(src) + 10
st, s3 = req("POST", "/sessions"); sid3, tok3 = s3["session_id"], s3["token"]
st, _ = req("PUT", "/sessions/%s/photos?zone=%s&kind=before" % (sid3, ZONE), src, tok3, "image/jpeg")
check("first-upload-under-quota", st == 201)
st, _ = req("PUT", "/sessions/%s/photos?zone=%s&kind=before" % (sid3, ZONE), src, tok3, "image/jpeg")
check("session-storage-quota-refused", st == 409)
ST.MAX_SESSION_BYTES = old_quota

# A restart must not silently rearm every limiter: a fresh Store pointed at
# the same data directory should still see hits recorded before "restart".
store_a = ST.Store(tmp)
check("fresh-allow", store_a.allow("probe", "1.2.3.4", 1, 3600) is True)
check("second-hit-blocked-same-instance", store_a.allow("probe", "1.2.3.4", 1, 3600) is False)
store_b = ST.Store(tmp)                       # simulates the process restarting
check("limit-persists-across-restart", store_b.allow("probe", "1.2.3.4", 1, 3600) is False)

SV.SESSIONS_PER_IP_HOUR = 0
st, _ = req("POST", "/sessions"); check("session-rate-limit", st == 429)

srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
if fails:
    print("FAIL %d/%d:" % (len(fails), n), fails); sys.exit(1)
print("OK: photos service, %d/%d checks pass" % (n, n))
