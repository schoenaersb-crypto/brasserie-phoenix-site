/* ============================================================
   reservation.js — génère un message pré-rempli vers WhatsApp ou email
   Aucun serveur : on ouvre simplement wa.me / mailto avec le texte.
   ============================================================ */
(function () {
  "use strict";

  /* ============================================================
     CIBLE DE RÉSERVATION — point unique à modifier
     ------------------------------------------------------------
     Aujourd'hui : WhatsApp + email (aucun serveur, aucune donnée stockée).
     Le numéro / l'email viennent de data/infos.json.

     👉 POUR BRANCHER UN VRAI MOTEUR DE RÉSERVATION plus tard
        (widget, TheFork, Zenchef, SevenRooms, lien maison…),
        il suffit de changer 'mode' ci-dessous et, le cas échéant,
        de renseigner 'url'. Rien d'autre dans le code n'est à toucher.

        mode: "whatsapp_email"  → comportement actuel (2 boutons)
        mode: "url"             → redirige vers RESERVATION.url (moteur externe)
     ============================================================ */
  var RESERVATION = {
    mode: "whatsapp_email",
    url: "",                 // ex. "https://widget.mon-moteur.com/brasserie-phoenix"
    ouvrir_dans_nouvel_onglet: true
  };

  /* ============================================================
     HORAIRES DE CUISINE — créneaux de réservation
     ------------------------------------------------------------
     La salle est ouverte du jeudi au lundi ; la CUISINE sert
     déjeuner 12h00–15h00 et dîner 18h00–22h00. On propose donc des
     créneaux (dernière prise de commande ~30 min avant la fermeture
     de la cuisine), et on bloque mardi et mercredi (fermeture salle).
     ============================================================ */
  var JOURS_FERMES = [2, 3]; // 0=dimanche … 2=mardi, 3=mercredi
  var SERVICES = {
    dejeuner: ["12:00", "12:30", "13:00", "13:30", "14:00", "14:30"],
    diner:    ["18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30"]
  };

  var infos = null;

  function t(p) { return window.Phoenix ? window.Phoenix.t(p) : ""; }

  /* Remplit un modèle "…{cle}…" avec les valeurs du formulaire */
  function remplir(modele, valeurs) {
    return modele.replace(/\{(\w+)\}/g, function (_, cle) {
      return valeurs[cle] != null && valeurs[cle] !== "" ? valeurs[cle] : "—";
    });
  }

  /* Jour de la semaine d'une date "YYYY-MM-DD" (en local, sans décalage UTC) */
  function jourSemaine(valeur) {
    var p = (valeur || "").split("-");
    if (p.length !== 3) return -1;
    return new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2])).getDay();
  }

  function estJourFerme(valeur) {
    return JOURS_FERMES.indexOf(jourSemaine(valeur)) !== -1;
  }

  function lireFormulaire() {
    var svc = document.getElementById("r-service");
    return {
      date: document.getElementById("r-date").value,
      service: svc ? (svc.options[svc.selectedIndex] ? svc.options[svc.selectedIndex].textContent : "") : "",
      heure: document.getElementById("r-creneau").value,
      personnes: document.getElementById("r-personnes").value,
      nom: document.getElementById("r-nom").value.trim(),
      telephone: document.getElementById("r-tel").value.trim()
    };
  }

  function valide(v) {
    return v.date && !estJourFerme(v.date) && v.heure && v.personnes && v.nom;
  }

  function afficherErreur(montrer, cle) {
    var box = document.getElementById("form-erreur");
    if (!box) return;
    if (montrer) { box.textContent = t(cle || "form.requis"); box.hidden = false; }
    else { box.hidden = true; }
  }

  /* Remplit le sélecteur de service (déjeuner / dîner) */
  function remplirServices() {
    var sel = document.getElementById("r-service");
    if (!sel) return;
    var courant = sel.value;
    sel.innerHTML = "";
    [["dejeuner", "form.service_dejeuner"], ["diner", "form.service_diner"]].forEach(function (s) {
      var o = document.createElement("option");
      o.value = s[0];
      o.textContent = t(s[1]) || s[0];
      sel.appendChild(o);
    });
    if (courant) sel.value = courant;
    remplirCreneaux();
  }

  /* Remplit les créneaux horaires selon le service choisi */
  function remplirCreneaux() {
    var sel = document.getElementById("r-service");
    var cre = document.getElementById("r-creneau");
    if (!sel || !cre) return;
    var courant = cre.value;
    var liste = SERVICES[sel.value] || SERVICES.dejeuner;
    cre.innerHTML = "";
    liste.forEach(function (h) {
      var o = document.createElement("option");
      o.value = h; o.textContent = h;
      cre.appendChild(o);
    });
    if (liste.indexOf(courant) !== -1) cre.value = courant;
  }

  function construireMessage() {
    var v = lireFormulaire();
    if (v.date && estJourFerme(v.date)) { afficherErreur(true, "form.ferme_jour"); return null; }
    if (!valide(v)) { afficherErreur(true, "form.requis"); return null; }
    afficherErreur(false);
    var modele = t("form.message_modele");
    return remplir(modele, v);
  }

  function ouvrirWhatsApp() {
    var msg = construireMessage();
    if (msg == null) return;
    var num = (infos && infos.telephone_wa) ? infos.telephone_wa : "34744622975";
    window.open("https://wa.me/" + num + "?text=" + encodeURIComponent(msg), "_blank", "noopener");
  }

  function ouvrirEmail() {
    var msg = construireMessage();
    if (msg == null) return;
    var mail = (infos && infos.email) ? infos.email : "brasseriephoenixrestaurant@gmail.com";
    var sujet = "Réservation Brasserie Phoenix";
    window.location.href = "mailto:" + mail +
      "?subject=" + encodeURIComponent(sujet) +
      "&body=" + encodeURIComponent(msg);
  }

  /* Redirige vers un moteur de réservation externe (mode "url"). */
  function ouvrirMoteur() {
    if (!RESERVATION.url) return;
    if (RESERVATION.ouvrir_dans_nouvel_onglet) {
      window.open(RESERVATION.url, "_blank", "noopener");
    } else {
      window.location.href = RESERVATION.url;
    }
  }

  function init() {
    var btnWa = document.getElementById("btn-wa");
    var btnMail = document.getElementById("btn-email");

    // Aiguillage selon la cible de réservation configurée en haut du fichier.
    if (RESERVATION.mode === "url" && RESERVATION.url) {
      if (btnWa) btnWa.addEventListener("click", ouvrirMoteur);
      if (btnMail) btnMail.addEventListener("click", ouvrirMoteur);
    } else {
      // mode par défaut "whatsapp_email"
      if (btnWa) btnWa.addEventListener("click", ouvrirWhatsApp);
      if (btnMail) btnMail.addEventListener("click", ouvrirEmail);
    }

    // pré-remplir la date du jour comme valeur minimale
    var dateInput = document.getElementById("r-date");
    if (dateInput) {
      var d = new Date();
      var iso = d.getFullYear() + "-" +
        String(d.getMonth() + 1).padStart(2, "0") + "-" +
        String(d.getDate()).padStart(2, "0");
      dateInput.min = iso;
      // avertir immédiatement si l'utilisateur choisit un jour de fermeture
      dateInput.addEventListener("change", function () {
        if (estJourFerme(dateInput.value)) afficherErreur(true, "form.ferme_jour");
        else afficherErreur(false);
      });
    }

    // service / créneaux (horaires de cuisine)
    remplirServices();
    var svc = document.getElementById("r-service");
    if (svc) svc.addEventListener("change", remplirCreneaux);
    // reconstruire les libellés traduits au changement de langue
    if (window.Phoenix) window.Phoenix.onLangChange(remplirServices);

    // charger infos (numéro / email) — repli sur valeurs par défaut si échec
    fetch("data/infos.json")
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (d) { infos = d; })
      .catch(function () { /* valeurs par défaut utilisées */ });
  }

  // Avec defer, le DOM est prêt à l'exécution ; sinon on attend DOMContentLoaded.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
