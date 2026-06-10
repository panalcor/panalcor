// Service Worker — PANALCOR v7 (con FCM push)
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey:            "AIzaSyC_AJEkrbWqfE65Mt_f5V0LfemPJc10UuU",
  authDomain:        "panalcor-mantenimiento.firebaseapp.com",
  databaseURL:       "https://panalcor-mantenimiento-default-rtdb.europe-west1.firebasedatabase.app",
  projectId:         "panalcor-mantenimiento",
  storageBucket:     "panalcor-mantenimiento.firebasestorage.app",
  messagingSenderId: "67593058609",
  appId:             "1:67593058609:web:c33fa1fa4fce2932485810"
});

const messaging = firebase.messaging();

// Notificaciones en background (app cerrada o en segundo plano)
messaging.onBackgroundMessage(function(payload) {
  const n = payload.notification || {};
  const data = payload.data || {};
  self.registration.showNotification(n.title || 'PANALCOR', {
    body:  n.body  || '',
    icon:  '/icons/icon-192.png',
    badge: '/icons/icon-192.png',
    tag:   data.tag || 'panalcor',
    data:  data
  });
});

// Click en notificacion → abrir pagina correspondiente
self.addEventListener('notificationclick', function(e) {
  e.notification.close();
  var url = e.notification.data && e.notification.data.url
    ? e.notification.data.url
    : '/mis_tareas.html';
  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(cs) {
      for (var i = 0; i < cs.length; i++) {
        if (cs[i].url.includes(url.split('?')[0]) && 'focus' in cs[i]) {
          return cs[i].focus();
        }
      }
      return clients.openWindow(url);
    })
  );
});

// ── Cache shell ───────────────────────────────────────────────────
const CACHE = 'panalcor-v9';
const SHELL = [
  'panalcor_inicio.html','maquina.html','landing.html','admin.html',
  'averias.html','mis_tareas.html','plan_preventivo.html','preventivo.html',
  'encargados.html','turnos.html','historial_maquina.html','parte_trabajo.html',
  'calendario.html','manual.html','mecanicos.html','manifest.json',
  'fcm.js','offline.js',
  'icons/icon-192.png','icons/icon-512.png'
];

self.addEventListener('install', function(e) {
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(SHELL); }));
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); }));
    }).then(function(){ return self.clients.claim(); })
    .then(function(){
      return self.clients.matchAll({ type: 'window' }).then(function(cls){
        cls.forEach(function(c){ c.postMessage({ type: 'SW_UPDATED' }); });
      });
    })
  );
});

self.addEventListener('fetch', function(e) {
  // Solo cachear peticiones http/https
  if (!e.request.url.startsWith('http')) return;

  // API del servidor local: siempre a red, nunca cachear
  if (e.request.url.includes('/api/')) return;

  if (e.request.url.includes('firebase') ||
      e.request.url.includes('googleapis') ||
      e.request.url.includes('gstatic') ||
      e.request.url.includes('cdn.') ||
      e.request.url.includes('sheetjs') ||
      e.request.url.includes('jsdelivr')) {
    return;
  }
  e.respondWith(
    fetch(e.request).then(function(res) {
      // Solo cachear respuestas válidas
      if (res && res.status === 200 && res.type !== 'opaque') {
        var clone = res.clone();
        caches.open(CACHE).then(function(c){ c.put(e.request, clone); });
      }
      return res;
    }).catch(function() {
      return caches.match(e.request);
    })
  );
});
