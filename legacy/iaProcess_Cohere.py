import os
import time
import exportador
import json
import cohere
from dotenv import load_dotenv

load_dotenv()

# CONFIGURACIÃ“N DE COHERE
# AsegÃºrate de que en tu .env diga: COHERE_API_KEY=tu_clave_aqui
# Consigue una gratis en: https://dashboard.cohere.com/api-keys
api_key = os.environ.get("COHERE_API_KEY")

def obtener_articulos():
    import os, json
    import pdf_utils
    class VirtualArticle:
        def __init__(self, pmid, abstract):
            self.pmid = pmid
            self.abstract = abstract

    ruta_custom = "outputs/.custom_prompts.json"
    if os.path.exists(ruta_custom):
        try:
            with open(ruta_custom, "r", encoding="utf-8") as f:
                data = json.load(f)
                pdf_path = data.get("pdf_path", "")
                if pdf_path and os.path.exists(pdf_path):
                    texto = pdf_utils.extraer_texto_pdf(pdf_path)
                    if texto.strip():
                        return [VirtualArticle("PDF_Local", texto)]
        except Exception as e:
            pass
    return []

def analizar_individual(abstract, co_client):
    prompt_base = """Extrae informaciÃ³n del siguiente abstract cientÃ­fico en ESPAÃ‘OL.
Responde estrictamente con este formato JSON:
{
  "organismo": "GÃ©nero y especie",
  "usa_hongos": "SÃ­/No",
  "tecnica": "MÃ©todo principal",
  "bioremediacion": "SÃ­/No (contaminante)",
  "localizacion": "PaÃ­s o regiÃ³n",
  "hallazgo": "Resultado principal"
}
Abstract: {abstract}"""
    ruta_custom = "outputs/.custom_prompts.json"
    if os.path.exists(ruta_custom):
        try:
            with open(ruta_custom, "r", encoding="utf-8") as f:
                prompt_base = json.load(f).get("individual", prompt_base)
        except: pass

    prompt = prompt_base.replace("{abstract}", abstract)
    
    for attempt in range(3):
        try:
            response = co_client.chat(
                model="command-r-08-2024", # Modelo muy rÃ¡pido y eficiente
                message=prompt,
            )
            respuesta = response.text
            break
        except Exception as e:
            if "429" in str(e):
                print(f"\n[DEBUG] LÃ­mite de cuota o rate limit. Esperando 15s... (Intento {attempt+1}/3)")
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
    prompt_base = """ActÃºa como un analista cientÃ­fico de alto nivel. Basado en los siguientes datos extraÃ­dos de abstracts, genera un reporte estructurado y visualmente claro en ESPAÃ‘OL. 
    
Es OBLIGATORIO que incluyas tablas Markdown (cuadros) para resumir la informaciÃ³n de manera elegante.

Estructura requerida:
1. **EstadÃ­stica de organismos**: Crea un cuadro (Markdown table) con las columnas 'Organismo' y 'Frecuencia/Apariciones'.
2. **Uso de hongos**: Un resumen analÃ­tico sobre el protagonismo de los hongos en estos estudios.
3. **Mapa de BiorremediaciÃ³n**: Crea una tabla cruzada detallando 'Contaminante', 'Organismo asociado' y 'TÃ©cnica utilizada'.
4. **ConclusiÃ³n Global**: Una sÃ­ntesis profesional sobre el estado del arte y hacia dÃ³nde apunta la investigaciÃ³n.

Datos a procesar: 
{datos}"""
    ruta_custom = "outputs/.custom_prompts.json"
    if os.path.exists(ruta_custom):
        try:
            with open(ruta_custom, "r", encoding="utf-8") as f:
                prompt_base = json.load(f).get("global", prompt_base)
        except: pass

    prompt = prompt_base.replace("{datos}", json.dumps(datos))
    try:
        # Para el meta-anÃ¡lisis general usamos su modelo mÃ¡s potente (Plus)
        response = co_client.chat(
            model="command-r-plus-08-2024", 
            message=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Error generando reporte final: {e}")
        return None

def main():
    
    if not api_key:
        print("FALTA API KEY: AÃ±ade 'COHERE_API_KEY' a tu archivo .env antes de usar este u otros scripts.")
        return
        
    co_client = cohere.Client(api_key)
    articulos = obtener_articulos()[:20]
    
    if not articulos:
        print("No se seleccionó ningún archivo PDF.")
        return

    print(f"--- Iniciando con Cohere (Command-R) ---")
    print(f"Procesando {len(articulos)} artÃ­culos...\n")
    
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
        print("\nGenerando metaanÃ¡lisis...")
        reporte = generar_metaanalisis_final(resultados, co_client)
        
        print("\n" + "="*60)
        print(" REPORTE TÃ‰CNICO Y ESTADÃSTICO ".center(60, "="))
        print(reporte)
        
        if reporte:
            with open("outputs/metaanalisis_cohere.txt", "w", encoding="utf-8") as f:
                f.write(reporte)
            print(f"\nðŸ’¾ Guardado en: outputs/metaanalisis_cohere.txt")
        exportador.guardar_csv(resultados, "outputs/metaanalisis_cohere.csv")
            
if __name__ == "__main__":
    main()

