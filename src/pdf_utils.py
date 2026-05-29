import fitz

def extraer_texto_pdf(ruta):
    texto = ""
    try:
        doc = fitz.open(ruta)
        for page in doc:
            texto += page.get_text() + "\n"
        doc.close()
    except Exception as e:
        print(f"Error leyendo PDF ({ruta}): {e}")
    return texto
