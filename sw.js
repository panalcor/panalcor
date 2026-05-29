// Service Worker — PANALCOR v4
const CACHE = 'panalcor-v5';
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
