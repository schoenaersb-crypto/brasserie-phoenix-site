/* ============================================================
   experience.js — couche « expérience » du redesign (motion/interaction).
   Comportements autonomes, activés seulement si leurs cibles existent :
     1. Barre de progression de défilement (#scroll-progress)
     2. Curseur personnalisé (#cursor / #cursor-dot) — pointeur fin
     3. Boutons magnétiques (.magnetic) — pointeur fin
     4. Titre héro en cascade (.hero-title) — découpe en lettres
     5. Compteurs animés ([data-count])
     6. Bandeau défilant (.marquee > .marquee__track)

   NE FAIT PAS : reveal-on-scroll ni tilt 3D (déjà dans ui.js / motion.js).
   Vanilla, zéro dépendance, zéro requête réseau. rAF + listeners passifs.
   Respecte prefers-reduced-motion : dégradation propre (valeurs finales,
   aucun mouvement suivant la souris ou le scroll).
   ============================================================ */
(function () {
  "use strict";

  var mq = window.matchMedia;
  // Mouvement réduit demandé par l'utilisateur (accessibilité).
  var REDUIT = !!(mq && mq("(prefers-reduced-motion: reduce)").matches);
  // Écrans avec un vrai pointeur (souris/trackpad) — pas de tactile.
  var POINTEUR_FIN = !!(mq && mq("(hover: hover) and (pointer: fine)").matches);

  // Interpolation linéaire (lissage du curseur).
  function lerp(a, b, t) { return a + (b - a) * t; }
  // Easing « easeOutCubic » pour les compteurs.
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  function clamp(v, min, max) { return v < min ? min : (v > max ? max : v); }

  /* ---------- 1. Barre de progression de défilement ---------- */
  function initScrollProgress() {
    var barre = document.getElementById("scroll-progress");
    if (!barre) return;

    var raf = null;
    function appliquer() {
      raf = null;
      var doc = document.documentElement;
      var max = (doc.scrollHeight - doc.clientHeight);
      var pct = max > 0 ? (window.scrollY / max) * 100 : 0;
      barre.style.width = clamp(pct, 0, 100).toFixed(2) + "%";
    }
    function planifier() { if (!raf) raf = requestAnimationFrame(appliquer); }

    window.addEventListener("scroll", planifier, { passive: true });
    window.addEventListener("resize", planifier, { passive: true });
    appliquer(); // état initial
  }

  /* ---------- 2. Curseur personnalisé (desktop pointeur fin) ---------- */
  function initCursor() {
    if (REDUIT || !POINTEUR_FIN) return;
    var cercle = document.getElementById("cursor");
    if (!cercle) return;
    var point = document.getElementById("cursor-dot"); // optionnel

    // On masque le curseur natif seulement une fois le mode réellement actif.
    document.body.classList.add("has-cursor");

    var vx = window.innerWidth / 2, vy = window.innerHeight / 2; // cible (souris)
    var cx = vx, cy = vy;                                        // position lissée
    var vu = false; // le curseur a-t-il déjà bougé au moins une fois

    // Boucle d'animation permanente (léger lissage du gros cercle).
    function boucle() {
      cx = lerp(cx, vx, 0.18);
      cy = lerp(cy, vy, 0.18);
      cercle.style.transform =
        "translate3d(" + cx.toFixed(2) + "px," + cy.toFixed(2) + "px,0)";
      requestAnimationFrame(boucle);
    }
    requestAnimationFrame(boucle);

    window.addEventListener("pointermove", function (e) {
      vx = e.clientX; vy = e.clientY;
      if (!vu) { vu = true; cercle.classList.add("is-visible"); }
      // Le point suit sans lissage (position exacte de la souris).
      if (point) {
        point.style.transform =
          "translate3d(" + vx + "px," + vy + "px,0)";
      }
    }, { passive: true });

    // Cache le curseur quand la souris quitte la fenêtre.
    document.addEventListener("mouseleave", function () {
      cercle.classList.remove("is-visible");
      if (point) point.classList.remove("is-visible");
    });
    document.addEventListener("mouseenter", function () {
      cercle.classList.add("is-visible");
      if (point) point.classList.add("is-visible");
    });

    // Agrandissement au survol des éléments interactifs (délégation).
    var SELECTEUR = "a, .btn, .gal-item, .magnetic";
    document.addEventListener("pointerover", function (e) {
      if (e.target.closest && e.target.closest(SELECTEUR)) {
        cercle.classList.add("is-hover");
      }
    }, { passive: true });
    document.addEventListener("pointerout", function (e) {
      if (e.target.closest && e.target.closest(SELECTEUR)) {
        cercle.classList.remove("is-hover");
      }
    }, { passive: true });
  }

  /* ---------- 3. Boutons magnétiques (desktop pointeur fin) ---------- */
  function lierMagnetique(el) {
    if (el.__magnetic) return;
    el.__magnetic = true;

    var MAX = 14;         // déplacement maximal en px
    var raf = null, tx = 0, ty = 0;

    function appliquer() {
      raf = null;
      // On expose --mx/--my ET on pose transform pour être autonome du CSS.
      el.style.setProperty("--mx", tx.toFixed(2) + "px");
      el.style.setProperty("--my", ty.toFixed(2) + "px");
      el.style.transform = "translate(" + tx.toFixed(2) + "px," + ty.toFixed(2) + "px)";
    }
    function planifier() { if (!raf) raf = requestAnimationFrame(appliquer); }

    el.addEventListener("pointermove", function (e) {
      var r = el.getBoundingClientRect();
      // Vecteur depuis le centre, normalisé sur la demi-dimension.
      var dx = (e.clientX - (r.left + r.width / 2)) / (r.width / 2);
      var dy = (e.clientY - (r.top + r.height / 2)) / (r.height / 2);
      tx = clamp(dx, -1, 1) * MAX;
      ty = clamp(dy, -1, 1) * MAX;
      el.classList.add("is-magnetic");
      planifier();
    });

    el.addEventListener("pointerleave", function () {
      // Retour au repos ; la transition douce est gérée en CSS (hors is-magnetic).
      tx = 0; ty = 0;
      el.classList.remove("is-magnetic");
      planifier();
    });
  }

  function initMagnetic() {
    if (REDUIT || !POINTEUR_FIN) return;
    function scanner() {
      document.querySelectorAll(".magnetic").forEach(lierMagnetique);
    }
    scanner();
    // Les éléments peuvent arriver après le rendu des sections (data JSON).
    document.addEventListener("phoenix:sections-ready", scanner);
    document.addEventListener("phoenix:menu-ready", scanner);
  }

  /* ---------- 4. Titre héro en cascade (découpe en lettres) ---------- */
  function initHeroTitle() {
    var titre = document.querySelector(".hero-title");
    if (!titre || titre.__split) return;
    var texte = titre.textContent;
    if (!texte || !texte.trim()) return; // ne casse pas si vide
    titre.__split = true;

    var frag = document.createDocumentFragment();
    var index = 0;
    for (var i = 0; i < texte.length; i++) {
      var c = texte[i];
      var span = document.createElement("span");
      if (c === " ") {
        // Espace insécable pour préserver la césure visuelle.
        span.className = "space";
        span.innerHTML = "&nbsp;";
      } else {
        span.className = "char";
        span.textContent = c;
        span.style.setProperty("--i", index); // index pour délai échelonné CSS
        index++;
      }
      frag.appendChild(span);
    }
    titre.textContent = "";
    titre.appendChild(frag);

    // Si mouvement réduit : on affiche directement (le CSS neutralise la
    // transition sous prefers-reduced-motion) — on ajoute quand même .is-in.
    if (REDUIT) {
      titre.classList.add("is-in");
      return;
    }
    // Court délai pour déclencher l'apparition décalée gérée en CSS.
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { titre.classList.add("is-in"); });
    });
  }

  /* ---------- 5. Compteurs animés ([data-count]) ---------- */
  function animerCompteur(el) {
    if (el.__counted) return;
    el.__counted = true;

    var cible = parseFloat(el.getAttribute("data-count"));
    if (isNaN(cible)) return;
    var suffixe = el.getAttribute("data-suffix") || "";
    // Nombre de décimales à préserver (ex. 4.7 → 1, 9 → 0).
    var brut = el.getAttribute("data-count");
    var pointPos = brut.indexOf(".");
    var decimales = pointPos >= 0 ? (brut.length - pointPos - 1) : 0;

    function rendre(valeur) {
      el.textContent = valeur.toFixed(decimales) + suffixe;
    }

    // Mouvement réduit : valeur finale immédiate.
    if (REDUIT) { rendre(cible); return; }

    var DUREE = 1600; // ~1.6 s
    var debut = null;
    function etape(ts) {
      if (debut === null) debut = ts;
      var t = clamp((ts - debut) / DUREE, 0, 1);
      rendre(cible * easeOutCubic(t));
      if (t < 1) requestAnimationFrame(etape);
      else rendre(cible); // garantit la valeur exacte à la fin
    }
    requestAnimationFrame(etape);
  }

  function initCounters() {
    var cibles = document.querySelectorAll("[data-count]");
    if (!cibles.length) return;

    if (REDUIT || !("IntersectionObserver" in window)) {
      cibles.forEach(animerCompteur); // affiche directement la valeur finale
      return;
    }

    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (e) {
        if (e.isIntersecting) {
          animerCompteur(e.target);
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.4 });

    function observer() {
      document.querySelectorAll("[data-count]").forEach(function (el) {
        if (!el.__counted) obs.observe(el);
      });
    }
    observer();
    // Compteurs pouvant apparaître après remplissage des sections.
    document.addEventListener("phoenix:sections-ready", observer);
  }

  /* ---------- 6. Bandeau défilant (marquee) ---------- */
  function remplirMarquee(marquee) {
    if (marquee.__filled) return;
    var track = marquee.querySelector(".marquee__track");
    if (!track || !track.children.length) return;
    marquee.__filled = true;

    // Mouvement réduit : on laisse le contenu statique, pas de duplication.
    if (REDUIT) return;

    // Duplique le contenu pour garantir une boucle sans trou (le défilement
    // translateX est fait en CSS). On copie 2 fois (total ≈ 3× le contenu).
    var original = track.innerHTML;
    track.innerHTML = original + original + original;
    track.setAttribute("aria-hidden", "false");
  }

  function initMarquee() {
    function scanner() {
      document.querySelectorAll(".marquee").forEach(remplirMarquee);
    }
    scanner();
    document.addEventListener("phoenix:sections-ready", scanner);
  }

  /* ---------- Initialisation globale ---------- */
  function init() {
    initScrollProgress();
    initCursor();
    initMagnetic();
    initHeroTitle();
    initCounters();
    initMarquee();
  }

  // API publique minimale (rien d'autre exposé globalement).
  window.PhoenixX = {};

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
