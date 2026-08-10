/* ============================================================
   sw.js — Service worker de Brasserie Phoenix (version test)
   ------------------------------------------------------------
   Objectif : app installable qui s'ouvre instantanément et
   continue de fonctionner même sans connexion (ou en 3G faible
   sur la terrasse).

   Stratégie :
   - Page (HTML) et données (data/*.json) : réseau d'abord, puis
     copie en cache. Si le réseau échoue (hors-ligne), on sert la
     dernière version connue en cache plutôt qu'une erreur.
   - Fichiers statiques (css/js/images/polices) : cache d'abord
     pour un affichage instantané, avec une mise à jour silencieuse
     du cache en arrière-plan à chaque visite.

   Pour publier une mise à jour visible par les visiteurs déjà
   installés, il suffit de changer CACHE_VERSION ci-dessous : les
   anciens caches sont supprimés automatiquement à l'activation.
   ============================================================ */

var CACHE_VERSION = "phoenix-test-v1";

var COQUILLE = [
  "./",
  "./index.html",
  "./preview-manifest.webmanifest",
  "../assets/css/styles.css",
  "../assets/js/i18n.js",
  "../assets/js/menu.js",
  "../assets/js/sections.js",
  "../assets/js/ui.js",
  "../assets/js/reservation.js",
  "../assets/js/motion.js",
  "../assets/js/experience.js",
  "../assets/img/phoenix-logo.png",
  "../assets/img/favicon.png"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(function (cache) {
      return cache.addAll(COQUILLE).catch(function () {
        /* Si une ressource manque au premier essai, on n'empêche pas
           l'installation : le reste sera mis en cache au fil des visites. */
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (noms) {
      return Promise.all(
        noms
          .filter(function (nom) { return nom !== CACHE_VERSION; })
          .map(function (nom) { return caches.delete(nom); })
      );
    })
  );
  self.clients.claim();
});

function estDonneeOuPage(url) {
  return (
    url.pathname.endsWith(".json") ||
    url.pathname.endsWith("/") ||
    url.pathname.endsWith(".html")
  );
}

self.addEventListener("fetch", function (event) {
  var req = event.request;
  if (req.method !== "GET") return;

  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // polices Google etc. : laissées au navigateur

  if (estDonneeOuPage(url)) {
    // Réseau d'abord (fraîcheur), cache en secours (hors-ligne).
    event.respondWith(
      fetch(req)
        .then(function (rep) {
          var copie = rep.clone();
          caches.open(CACHE_VERSION).then(function (cache) { cache.put(req, copie); });
          return rep;
        })
        .catch(function () { return caches.match(req); })
    );
    return;
  }

  // Fichiers statiques : cache d'abord (instantané), réseau en secours + mise à jour silencieuse.
  event.respondWith(
    caches.match(req).then(function (repCache) {
      var fetchPromise = fetch(req)
        .then(function (rep) {
          var copie = rep.clone();
          caches.open(CACHE_VERSION).then(function (cache) { cache.put(req, copie); });
          return rep;
        })
        .catch(function () { return repCache; });
      return repCache || fetchPromise;
    })
  );
});
