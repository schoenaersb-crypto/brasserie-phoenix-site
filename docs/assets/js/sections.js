/* ============================================================
   sections.js — rend les sections du redesign à partir des data/*.json :
     · L'esprit Phoenix (récit)   → data/esprit.json
     · Plats signature            → data/signature.json
     · Galerie + visionneuse      → data/galerie.json
     · Avis clients               → data/avis.json
   Se redessine à chaque changement de langue. Aucune dépendance externe.
   ============================================================ */
(function () {
  "use strict";

  var DATA = {}; // { esprit, signature, galerie, avis }

  function tr(v) { return window.Phoenix ? window.Phoenix.tr(v) : (v && v.fr) || ""; }
  function t(p) { return window.Phoenix ? window.Phoenix.t(p) : ""; }
  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function montrer(id, visible) {
    var s = document.getElementById(id);
    if (s) s.hidden = !visible;
  }

  /* Crée une <img> en chargement anticipé (data-src + placeholder crème).
     Le chargement réel est déclenché par ui.js (IntersectionObserver,
     rootMargin ~500px), pour que l'image soit prête avant d'entrer à l'écran. */
  function imgLazy(src, alt) {
    var im = document.createElement("img");
    im.alt = alt || "";
    im.setAttribute("decoding", "async");
    im.setAttribute("loading", "lazy");
    im.className = "lazyimg";
    im.dataset.src = src;
    return im;
  }

  /* ---------- L'esprit Phoenix (récit) ---------- */
  function rendreEsprit() {
    var d = DATA.esprit;
    if (!d || !d.actif) { montrer("esprit", false); return; }
    montrer("esprit", true);

    var img = document.getElementById("esprit-image");
    if (img && d.image) {
      img.alt = tr(d.image_alt);
      img.setAttribute("decoding", "async");
      img.classList.add("lazyimg");
      img.removeAttribute("src");
      img.dataset.src = d.image;
    }

    var sur = document.getElementById("esprit-surtitre");
    if (sur) sur.textContent = tr(d.sur_titre);
    var titre = document.getElementById("esprit-titre");
    if (titre) titre.textContent = tr(d.titre);

    var paras = document.getElementById("esprit-paragraphes");
    if (paras) {
      paras.innerHTML = "";
      (d.paragraphes || []).forEach(function (p) { paras.appendChild(el("p", null, tr(p))); });
    }

    var reperes = document.getElementById("esprit-reperes");
    if (reperes) {
      reperes.innerHTML = "";
      (d.reperes || []).forEach(function (r) {
        var li = el("li");
        li.appendChild(el("span", "repere-valeur", r.valeur));
        li.appendChild(el("span", "repere-texte", tr(r.texte)));
        reperes.appendChild(li);
      });
    }
  }

  /* ---------- Plats signature ---------- */
  function rendreSignature() {
    var d = DATA.signature;
    var cont = document.getElementById("signature-contenu");
    if (!d || !d.actif || !cont) { montrer("signature", false); return; }
    montrer("signature", true);
    cont.innerHTML = "";

    (d.plats || []).forEach(function (p) {
      var card = el("article", "sig-card");

      var media = el("div", "sig-media");
      media.appendChild(imgLazy(p.image, tr(p.nom)));
      if (p.etiquette && tr(p.etiquette)) media.appendChild(el("span", "sig-tag", tr(p.etiquette)));
      card.appendChild(media);

      var corps = el("div", "sig-corps");
      var tete = el("div", "sig-tete");
      tete.appendChild(el("h3", "sig-nom", tr(p.nom)));
      var prixTxt = p.prix ? p.prix : (p.prix_texte ? tr(p.prix_texte) : "");
      if (prixTxt) tete.appendChild(el("span", "sig-prix" + (p.prix ? "" : " sig-prix-jour"), prixTxt));
      corps.appendChild(tete);
      var desc = tr(p.desc);
      if (desc) corps.appendChild(el("p", "sig-desc", desc));
      card.appendChild(corps);

      cont.appendChild(card);
    });
  }

  /* ---------- Galerie ---------- */
  var galerieImages = []; // [{src, legende}] dans l'ordre affiché

  function rendreGalerie() {
    var d = DATA.galerie;
    var cont = document.getElementById("galerie-contenu");
    if (!d || !d.actif || !cont) { montrer("galerie", false); return; }
    montrer("galerie", true);
    cont.innerHTML = "";
    galerieImages = (d.images || []).map(function (im) { return { src: im.src, legende: tr(im.legende) }; });

    galerieImages.forEach(function (im, i) {
      var btn = el("button", "gal-item");
      btn.type = "button";
      btn.setAttribute("aria-label", im.legende || ("Image " + (i + 1)));
      btn.appendChild(imgLazy(im.src, im.legende || ""));
      btn.appendChild(el("span", "gal-legende", im.legende));
      btn.addEventListener("click", function () { ouvrirLightbox(i); });
      cont.appendChild(btn);
    });
  }

  /* ---------- Visionneuse (lightbox) ---------- */
  var lbIndex = 0;
  var declencheur = null; // élément à re-focaliser à la fermeture

  function majLightbox() {
    var im = galerieImages[lbIndex];
    if (!im) return;
    var img = document.getElementById("lightbox-img");
    var cap = document.getElementById("lightbox-caption");
    if (img) { img.src = im.src; img.alt = im.legende || ""; }
    if (cap) cap.textContent = im.legende || "";
  }

  function ouvrirLightbox(i) {
    if (!galerieImages.length) return;
    lbIndex = i;
    declencheur = document.activeElement;
    majLightbox();
    var lb = document.getElementById("lightbox");
    if (!lb) return;
    lb.hidden = false;
    document.body.classList.add("no-scroll");
    var close = document.getElementById("lightbox-close");
    if (close) close.focus();
  }

  function fermerLightbox() {
    var lb = document.getElementById("lightbox");
    if (!lb) return;
    lb.hidden = true;
    document.body.classList.remove("no-scroll");
    if (declencheur && declencheur.focus) declencheur.focus();
  }

  function naviguer(pas) {
    if (!galerieImages.length) return;
    lbIndex = (lbIndex + pas + galerieImages.length) % galerieImages.length;
    majLightbox();
  }

  function initLightbox() {
    var lb = document.getElementById("lightbox");
    if (!lb) return;
    var close = document.getElementById("lightbox-close");
    var prev = document.getElementById("lightbox-prev");
    var next = document.getElementById("lightbox-next");
    if (close) close.addEventListener("click", fermerLightbox);
    if (prev) prev.addEventListener("click", function () { naviguer(-1); });
    if (next) next.addEventListener("click", function () { naviguer(1); });
    // clic sur le fond (hors image/boutons) ferme
    lb.addEventListener("click", function (e) { if (e.target === lb) fermerLightbox(); });
    // clavier : Échap ferme, flèches naviguent, Tab reste dans la boîte
    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") { fermerLightbox(); }
      else if (e.key === "ArrowLeft") { naviguer(-1); }
      else if (e.key === "ArrowRight") { naviguer(1); }
      else if (e.key === "Tab") { piegerFocus(e, lb); }
    });
  }

  function piegerFocus(e, boite) {
    var focusables = boite.querySelectorAll("button, [href], img[tabindex]");
    if (!focusables.length) return;
    var premier = focusables[0], dernier = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === premier) { e.preventDefault(); dernier.focus(); }
    else if (!e.shiftKey && document.activeElement === dernier) { e.preventDefault(); premier.focus(); }
  }

  /* ---------- Avis (macaron 9/10 + citations réelles) ---------- */
  function rendreAvis() {
    var d = DATA.avis;
    var cont = document.getElementById("avis-contenu");
    var mac = document.getElementById("avis-macaron");
    if (!d || !d.actif || !cont) { montrer("avis", false); return; }
    montrer("avis", true);

    // Macaron : note globale + nombre d'avis (preuve sociale, sans lien TheFork)
    if (mac) {
      mac.innerHTML = "";
      if (d.note_globale) mac.appendChild(el("span", "macaron-note", d.note_globale));
      var det = el("div", "macaron-detail");
      if (d.nombre_avis) det.appendChild(el("span", "macaron-nb", tr(d.nombre_avis)));
      if (d.source) det.appendChild(el("span", "macaron-src", tr(d.source)));
      mac.appendChild(det);
    }

    cont.innerHTML = "";
    (d.avis || []).forEach(function (a) {
      var card = el("figure", "avis-card");

      // note : étoiles (nombre ≤ 5) ou pastille texte (ex. "10/10")
      if (a.note != null) {
        if (typeof a.note === "number") {
          var n = Math.max(0, Math.min(5, a.note));
          var st = el("span", "avis-note");
          st.setAttribute("aria-label", n + "/5");
          for (var i = 0; i < 5; i++) st.appendChild(el("span", "etoile" + (i < n ? " pleine" : ""), "★"));
          card.appendChild(st);
        } else {
          card.appendChild(el("span", "avis-note-txt", a.note));
        }
      }

      var bloc = el("blockquote", "avis-texte");
      bloc.textContent = "« " + tr(a.texte) + " »";
      card.appendChild(bloc);

      if (a.auteur || a.source) {
        var pied = el("figcaption", "avis-pied");
        if (a.auteur) pied.appendChild(el("span", "avis-auteur", a.auteur));
        if (a.source) pied.appendChild(el("span", "avis-source", tr(a.source)));
        card.appendChild(pied);
      }
      cont.appendChild(card);
    });
  }

  /* ---------- Rendu global ---------- */
  function rendreTout() {
    rendreEsprit();
    rendreSignature();
    rendreGalerie();
    rendreAvis();
    // signale aux autres scripts (apparitions + chargement anticipé des images)
    // que du contenu vient d'arriver / d'être redessiné
    document.dispatchEvent(new CustomEvent("phoenix:sections-ready"));
  }

  /* ---------- Chargement ---------- */
  function charger() {
    var urls = {
      esprit: "data/esprit.json",
      signature: "data/signature.json",
      galerie: "data/galerie.json",
      avis: "data/avis.json"
    };
    Promise.all(Object.keys(urls).map(function (nom) {
      return fetch(urls[nom])
        .then(function (r) { return r.json(); })
        .then(function (d) { DATA[nom] = d; })
        .catch(function () { DATA[nom] = null; });
    })).then(function () {
      rendreTout();
      if (window.Phoenix) window.Phoenix.onLangChange(rendreTout);
    });
  }

  initLightbox();

  if (window.Phoenix && window.Phoenix.t("nav.accueil")) {
    charger();
  } else {
    document.addEventListener("phoenix:i18n-ready", charger, { once: true });
  }
})();
