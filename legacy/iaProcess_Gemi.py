import os
import time
import exportador
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# CONFIGURACIÃ“N DE OPENROUTER PARA GEMINI
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

def llamar_ia(prompt, es_json=False, retries=3):
    for attempt in range(retries):
        try:
            # En OpenRouter usamos 'google/gemini-2.5-flash'
            completion = client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "Eres un sistema de extracciÃ³n de informaciÃ³n cientÃ­fica preciso y estricto."},
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
                print(f"\n[DEBUG] LÃ­mite de cuota o rate limit. Esperando 10s... (Intento {attempt+1}/{retries})")
                time.sleep(10)
            else:
                print(f"\n[DEBUG] Error en la API mediante OpenRouter: {error_str}")
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
    prompt_base = """ActÃºa como analista cientÃ­fico. Genera un reporte detallado en ESPAÃ‘OL:
1. EstadÃ­stica de organismos
2. Uso de hongos
3. Tipos de biorremediaciÃ³n
4. ConclusiÃ³n global
Datos: {datos}"""
    ruta_custom = "outputs/.custom_prompts.json"
    if os.path.exists(ruta_custom):
        try:
            with open(ruta_custom, "r", encoding="utf-8") as f:
                prompt_base = json.load(f).get("global", prompt_base)
        except: pass

    prompt = prompt_base.replace("{datos}", json.dumps(datos))
    return llamar_ia(prompt, es_json=False)

def main():
    articulos = obtener_articulos()[:20]

    if not articulos:
        print("No se seleccionó ningún archivo PDF.")
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
        print("\nGenerando metaanÃ¡lisis...")
        reporte = generar_metaanalisis_final(resultados)
        
        print("\n" + "="*60)
        print(reporte)
        
        with open("outputs/metaanalisis_gemini_openrouter.txt", "w", encoding="utf-8") as f:
            f.write(reporte or "Error")
        print(f"\nðŸ’¾ Guardado en: metaanalisis_gemini_openrouter.txt")
        exportador.guardar_csv(resultados, "outputs/metaanalisis_gemini_openrouter.csv")

if __name__ == "__main__":
    main()
