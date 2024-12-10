from flask import Flask, render_template, request, send_file
import PyPDF2
import re
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import logging

app = Flask(__name__)

# Configuração de logging para monitorar a aplicação
logging.basicConfig(level=logging.INFO)

# Definir o caminho do template PDF, podendo ser configurado via variável de ambiente
TEMPLATE_PATH = os.getenv('PDF_TEMPLATE_PATH', 'receituariopsico.pdf')

# Limitar o tamanho máximo do arquivo para 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


def extrair_informacoes(conteudo_pdf: bytes):
    """
    Extrai informações específicas de um arquivo PDF.
    Retorna um dicionário com Data, Avisos e Pacientes.
    """
    try:
        leitor = PyPDF2.PdfReader(io.BytesIO(conteudo_pdf))
        conteudo = ""
        for pagina in leitor.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                conteudo += texto_pagina

        # Definição das expressões regulares para extração
        padrao_data = r"Data:\s*(\d{2}/\d{2}/\d{4})"
        padrao_aviso = r"\d{2}:\d{2}\s+(\d{6})"
        padrao_paciente = r"(\d{6})\s+SL\s+\d+\s+\d+\s+\w+\s+\d+\s+([A-Za-z\s]+)"

        # Extração dos dados usando regex
        data = re.search(padrao_data, conteudo)
        avisos = re.findall(padrao_aviso, conteudo)
        pacientes = re.findall(padrao_paciente, conteudo)

        logging.info("Informações extraídas com sucesso.")
        return {
            "Data": data.group(1) if data else "Não encontrada",
            "Avisos": avisos,
            "Pacientes": pacientes
        }
    except PyPDF2.errors.PdfReadError as e:
        logging.error(f"Erro ao ler o PDF: {e}")
        return {"erro": "Erro ao ler o arquivo PDF."}
    except Exception as e:
        logging.error(f"Erro inesperado ao extrair informações: {e}")
        return {"erro": "Ocorreu um erro inesperado durante a extração."}


def gerar_pdf_com_dados(template_path, dados):
    """
    Gera um novo PDF combinando o template com os dados extraídos.
    Cada paciente e aviso são inseridos em uma nova página.
    """
    try:
        # Carrega o template PDF
        leitor_template = PdfReader(template_path)
        escritor = PdfWriter()

        pacientes = dados.get("Pacientes", [])
        avisos = dados.get("Avisos", [])
        total_paginas_template = len(leitor_template.pages)

        # Determina o número total de páginas necessárias
        total_paginas = len(pacientes)

        for i in range(total_paginas):
            # Cria um PDF em memória para adicionar os textos
            pacote = io.BytesIO()
            can = canvas.Canvas(pacote, pagesize=A4)
            can.setFont("Helvetica", 12)

            # **Coordenadas**
            data_coords = (385, 727)       # Data
            paciente_coords = (103, 744)   # Paciente
            aviso_coords = (145, 727)      # Aviso

            # Adiciona a Data
            data_formatada = dados['Data'].replace("/", "   ")
            can.drawString(data_coords[0], data_coords[1], data_formatada)

            # Adiciona o Nome do Paciente
            paciente_nome = pacientes[i][1].replace('\n', ' ').strip()
            can.drawString(paciente_coords[0], paciente_coords[1], paciente_nome)

            # Adiciona o Aviso correspondente, se existir
            if i < len(avisos):
                aviso_texto = avisos[i].strip()
                can.drawString(aviso_coords[0], aviso_coords[1], aviso_texto)

            # Finaliza a página em memória
            can.showPage()
            can.save()
            pacote.seek(0)

            # Carrega a página gerada com reportlab
            texto_pdf = PdfReader(pacote)
            texto_pagina = texto_pdf.pages[0]

            # Carrega a página do template (copia para evitar modificação direta)
            template_pagina = leitor_template.pages[i % total_paginas_template]

            # Cria um novo PDF com a página do template e a sobreposição do texto
            novo_pdf = PdfWriter()
            novo_pdf.add_page(template_pagina)
            novo_pdf.pages[0].merge_page(texto_pagina)

            # Adiciona a página combinada ao PDF final
            escritor.add_page(novo_pdf.pages[0])

        # Gera o PDF final em memória
        saida = io.BytesIO()
        escritor.write(saida)
        saida.seek(0)
        logging.info("PDF final gerado com sucesso.")
        return saida

    except Exception as e:
        logging.error(f"Erro ao gerar PDF com dados: {e}")
        return None


@app.route('/')
def index():
    """
    Rota principal que renderiza a página HTML para upload e processamento do PDF.
    """
    return render_template('painelreceituariopsico.html')


@app.route('/processar-pdf', methods=['POST'])
def processar_pdf():
    """
    Rota para processar o PDF enviado pelo usuário.
    Extrai as informações e gera um novo PDF combinado.
    """
    if 'pdf_file' not in request.files:
        logging.warning("Nenhum arquivo enviado na requisição.")
        return "Nenhum arquivo enviado", 400

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        logging.warning("Nenhum arquivo selecionado pelo usuário.")
        return "Nenhum arquivo selecionado", 400

    if not pdf_file.filename.lower().endswith('.pdf'):
        logging.warning("Arquivo enviado não é um PDF válido.")
        return "O arquivo enviado não é um PDF válido.", 400

    try:
        pdf_bytes = pdf_file.read()
        informacoes = extrair_informacoes(pdf_bytes)

        # Verifica se houve erro na extração
        if "erro" in informacoes:
            return informacoes["erro"], 500

        # Gera o PDF final já combinado
        pdf_final = gerar_pdf_com_dados(TEMPLATE_PATH, informacoes)

        if pdf_final is None:
            return "Erro ao gerar o PDF final.", 500

        # Retorna o PDF para download
        return send_file(
            pdf_final,
            as_attachment=True,
            download_name="resultado_final.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        logging.error(f"Erro no processamento do PDF: {e}")
        return f"Ocorreu um erro durante o processamento: {e}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # nosec

