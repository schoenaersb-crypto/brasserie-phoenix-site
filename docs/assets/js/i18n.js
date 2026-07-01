/* ============================================================
   i18n.js — moteur multilingue (FR / NL / ES / EN)
   - Détecte la langue du navigateur, repli sur le français.
   - Mémorise le choix dans localStorage.
   - Remplit les éléments [data-ui="chemin.vers.texte"].
   - Expose window.Phoenix.{lang, t(), onLangChange()} pour menu.js / reservation.js.
   ============================================================ */
(function () {
  "use strict";

  var LANGUES = ["fr", "nl", "es", "en"];
  var DEFAUT = "fr";
  var CLE_STOCKAGE = "phoenix_lang";

  var ui = null;                 // contenu de data/ui.json
  var lang = DEFAUT;
  var abonnes = [];              // callbacks appelés à chaque changement de langue

  /* Récupère une valeur imbriquée via un chemin "a.b.c" */
  function chemin(obj, path) {
    return path.split(".").reduce(function (o, k) {
      return (o && o[k] !== undefined) ? o[k] : undefined;
    }, obj);
  }

  /* Traduit un objet {fr,nl,es,en} vers la langue courante (repli FR puis 1re dispo) */
  function tr(valeur) {
    if (valeur == null) return "";
    if (typeof valeur === "string") return valeur;
    if (valeur[lang]) return valeur[lang];
    if (valeur[DEFAUT]) return valeur[DEFAUT];
    for (var k in valeur) { if (valeur[k]) return valeur[k]; }
    return "";
  }

  /* Traduit un libellé d'interface via son chemin dans ui.json (ex "hero.slogan") */
  function t(path) { return tr(chemin(ui, path)); }

  /* Détermine la langue initiale : stockage > navigateur > défaut */
  function langueInitiale() {
    var sauvee = null;
    try { sauvee = localStorage.getItem(CLE_STOCKAGE); } catch (e) {}
    if (sauvee && LANGUES.indexOf(sauvee) !== -1) return sauvee;
    var nav = (navigator.language || navigator.userLanguage || DEFAUT).slice(0, 2).toLowerCase();
    return LANGUES.indexOf(nav) !== -1 ? nav : DEFAUT;
  }

  /* Applique la langue : maj <html lang>, remplit les [data-ui], notifie les abonnés */
  function appliquer() {
    document.documentElement.setAttribute("lang", lang);

    var els = document.querySelectorAll("[data-ui]");
    els.forEach(function (el) {
      var val = t(el.getAttribute("data-ui"));
      if (val) el.textContent = val;
    });

    // état visuel des boutons de langue
    var boutons = document.querySelectorAll("#lang-switch button");
    boutons.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false");
    });

    abonnes.forEach(function (cb) { try { cb(lang); } catch (e) { console.error(e); } });
  }

  function setLang(nouvelle) {
    if (LANGUES.indexOf(nouvelle) === -1) return;
    lang = nouvelle;
    try { localStorage.setItem(CLE_STOCKAGE, lang); } catch (e) {}
    appliquer();
  }

  /* Construit les boutons de langue à partir de ui.langues */
  function construireSelecteur() {
    var box = document.getElementById("lang-switch");
    if (!box || !ui.langues) return;
    box.innerHTML = "";
    ui.langues.forEach(function (l) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = l.label;
      b.setAttribute("data-lang", l.code);
      b.setAttribute("aria-label", l.nom);
      b.addEventListener("click", function () { setLang(l.code); });
      box.appendChild(b);
    });
  }

  /* API publique pour les autres scripts */
  window.Phoenix = {
    get lang() { return lang; },
    t: t,
    tr: tr,
    setLang: setLang,
    onLangChange: function (cb) { if (typeof cb === "function") abonnes.push(cb); }
  };

  /* Démarrage : charge ui.json puis initialise */
  fetch("data/ui.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      ui = data;
      lang = langueInitiale();
      construireSelecteur();
      appliquer();
      document.dispatchEvent(new CustomEvent("phoenix:i18n-ready"));
    })
    .catch(function (e) {
      console.error("Impossible de charger ui.json", e);
    });
})();
