from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def criar_pdf_de_ajuste(coordenadas=None):
    """
    Cria um PDF com marcações para ajudar a identificar as coordenadas.
    """
    c = canvas.Canvas("ajuste_coordenadas.pdf", pagesize=A4)
    largura, altura = A4

    # Desenhar linhas horizontais e verticais a cada 50 unidades
    for x in range(0, int(largura), 50):
        c.line(x, 0, x, altura)
    for y in range(0, int(altura), 50):
        c.line(0, y, largura, y)

    # Se houver coordenadas específicas para marcar
    if coordenadas:
        c.setStrokeColorRGB(1, 0, 0)  # Vermelho para destaque
        c.setLineWidth(2)
        for coord in coordenadas:
            c.circle(coord[0], coord[1], 5, fill=1)
            c.drawString(coord[0] + 10, coord[1], f"({coord[0]}, {coord[1]})")

    c.save()

# Exemplo de uso:
# Cria um PDF com uma grade e marcações em coordenadas específicas
criar_pdf_de_ajuste([(150, 700), (400, 750), (150, 650)])

