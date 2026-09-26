/* Before and after photographs for the Home Quest.
 *
 * WHY THIS IS NOT localStorage
 * ----------------------------
 * A phone photograph is three to five megabytes. localStorage holds about five
 * in total, stores strings only, and throws when it fills. Putting one picture
 * in it would end the app. IndexedDB stores Blobs natively, runs off the main
 * thread, and has a quota measured in a share of free disk rather than in
 * kilobytes.
 *
 * WHY THE PICTURES NEVER LEAVE THE PHONE
 * --------------------------------------
 * These are photographs of the inside of somebody's home, often with their
 * possessions and sometimes their children's rooms in frame. There is no upload
 * here and no account to upload to: the database is on the device, the site is
 * static, and nothing in this file makes a network request. That is a deliberate
 * design constraint, not an unfinished feature, and the interface says so
 * plainly where a person can read it before they take the first picture.
 *
 * WHY THEY ARE RESIZED FIRST
 * --------------------------
 * A modern phone camera produces a 12 megapixel image. Nobody needs 12
 * megapixels to see that a counter is clear. Downscaling to 1600px on the long
 * edge costs nothing anybody can see on a phone and turns a 4 MB file into
 * roughly 300 KB, which is the difference between a hundred zones fitting and
 * the quota erroring out halfway through the house.
 */
(function () {
  "use strict";

  var DB = "6s-quest-photos";
  var STORE = "shots";
  var VERSION = 1;
  var MAX_EDGE = 1600;
  var QUALITY = 0.82;

  var dbp = null;

  function open() {
    if (dbp) { return dbp; }
    dbp = new Promise(function (resolve, reject) {
      if (!window.indexedDB) { reject(new Error("no indexeddb")); return; }
      var req = indexedDB.open(DB, VERSION);
      req.onupgradeneeded = function () {
        var d = req.result;
        if (!d.objectStoreNames.contains(STORE)) {
          d.createObjectStore(STORE, { keyPath: "id" });
        }
      };
      req.onsuccess = function () { resolve(req.result); };
      req.onerror = function () { reject(req.error); };
    });
    return dbp;
  }

  function tx(mode, fn) {
    return open().then(function (d) {
      return new Promise(function (resolve, reject) {
        var t = d.transaction(STORE, mode);
        var req = fn(t.objectStore(STORE));
        /* Resolve with the request's result, which is undefined when a get
           finds nothing. The first version of this fell back to the request
           OBJECT when result was undefined, and an IDBRequest is truthy, so a
           missing photograph read as a present one: both slots rendered filled
           and the after slot pointed an img at null. Caught by storing one
           picture and counting two.
           A write returns no request worth reporting, hence the guard rather
           than a bare req.result. */
        t.oncomplete = function () {
          resolve(req && "result" in req ? req.result : undefined);
        };
        t.onerror = function () { reject(t.error); };
        t.onabort = function () { reject(t.error); };
      });
    });
  }

  function id(room, zone, kind) { return room + "|" + zone + "|" + kind; }

  /* Draw the picture into a canvas at a sane size and re-encode it. Also strips
     every EXIF field in the process, which matters more than the file size:
     phone photographs carry GPS coordinates, and a picture of somebody's
     kitchen tagged with their address is a different object entirely. */
  function shrink(file) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(file);
      var img = new Image();
      img.onload = function () {
        URL.revokeObjectURL(url);
        var w = img.naturalWidth, h = img.naturalHeight;
        var scale = Math.min(1, MAX_EDGE / Math.max(w, h));
        var cw = Math.round(w * scale), ch = Math.round(h * scale);
        var c = document.createElement("canvas");
        c.width = cw; c.height = ch;
        c.getContext("2d").drawImage(img, 0, 0, cw, ch);
        c.toBlob(function (blob) {
          if (blob) { resolve({ blob: blob, w: cw, h: ch }); }
          else { reject(new Error("encode failed")); }
        }, "image/jpeg", QUALITY);
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        reject(new Error("not an image this browser can read"));
      };
      img.src = url;
    });
  }

  var API = {
    supported: function () { return !!window.indexedDB; },

    put: function (room, zone, kind, file) {
      return shrink(file).then(function (r) {
        return tx("readwrite", function (s) {
          return s.put({ id: id(room, zone, kind), room: room, zone: zone,
                         kind: kind, blob: r.blob, w: r.w, h: r.h,
                         at: Date.now() });
        }).then(function () { return r; });
      });
    },

    get: function (room, zone, kind) {
      return tx("readonly", function (s) { return s.get(id(room, zone, kind)); });
    },

    del: function (room, zone, kind) {
      return tx("readwrite", function (s) { return s.delete(id(room, zone, kind)); });
    },

    /* Every shot for one zone, as {before, after}. */
    pair: function (room, zone) {
      return Promise.all([API.get(room, zone, "before"), API.get(room, zone, "after")])
        .then(function (r) { return { before: r[0], after: r[1] }; });
    },

    all: function () {
      return tx("readonly", function (s) { return s.getAll(); });
    },

    /* What the pictures are costing, so somebody can see it before a phone
       tells them the hard way. */
    usage: function () {
      return API.all().then(function (rows) {
        var bytes = rows.reduce(function (n, r) {
          return n + (r.blob ? r.blob.size : 0);
        }, 0);
        return { count: rows.length, bytes: bytes };
      });
    },

    clearZone: function (room, zone) {
      return Promise.all([API.del(room, zone, "before"), API.del(room, zone, "after")]);
    },

    objectUrl: function (rec) {
      return rec && rec.blob ? URL.createObjectURL(rec.blob) : null;
    }
  };

  window.QuestPhotos = API;
})();
