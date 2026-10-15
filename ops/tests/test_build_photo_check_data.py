#!/usr/bin/env python3
"""
Prove ops/build_photo_check_data.py produces exactly the 114 zone slugs the
Photos API itself returns from GET /v1/zones (photos/methodology.py), so the
photo-check.html zone picker can never offer a slug that endpoint rejects.

Run:  python ops/tests/test_build_photo_check_data.py
"""
import importlib.util
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_photo_check_data as G                              # noqa: E402


def _load_methodology():
    spec = importlib.util.spec_from_file_location(
        "sixs_photos_methodology_test", os.path.join(ROOT, "photos", "methodology.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_matches_photos_api_zone_list():
    rows = G.zone_rows()
    slugs = {r["slug"] for r in rows}
    api_slugs = set(_load_methodology().zone_slugs())
    assert slugs == api_slugs, "zone picker drifted from GET /v1/zones: %r" % (slugs ^ api_slugs)


def test_114_unique_slugs():
    rows = G.zone_rows()
    assert len(rows) == 114, "expected 114 zones, got %d" % len(rows)
    slugs = [r["slug"] for r in rows]
    assert len(slugs) == len(set(slugs)), "duplicate slug in zone_rows()"


def test_every_row_has_room_and_name():
    for r in G.zone_rows():
        assert r.get("room"), "zone %r has no room" % r
        assert r.get("name"), "zone %r has no name" % r


def test_build_is_idempotent_and_matches_committed_file():
    """Running the generator twice must produce byte-identical output, and
    that output must match what is already committed (the same shape
    gate_generator_ownership checks for every other build_*.py)."""
    before = io.open(G.OUT, encoding="utf-8").read() if os.path.exists(G.OUT) else None
    path, _n = G.build()
    first = io.open(path, encoding="utf-8").read()
    path2, _n2 = G.build()
    second = io.open(path2, encoding="utf-8").read()
    assert first == second, "build() is not idempotent"
    if before is not None:
        assert before == first, (
            "site/assets/js/photo-check-zones.js on disk does not match what "
            "ops/build_photo_check_data.py produces; run the generator and commit its output")


def test_output_is_valid_json_payload():
    src = io.open(G.OUT, encoding="utf-8").read()
    marker = "window.PHOTO_CHECK_ZONES = "
    assert marker in src
    payload = src.split(marker, 1)[1].rstrip(";\n")
    rows = json.loads(payload)
    assert isinstance(rows, list) and len(rows) == 114


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL", t.__name__, "-", e)
    print("%d/%d passed" % (len(tests) - failed, len(tests)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
