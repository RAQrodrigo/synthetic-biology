import os
import time
from openai import OpenAI
from pony.orm import db_session
from database import Article, init_db
from dotenv import load_dotenv

load_dotenv()

# Configuración de OpenRouter
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY"),
)

@db_session
def obtener_articulos():
    todos = Article.select()[:] 
    return [a for a in todos if a.abstract and a.abstract.strip() != ""]

def llamar_ia(prompt):
    """Llamada a DeepSeek a través de OpenRouter"""
    try:
        completion = client.chat.completions.create(
          # Usamos la versión gratuita de DeepSeek Chat
          model="deepseek/deepseek-chat:free", 
          messages=[
            {
              "role": "user",
              "content": prompt
            }
          ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en la API: {e}"

def analizar_individual(abstract):
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
    return llamar_ia(prompt)

def generar_metaanalisis_final(sintesis_acumulada):
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
    return llamar_ia(prompt)

def main():
    init_db()
    articulos = obtener_articulos()[:20] 
    
    if not articulos:
        print("No hay artículos en la base de datos.")
        return

    print(f"Extrayendo datos con DeepSeek (via OpenRouter) de {len(articulos)} artículos...")
    
    analisis_totales = []
    for i, art in enumerate(articulos):
        print(f"[{i+1}/20] Procesando PMID: {art.pmid}...")
        resumen_tecnico = analizar_individual(art.abstract)
        
        # Manejo de errores simple
        if "Error" in resumen_tecnico:
            print(f"Fallo en {art.pmid}, reintentando...")
            time.sleep(2)
            resumen_tecnico = analizar_individual(art.abstract)

        analisis_totales.append(f"--- DATOS ARTÍCULO {art.pmid} ---\n{resumen_tecnico}")
        # Los modelos gratuitos suelen tener límites de velocidad (Rate Limits)
        time.sleep(2) 

    print("\nGenerando Metaanálisis Global...")
    reporte_final = generar_metaanalisis_final("\n\n".join(analisis_totales))
    
    print("\n" + "="*60)
    print(" REPORTE TÉCNICO DEEPSEEK (OPENROUTER) ".center(60, "="))
    print(reporte_final)
    
    with open("metaanalisis_deepseek_free.txt", "w", encoding="utf-8") as f:
        f.write(reporte_final)

if __name__ == "__main__":
    main()