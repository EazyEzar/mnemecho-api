// mnemecho.com: remember the language a visitor picks, play the native sentences,
// and run the status check.
(function () {
  "use strict";

  document.querySelectorAll("a[data-lang]").forEach(function (link) {
    link.addEventListener("click", function () {
      try { localStorage.setItem("lang", link.getAttribute("data-lang")); } catch (e) {}
    });
  });

  // Phase 78c: the native sentences on the learner home. One plays at a time.
  var player = null, playing = null;
  function stop() {
    if (!playing) return;
    playing.setAttribute("aria-pressed", "false");
    var card = playing.closest("[data-say]");
    card.classList.remove("playing");
    card.style.setProperty("--heard", "0");
    playing = null;
  }
  document.querySelectorAll("[data-say] .play").forEach(function (button) {
    button.addEventListener("click", function () {
      var again = playing === button;
      if (player) { player.pause(); }
      stop();
      if (again) return;
      player = new Audio(button.getAttribute("data-src"));
      var card = button.closest("[data-say]");
      card.style.setProperty("--heard", "0");
      player.addEventListener("timeupdate", function () {
        if (this.duration) card.style.setProperty("--heard", String(this.currentTime / this.duration));
      });
      player.addEventListener("ended", stop);
      player.addEventListener("error", stop);
      playing = button;
      button.setAttribute("aria-pressed", "true");
      button.closest("[data-say]").classList.add("playing");
      player.play().catch(stop);
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
