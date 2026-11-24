// Karmapolis: service worker minimo (serve per installare il gioco come app sul telefono).
// Non tocca le richieste: le lascia passare al browser, così si carica sempre l'ultima versione (e Safari non si confonde).
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',()=>{});
