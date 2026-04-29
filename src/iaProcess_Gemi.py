import os
import time
import json
from openai import OpenAI
from pony.orm import db_session
from database import Article, init_db
from dotenv import load_dotenv

load_dotenv()

# CONFIGURACIÓN DE OPENROUTER PARA GEMINI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

@db_session
def obtener_articulos():
    todos = Article.select()[:]
    return [a for a in todos if a.abstract and a.abstract.strip() != ""]

def llamar_ia(prompt, es_json=False, retries=3):
    for attempt in range(retries):
        try:
            # En OpenRouter usamos 'google/gemini-2.5-flash'
            completion = client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "Eres un sistema de extracción de información científica preciso y estricto."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1500,
                response_format={"type": "json_object"} if es_json else None
            )
            return completion.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                print(f"\n[DEBUG] Límite de cuota o rate limit. Esperando 10s... (Intento {attempt+1}/{retries})")
                time.sleep(10)
            else:
                print(f"\n[DEBUG] Error en la API mediante OpenRouter: {error_str}")
                return None
    return None

def analizar_individual(abstract):
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
    respuesta = llamar_ia(prompt, es_json=True)
    if not respuesta: return None

    try:
        json_str = respuesta.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        return json.loads(json_str.strip())
    except:
        return None

def generar_metaanalisis_final(datos):
    prompt = f"""
    Actúa como analista científico. Genera un reporte detallado en ESPAÑOL:
    1. Estadística de organismos
    2. Uso de hongos
    3. Tipos de biorremediación
    4. Conclusión global
    Datos: {json.dumps(datos)}
    """
    return llamar_ia(prompt, es_json=False)

def main():
    init_db()
    articulos = obtener_articulos()[:20]

    if not articulos:
        print("No hay artículos en la base de datos.")
        return

    print(f"--- Iniciando con Gemini (OpenRouter) ---")
    resultados = []

    for i, art in enumerate(articulos):
        print(f"[{i+1}/20] PMID: {art.pmid}...", end=" ", flush=True)
        
        resultado = analizar_individual(art.abstract)
        
        if resultado:
            resultados.append(resultado)
            print("[OK]")
        else:
            print("[ERROR]")
        
        time.sleep(2)

    if resultados:
        print("\nGenerando metaanálisis...")
        reporte = generar_metaanalisis_final(resultados)
        
        print("\n" + "="*60)
        print(reporte)
        
        with open("metaanalisis_gemini_openrouter.txt", "w", encoding="utf-8") as f:
            f.write(reporte or "Error")
        print(f"\n💾 Guardado en: metaanalisis_gemini_openrouter.txt")

if __name__ == "__main__":
    main()