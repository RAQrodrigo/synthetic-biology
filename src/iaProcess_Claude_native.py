import os
import time
import json
from anthropic import Anthropic
from pony.orm import db_session
from database import Article, init_db
from dotenv import load_dotenv

load_dotenv()

# Configuración directa de Anthropic (Claude)
client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

@db_session
def obtener_articulos():
    todos = Article.select()[:]
    return [a for a in todos if a.abstract and a.abstract.strip() != ""]

def llamar_ia(prompt, retries=5):
    for attempt in range(retries):
        try:
            message = client.messages.create(
                # Puedes usar "claude-3-haiku-20240307" o "claude-3-5-sonnet-latest"
                model="claude-3-haiku-20240307", 
                max_tokens=1000,
                temperature=0,
                system="Eres un sistema de extracción de información científica preciso y estricto.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate-limited" in error_msg.lower():
                print(f"\n[DEBUG] Límite de cuota o rate limit. Esperando 30s... (Intento {attempt+1}/{retries})")
                time.sleep(30)
                continue
            else:
                print(f"\n[DEBUG] Error detallado: {error_msg}")
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
    respuesta = llamar_ia(prompt)
    if not respuesta:
        return None

    try:
        # Fallback de limpieza por si Claude añade etiquetas markdown
        json_str = respuesta.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        return json.loads(json_str.strip())
    except:
        print("[DEBUG] Error parseando JSON, respuesta cruda:")
        print(respuesta)
        return None

def generar_metaanalisis_final(datos):
    prompt = f"""
    Actúa como analista de datos científicos. Basado en los datos proporcionados, genera un reporte cuantitativo usando Markdown en ESPAÑOL.
    El reporte debe contener principalmente datos duros en formato de TABLAS y minimizar el texto narrativo.
    
    Genera obligatoriamente:
    1. Una tabla con el conteo de organismos encontrados (Organismo | Frecuencia), agrupados por nombre.
    2. Una tabla sobre uso de hongos (Sí/No | Frecuencia).
    3. Una tabla sobre tipos de biorremediación (Contaminante o Técnica | Frecuencia).
    
    Agrega una muy breve conclusión global en viñetas al final. No agregues texto introductorio innecesario.
    
    Datos: {json.dumps(datos)}
    """
    return llamar_ia(prompt)

def main():
    init_db()
    articulos = obtener_articulos()[:20]

    if not articulos:
        print("No hay artículos en la base de datos.")
        return

    print(f"--- Iniciando con Claude (API Nativa) ---")
    print(f"Procesando {len(articulos)} artículos...\n")

    resultados = []

    for i, art in enumerate(articulos):
        print(f"[{i+1}/20] PMID: {art.pmid}...", end=" ", flush=True)

        resultado = analizar_individual(art.abstract)

        if resultado is None:
            print(" Reintentando...", end=" ", flush=True)
            time.sleep(2)
            resultado = analizar_individual(art.abstract)

        if resultado:
            resultados.append(resultado)
            print("[OK]")
        else:
            print("[ERROR]")

        time.sleep(2)

    print("\nGenerando metaanálisis...\n")
    reporte = generar_metaanalisis_final(resultados)

    print("\n" + "="*60)
    print(" REPORTE FINAL ".center(60, "="))
    print(reporte)

    with open("outputs/metaanalisis_claude_nativo.txt", "w", encoding="utf-8") as f:
        f.write(reporte or "Error generando reporte")

    print(f"\n💾 Guardado en: outputs/metaanalisis_claude_nativo.txt")

if __name__ == "__main__":
    main()
