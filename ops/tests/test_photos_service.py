"""End-to-end tests for the photo service, over real HTTP.
Run: python ops/tests/test_photos_service.py"""
import io, json, os, shutil, sys, tempfile, threading, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "photos"))
os.environ.pop("ANTHROPIC_API_KEY", None)
import server as SV
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

SV.SESSIONS_PER_IP_HOUR = 0
st, _ = req("POST", "/sessions"); check("session-rate-limit", st == 429)

srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
if fails:
    print("FAIL %d/%d:" % (len(fails), n), fails); sys.exit(1)
print("OK: photos service, %d/%d checks pass" % (n, n))
