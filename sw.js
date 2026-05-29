// Service Worker — PANALCOR v6
const CACHE = 'panalcor-v6';
const SHELL = [
  'panalcor_inicio.html',
  'maquina.html',
  'landing.html',
  'admin.html',
  'averias.html',
  'mis_tareas.html',
  'plan_preventivo.html',
  'preventivo.html',
  'encargados.html',
  'turnos.html',
  'historial_maquina.html',
  'parte_trabajo.html',
  'calendario.html',
  'manual.html',
  'manifest.json',
  'icons/icon-192.png',
  'icons/icon-512.png'
];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE).then(function(c) { return c.addAll(SHELL); })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); }));
    }).then(function(){
      return self.clients.claim();
    }).then(function(){
      // Avisar a todas las pestañas para que recarguen con el nuevo código
      return self.clients.matchAll({ type: 'window' }).then(function(clients){
        clients.forEach(function(client){ client.postMessage({ type: 'SW_UPDATED' }); });
      });
    })
  );
});

self.addEventListener('fetch', function(e) {
  // Firebase y CDN siempre en red
  if (e.request.url.includes('firebase') ||
      e.request.url.includes('googleapis') ||
      e.request.url.includes('cdn.') ||
      e.request.url.includes('sheetjs') ||
      e.request.url.includes('jsdelivr')) {
    return;
  }
  e.respondWith(
    fetch(e.request).then(function(res) {
      var clone = res.clone();
      caches.open(CACHE).then(function(c){ c.put(e.request, clone); });
      return res;
    }).catch(function() {
      return caches.match(e.request);
    })
  );
});
