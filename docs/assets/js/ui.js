/* ============================================================
   ui.js — comportements d'interface du redesign :
     · Menu mobile (hamburger) avec accessibilité clavier
     · État "réduit" de l'en-tête au défilement
     · Apparition en fondu des sections (reveal on scroll)
     · Traduction des libellés aria (data-ui-label)
   Aucune dépendance externe.
   ============================================================ */
(function () {
  "use strict";

  /* ---------- Menu mobile (hamburger) ---------- */
  function initNav() {
    var toggle = document.getElementById("nav-toggle");
    var nav = document.getElementById("main-nav");
    var backdrop = document.getElementById("nav-backdrop");
    if (!toggle || !nav) return;

    function label(cle, repli) {
      return (window.Phoenix && window.Phoenix.t(cle)) || repli;
    }

    function ouvrir(etat) {
      document.body.classList.toggle("nav-open", etat);
      toggle.setAttribute("aria-expanded", etat ? "true" : "false");
      toggle.setAttribute("aria-label", etat ? label("a11y.fermer_menu", "Fermer le menu")
                                             : label("a11y.ouvrir_menu", "Ouvrir le menu"));
      if (backdrop) backdrop.hidden = !etat;
    }

    toggle.addEventListener("click", function () {
      ouvrir(!document.body.classList.contains("nav-open"));
    });

    // fermer au clic sur un lien, sur le voile, ou avec Échap
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") ouvrir(false);
    });
    if (backdrop) backdrop.addEventListener("click", function () { ouvrir(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("nav-open")) ouvrir(false);
    });

    // repli sur bureau si on élargit la fenêtre
    window.addEventListener("resize", function () {
      if (window.innerWidth >= 760 && document.body.classList.contains("nav-open")) ouvrir(false);
    });
  }

  /* ---------- En-tête réduit au défilement ---------- */
  function initHeader() {
    var header = document.getElementById("site-header");
    if (!header) return;
    function maj() {
      header.classList.toggle("is-scrolled", window.scrollY > 12);
    }
    maj();
    window.addEventListener("scroll", maj, { passive: true });
  }

  /* ---------- Scrollspy : surligne le lien de la section visible ---------- */
  function initScrollSpy() {
    var liens = {};
    document.querySelectorAll('.main-nav a[href^="#"]').forEach(function (a) {
      liens[a.getAttribute("href").slice(1)] = a;
    });
    if (!("IntersectionObserver" in window)) return;

    var courant = null;
    function activer(id) {
      if (courant === id) return;
      courant = id;
      Object.keys(liens).forEach(function (k) { liens[k].removeAttribute("aria-current"); });
      if (liens[id]) liens[id].setAttribute("aria-current", "true");
    }

    var spy = new IntersectionObserver(function (entrees) {
      var visibles = entrees.filter(function (e) { return e.isIntersecting; });
      if (!visibles.length) return;
      // la section active = celle dont le haut est le plus proche du milieu de l'écran
      visibles.sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
      activer(visibles[0].target.id);
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });

    function observer() {
      Object.keys(liens).forEach(function (id) {
        var sec = document.getElementById(id);
        if (sec) spy.observe(sec);
      });
    }
    observer();
    // ré-observer les sections révélées après remplissage (data JSON)
    document.addEventListener("phoenix:sections-ready", observer);
  }

  /* ---------- Apparition des sections au défilement ---------- */
  function initReveal() {
    var cibles = document.querySelectorAll(".reveal");
    if (!cibles.length) return;

    // repli : si pas d'IntersectionObserver ou mouvement réduit, tout afficher
    var reduit = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduit || !("IntersectionObserver" in window)) {
      cibles.forEach(function (c) { c.classList.add("visible"); });
      return;
    }

    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (entree) {
        if (entree.isIntersecting) {
          entree.target.classList.add("visible");
          obs.unobserve(entree.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });

    cibles.forEach(function (c) { obs.observe(c); });

    // quand les sections cachées (hidden) sont remplies puis affichées, les (ré)observer
    document.addEventListener("phoenix:sections-ready", function () {
      document.querySelectorAll(".reveal:not(.visible)").forEach(function (c) {
        if (!c.hidden) obs.observe(c);
      });
    });
  }

  /* ---------- Chargement anticipé des images (lazy + IntersectionObserver) ----------
     Les images marquées .lazyimg[data-src] commencent à charger ~500 px AVANT
     d'entrer dans le viewport : au défilement, l'image suivante est déjà prête,
     sans trou blanc (un fond crème sert de placeholder, fondu à l'arrivée). */
  var lazyObserver = null;

  function chargerImage(img) {
    if (!img.dataset.src) return;
    img.addEventListener("load", function () { img.classList.add("is-loaded"); }, { once: true });
    img.addEventListener("error", function () { img.classList.add("is-loaded"); }, { once: true });
    img.src = img.dataset.src;
    img.removeAttribute("data-src");
  }

  function scanLazy() {
    var imgs = document.querySelectorAll("img.lazyimg[data-src]");
    if (lazyObserver) {
      imgs.forEach(function (img) { lazyObserver.observe(img); });
    } else {
      // repli sans IntersectionObserver : on charge tout de suite
      imgs.forEach(chargerImage);
    }
  }

  function initLazy() {
    if ("IntersectionObserver" in window) {
      lazyObserver = new IntersectionObserver(function (entrees) {
        entrees.forEach(function (e) {
          if (e.isIntersecting) { chargerImage(e.target); lazyObserver.unobserve(e.target); }
        });
      }, { rootMargin: "500px 0px 500px 0px", threshold: 0 });
    }
    scanLazy();
    // rescanner quand de nouvelles images arrivent (rendu des sections, langue)
    document.addEventListener("phoenix:sections-ready", scanLazy);
    document.addEventListener("phoenix:menu-ready", scanLazy);
  }

  /* ---------- Traduction des libellés aria (data-ui-label) ---------- */
  function appliquerLabels() {
    if (!window.Phoenix) return;
    document.querySelectorAll("[data-ui-label]").forEach(function (elem) {
      var val = window.Phoenix.t(elem.getAttribute("data-ui-label"));
      // ne pas écraser le libellé "ouvrir/fermer" dynamique du hamburger déjà géré
      if (val && elem.id !== "nav-toggle") elem.setAttribute("aria-label", val);
    });
  }

  function init() {
    initNav();
    initHeader();
    initScrollSpy();
    initReveal();
    initLazy();
    appliquerLabels();
    if (window.Phoenix) window.Phoenix.onLangChange(appliquerLabels);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
