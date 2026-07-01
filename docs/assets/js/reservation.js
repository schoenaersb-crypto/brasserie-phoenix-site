/* ============================================================
   reservation.js — génère un message pré-rempli vers WhatsApp ou email
   Aucun serveur : on ouvre simplement wa.me / mailto avec le texte.
   ============================================================ */
(function () {
  "use strict";

  var infos = null;

  function t(p) { return window.Phoenix ? window.Phoenix.t(p) : ""; }

  /* Remplit un modèle "…{cle}…" avec les valeurs du formulaire */
  function remplir(modele, valeurs) {
    return modele.replace(/\{(\w+)\}/g, function (_, cle) {
      return valeurs[cle] != null && valeurs[cle] !== "" ? valeurs[cle] : "—";
    });
  }

  function lireFormulaire() {
    return {
      date: document.getElementById("r-date").value,
      heure: document.getElementById("r-heure").value,
      personnes: document.getElementById("r-personnes").value,
      nom: document.getElementById("r-nom").value.trim(),
      telephone: document.getElementById("r-tel").value.trim()
    };
  }

  function valide(v) {
    return v.date && v.heure && v.personnes && v.nom;
  }

  function afficherErreur(montrer) {
    var box = document.getElementById("form-erreur");
    if (!box) return;
    if (montrer) { box.textContent = t("form.requis"); box.hidden = false; }
    else { box.hidden = true; }
  }

  function construireMessage() {
    var v = lireFormulaire();
    if (!valide(v)) { afficherErreur(true); return null; }
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

  function init() {
    var btnWa = document.getElementById("btn-wa");
    var btnMail = document.getElementById("btn-email");
    if (btnWa) btnWa.addEventListener("click", ouvrirWhatsApp);
    if (btnMail) btnMail.addEventListener("click", ouvrirEmail);

    // pré-remplir la date du jour comme valeur minimale
    var dateInput = document.getElementById("r-date");
    if (dateInput) {
      var d = new Date();
      var iso = d.getFullYear() + "-" +
        String(d.getMonth() + 1).padStart(2, "0") + "-" +
        String(d.getDate()).padStart(2, "0");
      dateInput.min = iso;
    }

    // charger infos (numéro / email) — repli sur valeurs par défaut si échec
    fetch("data/infos.json")
      .then(function (r) { return r.json(); })
      .then(function (d) { infos = d; })
      .catch(function () { /* valeurs par défaut utilisées */ });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
