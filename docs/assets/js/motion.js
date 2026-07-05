/* ============================================================
   motion.js — mise en mouvement 3D des photos (fluide, senior).
     · Inclinaison 3D au pointeur (parallaxe de la souris) sur les
       visuels : plats signature, galerie, photo du récit.
     · Reflet spéculaire discret qui suit le curseur.
   Progressive enhancement : désactivé au tactile et si l'utilisateur
   préfère les mouvements réduits. Aucune dépendance. 60 fps (rAF).
   ============================================================ */
(function () {
  "use strict";

  var mq = window.matchMedia;
  var reduit = mq && mq("(prefers-reduced-motion: reduce)").matches;
  var finPointeur = mq && mq("(hover: hover) and (pointer: fine)").matches;
  // Seuls les écrans avec souris/trackpad et sans réduction de mouvement
  if (reduit || !finPointeur) return;

  var AMPLITUDE = 6; // degrés d'inclinaison max

  function lier(el) {
    if (el.__tilt) return;
    el.__tilt = true;
    el.classList.add("tilt");

    var raf = null, rx = 0, ry = 0, mx = 50, my = 50;

    function appliquer() {
      raf = null;
      el.style.setProperty("--rx", rx.toFixed(2) + "deg");
      el.style.setProperty("--ry", ry.toFixed(2) + "deg");
      el.style.setProperty("--mx", mx.toFixed(1) + "%");
      el.style.setProperty("--my", my.toFixed(1) + "%");
    }
    function planifier() { if (!raf) raf = requestAnimationFrame(appliquer); }

    el.addEventListener("pointermove", function (e) {
      var r = el.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width;   // 0 → 1
      var py = (e.clientY - r.top) / r.height;   // 0 → 1
      ry = (px - 0.5) * (AMPLITUDE * 2);         // gauche/droite
      rx = (0.5 - py) * (AMPLITUDE * 2);         // haut/bas
      mx = px * 100; my = py * 100;
      el.classList.add("is-tilting");
      planifier();
    });

    el.addEventListener("pointerleave", function () {
      rx = 0; ry = 0; mx = 50; my = 50;
      el.classList.remove("is-tilting");
      planifier();
    });
  }

  function scanner() {
    document.querySelectorAll(".sig-media, .gal-item, .esprit-media").forEach(lier);
  }

  function init() {
    scanner();
    // les visuels arrivent après le rendu des sections (data JSON) → re-scanner
    document.addEventListener("phoenix:sections-ready", scanner);
    document.addEventListener("phoenix:menu-ready", scanner);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
