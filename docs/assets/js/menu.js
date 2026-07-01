/* ============================================================
   menu.js — génère le contenu du site à partir des fichiers data/*.json
   Rendu : navigation, carte, menu de la semaine, annonces, infos, réseaux.
   Se redessine à chaque changement de langue.
   ============================================================ */
(function () {
  "use strict";

  var DATA = {}; // { carte, semaine, annonces, infos }

  function tr(v) { return window.Phoenix ? window.Phoenix.tr(v) : (v && v.fr) || ""; }
  function t(p) { return window.Phoenix ? window.Phoenix.t(p) : ""; }
  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }

  /* ---------- Navigation (libellés traduits) ---------- */
  function rendreNav() {
    document.querySelectorAll("[data-nav]").forEach(function (a) {
      var txt = t("nav." + a.getAttribute("data-nav"));
      if (txt) a.textContent = txt;
    });
  }

  /* ---------- Un plat (ligne de carte) ---------- */
  function rendrePlat(item, options) {
    options = options || {};
    var wrap = el("article", "plat" + (item.coup_de_coeur ? " is-cdc" : ""));

    var tete = el("div", "plat-tete");
    tete.appendChild(el("span", "plat-nom", tr(item.nom)));
    if (item.origine && tr(item.origine)) tete.appendChild(el("span", "plat-origine", tr(item.origine)));
    if (item.coup_de_coeur) tete.appendChild(el("span", "badge-cdc", t("labels.coup_de_coeur")));
    wrap.appendChild(tete);

    // prix (normal ou "prix du jour")
    var prixTxt = item.prix_special ? tr(item.prix_texte) : item.prix;
    var prix = el("span", "plat-prix" + (item.prix_special ? " special" : ""), prixTxt);
    wrap.appendChild(prix);

    var desc = tr(item.desc);
    if (desc) wrap.appendChild(el("p", "plat-desc", desc));

    return wrap;
  }

  /* ---------- Sous-listes (sauces / accompagnements des viandes) ---------- */
  function rendreSousListe(bloc) {
    var b = el("div", "sous-bloc");
    b.appendChild(el("h4", null, tr(bloc.titre)));
    var ul = el("ul");
    bloc.liste.forEach(function (x) { ul.appendChild(el("li", null, tr(x))); });
    b.appendChild(ul);
    return b;
  }

  /* ---------- La carte complète ---------- */
  function rendreCarte() {
    var cont = document.getElementById("carte-contenu");
    if (!cont || !DATA.carte) return;
    cont.innerHTML = "";

    DATA.carte.categories.forEach(function (cat) {
      var bloc = el("div", "cat-bloc");
      bloc.appendChild(el("h3", "cat-titre", tr(cat.nom)));
      if (cat.note) bloc.appendChild(el("p", "cat-note", tr(cat.note)));

      var plats = el("div", "plats");
      cat.items.forEach(function (it) { plats.appendChild(rendrePlat(it)); });
      bloc.appendChild(plats);

      // viandes : sauces + accompagnements
      if (cat.sauces || cat.accompagnements) {
        var sous = el("div", "sous-listes");
        if (cat.sauces) sous.appendChild(rendreSousListe(cat.sauces));
        if (cat.accompagnements) sous.appendChild(rendreSousListe(cat.accompagnements));
        bloc.appendChild(sous);
      }
      cont.appendChild(bloc);
    });
  }

  /* ---------- Menu de la semaine ---------- */
  function rendreSemaine() {
    var section = document.getElementById("semaine");
    var cont = document.getElementById("semaine-contenu");
    var s = DATA.semaine;
    if (!section || !cont) return;

    if (!s || !s.actif) { section.hidden = true; return; }
    section.hidden = false;

    var titre = document.getElementById("semaine-titre");
    var sous = document.getElementById("semaine-soustitre");
    if (titre) titre.textContent = tr(s.titre);
    if (sous) sous.textContent = tr(s.sous_titre);

    cont.innerHTML = "";
    (s.plats || []).forEach(function (p) {
      var c = el("div", "semaine-plat");
      var tete = el("div", "plat-tete");
      tete.appendChild(el("span", "plat-nom", tr(p.nom)));
      if (p.prix) tete.appendChild(el("span", "plat-prix", p.prix));
      c.appendChild(tete);
      var d = tr(p.desc);
      if (d) c.appendChild(el("p", "plat-desc", d));
      cont.appendChild(c);
    });
  }

  /* ---------- Bandeau annonces ---------- */
  function rendreAnnonces() {
    var box = document.getElementById("annonces");
    var a = DATA.annonces;
    if (!box) return;
    if (!a || !a.actif || !a.annonces || !a.annonces.length) { box.hidden = true; return; }
    box.hidden = false;
    box.className = "annonces ton-" + (a.annonces[0].ton || "info");
    box.innerHTML = "";
    a.annonces.forEach(function (an) { box.appendChild(el("p", null, tr(an.texte))); });
  }

  /* ---------- Infos pratiques ---------- */
  function rendreInfos() {
    var cont = document.getElementById("infos-contenu");
    var i = DATA.infos;
    if (!cont || !i) return;
    cont.innerHTML = "";

    // Bloc contact
    var contact = el("div", "info-bloc");
    contact.appendChild(el("h3", null, i.nom));
    contact.appendChild(el("p", null, i.adresse));
    var pTel = el("p");
    var aTel = el("a", "lien-fort", i.telephone_affiche);
    aTel.href = "tel:" + i.telephone_affiche.replace(/\s/g, "");
    pTel.appendChild(aTel);
    contact.appendChild(pTel);
    var pMail = el("p");
    var aMail = el("a", "lien-fort", i.email);
    aMail.href = "mailto:" + i.email;
    pMail.appendChild(aMail);
    contact.appendChild(pMail);
    var iframe = document.createElement("iframe");
    iframe.className = "info-map";
    iframe.loading = "lazy";
    iframe.title = "Plan";
    iframe.src = "https://maps.google.com/maps?q=" +
      encodeURIComponent("Brasserie Phoenix, Av. Desiderio Rodríguez 37, Torrevieja") +
      "&output=embed";
    contact.appendChild(iframe);
    cont.appendChild(contact);

    // Bloc horaires
    if (i.horaires) {
      var h = el("div", "info-bloc");
      h.appendChild(el("h3", null, tr(i.horaires.note)));
      var ul = el("ul", "info-horaires");
      (i.horaires.lignes || []).forEach(function (ligne) {
        var li = el("li");
        li.appendChild(el("span", null, tr(ligne.jours)));
        li.appendChild(el("span", null, ligne.heures));
        ul.appendChild(li);
      });
      h.appendChild(ul);
      cont.appendChild(h);
    }
  }

  /* ---------- Réseaux (footer) ---------- */
  function rendreSocial() {
    var box = document.getElementById("footer-social");
    var i = DATA.infos;
    if (!box || !i || !i.reseaux) return;
    box.innerHTML = "";
    var libelle = t("footer.suivez");
    if (libelle) { var lab = el("span"); lab.textContent = libelle + " :"; box.appendChild(lab); }
    var noms = { instagram: "Instagram", facebook: "Facebook", tiktok: "TikTok" };
    Object.keys(i.reseaux).forEach(function (k) {
      if (!i.reseaux[k]) return;
      var a = el("a", null, noms[k] || k);
      a.href = i.reseaux[k]; a.target = "_blank"; a.rel = "noopener";
      box.appendChild(a);
    });
  }

  /* ---------- Tout (re)dessiner ---------- */
  function rendreTout() {
    rendreNav();
    rendreCarte();
    rendreSemaine();
    rendreAnnonces();
    rendreInfos();
    rendreSocial();
  }

  /* ---------- Chargement des données ---------- */
  function charger() {
    var fichiers = ["carte", "semaine", "annonces", "infos"];
    var urls = {
      carte: "data/carte.json",
      semaine: "data/menu-semaine.json",
      annonces: "data/annonces.json",
      infos: "data/infos.json"
    };
    Promise.all(fichiers.map(function (nom) {
      return fetch(urls[nom]).then(function (r) { return r.json(); }).then(function (d) { DATA[nom] = d; });
    })).then(function () {
      rendreTout();
      if (window.Phoenix) window.Phoenix.onLangChange(rendreTout);
    }).catch(function (e) { console.error("Erreur de chargement des données", e); });
  }

  // année du footer
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  // on attend que i18n soit prêt (pour disposer des traductions), sinon on charge quand même
  if (window.Phoenix && window.Phoenix.t("nav.accueil")) {
    charger();
  } else {
    document.addEventListener("phoenix:i18n-ready", charger, { once: true });
  }
})();
