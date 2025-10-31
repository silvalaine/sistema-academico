import sys
import traceback

try:
    # Importar a aplicação do flask. Se houver erro durante a importação,
    # vamos imprimir o traceback para que apareça nos logs do Vercel.
    from app import app as application
except Exception:
    traceback.print_exc()
    # Re-levantar para que o ambiente que hospeda (Vercel) registre o erro.
    raise

if __name__ == '__main__':
    application.run()