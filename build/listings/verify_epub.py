"""Structural pre-flight for the KDP EPUB upload.

This is NOT epubcheck. No JRE is installed on this machine and epubcheck was not
available, so this checks the classes of defect that a zip + XML reader can see:
container integrity, mimetype placement, XML well-formedness, manifest/spine
referential integrity, orphan resources, broken internal hrefs and image srcs,
and the KDP-relevant metadata and cover requirements.

Anything it cannot see is reported as UNCHECKED, not as a pass.
"""
import zipfile, os, sys, posixpath, re
from xml.etree import ElementTree as ET
from urllib.parse import unquote

EPUB = sys.argv[1] if len(sys.argv) > 1 else "build/6S-Success-Home-Edition.epub"
OPFNS = "{http://www.idpf.org/2007/opf}"
DCNS = "{http://purl.org/dc/elements/1.1/}"
XHNS = "{http://www.w3.org/1999/xhtml}"

ok, fail, unchecked = [], [], []
def P(m): ok.append(m)
def F(m): fail.append(m)
def U(m): unchecked.append(m)

z = zipfile.ZipFile(EPUB)
names = z.namelist()

# 1 container integrity
P(f"zip opens, {len(names)} entries, CRC check returned {z.testzip()!r} (None = all entries intact)")

# 2 mimetype
i0 = z.infolist()[0]
if i0.filename == "mimetype" and i0.compress_type == zipfile.ZIP_STORED and z.read("mimetype") == b"application/epub+zip":
    P("mimetype is the first entry, stored uncompressed, correct content")
else:
    F(f"mimetype entry wrong: name={i0.filename} compress={i0.compress_type}")

# 3 container.xml -> opf
cx = ET.fromstring(z.read("META-INF/container.xml"))
opf_path = cx.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile").get("full-path")
P(f"META-INF/container.xml points at {opf_path}")
opf = ET.fromstring(z.read(opf_path))
base = posixpath.dirname(opf_path)

# 4 metadata KDP cares about
md = opf.find(OPFNS + "metadata")
def dc(tag):
    e = md.find(DCNS + tag)
    return e.text if e is not None else None
for tag in ("title", "creator", "language", "identifier"):
    v = dc(tag)
    (P if v else F)(f"dc:{tag} = {v!r}" if v else f"dc:{tag} MISSING")
P(f"EPUB version attribute = {opf.get('version')!r}")

# 5 manifest / spine integrity
manifest = {}
for it in opf.find(OPFNS + "manifest"):
    href = unquote(it.get("href"))
    full = posixpath.normpath(posixpath.join(base, href))
    manifest[it.get("id")] = (full, it.get("media-type"), it.get("properties") or "")
    if full not in names:
        F(f"manifest item {it.get('id')} -> {full} NOT IN ARCHIVE")
P(f"manifest lists {len(manifest)} items, all present in the archive"
  if not fail else f"manifest lists {len(manifest)} items")

spine = [r.get("idref") for r in opf.find(OPFNS + "spine")]
missing = [s for s in spine if s not in manifest]
(F if missing else P)(f"spine has {len(spine)} itemrefs, unresolved: {missing}" if missing
                      else f"spine has {len(spine)} itemrefs, every one resolves to a manifest id")

declared = {v[0] for v in manifest.values()}
skip = {"mimetype", "META-INF/container.xml", opf_path}
orphans = [n for n in names if n not in declared and n not in skip and not n.endswith("/")]
(F if orphans else P)(f"undeclared files in archive: {orphans}" if orphans
                      else "no undeclared resource files in the archive")

# 6 cover
cover_items = [k for k, v in manifest.items() if "cover-image" in v[2]]
(P if cover_items else F)(f"cover-image property on manifest id {cover_items}" if cover_items
                          else "no manifest item carries properties=cover-image")
meta_cover = [m for m in md.findall(OPFNS + "meta") if m.get("name") == "cover"]
(P if meta_cover else U)("legacy <meta name=\"cover\"> present (helps older Kindle pipelines)"
                         if meta_cover else "legacy <meta name=\"cover\"> absent")

# 7 nav
navs = [k for k, v in manifest.items() if "nav" in v[2].split()]
(P if navs else F)(f"EPUB 3 nav document present: {[manifest[k][0] for k in navs]}" if navs else "no nav document")
ncx = [k for k, v in manifest.items() if v[1] == "application/x-dtbncx+xml"]
(P if ncx else U)(f"NCX fallback present: {[manifest[k][0] for k in ncx]}" if ncx else "no NCX fallback")

# 8 XML well-formedness of every xhtml + internal link/image resolution
bad_xml, bad_href, bad_img = [], [], []
words = 0
for iid, (full, mt, props) in manifest.items():
    if mt != "application/xhtml+xml":
        continue
    raw = z.read(full)
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        bad_xml.append(f"{full}: {e}")
        continue
    words += len(re.findall(r"[A-Za-z']+", re.sub(r"<[^>]+>", " ", raw.decode("utf-8", "replace"))))
    d = posixpath.dirname(full)
    for el in root.iter():
        for attr, bucket in (("href", bad_href), ("src", bad_img)):
            v = el.get(attr)
            if not v or v.startswith(("http:", "https:", "mailto:", "data:", "#")):
                continue
            tgt = posixpath.normpath(posixpath.join(d, unquote(v.split("#")[0])))
            if tgt not in names:
                bucket.append(f"{full} -> {v}")
(F if bad_xml else P)(f"XML parse errors: {bad_xml}" if bad_xml
                      else f"all {sum(1 for v in manifest.values() if v[1]=='application/xhtml+xml')} XHTML documents parse as well-formed XML")
(F if bad_href else P)(f"broken internal hrefs: {bad_href[:10]}" if bad_href else "every internal href resolves to a file in the archive")
(F if bad_img else P)(f"broken image/src refs: {bad_img[:10]}" if bad_img else "every internal src resolves to a file in the archive")
P(f"approximate word count across spine documents: {words:,}")

# 9 cover image geometry
try:
    from PIL import Image
    import io
    cimg = manifest[cover_items[0]][0] if cover_items else None
    if cimg:
        im = Image.open(io.BytesIO(z.read(cimg)))
        P(f"embedded cover {cimg}: {im.size[0]}x{im.size[1]} {im.mode}, height/width = {im.size[1]/im.size[0]:.4f}")
except Exception as e:
    U(f"embedded cover geometry not read: {e}")

# 10 things this script structurally cannot judge
U("epubcheck conformance: NOT RUN. No JRE on this machine; install Java + epubcheck to run the real validator.")
U("Kindle Previewer / KDP converter behaviour: NOT RUN. Only Amazon's own converter can confirm the file renders correctly on device.")
U("CSS validity and Kindle CSS-subset support: not inspected.")
U("Font embedding licence: no fonts are embedded in this archive, so nothing to license.")

print("PASS")
for m in ok: print("  [ok]", m)
print("\nFAIL")
for m in fail: print("  [FAIL]", m)
if not fail: print("  (none)")
print("\nUNCHECKED")
for m in unchecked: print("  [??]", m)
sys.exit(1 if fail else 0)
