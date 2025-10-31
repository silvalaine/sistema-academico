import pdfkit
from flask import render_template
import os
import traceback
from datetime import datetime

def generate_pdf(template_name, output_file, **kwargs):
    """
    Gera um arquivo PDF a partir de um template.
    """
    try:
        print("\nDEBUG: Iniciando geração de PDF")
        print(f"DEBUG: Template: {template_name}")
        print(f"DEBUG: Arquivo de saída: {output_file}")
        
        # Renderizar o template HTML com os dados
        html_content = render_template(template_name, pdf_mode=True, **kwargs)
        print("DEBUG: Template renderizado com sucesso")
        
        # Configurações para o pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '1.0cm',
            'margin-right': '1.0cm',
            'margin-bottom': '1.0cm',
            'margin-left': '1.0cm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # Configurar caminho do wkhtmltopdf se fornecido via variável de ambiente
        wkhtmltopdf_path = os.environ.get('WKHTMLTOPDF_PATH')
        print(f"DEBUG: Caminho do wkhtmltopdf: {wkhtmltopdf_path}")
        
        config = None
        if wkhtmltopdf_path:
            try:
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                print("DEBUG: Configuração do wkhtmltopdf criada com sucesso")
            except Exception as e:
                print(f"DEBUG: Erro ao configurar wkhtmltopdf: {str(e)}")
                # fallback para configuração padrão; erro será tratado abaixo
                config = None

        # Gerar o PDF
        if config:
            pdfkit.from_string(html_content, output_file, options=options, configuration=config)
        else:
            pdfkit.from_string(html_content, output_file, options=options)
        return True, output_file
    except Exception as e:
        # Registrar o erro em um arquivo de log para diagnóstico
        try:
            log_path = os.path.join('static', 'relatorios', 'pdf_errors.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Erro ao gerar PDF: {str(e)}\n")
                f.write(traceback.format_exc())
                f.write('\n---\n')
        except Exception:
            pass
        print(f"Erro ao gerar PDF: {str(e)}")
        return False, str(e)