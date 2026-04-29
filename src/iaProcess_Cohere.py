import os
import time
import json
import cohere
from pony.orm import db_session
from database import Article, init_db
from dotenv import load_dotenv

load_dotenv()

# CONFIGURACIÓN DE COHERE
# Asegúrate de que en tu .env diga: COHERE_API_KEY=tu_clave_aqui
# Consigue una gratis en: https://dashboard.cohere.com/api-keys
api_key = os.environ.get("COHERE_API_KEY")

@db_session
def obtener_articulos():
    todos = Article.select()[:]
    return [a for a in todos if a.abstract and a.abstract.strip() != ""]

def analizar_individual(abstract, co_client):
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
    
    for attempt in range(3):
        try:
            response = co_client.chat(
                model="command-r-08-2024", # Modelo muy rápido y eficiente
                message=prompt,
            )
            respuesta = response.text
            break
        except Exception as e:
            if "429" in str(e):
                print(f"\n[DEBUG] Límite de cuota o rate limit. Esperando 15s... (Intento {attempt+1}/3)")
                time.sleep(15)
                continue
            else:
                print(f"\n[DEBUG] Error en la API de Cohere: {e}")
                return None
    else:
        return None

    try:
        # Fallback de limpieza por si llega texto adicional o tags Markdown
        json_str = respuesta.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        return json.loads(json_str.strip())
    except Exception as e:
        print(f"\n[DEBUG] Error JSON: {e}")
        print(f"[DEBUG] Respuesta cruda:\n{respuesta}")
        return None

def generar_metaanalisis_final(datos, co_client):
    prompt = f"""
    Actúa como un analista científico de alto nivel. Basado en los siguientes datos extraídos de abstracts, genera un reporte estructurado y visualmente claro en ESPAÑOL. 
    
    Es OBLIGATORIO que incluyas tablas Markdown (cuadros) para resumir la información de manera elegante.

    Estructura requerida:
    1. **Estadística de organismos**: Crea un cuadro (Markdown table) con las columnas 'Organismo' y 'Frecuencia/Apariciones'.
    2. **Uso de hongos**: Un resumen analítico sobre el protagonismo de los hongos en estos estudios.
    3. **Mapa de Biorremediación**: Crea una tabla cruzada detallando 'Contaminante', 'Organismo asociado' y 'Técnica utilizada'.
    4. **Conclusión Global**: Una síntesis profesional sobre el estado del arte y hacia dónde apunta la investigación.

    Datos a procesar: 
    {json.dumps(datos)}
    """
    try:
        # Para el meta-análisis general usamos su modelo más potente (Plus)
        response = co_client.chat(
            model="command-r-plus-08-2024", 
            message=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Error generando reporte final: {e}")
        return None

def main():
    init_db()
    
    if not api_key:
        print("FALTA API KEY: Añade 'COHERE_API_KEY' a tu archivo .env antes de usar este u otros scripts.")
        return
        
    co_client = cohere.Client(api_key)
    articulos = obtener_articulos()[:20]
    
    if not articulos:
        print("No hay artículos en la base de datos.")
        return

    print(f"--- Iniciando con Cohere (Command-R) ---")
    print(f"Procesando {len(articulos)} artículos...\n")
    
    resultados = []
    
    for i, art in enumerate(articulos):
        print(f"[{i+1}/20] Procesando PMID: {art.pmid}...", end=" ", flush=True)
        
        resultado = analizar_individual(art.abstract, co_client)
        if resultado:
            resultados.append(resultado)
            print("[OK]")
        else:
            print("[ERROR]")
            
        # Cohere otorga ~10 peticiones/minuto en cuentas gratuitas recientes, o 100 en Trial. 
        # Ponemos 5s por seguridad.
        time.sleep(5) 

    if resultados:
        print("\nGenerando metaanálisis...")
        reporte = generar_metaanalisis_final(resultados, co_client)
        
        print("\n" + "="*60)
        print(" REPORTE TÉCNICO Y ESTADÍSTICO ".center(60, "="))
        print(reporte)
        
        if reporte:
            with open("outputs/metaanalisis_cohere.txt", "w", encoding="utf-8") as f:
                f.write(reporte)
            print(f"\n💾 Guardado en: outputs/metaanalisis_cohere.txt")
            
if __name__ == "__main__":
    main()
