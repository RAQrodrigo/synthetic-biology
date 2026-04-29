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

import json

def analizar_individual(abstract):
    """Extrae datos técnicos específicos de cada abstract"""
    prompt = f"""
    Extrae información del siguiente abstract científico en ESPAÑOL.
    Responde estrictamente con este formato JSON:
    {{
      "organismo": "Género y especie",
      "usa_hongos": "Sí/No",
      "tecnica": "Método principal",
      "bioremediacion": "Sí/No (contaminante)",
      "localizacion": "País o región",
      "hallazgo": "Resultado principal"
    }}
    Abstract: {abstract}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    respuesta = chat_completion.choices[0].message.content
    try:
        return json.loads(respuesta)
    except Exception as e:
        # Fallback en caso de que Llama envié markdown
        try:
            return json.loads(respuesta.strip().strip("`").replace("json\n", ""))
        except:
            return None

def generar_metaanalisis_final(datos):
    """Genera un reporte estadístico basado en los datos extraídos"""
    prompt = f"""
    Actúa como analista científico. Genera un reporte detallado en ESPAÑOL:
    1. Estadística de organismos
    2. Uso de hongos
    3. Tipos de biorremediación
    4. Conclusión global
    Datos: {json.dumps(datos)}
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

    print(f"--- Iniciando con Llama 3.3 (Groq) ---")
    print(f"Extrayendo datos biotecnológicos de {len(articulos)} artículos...\n")
    
    analisis_totales = []
    for i, art in enumerate(articulos):
        print(f"[{i+1}/20] Procesando PMID: {art.pmid}...", end=" ", flush=True)
        try:
            # Aquí la IA ya extrae técnica, localización, hongos, etc.
            resumen_tecnico = analizar_individual(art.abstract)
            if resumen_tecnico:
                analisis_totales.append(resumen_tecnico)
                print("[OK]")
            else:
                print("[ERROR]")
            time.sleep(1.5) 
        except Exception as e:
            print(f"[ERROR en {art.pmid}: {e}]")

    print("\nSintetizando tendencias y estadísticas...")
    try:
        reporte_final = generar_metaanalisis_final(analisis_totales)
        
        print("\n" + "="*60)
        print(" REPORTE TÉCNICO Y ESTADÍSTICO ".center(60, "="))
        print(reporte_final)
        
        with open("metaanalisis_llama_groq.txt", "w", encoding="utf-8") as f:
            f.write(reporte_final)
            
    except Exception as e:
        print(f"Error final: {e}")

if __name__ == "__main__":
    main()