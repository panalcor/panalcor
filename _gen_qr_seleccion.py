import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import gen_qr_pdf as g

ids_imprimir = {
  'MAQ-151','MAQ-153','MAQ-156'
}
maquinas_sel = [m for m in g.MAQUINAS if m['id'] in ids_imprimir]

OUT = 'QR_para_imprimir.pdf'
PW, PH = A4
COLS, ROWS = 3, 2
MARGIN_X, MARGIN_Y = g.MARGIN_X, g.MARGIN_Y
HDR_H, CW, CH = g.HDR_H, g.CW, g.CH
cell_w = (PW - 2*MARGIN_X) / COLS
cell_h = (PH - HDR_H - 2*MARGIN_Y) / ROWS

pdf = canvas.Canvas(OUT, pagesize=A4)
per_page = COLS * ROWS
page = 1
g.draw_header(pdf, page)

for i, m in enumerate(maquinas_sel):
    if i > 0 and i % per_page == 0:
        pdf.showPage()
        page += 1
        g.draw_header(pdf, page)
    col = i % COLS
    row = (i // COLS) % ROWS
    card_img = g.make_card(m)
    buf = io.BytesIO()
    card_img.save(buf, 'PNG', dpi=(300, 300))
    buf.seek(0)
    scale = min((cell_w - 8) / CW, (cell_h - 8) / CH)
    w_pt = CW * scale
    h_pt = CH * scale
    x = MARGIN_X + col * cell_w + (cell_w - w_pt) / 2
    y = PH - HDR_H - MARGIN_Y - (row + 1) * cell_h + (cell_h - h_pt) / 2
    pdf.drawImage(ImageReader(buf), x, y, width=w_pt, height=h_pt, preserveAspectRatio=True)

pdf.save()
print(f'Listo: {OUT}')
print(f'Total: {len(maquinas_sel)} maquinas en {page} paginas')
