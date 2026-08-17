/* Progressive enhancement only: every action here has a server-rendered
   fallback, so the app stays usable with JavaScript disabled. */
(function () {
  "use strict";

  var toastEl = document.querySelector("[data-toast]");
  var toastTimer;

  function toast(message) {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.hidden = false;
    // Force a reflow so the transition runs when toasting twice in a row.
    void toastEl.offsetWidth;
    toastEl.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toastEl.classList.remove("is-visible");
    }, 2200);
  }

  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // Clipboard API needs HTTPS; fall back for plain-HTTP deployments.
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      try {
        document.execCommand("copy") ? resolve() : reject(new Error("copy failed"));
      } catch (err) {
        reject(err);
      } finally {
        document.body.removeChild(area);
      }
    });
  }

  document.addEventListener("click", function (event) {
    var copyBtn = event.target.closest("[data-copy]");
    if (copyBtn) {
      copy(copyBtn.dataset.copy).then(
        function () { toast("Copied to clipboard"); },
        function () { toast("Could not copy — select the link manually"); }
      );
      return;
    }

    var qrBtn = event.target.closest("[data-qr]");
    if (qrBtn) {
      var dialog = document.getElementById("qr-dialog");
      if (!dialog || !dialog.showModal) return; // let the link navigate instead
      event.preventDefault();
      dialog.querySelector("[data-qr-image]").src = qrBtn.dataset.qr;
      dialog.querySelector("[data-qr-label]").textContent = qrBtn.dataset.url || "";
      dialog.querySelector("[data-qr-download]").href = qrBtn.dataset.qr + "?download=1";
      dialog.showModal();
      return;
    }

    if (event.target.closest("[data-qr-close]")) {
      document.getElementById("qr-dialog").close();
      return;
    }

    var themeBtn = event.target.closest("[data-theme-toggle]");
    if (themeBtn) {
      var next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
      document.documentElement.dataset.theme = next;
      localStorage.setItem("theme", next);
    }
  });

  document.addEventListener("submit", function (event) {
    var form = event.target.closest("[data-confirm]");
    if (form && !window.confirm(form.dataset.confirm)) {
      event.preventDefault();
    }
  });
})();
