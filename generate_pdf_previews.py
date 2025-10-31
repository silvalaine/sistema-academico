import os
import sys
from glob import glob

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(PROJECT_ROOT, 'static', 'relatorios')
OUT_DIR = os.path.join(PDF_DIR, 'previews')
os.makedirs(OUT_DIR, exist_ok=True)

pdfs = glob(os.path.join(PDF_DIR, 'test_*.pdf'))
if not pdfs:
    print('Nenhum PDF de teste encontrado em', PDF_DIR)
    sys.exit(1)

print('Encontrados', len(pdfs), 'PDF(s). Tentando gerar previews...')

for pdf in pdfs:
    name = os.path.splitext(os.path.basename(pdf))[0]
    out_png = os.path.join(OUT_DIR, f'{name}.png')
    try:
        # Tentar PyMuPDF (fitz)
        try:
            import fitz
            doc = fitz.open(pdf)
            page = doc.load_page(0)
            mat = fitz.Matrix(2, 2)  # escala para melhorar resolução
            pix = page.get_pixmap(matrix=mat, alpha=False)
            pix.save(out_png)
            print(f'{name}: gerado com PyMuPDF -> {out_png}')
            continue
        except Exception as e:
            fitz_err = e
        # Tentar pdf2image
        try:
            from pdf2image import convert_from_path, convert_from_bytes
            # Tentamos convert_from_path; caso falhe por falta do poppler, tentamos convert_from_bytes
            try:
                images = convert_from_path(pdf, dpi=150)
            except Exception:
                with open(pdf, 'rb') as f:
                    data = f.read()
                images = convert_from_bytes(data, dpi=150)
            if images:
                images[0].save(out_png, 'PNG')
                print(f'{name}: gerado com pdf2image -> {out_png}')
                continue
        except Exception as e:
            p2i_err = e
        # Se chegou aqui, não conseguiu usar bibliotecas
        print(f'{name}: falha ao gerar preview. Erros: fitz: {getattr(fitz_err, "", fitz_err)} | pdf2image: {getattr(p2i_err, "", p2i_err)}')
    except Exception as exc:
        print(f'{name}: erro inesperado ->', exc)

print('Concluído.')
