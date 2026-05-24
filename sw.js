// Service Worker — PANALCOR v1.0
const CACHE = 'panalcor-v1';
const SHELL = [
  'landing.html',
  'admin.html',
  'mecanicos.html',
  'averias.html',
  'mis_tareas.html',
  'maquinas_admin.html',
  'plan_preventivo.html',
  'preventivo.html',
  'encargados.html',
  'turnos.html',
  'historial_maquina.html',
  'qr_maquinas.html',
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
    })
  );
  self.clients.claim();
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
