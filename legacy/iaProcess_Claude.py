import os
import time
import exportador
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ConfiguraciÃ³n de Claude a travÃ©s de OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

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

def llamar_ia(prompt, retries=5):
    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                # En OpenRouter, debes usar el prefijo anthropic/
                model="anthropic/claude-3-haiku", 
                messages=[
                    {"role": "system", "content": "Eres un sistema de extracciÃ³n de informaciÃ³n cientÃ­fica preciso y estricto."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            return completion.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate-limited" in error_msg.lower():
                print(f"\n[DEBUG] LÃ­mite de cuota o rate limit. Esperando 30s... (Intento {attempt+1}/{retries})")
                time.sleep(30)
                continue
            else:
                print(f"\n[DEBUG] Error detallado: {error_msg}")
                return None
    return None

def analizar_individual(abstract):
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
    respuesta = llamar_ia(prompt)
    if not respuesta:
        return None

    try:
        # Fallback de limpieza por si Claude aÃ±ade etiquetas markdown como ```json
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
    prompt_base = """ActÃºa como analista de datos cientÃ­ficos. Basado en los datos proporcionados, genera un reporte cuantitativo usando Markdown en ESPAÃ‘OL.
El reporte debe contener principalmente datos duros en formato de TABLAS y minimizar el texto narrativo.

Genera obligatoriamente:
1. Una tabla con el conteo de organismos encontrados (Organismo | Frecuencia), agrupados por nombre.
2. Una tabla sobre uso de hongos (SÃ­/No | Frecuencia).
3. Una tabla sobre tipos de biorremediaciÃ³n (Contaminante o TÃ©cnica | Frecuencia).

Agrega una muy breve conclusiÃ³n global en viÃ±etas al final. No agregues texto introductorio innecesario.

Datos: {datos}"""
    ruta_custom = "outputs/.custom_prompts.json"
    if os.path.exists(ruta_custom):
        try:
            with open(ruta_custom, "r", encoding="utf-8") as f:
                prompt_base = json.load(f).get("global", prompt_base)
        except: pass

    prompt = prompt_base.replace("{datos}", json.dumps(datos))
    return llamar_ia(prompt)

def main():
    articulos = obtener_articulos()[:20]

    if not articulos:
        print("No se seleccionó ningún archivo PDF.")
        return

    print(f"--- Iniciando con Claude (OpenRouter) ---")
    print(f"Procesando {len(articulos)} artÃ­culos...\n")

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

    print("\nGenerando metaanÃ¡lisis...\n")
    reporte = generar_metaanalisis_final(resultados)

    print("\n" + "="*60)
    print(" REPORTE FINAL ".center(60, "="))
    print(reporte)

    with open("outputs/metaanalisis_claude.txt", "w", encoding="utf-8") as f:
        f.write(reporte or "Error generando reporte")

    print(f"\nðŸ’¾ Guardado en: outputs/metaanalisis_claude.txt")
        exportador.guardar_csv(resultados, "outputs/metaanalisis_claude.csv")

if __name__ == "__main__":
    main()

