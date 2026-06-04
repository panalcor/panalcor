// offline.js — Indicador de conexión y gestión offline PANALCOR
// Incluir en todas las páginas de mecánicos después de inicializar Firebase

(function() {
  'use strict';

  var _banner = null;
  var _estaOffline = !navigator.onLine;

  // ── Crear banner ─────────────────────────────────────────────────
  function crearBanner() {
    if (_banner) return;
    _banner = document.createElement('div');
    _banner.id = '_offlineBanner';
    _banner.style.cssText = [
      'position:fixed', 'top:0', 'left:0', 'right:0',
      'background:#922b21', 'color:#fff',
      'text-align:center', 'padding:8px 16px',
      'font-family:Barlow,sans-serif', 'font-size:0.85rem', 'font-weight:700',
      'z-index:99999', 'display:none',
      'letter-spacing:0.03em', 'line-height:1.4'
    ].join(';');
    document.body.appendChild(_banner);
  }

  function mostrarBanner(msg) {
    crearBanner();
    _banner.innerHTML = msg;
    _banner.style.display = 'block';
    // Empujar el contenido hacia abajo para que no tape nada
    document.body.style.paddingTop = (_banner.offsetHeight + 2) + 'px';
  }

  function ocultarBanner() {
    if (!_banner) return;
    _banner.style.display = 'none';
    document.body.style.paddingTop = '';
  }

  // ── Listeners navegador ──────────────────────────────────────────
  window.addEventListener('online', function() {
    _estaOffline = false;
    ocultarBanner();
    // Intentar sincronizar cola pendiente
    _sincronizarCola();
  });

  window.addEventListener('offline', function() {
    _estaOffline = true;
    mostrarBanner('📵 Sin conexión — Los cambios se guardarán cuando vuelva la red');
  });

  // Si ya está offline al cargar
  if (!navigator.onLine) {
    document.addEventListener('DOMContentLoaded', function() {
      mostrarBanner('📵 Sin conexión — Los cambios se guardarán cuando vuelva la red');
    });
  }

  // ── Firebase .info/connected ─────────────────────────────────────
  // Detecta también cuando hay red pero Firebase no responde
  function initFirebaseOnline() {
    if (typeof firebase === 'undefined' || !firebase.apps.length) return;
    try {
      firebase.database().ref('.info/connected').on('value', function(snap) {
        if (snap.val() === false && navigator.onLine) {
          // Hay red pero no Firebase → modo degradado
          mostrarBanner('⚡ Conectando con el servidor... Los datos pueden no estar actualizados');
        } else if (snap.val() === true) {
          if (_estaOffline) return; // ya lo gestiona el listener offline
          ocultarBanner();
        }
      });
    } catch(e) {}
  }

  // ── keepSynced para datos críticos ───────────────────────────────
  function initKeepSynced() {
    // keepSynced desactivado — puede causar descargas masivas de datos
  }

  // ── Cola offline para acciones críticas ─────────────────────────
  var COLA_KEY = 'panalcor_cola_offline';

  function encolar(tipo, datos) {
    var cola = _getCola();
    cola.push({ tipo: tipo, datos: datos, ts: Date.now() });
    localStorage.setItem(COLA_KEY, JSON.stringify(cola));
  }

  function _getCola() {
    try { return JSON.parse(localStorage.getItem(COLA_KEY) || '[]'); } catch(e) { return []; }
  }

  function _sincronizarCola() {
    var cola = _getCola();
    if (!cola.length) return;
    if (typeof firebase === 'undefined' || !firebase.apps.length) return;

    var pendiente = cola.slice();
    localStorage.removeItem(COLA_KEY);

    var exito = 0;
    var fallidos = [];

    function procesarSiguiente(i) {
      if (i >= pendiente.length) {
        if (fallidos.length) localStorage.setItem(COLA_KEY, JSON.stringify(fallidos));
        if (exito > 0) _mostrarToastSync('✅ ' + exito + ' acción' + (exito>1?'es':'') + ' sincronizada' + (exito>1?'s':'') + ' con el servidor');
        return;
      }
      var item = pendiente[i];
      _ejecutarAccion(item).then(function() {
        exito++;
        procesarSiguiente(i + 1);
      }).catch(function() {
        fallidos.push(item);
        procesarSiguiente(i + 1);
      });
    }
    procesarSiguiente(0);
  }

  function _ejecutarAccion(item) {
    var db = firebase.database();
    if (item.tipo === 'tarea_hecha') {
      return db.ref('asignaciones/' + item.datos.mes + '/' + item.datos.id)
               .update({ hecho: item.datos.hecho, hechoEn: item.datos.hechoEn });
    }
    if (item.tipo === 'pedido') {
      return db.ref('pedidos').push(item.datos);
    }
    return Promise.resolve();
  }

  function _mostrarToastSync(msg) {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1e8449;color:#fff;border-radius:10px;padding:10px 20px;font-family:Barlow,sans-serif;font-size:0.85rem;font-weight:700;z-index:99999;white-space:nowrap;box-shadow:0 4px 16px rgba(0,0,0,0.4)';
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(function(){ if (el.parentNode) el.remove(); }, 4000);
  }

  // ── API pública ──────────────────────────────────────────────────
  window.OfflinePANALCOR = {
    estaOffline: function() { return _estaOffline || !navigator.onLine; },
    encolar:     encolar,
    sincronizar: _sincronizarCola,
    init: function() {
      initFirebaseOnline();
      initKeepSynced();
      // Intentar sincronizar cola al cargar si hay conexión
      if (navigator.onLine) setTimeout(_sincronizarCola, 2000);
    }
  };

})();
