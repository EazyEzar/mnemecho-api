// mnemecho.com/<lang>/pricing: Paddle's checkout (phase 187). Paddle approves this
// domain, so the overlay runs here. account.mnemecho.com/plan/checkout sends a signed
// in learner here with #buy=<token>&price=<month|year>; the token names the learner
// (user id, email, expiry) and is signed by our server, which checks it again when
// Paddle reports the new subscription. ?_ptxn=<txn> (a new card, or Paddle's own mail
// after a failed payment) is opened by Paddle.js itself.
(function () {
  "use strict";
  var box = document.getElementById("checkout");
  var note = document.getElementById("checkout-note");
  if (!box || !note) return;
  var nl = document.documentElement.lang === "nl";
  var words = nl ? {
    noPaddle: "De betaalpagina van Paddle laadde niet. Herlaad de pagina, of zet een blokkering voor paddle.com uit.",
    expired: "Die link is verlopen. Kies opnieuw een abonnement; je logt dan in op je account.",
    ready: "Ingelogd als {email}. Kies per maand of per jaar.",
    done: "Dank je. Je abonnement opent zodra Paddle de betaling bevestigt."
  } : {
    noPaddle: "Paddle's checkout did not load. Reload the page, or turn off a blocker for paddle.com.",
    expired: "That link has expired. Choose a plan again; you sign in to your account first.",
    ready: "Signed in as {email}. Choose monthly or yearly.",
    done: "Thank you. Your plan opens as soon as Paddle confirms the payment."
  };
  var account = box.getAttribute("data-account");
  var success = account + "/plan?bought=1";

  function say(text, kind) {
    note.textContent = text;
    note.setAttribute("data-kind", kind || "info");
    note.hidden = false;
  }

  function readToken(token) {
    try {
      var part = token.split(".")[0].replace(/-/g, "+").replace(/_/g, "/");
      var claim = JSON.parse(atob(part + "===".slice((part.length + 3) % 4)));
      if (typeof claim.u !== "number" || typeof claim.e !== "string" || typeof claim.x !== "number") return null;
      return claim;
    } catch (e) {
      return null;
    }
  }

  // The fragment never reaches a server; drop it so a reload does not reopen the checkout.
  var params = {};
  location.hash.replace(/^#/, "").split("&").forEach(function (pair) {
    var at = pair.indexOf("=");
    if (at > 0) params[pair.slice(0, at)] = decodeURIComponent(pair.slice(at + 1));
  });
  if (params.buy) history.replaceState(null, "", location.pathname + location.search);

  if (!window.Paddle) {
    if (params.buy || /[?&]_ptxn=/.test(location.search)) say(words.noPaddle, "error");
    return;
  }
  if (box.getAttribute("data-env") === "sandbox") window.Paddle.Environment.set("sandbox");
  window.Paddle.Initialize({
    token: box.getAttribute("data-token"),
    checkout: { settings: { displayMode: "overlay", theme: "light", locale: nl ? "nl" : "en", successUrl: success } },
    // An overlay Paddle opens by itself from ?_ptxn ignores successUrl (78b walk).
    eventCallback: function (ev) {
      if (ev && ev.name === "checkout.completed") {
        say(words.done);
        location.assign(success);
      }
    }
  });

  if (!params.buy) return;
  var claim = readToken(params.buy);
  if (!claim || claim.x * 1000 < Date.now()) {
    say(words.expired, "error");
    return;
  }
  say(words.ready.replace("{email}", claim.e));

  function open(kind) {
    var price = box.getAttribute("data-" + kind);
    if (!price) return;
    window.Paddle.Checkout.open({
      items: [{ priceId: price, quantity: 1 }],
      customer: { email: claim.e },
      customData: { user_id: String(claim.u), plan_token: params.buy },
      settings: { displayMode: "overlay", theme: "light", locale: nl ? "nl" : "en", successUrl: success }
    });
  }

  document.querySelectorAll("a[data-buy]").forEach(function (link) {
    link.addEventListener("click", function (event) {
      if (claim.x * 1000 < Date.now()) return; // expired since: the link signs in again
      event.preventDefault();
      open(link.getAttribute("data-buy"));
    });
  });
  if (params.price === "month" || params.price === "year") open(params.price);
})();
