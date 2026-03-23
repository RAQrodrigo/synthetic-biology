import os
import time
from groq import Groq
from pony.orm import db_session, select
from database import Article, init_db
from dotenv import load_dotenv

load_dotenv()

# Configuración
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

@db_session
def obtener_articulos():
    # Traemos todos y filtramos en Python para evitar errores de descompilación en Python 3.11+
    todos = Article.select()[:] 
    return [a for a in todos if a.abstract and a.abstract.strip() != ""]

def analizar_individual(abstract):
    """Analiza un abstract individualmente para extraer lo esencial"""
    prompt = f"""
    Eres un experto en investigación médica. Resume este abstract en 3 puntos clave:
    1. Objetivo principal.
    2. Resultado más importante.
    3. Conclusión de los autores.
    
    Responde estrictamente en español.
    Abstract: {abstract}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def generar_metaanalisis_final(sintesis_acumulada):
    """Toma los 20 análisis individuales y crea el reporte final"""
    prompt = f"""
    Eres un científico de datos médicos. Basado en los siguientes resúmenes de múltiples estudios, 
    redacta un metaanálisis cualitativo estructurado en ESPAÑOL:
    1. Consenso general de la literatura analizada.
    2. Contradicciones detectadas entre estudios.
    3. Limitaciones comunes y vacíos de conocimiento.
    
    Datos de los estudios:
    {sintesis_acumulada}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def main():
    init_db()
    
    # 1. Obtener todos y recortar a los primeros 20
    lista_completa = obtener_articulos()
    articulos = lista_completa[:20] 
    
    if not articulos:
        print("No hay artículos en la base de datos para analizar.")
        return

    print(f"Analizando una muestra de {len(articulos)} artículos...")
    
    analisis_totales = []
    
    # 2. Procesar con pausas para respetar el Rate Limit
    for i, art in enumerate(articulos):
        print(f"[{i+1}/{len(articulos)}] Analizando PMID: {art.pmid}...")
        try:
            resumen = analizar_individual(art.abstract)
            analisis_totales.append(f"PMID {art.pmid}: {resumen}")
            
            # Pausa de seguridad para no saturar la API gratuita
            time.sleep(1.5) 
            
        except Exception as e:
            print(f"Error analizando {art.pmid}: {e}")

    # 3. Generar el reporte final
    print("\nGenerando Metaanálisis Global...")
    try:
        texto_para_meta = "\n\n".join(analisis_totales)
        reporte_final = generar_metaanalisis_final(texto_para_meta)
        
        print("\n" + "="*50)
        print("REPORTE DE METAANÁLISIS (Muestra de 20)")
        print("="*50)
        print(reporte_final)
        
        with open("metaanalisis_reporte_20.txt", "w", encoding="utf-8") as f:
            f.write(reporte_final)
        print(f"\nReporte guardado con éxito.")
            
    except Exception as e:
        print(f"Error en el paso final: {e}")

if __name__ == "__main__":
    main()