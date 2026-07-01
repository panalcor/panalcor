"""
Genera QR_maquinas_PANALCOR.pdf replicando el diseno de qr_maquinas.html:
  - Tarjetas BLANCAS con borde fino gris
  - PANALCOR S.L. (dorado, pequeño)
  - Area (gris muy pequeño uppercase)
  - ID maquina (dorado)
  - NOMBRE (navy bold, grande)
  - tipo . fabricante (gris pequeno)
  - QR 140x140 navy-sobre-blanco
  - hint "Escanear para declarar averia"
  - URL -> maquina.html dispatcher (rol-aware)
  - Layout: A4 landscape, 4 columnas x 3 filas = 12 por pagina
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
import io, urllib.parse

BASE_URL = "https://panalcor.github.io/panalcor/averias.html"
OUT = r"C:\Users\fjha_\Downloads\GESTION 3.0\QR_maquinas_PANALCOR.pdf"

MAQUINAS = [
  {'id':'MAQ-001','n':'PABAT 1','t':'AMASADORA','f':'NEOTECH','a':'OBRADOR'},
  {'id':'MAQ-002','n':'PABAT 2','t':'AMASADORA','f':'NEOTECH','a':'OBRADOR'},
  {'id':'MAQ-003','n':'PABAT 3','t':'AMASADORA','f':'NEOTECH','a':'OBRADOR'},
  {'id':'MAQ-004','n':'PABAT 4','t':'AMASADORA','f':'NEOTECH','a':'OBRADOR'},
  {'id':'MAQ-005','n':'PABAT 5','t':'AMASADORA','f':'NEOTECH','a':'OBRADOR'},
  {'id':'MAQ-006','n':'PABAT 6','t':'AMASADORA','f':'NEOTECH','a':'OBRADOR'},
  {'id':'MAQ-007','n':'PABAT 7','t':'AMASADORA','f':'NEOTECH','a':'OBRADOR'},
  {'id':'MAQ-008','n':'PABAT 8','t':'AMASADORA','f':'MAGER','a':'OBRADOR'},
  {'id':'MAQ-009','n':'AMASADORA CANDEAL','t':'AMASADORA','f':'KEMPER','a':'OBRADOR'},
  {'id':'MAQ-010','n':'LINEA 1','t':'FORMADORA-ENTABLADORA','f':'TECKMAPA','a':'OBRADOR'},
  {'id':'MAQ-011','n':'LINEA 2','t':'FORMADORA-ENTABLADORA','f':'TECKMAPA','a':'OBRADOR'},
  {'id':'MAQ-012','n':'LINEA 3','t':'FORMADORA-ENTABLADORA','f':'TECKMAPA','a':'OBRADOR'},
  {'id':'MAQ-013','n':'LINEA 4','t':'FORMADORA-ENTABLADORA','f':'TECKMAPA','a':'OBRADOR'},
  {'id':'MAQ-014','n':'LINEA 5','t':'FORMADORA-ENTABLADORA','f':'TECKMAPA','a':'OBRADOR'},
  {'id':'MAQ-015','n':'LINEA 6','t':'FORMADORA-ENTABLADORA','f':'BEOR','a':'OBRADOR'},
  {'id':'MAQ-016','n':'LINEA 7','t':'FORMADORA-ENTABLADORA','f':'TECKMAPA','a':'OBRADOR'},
  {'id':'MAQ-017','n':'CARRUSEL 1','t':'CARRUSEL','f':'SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-018','n':'CARRUSEL 2','t':'CARRUSEL','f':'SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-019','n':'CARRUSEL 3','t':'CARRUSEL','f':'SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-020','n':'CARRUSEL 4','t':'CARRUSEL','f':'SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-021','n':'CARRUSEL 5','t':'CARRUSEL','f':'SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-022','n':'CARRUSEL 6','t':'CARRUSEL','f':'SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-023','n':'VOLCADOR 1','t':'VOLCADOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-024','n':'VOLCADOR 2','t':'VOLCADOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-025','n':'VOLCADOR 3','t':'VOLCADOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-026','n':'VOLCADOR 4','t':'VOLCADOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-027','n':'VOLCADOR 5','t':'VOLCADOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-028','n':'VOLCADOR 6','t':'VOLCADOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-029','n':'VOLCADOR 7','t':'VOLCADOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-030','n':'REPARTIDOR 1','t':'REPARTIDOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-031','n':'REPARTIDOR 2','t':'REPARTIDOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-032','n':'REPARTIDOR 3','t':'REPARTIDOR','f':'','a':'OBRADOR'},
  {'id':'MAQ-033','n':'DIVISORA 11','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-034','n':'DIVISORA 18','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-035','n':'DIVISORA 19','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-036','n':'DIVISORA 3','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-037','n':'DIVISORA 7','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-038','n':'DIVISORA 1','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-039','n':'DIVISORA 12','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-040','n':'DIVISORA 6','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-041','n':'DIVISORA 10','t':'DIVISORAS','f':'SUBAL','a':'OBRADOR'},
  {'id':'MAQ-042','n':'CAMARA DE BOLAS N1','t':'CAMARA REPOSO','f':'ZELAIETA','a':'OBRADOR'},
  {'id':'MAQ-043','n':'CAMARA DE BOLAS N2','t':'CAMARA REPOSO','f':'ZELAIETA','a':'OBRADOR'},
  {'id':'MAQ-044','n':'CAMARA DE BOLAS N3','t':'CAMARA REPOSO','f':'ZELAIETA','a':'OBRADOR'},
  {'id':'MAQ-045','n':'CAMARA DE BOLAS N4','t':'CAMARA REPOSO','f':'ZELAIETA','a':'OBRADOR'},
  {'id':'MAQ-046','n':'CAMARA DE BOLAS N5','t':'CAMARA REPOSO','f':'ZELAIETA','a':'OBRADOR'},
  {'id':'MAQ-047','n':'CAMARA DE BOLAS N6','t':'CAMARA REPOSO','f':'ZELAIETA','a':'OBRADOR'},
  {'id':'MAQ-048','n':'CAMARA DE BOLAS N7','t':'CAMARA REPOSO','f':'ZELAIETA','a':'OBRADOR'},
  {'id':'MAQ-049','n':'EMBOLADORA 2','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-050','n':'EMBOLADORA 7','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-051','n':'EMBOLADORA 6','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-052','n':'EMBOLADORA 11','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-053','n':'EMBOLADORA 10','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-054','n':'EMBOLADORA 4','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-055','n':'EMBOLADORA 9','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-056','n':'EMBOLADORA 5','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-057','n':'EMBOLADORA 1','t':'EMBOLADORA','f':'','a':'OBRADOR'},
  {'id':'MAQ-058','n':'FERMENTADORA RELAMPAGO','t':'FERMENTADORA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-059','n':'FERMENTADORA TRUENO','t':'FERMENTADORA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-060','n':'HORNO 1','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-061','n':'HORNO 2','t':'HORNO','f':'GPG','a':'HORNOS'},
  {'id':'MAQ-062','n':'HORNO 3','t':'HORNO','f':'GPG','a':'HORNOS'},
  {'id':'MAQ-063','n':'HORNO 4','t':'HORNO','f':'GPG','a':'HORNOS'},
  {'id':'MAQ-064','n':'HORNO 5','t':'HORNO','f':'GPG','a':'HORNOS'},
  {'id':'MAQ-065','n':'HORNO 6','t':'HORNO','f':'GPG','a':'HORNOS'},
  {'id':'MAQ-066','n':'HORNO 7','t':'HORNO','f':'GPG','a':'HORNOS'},
  {'id':'MAQ-067','n':'HORNO 8','t':'HORNO','f':'GPG','a':'HORNOS'},
  {'id':'MAQ-068','n':'HORNO 9','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-069','n':'HORNO 10','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-070','n':'HORNO 11','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-071','n':'HORNO 12','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-072','n':'HORNO 13','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-073','n':'HORNO 14','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-074','n':'HORNO 15','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-075','n':'HORNO 16 (1TRUENO)','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-076','n':'HORNO 17 (2TRUENO)','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-077','n':'HORNO 18 (3TRUENO)','t':'HORNO','f':'BEGESA','a':'HORNOS'},
  {'id':'MAQ-078','n':'HORNO 19 (4TRUENO)','t':'HORNO','f':'GPG','a':'HORNOS'},
  {'id':'MAQ-079','n':'TALLADORA RELAMPAGO','t':'TALLADORA','f':'PORTICEL','a':'HORNOS'},
  {'id':'MAQ-080','n':'TALLADORA TRUENO','t':'TALLADORA','f':'AYMI','a':'HORNOS'},
  {'id':'MAQ-081','n':'TUNEL PREFRIO','t':'TUNEL PREFRIO','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-082','n':'TUNEL 1','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-083','n':'TUNEL 2','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-084','n':'TUNEL 3','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-085','n':'TUNEL 4','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-086','n':'TUNEL 5','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-087','n':'TUNEL 6','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-088','n':'TUNEL 7','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-089','n':'TUNEL 8','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-090','n':'TUNEL 9 (1 TRUENO)','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-091','n':'TUNEL 10 (2 TRUENO)','t':'TUNEL CONGELACION','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-092','n':'MAQUINA DE CAJAS','t':'FORMADORA CAJAS','f':'TAVIL','a':'ENVASADO'},
  {'id':'MAQ-093','n':'FORMADORA-EMBOLSADORA','t':'FORMADORA CAJAS','f':'TAVIL','a':'ENVASADO'},
  {'id':'MAQ-094','n':'MAQUINA DE BOLSAS','t':'EMBOLSADORA','f':'PATTYN','a':'ENVASADO'},
  {'id':'MAQ-095','n':'DESCARGADOR 1','t':'CARGADOR/DESCARGADOR','f':'PORTICEL','a':'ENVASADO'},
  {'id':'MAQ-096','n':'DESCARGADOR 2','t':'CARGADOR/DESCARGADOR','f':'PORTICEL','a':'ENVASADO'},
  {'id':'MAQ-097','n':'CARGADOR 1','t':'CARGADOR/DESCARGADOR','f':'PORTICEL','a':'ENVASADO'},
  {'id':'MAQ-098','n':'CARGADOR 2','t':'CARGADOR/DESCARGADOR','f':'PORTICEL','a':'ENVASADO'},
  {'id':'MAQ-099','n':'DESMOLDEO 1','t':'DESMOLDEO','f':'PORTICEL','a':'ENVASADO'},
  {'id':'MAQ-100','n':'DESMOLDEO 2','t':'DESMOLDEO','f':'PORTICEL','a':'ENVASADO'},
  {'id':'MAQ-101','n':'CONTADORA 1','t':'CONTADORA','f':'LOYJAR','a':'ENVASADO'},
  {'id':'MAQ-102','n':'CONTADORA 2','t':'CONTADORA','f':'PORTICEL','a':'ENVASADO'},
  {'id':'MAQ-103','n':'CAMINO DE RODILLOS','t':'C. RODILLOS','f':'TAVIL','a':'ENVASADO'},
  {'id':'MAQ-104','n':'IMPRESORA RELAMPAGO','t':'IMPRESORA','f':'UBS','a':'ENVASADO'},
  {'id':'MAQ-105','n':'IMPRESORA TRUENO','t':'IMPRESORA','f':'UBS','a':'ENVASADO'},
  {'id':'MAQ-106','n':'PRECINTADORA','t':'PRECINTADORA','f':'SOCO-SYSTEM','a':'ENVASADO'},
  {'id':'MAQ-107','n':'M. PEGATINAS','t':'M. PEGATINAS','f':'PANALCOR','a':'ENVASADO'},
  {'id':'MAQ-108','n':'ROBOT','t':'ROBOT','f':'IPLA-FANUC','a':'ENVASADO'},
  {'id':'MAQ-109','n':'ENFARDADORA RELAMPAGO','t':'ENFARDADORA','f':'IPLA-ROBOPAC','a':'ENVASADO'},
  {'id':'MAQ-110','n':'ENFARDADORA TRUENO','t':'ENFARDADORA','f':'','a':'ENVASADO'},
  {'id':'MAQ-111','n':'LAVADORA','t':'EMBOLADORA','f':'SOMENGIL','a':'OBRADOR'},
  {'id':'MAQ-112','n':'SILOS','t':'SILOS HARINA','f':'AGRIFLEX','a':'SILOS'},
  {'id':'MAQ-113','n':'TURBINAS','t':'SILOS HARINA','f':'','a':'SILOS'},
  {'id':'MAQ-114','n':'CUADRO SILOS','t':'SILOS HARINA','f':'AGRIFLEX','a':'SILOS'},
  {'id':'MAQ-115','n':'CUADRO HARINA','t':'SILOS HARINA','f':'','a':'SILOS'},
  {'id':'MAQ-116','n':'ADITIVOS','t':'ADITIVOS','f':'','a':'OBRADOR'},
  {'id':'MAQ-117','n':'CUADRO ADITIVOS','t':'ADITIVOS','f':'','a':'OBRADOR'},
  {'id':'MAQ-118','n':'REVOLVER','t':'ADITIVOS','f':'DAMM-SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-119','n':'TOLVA 1','t':'TOLVA HARINA','f':'DAMM-SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-120','n':'TOLVA 2','t':'TOLVA HARINA','f':'DAMM-SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-121','n':'TOLVA 3','t':'TOLVA HARINA','f':'DAMM-SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-122','n':'TOLVA 4','t':'TOLVA HARINA','f':'DAMM-SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-123','n':'TOLVA 5','t':'TOLVA HARINA','f':'DAMM-SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-124','n':'TOLVA 6','t':'TOLVA HARINA','f':'DAMM-SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-125','n':'TOLVA 7','t':'TOLVA HARINA','f':'DAMM-SABATECNO','a':'OBRADOR'},
  {'id':'MAQ-126','n':'LEVADURA TANQUE 1','t':'LEVADURA','f':'BPF','a':'SILOS'},
  {'id':'MAQ-127','n':'LEVADURA TANQUE 2','t':'LEVADURA','f':'BPF','a':'SILOS'},
  {'id':'MAQ-128','n':'LEVADURA CUADRO GENERAL Y BOMBAS','t':'LEVADURA','f':'BPF','a':'SILOS'},
  {'id':'MAQ-129','n':'LEVADURA CUADRO GLICOL','t':'LEVADURA','f':'','a':'SILOS'},
  {'id':'MAQ-130','n':'CAMARA STOCK 1','t':'CAMARA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-131','n':'CAMARA STOCK 2','t':'CAMARA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-132','n':'CAMARA STOCK 3','t':'CAMARA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-133','n':'CAMARA STOCK 4','t':'CAMARA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-134','n':'CAMARA STOCK 5 (TRUENO)','t':'CAMARA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-135','n':'TANQUE 1','t':'AGUA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-136','n':'TANQUE 2','t':'AGUA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-137','n':'TANQUE 3','t':'AGUA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-138','n':'TANQUE 4','t':'AGUA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-139','n':'TANQUE 5 (TRUENO)','t':'AGUA','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-140','n':'A/A OBRADOR','t':'A/A','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-141','n':'A/A VESTUARIO','t':'A/A','f':'INFRIMA','a':'FRIO/CLIMA'},
  {'id':'MAQ-142','n':'A/A OFICINAS','t':'A/A','f':'','a':'FRIO/CLIMA'},
  {'id':'MAQ-143','n':'TRANSFORMADOR','t':'A/A','f':'INFRISA','a':'FRIO/CLIMA'},
  {'id':'MAQ-144','n':'CONDENSADORES ELECTRICOS','t':'ELECTRICIDAD','f':'JACGA','a':'FRIO/CLIMA'},
  {'id':'MAQ-145','n':'CUADROS GENERALES','t':'ELECTRICIDAD','f':'JACGA','a':'FRIO/CLIMA'},
  {'id':'MAQ-146','n':'A/A MUELLE','t':'A/A','f':'','a':'FRIO/CLIMA'},
  {'id':'MAQ-147','n':'EXTRACTORES RELAMPAGO','t':'EXTRACTORES','f':'','a':'FRIO/CLIMA'},
  {'id':'MAQ-148','n':'EXTRACTORES TRUENO','t':'EXTRACTORES','f':'','a':'FRIO/CLIMA'},
  {'id':'MAQ-149','n':'EVAPORATIVAS','t':'EVAPORATIVAS','f':'','a':'FRIO/CLIMA'},
  {'id':'MAQ-150','n':'REFINADORA','t':'REFINADORA','f':'','a':'OBRADOR TRUENO'},
  {'id':'MAQ-151','n':'TUNEL PREFRIO ARRASTRE','t':'PRECINTADORA','f':'','a':'ENVASADO'},
  {'id':'MAQ-152','n':'PRECINTADORA TRUENO','t':'PRECINTADORA','f':'','a':'ENVASADO'},
  {'id':'MAQ-153','n':'COMPRESOR TRUENO 1','t':'COMPRESORES','f':'','a':'COMPRESORES'},
  {'id':'MAQ-154','n':'COMPRESOR 1','t':'COMPRESORES','f':'','a':'COMPRESORES'},
  {'id':'MAQ-155','n':'COMPRESOR 2','t':'COMPRESORES','f':'','a':'COMPRESORES'},
  {'id':'MAQ-156','n':'COMPRESOR 3','t':'COMPRESORES','f':'','a':'COMPRESORES'},
  {'id':'MAQ-157','n':'SECADOR 1','t':'SECADORES','f':'','a':'COMPRESORES'},
  {'id':'MAQ-158','n':'SECADOR 2','t':'SECADORES','f':'','a':'COMPRESORES'},
  {'id':'MAQ-159','n':'SECADOR ABSORCION','t':'SECADORES','f':'','a':'COMPRESORES'},
  {'id':'MAQ-162','n':'ESCARCHADORA','t':'ESCARCHADORA','f':'','a':'TRUENO'},
  {'id':'MAQ-163','n':'SILO 1 TRUENO','t':'SILOS TRUENO','f':'GASHOR','a':'TRUENO'},
  {'id':'MAQ-164','n':'SILO 2 TRUENO','t':'SILOS TRUENO','f':'GASHOR','a':'TRUENO'},
  {'id':'MAQ-165','n':'CUADRO SILOS TRUENO','t':'ELECTRICIDAD','f':'GASHOR','a':'TRUENO'},
]

# ── Fonts ──────────────────────────────────────────────────────
try:
    F_BOLD   = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",  18)
    F_NAME   = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",  22)
    F_ID     = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",  13)
    F_SMALL  = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",    11)
    F_TINY   = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",     9)
except Exception:
    F_BOLD = F_NAME = F_ID = F_SMALL = F_TINY = ImageFont.load_default()

# ── Colores ────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
NAVY   = (26,  45,  66)    # #1a2d42
GOLD   = (201, 162, 39)    # #c9a227
GRAY   = (120, 140, 160)   # text-dim aprox
LGRAY  = (180, 180, 180)   # border
BLACK  = (0,   0,   0)

QR_PX = 150   # QR en pixeles dentro de la tarjeta

# ── Tarjeta: 290 x 320 px ─────────────────────────────────────
CW, CH = 290, 310

def make_card(m):
    url = BASE_URL + '?maq=' + urllib.parse.quote(m['id'])

    # QR negro sobre blanco
    qr = qrcode.QRCode(version=None,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=5, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=NAVY, back_color=WHITE) \
               .convert('RGB') \
               .resize((QR_PX, QR_PX), Image.LANCZOS)

    card = Image.new('RGB', (CW, CH), WHITE)
    draw = ImageDraw.Draw(card)

    # Borde
    draw.rectangle([0, 0, CW-1, CH-1], outline=LGRAY, width=1)
    # Linea dorada superior fina
    draw.rectangle([0, 0, CW-1, 3], fill=GOLD)

    y = 8

    # PANALCOR S.L.
    brand = 'PANALCOR S.L.'
    bb = draw.textbbox((0,0), brand, font=F_TINY)
    draw.text(((CW - (bb[2]-bb[0])) // 2, y), brand, fill=GOLD, font=F_TINY)
    y += 14

    # Area
    area = m['a'].upper()
    bb = draw.textbbox((0,0), area, font=F_TINY)
    draw.text(((CW - (bb[2]-bb[0])) // 2, y), area, fill=GRAY, font=F_TINY)
    y += 14

    # ID en dorado
    bb = draw.textbbox((0,0), m['id'], font=F_ID)
    draw.text(((CW - (bb[2]-bb[0])) // 2, y), m['id'], fill=GOLD, font=F_ID)
    y += 18

    # Nombre en navy bold
    nombre = m['n']
    if len(nombre) > 20:
        # partir en dos lineas si es largo
        words = nombre.split()
        mid = len(words) // 2
        line1 = ' '.join(words[:mid])
        line2 = ' '.join(words[mid:])
        for line in [line1, line2]:
            bb = draw.textbbox((0,0), line, font=F_NAME)
            draw.text(((CW - (bb[2]-bb[0])) // 2, y), line, fill=NAVY, font=F_NAME)
            y += 24
    else:
        bb = draw.textbbox((0,0), nombre, font=F_NAME)
        draw.text(((CW - (bb[2]-bb[0])) // 2, y), nombre, fill=NAVY, font=F_NAME)
        y += 26

    # tipo · fabricante
    tf = m['t']
    if m['f']:
        tf += ' · ' + m['f']
    bb = draw.textbbox((0,0), tf, font=F_TINY)
    if bb[2]-bb[0] > CW-10:
        tf = m['t']
    bb = draw.textbbox((0,0), tf, font=F_TINY)
    draw.text(((CW - (bb[2]-bb[0])) // 2, y), tf, fill=GRAY, font=F_TINY)
    y += 14

    # Separador fino
    draw.line([(20, y+2), (CW-20, y+2)], fill=LGRAY, width=1)
    y += 8

    # QR centrado
    x_qr = (CW - QR_PX) // 2
    card.paste(qr_img, (x_qr, y))
    y += QR_PX + 6

    # Hint
    hint = 'Escanear para declarar averia'
    bb = draw.textbbox((0,0), hint, font=F_TINY)
    draw.text(((CW - (bb[2]-bb[0])) // 2, y), hint, fill=GRAY, font=F_TINY)

    return card

# ── PDF: A4 landscape, 4 cols x 3 rows ────────────────────────
PW, PH = landscape(A4)   # 842 x 595 pt
COLS, ROWS = 4, 3
MARGIN_X = 20
MARGIN_Y = 28
HDR_H = 22

cell_w = (PW - 2 * MARGIN_X) / COLS
cell_h = (PH - MARGIN_Y - HDR_H - 10) / ROWS

pdf = rl_canvas.Canvas(OUT, pagesize=landscape(A4))
pdf.setTitle('PANALCOR S.L. - Codigos QR Maquinas')

def draw_header(c, pg):
    c.setFillColorRGB(0.788, 0.635, 0.153)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(MARGIN_X, PH - 18, 'PANALCOR S.L.  -  Codigos QR por Maquina (escanear con movil)')
    c.setFont('Helvetica', 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawRightString(PW - MARGIN_X, PH - 18, 'Pag. ' + str(pg))
    c.setStrokeColorRGB(0.788, 0.635, 0.153)
    c.setLineWidth(0.5)
    c.line(MARGIN_X, PH - 22, PW - MARGIN_X, PH - 22)

per_page = COLS * ROWS
page = 1
draw_header(pdf, page)

for i, m in enumerate(MAQUINAS):
    if i > 0 and i % per_page == 0:
        pdf.showPage()
        page += 1
        draw_header(pdf, page)

    col = i % COLS
    row = (i // COLS) % ROWS

    card_img = make_card(m)
    buf = io.BytesIO()
    card_img.save(buf, 'PNG', dpi=(300, 300))
    buf.seek(0)

    # Escalar para que quepa bien en la celda con un poco de margen
    scale = min((cell_w - 8) / CW, (cell_h - 8) / CH)
    w_pt = CW * scale
    h_pt = CH * scale
    x = MARGIN_X + col * cell_w + (cell_w - w_pt) / 2
    y = PH - HDR_H - MARGIN_Y - (row + 1) * cell_h + (cell_h - h_pt) / 2

    pdf.drawImage(ImageReader(buf), x, y,
                  width=w_pt, height=h_pt,
                  preserveAspectRatio=True)

pdf.save()
print('Listo: ' + OUT)
print('Total: ' + str(len(MAQUINAS)) + ' maquinas en ' + str(page) + ' paginas (' + str(COLS) + 'x' + str(ROWS) + ' por pagina)')
