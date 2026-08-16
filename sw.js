/* PANALCOR — Service Worker de notificaciones */
self.addEventListener('install',  e => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

/* Al pulsar una notificación: abre la página correspondiente */
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || './panalcor_inicio.html';
  e.waitUntil(
    self.clients.matchAll({type:'window', includeUncontrolled:true}).then(cs => {
      for(const c of cs){
        if(c.url.includes('panalcor') && 'focus' in c){ c.focus(); return; }
      }
      if(self.clients.openWindow) return self.clients.openWindow(url);
    })
  );
});
