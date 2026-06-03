// fcm.js — Sistema de notificaciones en tiempo real PANALCOR
// Se incluye en las páginas de mecánicos después de inicializar Firebase

var _notifMecKey = null;
var _notifRef    = null;
var _notifVistas = JSON.parse(localStorage.getItem('notif_vistas') || '[]');

// Llamar cuando se sabe el nombre del mecánico
function fcmRegistrar(nombreMecanico) {
  if (!nombreMecanico) return;
  _notifMecKey = nombreMecanico.replace(/\s+/g, '_').toLowerCase();

  // Registrar presencia en Firebase
  firebase.database().ref('mecanicos_online/' + _notifMecKey).set({
    nombre: nombreMecanico,
    ts: Date.now()
  });

  // Escuchar notificaciones nuevas en tiempo real
  _notifRef = firebase.database().ref('notificaciones/' + _notifMecKey);
  _notifRef.on('child_added', function(snap) {
    var n = snap.val();
    if (!n) return;
    // Ignorar notificaciones ya vistas
    if (_notifVistas.indexOf(snap.key) !== -1) return;
    // Ignorar notificaciones muy antiguas (más de 24h)
    if (n.ts && Date.now() - n.ts > 86400000) return;
    _marcarVista(snap.key);
    _mostrarNotif(n.titulo, n.cuerpo, n.url, n.icono);
  });
}

function _marcarVista(key) {
  _notifVistas.push(key);
  if (_notifVistas.length > 200) _notifVistas = _notifVistas.slice(-100);
  localStorage.setItem('notif_vistas', JSON.stringify(_notifVistas));
}

function _mostrarNotif(titulo, cuerpo, url, icono) {
  // Toast visual
  var el = document.createElement('div');
  el.style.cssText = [
    'position:fixed', 'top:80px', 'right:16px',
    'background:#0d1b2a', 'border:1px solid #c9a227',
    'border-radius:12px', 'padding:14px 18px',
    'z-index:9999', 'max-width:320px', 'width:90%',
    'box-shadow:0 8px 32px rgba(0,0,0,0.6)',
    'cursor:pointer', 'font-family:Barlow,sans-serif',
    'animation:slideIn .3s ease'
  ].join(';');

  // Añadir animación si no existe
  if (!document.getElementById('_notifStyle')) {
    var s = document.createElement('style');
    s.id = '_notifStyle';
    s.textContent = '@keyframes slideIn{from{opacity:0;transform:translateX(40px)}to{opacity:1;transform:translateX(0)}}';
    document.head.appendChild(s);
  }

  el.innerHTML =
    '<div style="display:flex;align-items:flex-start;gap:10px">' +
      '<div style="font-size:1.4rem;flex-shrink:0">' + (icono || '🔔') + '</div>' +
      '<div style="flex:1;min-width:0">' +
        '<div style="font-size:0.82rem;font-weight:700;color:#f0c040;margin-bottom:3px">' + (titulo || 'PANALCOR') + '</div>' +
        '<div style="font-size:0.8rem;color:rgba(255,255,255,0.8);line-height:1.35">' + (cuerpo || '') + '</div>' +
      '</div>' +
      '<div style="font-size:1rem;color:rgba(255,255,255,0.3);flex-shrink:0;margin-left:4px" onclick="this.parentNode.parentNode.remove();event.stopPropagation()">✕</div>' +
    '</div>';

  if (url) {
    el.onclick = function() { window.location.href = url; };
  } else {
    el.onclick = function() { el.remove(); };
  }

  document.body.appendChild(el);
  setTimeout(function() { if (el.parentNode) el.remove(); }, 8000);

  // Intentar notificación nativa del sistema si tiene permiso
  if ('Notification' in window && Notification.permission === 'granted') {
    try {
      new Notification(titulo || 'PANALCOR', {
        body: cuerpo || '',
        icon: '/icons/icon-192.png',
        badge: '/icons/icon-192.png'
      });
    } catch(e) {}
  } else if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}

// ── Función que usa el admin para enviar notificaciones ────────────
// Se exporta globalmente para usarla desde admin.html también
function fcmEnviar(nombreMecanico, titulo, cuerpo, url, icono) {
  if (!nombreMecanico) return;
  var key = nombreMecanico.replace(/\s+/g, '_').toLowerCase();
  var ref = firebase.database().ref('notificaciones/' + key);
  ref.push({
    titulo: titulo || 'PANALCOR',
    cuerpo: cuerpo || '',
    url:    url    || '',
    icono:  icono  || '🔔',
    ts:     Date.now(),
    leida:  false
  });
}

// Enviar a varios mecánicos a la vez
function fcmEnviarVarios(mecanicos, titulo, cuerpo, url, icono) {
  if (!mecanicos || !mecanicos.length) return;
  mecanicos.forEach(function(m) {
    fcmEnviar(m, titulo, cuerpo, url, icono);
  });
}
