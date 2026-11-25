// mnemecho.com: carry a short link's source, remember the language a visitor picks, and run the status check.
(function () {
  "use strict";

  // Phase 223: a visit from a post's short link (mnemecho.com/ig lands on /en/?s=ig)
  // carries s and c on to the app, the account site and this site's own pages, so a
  // sign up after a look at Pricing still knows where it came from. Nothing is stored.
  var keep = [];
  var query = new URLSearchParams(location.search);
  ["s", "c", "utm_source", "utm_campaign"].forEach(function (key) {
    var value = query.get(key);
    if (value && /^[A-Za-z0-9_-]{1,40}$/.test(value)) keep.push([key, value]);
  });
  if (keep.length) {
    document.querySelectorAll("a[href]").forEach(function (link) {
      var url;
      try { url = new URL(link.getAttribute("href"), location.href); } catch (e) { return; }
      var ours = url.hostname === location.hostname || url.hostname === "mnemecho.com" ||
        /\.mnemecho\.com$/.test(url.hostname);
      if (!ours || !/^https?:$/.test(url.protocol)) return;
      if (url.hostname === location.hostname && url.pathname === location.pathname && url.hash) return;
      keep.forEach(function (pair) {
        if (!url.searchParams.has(pair[0])) url.searchParams.set(pair[0], pair[1]);
      });
      link.setAttribute("href", url.toString());
    });
  }

  document.querySelectorAll("a[data-lang]").forEach(function (link) {
    link.addEventListener("click", function () {
      try { localStorage.setItem("lang", link.getAttribute("data-lang")); } catch (e) {}
    });
  });

  var box = document.querySelector("[data-status-url]");
  if (!box) return;
  var dot = box.querySelector(".dot");
  var text = box.querySelector("[data-status-text]");
  var when = document.querySelector("[data-status-when]");
  var words = {
    up: box.getAttribute("data-up"),
    down: box.getAttribute("data-down"),
  };

  function show(state) {
    dot.className = "dot " + state;
    text.textContent = words[state];
    if (when) when.textContent = new Date().toLocaleTimeString(document.documentElement.lang);
  }

  function check() {
    var ctl = "AbortController" in window ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 8000);
    fetch(box.getAttribute("data-status-url"), { cache: "no-store", signal: ctl ? ctl.signal : undefined })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (body) { show(body && body.ok ? "up" : "down"); })
      .catch(function () { show("down"); })
      .finally(function () { clearTimeout(timer); });
  }

  check();
  setInterval(check, 60000);
})();
