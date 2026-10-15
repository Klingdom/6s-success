/* Photo Check: upload a before/after photo of one micro zone and get back
   that zone's own published method. Talks to the Photos API documented in
   PHOTOS-API.md (photos/server.py). That service is built and tested but
   NOT YET DEPLOYED (OWNER-ACTIONS.md item 22), so every call here is
   expected to fail until it is; this file treats "unreachable" as the
   normal first state, not an error, and never leaves the page looking
   broken because of it.

   No account: a session is a bearer token, shown once by the API and kept
   only in this browser's localStorage. Nothing here is sent to analytics
   except coarse milestone events, and never a zone name (same choice the
   Home Quest app made for its own events; see quest.js). */
(function () {
  "use strict";

  var API_BASE = "/api/photos/v1";
  var STORE_KEY = "sixs-photo-check-session";
  var HEALTH_TIMEOUT_MS = 4000;

  function track(name) {
    try {
      if (window.Measure && typeof window.Measure.track === "function") {
        window.Measure.track(name);
      }
    } catch (err) { /* analytics must never block the feature */ }
  }

  function $(id) { return document.getElementById(id); }

  function loadSession() {
    try {
      var raw = window.localStorage.getItem(STORE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (err) { return null; }
  }

  function saveSession(s) {
    try { window.localStorage.setItem(STORE_KEY, JSON.stringify(s)); }
    catch (err) { /* private browsing or a full quota; session still works in-memory */ }
  }

  function clearSession() {
    try { window.localStorage.removeItem(STORE_KEY); } catch (err) { /* ignore */ }
  }

  function fetchWithTimeout(url, opts, ms) {
    var ctrl = (typeof AbortController !== "undefined") ? new AbortController() : null;
    var merged = Object.assign({}, opts || {});
    if (ctrl) merged.signal = ctrl.signal;
    var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, ms) : null;
    return fetch(url, merged).finally(function () { if (timer) clearTimeout(timer); });
  }

  function apiCall(path, opts) {
    return fetchWithTimeout(API_BASE + path, opts, HEALTH_TIMEOUT_MS).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (body) {
        return { ok: r.ok, status: r.status, body: body };
      });
    });
  }

  function ensureSession() {
    var existing = loadSession();
    if (existing && existing.session_id && existing.token) {
      return Promise.resolve(existing);
    }
    return apiCall("/sessions", { method: "POST" }).then(function (res) {
      if (!res.ok) throw new Error("could not start a session");
      var s = { session_id: res.body.session_id, token: res.body.token };
      saveSession(s);
      return s;
    });
  }

  function authHeaders(session) {
    return { Authorization: "Bearer " + session.token };
  }

  function populateZonePicker(select, presetSlug) {
    var zones = window.PHOTO_CHECK_ZONES || [];
    var byRoom = {};
    zones.forEach(function (z) {
      (byRoom[z.room] = byRoom[z.room] || []).push(z);
    });
    Object.keys(byRoom).sort().forEach(function (room) {
      var group = document.createElement("optgroup");
      group.label = room;
      byRoom[room].forEach(function (z) {
        var opt = document.createElement("option");
        opt.value = z.slug;
        opt.textContent = z.name;
        if (z.slug === presetSlug) opt.selected = true;
        group.appendChild(opt);
      });
      select.appendChild(group);
    });
  }

  function showUnavailable() {
    $("pc-unavailable").hidden = false;
    $("pc-app").hidden = true;
    track("photo-check-unavailable");
  }

  function renderStep(step) {
    var li = document.createElement("li");
    var head = document.createElement("strong");
    head.textContent = step.action || (step.pass ? step.pass : "Step");
    li.appendChild(head);
    if (step.because) {
      var p = document.createElement("p");
      p.textContent = step.because;
      li.appendChild(p);
    }
    return li;
  }

  function renderResult(container, data) {
    container.innerHTML = "";
    container.hidden = false;

    var summary = document.createElement("p");
    summary.className = "pc-summary";
    summary.textContent = data.summary || "";
    container.appendChild(summary);

    if (!data.image_analyzed) {
      var note = document.createElement("p");
      note.className = "pc-note";
      note.textContent = "This answer is the zone's published method, not a reading of your "
        + "photo: no image analysis provider is configured yet.";
      container.appendChild(note);
    }

    if (Array.isArray(data.steps) && data.steps.length) {
      var h = document.createElement("h3");
      h.textContent = "What to do next";
      container.appendChild(h);
      var ol = document.createElement("ol");
      ol.className = "pc-steps";
      data.steps.forEach(function (s) { ol.appendChild(renderStep(s)); });
      container.appendChild(ol);
    }

    if (Array.isArray(data.after_check) && data.after_check.length) {
      var h2 = document.createElement("h3");
      h2.textContent = "Against the standard";
      container.appendChild(h2);
      var ul2 = document.createElement("ul");
      data.after_check.forEach(function (line) {
        var li = document.createElement("li");
        li.textContent = line;
        ul2.appendChild(li);
      });
      container.appendChild(ul2);
    }

    if (Array.isArray(data.safety) && data.safety.length) {
      var h3 = document.createElement("h3");
      h3.textContent = "Worth flagging";
      container.appendChild(h3);
      var ul3 = document.createElement("ul");
      ul3.className = "pc-safety";
      data.safety.forEach(function (line) {
        var li = document.createElement("li");
        li.textContent = line;
        ul3.appendChild(li);
      });
      container.appendChild(ul3);
    }

    if (data.zone_url) {
      var a = document.createElement("a");
      a.href = data.zone_url;
      a.textContent = "Read this zone's full method";
      container.appendChild(a);
    }
  }

  function init() {
    var app = $("pc-app");
    if (!app) return;

    apiCall("/health", { method: "GET" }).then(function (res) {
      if (!res.ok || !res.body || res.body.ok !== true) throw new Error("unhealthy");
      initApp();
    }).catch(function () {
      showUnavailable();
    });
  }

  function initApp() {
    var params = new URLSearchParams(window.location.search);
    var presetZone = params.get("zone") || "";
    var select = $("pc-zone");
    populateZonePicker(select, presetZone);

    var photos = {}; // kind -> {id, url}
    var currentSession = null;

    function currentZone() { return select.value; }

    function setStatus(msg, isError) {
      var el = $("pc-status");
      el.textContent = msg || "";
      el.className = isError ? "pc-status pc-status-error" : "pc-status";
    }

    function handleUpload(kind, file) {
      if (!file) return;
      if (!currentZone()) { setStatus("Choose a zone first.", true); return; }
      setStatus("Uploading...");
      ensureSession().then(function (session) {
        currentSession = session;
        return fetchWithTimeout(
          API_BASE + "/sessions/" + session.session_id + "/photos?zone="
            + encodeURIComponent(currentZone()) + "&kind=" + kind,
          { method: "PUT", headers: authHeaders(session), body: file },
          15000
        );
      }).then(function (r) {
        return r.json().then(function (body) { return { ok: r.ok, body: body }; });
      }).then(function (res) {
        if (!res.ok) throw new Error(res.body && res.body.error ? res.body.error : "upload failed");
        photos[kind] = { id: res.body.id };
        $("pc-thumb-" + kind).src = URL.createObjectURL(file);
        $("pc-thumb-" + kind).hidden = false;
        $("pc-analyze-" + kind).hidden = false;
        setStatus("Photo saved. Nothing is public; delete it any time below.");
        track("photo-check-uploaded");
      }).catch(function (err) {
        setStatus("Could not save that photo: " + err.message, true);
      });
    }

    function handleAnalyze(kind) {
      var photo = photos[kind];
      if (!photo || !currentSession) return;
      setStatus("Reading the method for this zone...");
      var body = { photo_id: photo.id };
      if (kind === "after" && photos.before) body.compare_to = photos.before.id;
      apiCall("/sessions/" + currentSession.session_id + "/analyze", {
        method: "POST",
        headers: Object.assign({ "Content-Type": "application/json" }, authHeaders(currentSession)),
        body: JSON.stringify(body)
      }).then(function (res) {
        if (!res.ok) throw new Error(res.body && res.body.error ? res.body.error : "could not analyze");
        renderResult($("pc-result"), res.body);
        setStatus("");
        track("photo-check-analyzed");
      }).catch(function (err) {
        setStatus("Could not read this zone's method: " + err.message, true);
      });
    }

    function handleClear() {
      if (!currentSession) { clearSession(); return; }
      apiCall("/sessions/" + currentSession.session_id, {
        method: "DELETE", headers: authHeaders(currentSession)
      }).finally(function () {
        clearSession();
        currentSession = null;
        photos = {};
        ["before", "after"].forEach(function (k) {
          $("pc-thumb-" + k).hidden = true;
          $("pc-analyze-" + k).hidden = true;
        });
        $("pc-result").hidden = true;
        setStatus("Every photo for this session is deleted.");
      });
    }

    ["before", "after"].forEach(function (kind) {
      $("pc-file-" + kind).addEventListener("change", function (e) {
        handleUpload(kind, e.target.files && e.target.files[0]);
      });
      $("pc-analyze-" + kind).addEventListener("click", function () { handleAnalyze(kind); });
    });
    $("pc-clear").addEventListener("click", handleClear);

    $("pc-app").hidden = false;
    track("photo-check-started");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
