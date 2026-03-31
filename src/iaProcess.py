import os
import time
from groq import Groq
from pony.orm import db_session
from database import Article, init_db
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@db_session
def obtener_articulos():
    todos = Article.select()[:] 
    return [a for a in todos if a.abstract and a.abstract.strip() != ""]

def analizar_individual(abstract):
    """Extrae datos técnicos específicos de cada abstract"""
    prompt = f"""
    Eres un experto en Biotecnología y Micología Ambiental. 
    Analiza el siguiente abstract y extrae estos datos en formato de lista breve:
    - ORGANISMO: (Género y especie)
    - USA HONGOS: (Sí/No y cuáles)
    - TÉCNICA: (Método principal usado)
    - BIOREMEDIACIÓN: (Sí/No y qué contaminante)
    - LOCALIZACIÓN: (País/Región del estudio)
    - HALLAZGO: (Una frase corta)

    Abstract: {abstract}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def generar_metaanalisis_final(sintesis_acumulada):
    """Genera un reporte estadístico basado en los datos extraídos"""
    prompt = f"""
    Actúa como un analista de datos científicos. Basado en la información de estos 20 estudios, 
    redacta un reporte de tendencias en ESPAÑOL:
    1. ESTADÍSTICA DE ORGANISMOS: ¿Qué se estudia más?
    2. RELEVANCIA MICOLÓGICA: Resumen del uso de hongos en la muestra.
    3. FOCO EN BIOREMEDIACIÓN: Tipos de contaminantes y efectividad reportada.
    4. MAPA TÉCNICO: ¿Qué tecnologías predominan?
    5. CONCLUSIÓN GLOBAL: ¿Hacia dónde va la investigación en este grupo de papers?

    Datos extraídos:
    {sintesis_acumulada}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def main():
    init_db()
    articulos = obtener_articulos()[:20] # Solo los primeros 20
    
    if not articulos:
        print("No hay artículos.")
        return

    print(f"Extrayendo datos biotecnológicos de {len(articulos)} artículos...")
    
    analisis_totales = []
    for i, art in enumerate(articulos):
        print(f"[{i+1}/20] Procesando PMID: {art.pmid}...")
        try:
            # Aquí la IA ya extrae técnica, localización, hongos, etc.
            resumen_tecnico = analizar_individual(art.abstract)
            analisis_totales.append(f"--- DATOS ARTÍCULO {art.pmid} ---\n{resumen_tecnico}")
            time.sleep(1.5) 
        except Exception as e:
            print(f"Error en {art.pmid}: {e}")

    print("\nSintetizando tendencias y estadísticas...")
    try:
        reporte_final = generar_metaanalisis_final("\n\n".join(analisis_totales))
        
        print("\n" + "="*60)
        print(" REPORTE TÉCNICO Y ESTADÍSTICO ".center(60, "="))
        print(reporte_final)
        
        with open("metaanalisis_biotec_20.txt", "w", encoding="utf-8") as f:
            f.write(reporte_final)
            
    except Exception as e:
        print(f"Error final: {e}")

if __name__ == "__main__":
    main()