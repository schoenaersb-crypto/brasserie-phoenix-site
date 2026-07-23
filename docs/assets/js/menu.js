/* ============================================================
   menu.js — génère le contenu du site à partir des fichiers data/*.json
   Rendu : navigation, carte, menu dégustation, annonces, infos, réseaux.
   Se redessine à chaque changement de langue.
   ============================================================ */
(function () {
  "use strict";

  var DATA = {}; // { carte, degustation, annonces, infos }

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

  /* ---------- La carte : chargée PAR CATÉGORIE, à la demande ----------
     - data/carte/index.json : ordre + en-têtes (léger, chargé une fois).
     - data/carte/<id>.<langue>.json : le détail d'une catégorie, dans la
       langue ACTIVE uniquement, chargé quand on approche la section
       (IntersectionObserver, rootMargin 400px). Squelette crème pendant
       le chargement. Erreur gérée par bloc (les autres s'affichent). */
  var carteObs = null;

  function langueCourante() {
    return (window.Phoenix && window.Phoenix.lang) || "fr";
  }

  function rendreCategorie(bloc, data) {
    var corps = bloc.querySelector(".cat-corps");
    corps.innerHTML = "";
    var plats = el("div", "plats");
    (data.items || []).forEach(function (it) { plats.appendChild(rendrePlat(it)); });
    corps.appendChild(plats);
    if (data.sauces || data.accompagnements) {
      var sous = el("div", "sous-listes");
      if (data.sauces) sous.appendChild(rendreSousListe(data.sauces));
      if (data.accompagnements) sous.appendChild(rendreSousListe(data.accompagnements));
      corps.appendChild(sous);
    }
    bloc.classList.remove("cat-loading");
    bloc.classList.add("cat-loaded");
  }

  function chargerCategorie(bloc) {
    if (bloc.getAttribute("data-loaded") === "1") return;
    bloc.setAttribute("data-loaded", "1");
    var id = bloc.getAttribute("data-cat");
    fetch("data/carte/" + id + "." + langueCourante() + ".json")
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (data) { rendreCategorie(bloc, data); })
      .catch(function (e) {
        console.error("Catégorie " + id + " indisponible", e);
        var corps = bloc.querySelector(".cat-corps");
        corps.innerHTML = "";
        corps.appendChild(el("p", "cat-erreur", t("carte.erreur") || "Chargement momentanément indisponible."));
        bloc.classList.remove("cat-loading");
      });
  }

  function rendreCarte() {
    var cont = document.getElementById("carte-contenu");
    var idx = DATA.carteIndex;
    if (!cont || !idx) return;

    cont.innerHTML = "";
    if (carteObs) { carteObs.disconnect(); carteObs = null; }

    var blocs = [];
    (idx.categories || []).forEach(function (cat) {
      var bloc = el("div", "cat-bloc cat-loading");
      bloc.setAttribute("data-cat", cat.id);
      bloc.appendChild(el("h3", "cat-titre", tr(cat.nom)));
      if (cat.note) bloc.appendChild(el("p", "cat-note", tr(cat.note)));
      var corps = el("div", "cat-corps");
      var sk = el("div", "cat-skeleton");
      for (var i = 0; i < 3; i++) sk.appendChild(el("div", "sk-ligne"));
      corps.appendChild(sk);
      bloc.appendChild(corps);
      cont.appendChild(bloc);
      blocs.push(bloc);
    });

    if ("IntersectionObserver" in window) {
      carteObs = new IntersectionObserver(function (entrees) {
        entrees.forEach(function (e) {
          if (e.isIntersecting) { chargerCategorie(e.target); carteObs.unobserve(e.target); }
        });
      }, { rootMargin: "400px 0px 400px 0px", threshold: 0 });
      blocs.forEach(function (b) { carteObs.observe(b); });
    } else {
      blocs.forEach(chargerCategorie); // repli : tout charger
    }
  }

  function chargerCarteIndex() {
    fetch("data/carte/index.json")
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (idx) { DATA.carteIndex = idx; rendreCarte(); })
      .catch(function (e) { console.error("Index de la carte indisponible", e); });
  }

  /* ---------- Menu Dégustation (5 temps, numérotés I–V) ---------- */
  function rendreDegustation() {
    var section = document.getElementById("degustation");
    var cont = document.getElementById("degustation-contenu");
    var s = DATA.degustation;
    if (!section || !cont) return;

    if (!s || !s.actif) { section.hidden = true; return; }
    section.hidden = false;

    var titre = document.getElementById("degustation-titre");
    var sous = document.getElementById("degustation-soustitre");
    if (titre) titre.textContent = tr(s.titre);
    if (sous) sous.textContent = tr(s.sous_titre);

    cont.innerHTML = "";

    // Prix du menu (badge) — ex. « 37,50 € »
    if (s.prix) {
      var badge = el("div", "degust-prix");
      badge.appendChild(el("span", "degust-prix-montant", tr(s.prix)));
      if (tr(s.prix_note)) badge.appendChild(el("span", "degust-prix-note", tr(s.prix_note)));
      cont.appendChild(badge);
    }

    // Les cinq temps, en fil vertical numéroté
    var liste = el("ol", "degust-temps");
    (s.temps || []).forEach(function (temps) {
      var li = el("li", "degust-item");
      li.appendChild(el("span", "degust-num", temps.num || ""));

      var body = el("div", "degust-body");
      if (tr(temps.label)) body.appendChild(el("span", "degust-label", tr(temps.label)));

      if (temps.choix && temps.items) {
        // Plat au choix : options séparées par « ou »
        var choix = el("div", "degust-choix");
        temps.items.forEach(function (it, idx) {
          if (idx > 0) choix.appendChild(el("span", "degust-ou", tr(s.choix_ou) || "ou"));
          var opt = el("div", "degust-option");
          var tete = el("div", "degust-tete");
          if (tr(it.tag)) tete.appendChild(el("span", "degust-tag", tr(it.tag)));
          tete.appendChild(el("span", "degust-nom", tr(it.nom)));
          opt.appendChild(tete);
          if (tr(it.desc)) opt.appendChild(el("p", "degust-desc", tr(it.desc)));
          choix.appendChild(opt);
        });
        body.appendChild(choix);
      } else {
        body.appendChild(el("h4", "degust-nom", tr(temps.nom)));
        if (tr(temps.desc)) body.appendChild(el("p", "degust-desc", tr(temps.desc)));
      }
      li.appendChild(body);
      liste.appendChild(li);
    });
    cont.appendChild(liste);
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

    // Bloc horaires (3 sous-blocs : Brasserie / Cuisine / Chiringuito)
    if (i.horaires && (i.horaires.blocs || i.horaires.lignes)) {
      var h = el("div", "info-bloc");
      h.appendChild(el("h3", null, t("sections.horaires_titre") || "Horaires"));

      var blocs = i.horaires.blocs || [{ titre: i.horaires.note, lignes: i.horaires.lignes }];
      blocs.forEach(function (b) {
        if (b.titre) h.appendChild(el("h4", "horaire-titre", tr(b.titre)));
        var ul = el("ul", "info-horaires");
        (b.lignes || []).forEach(function (ligne) {
          var li = el("li");
          li.appendChild(el("span", null, tr(ligne.jours)));
          var heures = typeof ligne.heures === "string" ? ligne.heures : tr(ligne.heures);
          li.appendChild(el("span", null, heures));
          ul.appendChild(li);
        });
        h.appendChild(ul);
      });
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
    rendreDegustation();
    rendreAnnonces();
    rendreInfos();
    rendreSocial();
  }

  /* ---------- Chargement des données ----------
     Chaque fichier est chargé INDÉPENDAMMENT : si l'un échoue (réseau,
     etc.), les autres sections s'affichent quand même. La carte ne
     dépend donc plus du chargement des infos/annonces. */
  function chargerUn(nom, url, rendre) {
    fetch(url)
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (d) { DATA[nom] = d; try { rendre(); } catch (e) { console.error("Rendu " + nom, e); } })
      .catch(function (e) { console.error("Chargement " + nom + " impossible", e); });
  }

  function charger() {
    rendreNav();
    chargerCarteIndex();
    chargerUn("degustation", "data/menu-degustation.json", rendreDegustation);
    chargerUn("annonces", "data/annonces.json", rendreAnnonces);
    chargerUn("infos", "data/infos.json", function () { rendreInfos(); rendreSocial(); });
    if (window.Phoenix) window.Phoenix.onLangChange(rendreTout);
  }

  // année du footer
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  // On attend i18n (pour les traductions), mais avec un filet de sécurité :
  // si l'événement tarde ou n'arrive jamais, on charge quand même les données
  // (les fichiers de contenu contiennent déjà leurs 4 langues, repli FR).
  var demarre = false;
  function lancer() { if (demarre) return; demarre = true; charger(); }

  if (window.Phoenix && window.Phoenix.t("nav.accueil")) {
    lancer();
  } else {
    document.addEventListener("phoenix:i18n-ready", lancer, { once: true });
    setTimeout(lancer, 4000);
  }
})();
