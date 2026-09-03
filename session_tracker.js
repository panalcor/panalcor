/* PANALCOR — Contabiliza el tiempo de uso por persona.
   Lee la sesión activa (panalcor_session) y va sumando segundos en
   Firebase mientras la pestaña esté visible en primer plano. */
(function(){
  try {
    var ps = JSON.parse(localStorage.getItem('panalcor_session') || 'null');
    if (!ps || !ps.nombre || !ps.rol) return;
    if (ps.expires && Date.now() > ps.expires) return;
    if (typeof firebase === 'undefined' || !firebase.apps || !firebase.apps.length) return;

    var DB = firebase.database();
    var nombreKey = String(ps.nombre).toUpperCase().replace(/[.#$\[\]\/]/g, '_');
    var TICK_MS = 15000;

    function hoy(){ return new Date().toISOString().slice(0,10); }
    function paginaActual(){ return location.pathname.split('/').pop() || 'panalcor_inicio.html'; }

    function tick(){
      if (document.visibilityState !== 'visible') return;
      DB.ref('tiempo_uso/' + hoy() + '/' + nombreKey).update({
        nombre: ps.nombre,
        rol: ps.rol,
        segundos: firebase.database.ServerValue.increment(TICK_MS / 1000),
        ultimaPagina: paginaActual(),
        ultimaConexion: firebase.database.ServerValue.TIMESTAMP
      }).catch(function(){});
    }

    setTimeout(tick, 4000);
    setInterval(tick, TICK_MS);
  } catch(e){}
})();
