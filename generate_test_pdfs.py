import os
import sys

# Certifique-se de que o diretório do projeto está no sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app

OUT_DIR = os.path.join(PROJECT_ROOT, 'static', 'relatorios')
os.makedirs(OUT_DIR, exist_ok=True)

client = app.test_client()

endpoints = {
    'notas': '/relatorios/notas?formato=pdf',
    'alunos': '/relatorios/alunos?formato=pdf',
    'turmas': '/relatorios/turmas?formato=pdf',
    'disciplinas': '/relatorios/disciplinas?formato=pdf',
    'frequencia': '/relatorios/frequencia?formato=pdf',
    'conteudo': '/relatorios/conteudo?formato=pdf',
    'boletim': '/relatorios/boletim?formato=pdf'
}

print('Iniciando geração de PDFs de teste...')
for name, url in endpoints.items():
    try:
        resp = client.get(url)
        filename = os.path.join(OUT_DIR, f"test_{name}.pdf")
        with open(filename, 'wb') as f:
            f.write(resp.data)
        print(f'{name}: status={resp.status_code}, content_type={resp.content_type}, bytes={len(resp.data)}, saved={filename}')
    except Exception as e:
        print(f'{name}: erro ao gerar ->', e)

print('Concluído.')
