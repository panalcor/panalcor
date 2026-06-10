"""
PANALCOR S.L. — Servidor Local de Mantenimiento
================================================
Requisitos: Python 3.7+  (sin pip install, solo librerías incluidas)
Uso:        Doble clic en arrancar.bat  (o: python servidor.py)
"""

import http.server
import json
import os
import socket
import datetime
import threading
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Evitar errores de codificación (emojis en consola) cuando la salida va a un pipe
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PORT     = 8080
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / 'averias_data.json'

# Base de datos SQLite paralela (opcional: si falla, el servidor sigue igual)
try:
    import bd_panalcor
except Exception as _e:
    bd_panalcor = None
    print(f'  ⚠️  Base de datos SQLite no disponible: {_e}')

# ── Helpers de datos ────────────────────────────────────────────
def load_averias():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_averias(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

# ── Handler HTTP ─────────────────────────────────────────────────
class PanalcorHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    # ── CORS para que el móvil pueda llamar a la API ──────────────
    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    # ── POST ──────────────────────────────────────────────────────
    def do_POST(self):
        path = urlparse(self.path).path

        if path == '/api/averia':
            length = int(self.headers.get('Content-Length', 0))
            raw    = self.rfile.read(length)
            try:
                averia = json.loads(raw.decode('utf-8'))
                # Metadatos de recepción
                averia['_desde_movil'] = True
                averia['_recibida']    = datetime.datetime.now().isoformat()
                averia['_ip_origen']   = self.client_address[0]
                data = load_averias()
                # Evitar duplicados por id
                ids = {a.get('id') for a in data}
                if averia.get('id') not in ids:
                    data.append(averia)
                    save_averias(data)
                    print(f'  [{_ts()}] 📱 Nueva avería recibida: {averia.get("maqNombre","?")} — {averia.get("tipo","?")}')
                # Guardar también en la BD SQLite (en paralelo, sin bloquear)
                if bd_panalcor:
                    try:
                        bd_panalcor.guardar_averia(averia)
                    except Exception as e:
                        print(f'  [{_ts()}] ⚠️  SQLite: {e}')
                self._json({'ok': True, 'total': len(data)})
            except Exception as e:
                print(f'  [{_ts()}] ❌ Error al guardar avería: {e}')
                self._json({'ok': False, 'error': str(e)}, 500)

        elif path == '/api/averias/clear':
            save_averias([])
            print(f'  [{_ts()}] 🗑️  Averías del servidor limpiadas')
            self._json({'ok': True})

        elif path == '/api/db/sync' and bd_panalcor:
            try:
                r = bd_panalcor.sync_completo()
                print(f'  [{_ts()}] 🗄️  Sync manual BD completado')
                self._json({'ok': True, 'resumen': r})
            except Exception as e:
                self._json({'ok': False, 'error': str(e)}, 500)

        else:
            self.send_error(404, 'Ruta no encontrada')

    # ── GET ───────────────────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/api/averias':
            data = load_averias()
            self._json({'averias': data, 'total': len(data)})

        elif path.startswith('/api/db/') and bd_panalcor:
            self._api_db(path)

        elif path == '/api/status':
            ip = get_local_ip()
            self._json({
                'ok':    True,
                'ip':    ip,
                'port':  PORT,
                'base':  f'http://{ip}:{PORT}',
                'total_averias': len(load_averias()),
            })

        else:
            # Servir archivos estáticos normalmente
            super().do_GET()

    # ── API de consultas sobre la BD SQLite ───────────────────────
    def _api_db(self, path):
        qs = parse_qs(urlparse(self.path).query)
        p  = lambda k: (qs.get(k) or [None])[0]
        try:
            if path == '/api/db/kpis':
                self._json({'ok': True, 'kpis': bd_panalcor.consultar_kpis()})
            elif path == '/api/db/averias':
                avs = bd_panalcor.consultar_averias(
                    q=p('q'), maq=p('maq'), mecanico=p('mecanico'),
                    desde=p('desde'), hasta=p('hasta'),
                    tipo=p('tipo'), estado=p('estado'),
                    limite=p('limite') or 300)
                self._json({'ok': True, 'averias': avs, 'total': len(avs)})
            elif path == '/api/db/maquinas':
                ms = bd_panalcor.consultar_maquinas(q=p('q'))
                self._json({'ok': True, 'maquinas': ms, 'total': len(ms)})
            elif path == '/api/db/repuestos':
                rs = bd_panalcor.consultar_repuestos(
                    q=p('q'), bajo_stock=p('bajo_stock') == '1',
                    limite=p('limite') or 300)
                self._json({'ok': True, 'repuestos': rs, 'total': len(rs)})
            elif path == '/api/db/info':
                self._json({'ok': True, 'info': bd_panalcor.info_bd()})
            else:
                self.send_error(404, 'Ruta de BD no encontrada')
        except Exception as e:
            self._json({'ok': False, 'error': str(e)}, 500)

    # ── JSON helper ───────────────────────────────────────────────
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_cors()
        self.end_headers()
        self.wfile.write(body)

    # ── Logs limpios ──────────────────────────────────────────────
    def log_message(self, fmt, *args):
        msg = fmt % args
        if '/api/' in msg:
            print(f'  [{_ts()}] 🔗 API: {msg}')
        # Silenciar logs de archivos estáticos para no llenar la consola

def _ts():
    return datetime.datetime.now().strftime('%H:%M:%S')


# ── Arranque ─────────────────────────────────────────────────────
if __name__ == '__main__':
    ip = get_local_ip()

    # Asegurarse de que existe el archivo de datos
    if not DATA_FILE.exists():
        save_averias([])

    linea = '═' * 54
    print(f'\n{linea}')
    print('  PANALCOR S.L. — Servidor de Mantenimiento Local')
    print(linea)
    print(f'  📂 Carpeta:          {BASE_DIR}')
    print(f'  💻 Desde este PC:    http://localhost:{PORT}/panalcor_inicio.html')
    print(f'  📱 Desde el móvil:   http://{ip}:{PORT}/panalcor_inicio.html')
    print(f'  🔧 QR Máquinas:      http://{ip}:{PORT}/qr_maquinas.html')
    print()
    print(f'  ⚠️  El móvil debe estar en la misma WiFi que este PC')
    print(f'  🛑 Para detener:     Ctrl + C')
    print(linea)
    print()

    # Sincronización de la BD SQLite en segundo plano (cada 15 min)
    if bd_panalcor:
        try:
            bd_panalcor.crear_esquema()
            bd_panalcor.sync_periodico(intervalo=900)
            print(f'  [{_ts()}] 🗄️  BD SQLite activa → panalcor.db (sync cada 15 min)')
            print(f'  [{_ts()}] 🔍 Consultas: http://localhost:{PORT}/consultas.html')
        except Exception as e:
            print(f'  [{_ts()}] ⚠️  BD SQLite desactivada: {e}')

    try:
        server = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), PanalcorHandler)
        print(f'  [{_ts()}] ✅ Servidor arrancado — escuchando en puerto {PORT}')
        print(f'  [{_ts()}] 📝 Averías recibidas de móvil → averias_data.json')
        print()
        server.serve_forever()
    except KeyboardInterrupt:
        print(f'\n  [{_ts()}] 🛑 Servidor detenido.')
    except OSError as e:
        if 'already in use' in str(e) or e.errno == 10048:
            print(f'\n  ❌ El puerto {PORT} ya está ocupado.')
            print(f'     Cierra otras instancias del servidor o cambia PORT en servidor.py')
        else:
            raise
