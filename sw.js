// Karmapolis: service worker minimo (serve per installare il gioco come app sul telefono). Non tiene copie vecchie: carica sempre l'ultima versione.
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{ e.respondWith(fetch(e.request)); });
